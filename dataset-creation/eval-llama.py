import json
from typing import List, Dict, Any
from collections import defaultdict
import logging
import tiktoken

# --- Original Evaluation Functions ---
def normalize_value(value: Any, flexible: bool = True) -> Any:
    """Normalize a string value for flexible matching."""
    if isinstance(value, str):
        return value.strip().lower() if flexible else value
    return value

def compare_fields(gold: Any, pred: Any, flexible: bool = True) -> tuple[int, int, int]:
    """Compare two values and return (TP, FP, FN)."""
    gold_norm = normalize_value(gold, flexible)
    pred_norm = normalize_value(pred, flexible)
    
    if gold_norm == pred_norm:
        return (1, 0, 0)  # TP
    elif not gold_norm and pred_norm:  # Empty gold, non-empty pred
        return (0, 1, 0)  # FP
    elif gold_norm and not pred_norm:  # Non-empty gold, empty pred
        return (0, 0, 1)  # FN
    else:
        return (0, 1, 1)  # FP and FN (mismatch)

def evaluate_json(gold: Dict, pred: Dict, flexible: bool = True) -> Dict[str, float]:
    """Evaluate a single pair of gold and predicted JSONs, returning field-wise F1 scores."""
    tp, fp, fn = defaultdict(int), defaultdict(int), defaultdict(int)

    def recursive_compare(gold_val: Any, pred_val: Any, prefix: str = "") -> tuple[int, int, int]:
        """Recursively compare gold and predicted values, returning (TP, FP, FN)."""
        if isinstance(gold_val, dict) and isinstance(pred_val, dict):
            total_tp, total_fp, total_fn = 0, 0, 0
            for key in set(gold_val.keys()) | set(pred_val.keys()):
                g_val = gold_val.get(key, "")
                p_val = pred_val.get(key, "")
                t, f_p, f_n = recursive_compare(g_val, p_val, f"{prefix}{key}.")
                total_tp += t
                total_fp += f_p
                total_fn += f_n
            return (total_tp, total_fp, total_fn)
        
        elif isinstance(gold_val, list) and isinstance(pred_val, list):
            total_tp, total_fp, total_fn = 0, 0, 0
            matched_pred = set()
            for i, g_item in enumerate(gold_val):
                best_match = None
                best_score = (0, 1, 1)  # Worst case: no match
                for j, p_item in enumerate(pred_val):
                    if j not in matched_pred:
                        t, f_p, f_n = recursive_compare(g_item, p_item, f"{prefix}[{i}].")
                        if t > best_score[0] or (t == best_score[0] and f_p + f_n < best_score[1] + best_score[2]):
                            best_match = j
                            best_score = (t, f_p, f_n)
                if best_match is not None:
                    matched_pred.add(best_match)
                    t, f_p, f_n = best_score
                else:
                    t, f_p, f_n = (0, 0, 1)  # No match found
                total_tp += t
                total_fp += f_p
                total_fn += f_n
            # Unmatched predicted items
            for j, p_item in enumerate(pred_val):
                if j not in matched_pred:
                    t, f_p, f_n = recursive_compare("", p_item, f"{prefix}[extra].")
                    total_tp += t
                    total_fp += f_p
                    total_fn += f_n
            return (total_tp, total_fp, total_fn)
        
        else:
            t, f_p, f_n = compare_fields(gold_val, pred_val, flexible)
            field = prefix.rstrip(".")
            tp[field] += t
            fp[field] += f_p
            fn[field] += f_n
            return (t, f_p, f_n)

    recursive_compare(gold, pred)

    f1_scores = {}
    for field in tp.keys():
        precision = tp[field] / (tp[field] + fp[field]) if tp[field] + fp[field] > 0 else 0
        recall = tp[field] / (tp[field] + fn[field]) if tp[field] + fn[field] > 0 else 0
        f1_scores[field] = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0

    return f1_scores

def is_field_included(field: str, fields_to_include: List[str]) -> bool:
    """Check if a field should be included based on exact match or prefix pattern."""
    if not fields_to_include:  # If no fields specified, include all
        return True
    for pattern in fields_to_include:
        if field == pattern or (pattern.endswith(".") and field.startswith(pattern)):
            return True
    return False

def compute_macro_f1(samples: List[Dict[str, Dict]], flexible: bool = True, fields_to_include: List[str] = None) -> Dict[str, float]:
    """Compute macro F1 scores across multiple samples, optionally filtering by specified fields."""
    field_f1_sums = defaultdict(float)
    field_counts = defaultdict(int)
    
    for sample in samples:
        gold = sample["gold"]
        pred = sample["pred"]
        f1_scores = evaluate_json(gold, pred, flexible)
        for field, score in f1_scores.items():
            if is_field_included(field, fields_to_include):
                field_f1_sums[field] += score
                field_counts[field] += 1
    
    macro_f1 = {}
    for field in field_f1_sums.keys():
        macro_f1[field] = field_f1_sums[field] / field_counts[field]
    
    # Overall macro F1 (average across only included fields)
    overall_f1 = sum(macro_f1.values()) / len(macro_f1) if macro_f1 else 0
    macro_f1["overall"] = overall_f1
    
    return macro_f1

# --- Token Counting Function ---
def count_tokens(text, model_name="gpt-4o"):
    encoder = tiktoken.encoding_for_model(model_name)
    tokens = encoder.encode(text)
    return len(tokens)

# --- File Processing and Evaluation ---
def load_json_file(file_path: str) -> List[Dict]:
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("JSON file must contain a list of samples")
        return data
    except FileNotFoundError:
        logging.error(f"File {file_path} not found")
        raise
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error loading JSON file: {str(e)}")
        raise

def prepare_samples(data: List[Dict]) -> tuple[List[Dict[str, Dict]], float, float, float]:
    """Prepare samples for macro F1 computation and compute average token counts."""
    samples = []
    input_token_counts = []
    output_token_counts = []
    total_token_counts = []
    
    for item in data:
        try:
            # Load ref_json as gold standard
            gold = json.loads(item.get("ref_json", "{}"))
            
            # Handle parsed_json
            parsed_json = item.get("parsed_json")
            if parsed_json is None or parsed_json.lower() == "null":
                pred = {}  # Treat null as empty dict
                output_tokens = 0  # No tokens for null output
            else:
                try:
                    pred = json.loads(parsed_json)
                    if not isinstance(pred, dict):
                        logging.warning(f"Parsed JSON is not a dictionary for text: {item.get('text', '')[:50]}...")
                        pred = {}
                        output_tokens = 0  # Treat non-dict as empty
                    else:
                        # Count tokens for parsed_json (string representation)
                        output_tokens = count_tokens(parsed_json)
                except json.JSONDecodeError:
                    logging.warning(f"Invalid parsed JSON for text: {item.get('text', '')[:50]}...")
                    pred = {}
                    output_tokens = 0  # Treat invalid JSON as empty
            
            samples.append({"gold": gold, "pred": pred})
            
            # Count tokens for input text
            input_text = item.get("text", "")
            input_tokens = count_tokens(input_text) if input_text else 0
            input_token_counts.append(input_tokens)
            output_token_counts.append(output_tokens)
            total_token_counts.append(input_tokens + output_tokens)
        
        except json.JSONDecodeError as e:
            logging.warning(f"Invalid ref_json for text: {item.get('text', '')[:50]}... Skipping sample.")
            continue
        except Exception as e:
            logging.warning(f"Error processing sample for text: {item.get('text', '')[:50]}... {str(e)}")
            continue
    
    # Compute average token counts
    avg_input_tokens = sum(input_token_counts) / len(input_token_counts) if input_token_counts else 0
    avg_output_tokens = sum(output_token_counts) / len(output_token_counts) if output_token_counts else 0
    avg_total_tokens = sum(total_token_counts) / len(total_token_counts) if total_token_counts else 0
    
    return samples, avg_input_tokens, avg_output_tokens, avg_total_tokens

def main(file_path: str):
    """Main function to compute macro F1 scores and average token counts from JSON file."""
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Load JSON data
    data = load_json_file(file_path)
    
    # Prepare samples and compute token counts
    samples, avg_input_tokens, avg_output_tokens, avg_total_tokens = prepare_samples(data)
    logging.info(f"Prepared {len(samples)} valid samples for evaluation")
    
    # Define fields to include for filtered evaluation
    fields_to_include = [
        "compensation.",
        "blood_group",
        "bags_needed",
        "hospital_name",
        "probable_day",
        "probable_time"
    ]
    
    # Compute macro F1 for all fields
    result_all = compute_macro_f1(samples, flexible=True)
    print("Macro F1 for All fields:")
    for field, score in result_all.items():
        print(f"  {field}: {score:.4f}")
    
    # Compute macro F1 for filtered fields
    result_filtered = compute_macro_f1(samples, flexible=True, fields_to_include=fields_to_include)
    print("\nMacro F1 for Filtered fields:")
    for field, score in result_filtered.items():
        print(f"  {field}: {score:.4f}")
    
    # Print average token counts
    print(f"\nAverage Input Tokens: {avg_input_tokens:.2f}")
    print(f"Average Output Tokens: {avg_output_tokens:.2f}")
    print(f"Average Total Tokens: {avg_total_tokens:.2f}")

if __name__ == "__main__":
    file_path = "llama-out.json"
    main(file_path)