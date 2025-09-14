import json
from typing import List, Dict, Any
from collections import defaultdict
import logging
import tiktoken
import os
import string
import enchant
from json_evaluation_utils import * 

# --- Language Detection ---
english_dict = enchant.Dict("en_US")

def detect_language(text, word_threshold=0.7, ascii_threshold=0.8):
    """
    Classify a given string as one of the following:
    
    - "bn"  : Bengali (Unicode Bangla script characters)
    - "en"  : English (ASCII characters, high proportion of dictionary-valid English words)
    - "tbn" : Transliterated Bengali (ASCII characters, but words mostly not valid English)
    
    Logic:
    - If ≥30% of characters are in Bengali Unicode block → return "bn"
    - If mostly ASCII:
        - If ≥60% of words are valid English → return "en"
        - Otherwise → return "tbn"
    - If all else fails, default fallback is "en"
    
    Args:
        text (str): Input text to classify
        word_threshold (float): Minimum ratio of English dictionary words for "en"
        ascii_threshold (float): Minimum ASCII character ratio to consider for en/tbn
    
    Returns:
        str: One of "bn", "en", or "tbn"
    """
    text = text.strip()
    if not text:
        return "en"

    total_chars = len(text)
    if total_chars == 0:
        return "en"

    # Count Bengali characters using Unicode block
    bengali_chars = sum(0x0980 <= ord(c) <= 0x09FF for c in text)
    bengali_ratio = bengali_chars / total_chars

    if bengali_ratio > 0.3:
        return "bn"

    # Process ASCII / English detection
    import re
    possible_english_words = [re.sub(r'[^\w\s]', ' ', w).lower() for w in text.split()]
    possible_english_words = [w for w in possible_english_words if w]

    nw = []

    for w in possible_english_words:
        nw.extend(w.split())

    possible_english_words = nw

    def filter_words(words):
        # Return a list of words that contain only English letters
        return [word for word in words if re.match(r'^[a-zA-Z]+$', word) and len(word) > 1]
    
    possible_english_words = filter_words(possible_english_words)

    if not possible_english_words:
        return "en"

    valid_english_words = sum(english_dict.check(w) for w in possible_english_words)
    english_ratio = valid_english_words / len(possible_english_words)

    ascii_chars = sum(ord(c) < 128 for c in text)
    ascii_ratio = ascii_chars / total_chars

    if ascii_ratio < ascii_threshold:
        return "en"

    if english_ratio > word_threshold:
        return "en"
    else:
        return "tbn"

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

def compute_tree_edit_distance(samples: List[Dict[str, Dict]]) -> Dict[str, float]:
    """Compute macro F1 scores across multiple samples, optionally filtering by specified fields."""
    field_f1_sums = defaultdict(float)
    field_counts = defaultdict(int)

    total = 0 
    
    for sample in samples:
        gold = sample["gold"]
        pred = sample["pred"]
        tree_edit_distance = calculate_tree_edit_distance(gold, pred)
        total += tree_edit_distance
    
    return 1 - (total / len(samples))

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

def prepare_samples(data: List[Dict]) -> tuple[Dict[str, List[Dict[str, Dict]]], Dict[str, float], Dict[str, float], Dict[str, float]]:
    """Prepare samples for macro F1 computation, group by language, and compute average token counts."""
    samples_by_language = defaultdict(list)
    token_counts_by_language = defaultdict(lambda: {"input": [], "output": [], "total": []})
    
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
            
            # Detect language
            input_text = item.get("text", "")
            language = detect_language(input_text)
            
            sample = {"gold": gold, "pred": pred}
            
            # Add to language-specific groups and total
            samples_by_language[language].append(sample)
            samples_by_language["total"].append(sample)
            
            # Count tokens for input text
            input_tokens = count_tokens(input_text) if input_text else 0
            total_tokens = input_tokens + output_tokens
            
            # Store token counts by language
            token_counts_by_language[language]["input"].append(input_tokens)
            token_counts_by_language[language]["output"].append(output_tokens)
            token_counts_by_language[language]["total"].append(total_tokens)
            
            token_counts_by_language["total"]["input"].append(input_tokens)
            token_counts_by_language["total"]["output"].append(output_tokens)
            token_counts_by_language["total"]["total"].append(total_tokens)
        
        except json.JSONDecodeError as e:
            logging.warning(f"Invalid ref_json for text: {item.get('text', '')[:50]}... Skipping sample.")
            continue
        except Exception as e:
            logging.warning(f"Error processing sample for text: {item.get('text', '')[:50]}... {str(e)}")
            continue
    
    # Compute average token counts by language
    avg_token_counts = {}
    for lang, counts in token_counts_by_language.items():
        avg_input = sum(counts["input"]) / len(counts["input"]) if counts["input"] else 0
        avg_output = sum(counts["output"]) / len(counts["output"]) if counts["output"] else 0
        avg_total = sum(counts["total"]) / len(counts["total"]) if counts["total"] else 0
        
        avg_token_counts[lang] = {
            "input": avg_input,
            "output": avg_output,
            "total": avg_total
        }
    
    return samples_by_language, avg_token_counts

def main(file_path: str):
    """Main function to compute macro F1 scores and average token counts from JSON file."""
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Load JSON data
    data = load_json_file(file_path)
    
    # Prepare samples and compute token counts
    samples_by_language, avg_token_counts = prepare_samples(data)
    
    # Define fields to include for filtered evaluation
    fields_to_include = [
        "compensation.",
        "blood_group",
        "bags_needed",
        # "hospital_name",
        "location",
        # "probable_day",
        "probable_time"
    ]
    
    # Languages to evaluate
    languages = ["bn", "en", "tbn", "total"]
    
    # Create results dictionary in the same format as evaluate-parser-models.py
    results = {
        "lora-finetuned-llama": {
            "zero_shot": {}
        }
    }
    
    print("Language-wise Evaluation Results:")
    print("=" * 60)
    
    for lang in languages:
        samples = samples_by_language.get(lang, [])
        if not samples:
            print(f"\nNo samples found for language: {lang}")
            results["lora-finetuned-llama"]["zero_shot"][lang] = {
                "macro_f1_score": 0.0,
                "tree_edit_distance": 0.0,
                "final_score": 0.0,
                "avg_cost": 0.0,
                "avg_input_tokens": 0.0,
                "avg_output_tokens": 0.0,
                "avg_total_tokens": 0.0,
                "avg_inference_time": 0.0
            }
            continue
        
        print(f"\n{lang.upper()} Language Results ({len(samples)} samples):")
        print("-" * 40)
        
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
        
        # Compute tree edit distance
        tree_edit_distance = compute_tree_edit_distance(samples)
        print(f"\nTree Edit Distance: {tree_edit_distance:.4f}")

        final_score = 0.2 * tree_edit_distance + 0.8 * result_filtered["overall"]
        print(f"Final Score: {final_score:.4f}")
        
        # Print average token counts
        token_stats = avg_token_counts.get(lang, {"input": 0, "output": 0, "total": 0})
        print(f"\nAverage Input Tokens: {token_stats['input']:.2f}")
        print(f"Average Output Tokens: {token_stats['output']:.2f}")
        print(f"Average Total Tokens: {token_stats['total']:.2f}")
        
        # Store results
        results["lora-finetuned-llama"]["zero_shot"][lang] = {
            "macro_f1_score": result_filtered["overall"],
            "tree_edit_distance": tree_edit_distance,
            "final_score": final_score,
            "avg_cost": 0.0,  # Not applicable for local model
            "avg_input_tokens": token_stats['input'],
            "avg_output_tokens": token_stats['output'],
            "avg_total_tokens": token_stats['total'],
            "avg_inference_time": 0.0  # this is tracked earlier in Kaggle
        }
    
    # Create results directory if it doesn't exist
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Save results to JSON file
    output_path = os.path.join(results_dir, "lora_finetuned_llama_evaluation_results.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Evaluation results saved to {output_path}")
    print("\nFinal Results Summary:")
    print(json.dumps(results, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    file_path = "llama-out.json"
    main(file_path)