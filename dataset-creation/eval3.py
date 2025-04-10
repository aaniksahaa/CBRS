from typing import Dict, List, Any
from collections import defaultdict
import os
import json

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

def load_json_file(filepath: str) -> Dict:
    """Load a JSON file and return its contents."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_predictions_and_gold(base_dir: str) -> Dict[str, Dict[str, List[Dict[str, Dict]]]]:
    """Organize predictions and gold data from the directory structure, including token counts and inference time."""
    data = defaultdict(lambda: defaultdict(list))
    gold_data = {}

    # Walk through the parsed/single directory
    for root, _, files in os.walk(os.path.join(base_dir, 'parsed', 'single')):
        for filename in files:
            if filename.endswith('.json'):
                filepath = os.path.join(root, filename)
                content = load_json_file(filepath)
                
                # Extract parsed_json or full content for gold
                if 'gold' in root:
                    gold_data[filename] = content.get('parsed_json', content)
                else:
                    # Extract model, method, and metadata from path and content
                    parts = root.split(os.sep)
                    model_name = parts[-2]  # e.g., deepseek-v3
                    method = parts[-1]      # e.g., few_shot or zero_shot
                    pred_json = content.get('parsed_json', content)
                    language = content.get('blood_donation_request_metadata', {}).get('language', 'unknown')
                    total_cost = content.get('total_cost', 0.0)
                    input_tokens = content.get('input_tokens', 0)
                    output_tokens = content.get('output_tokens', 0)
                    total_tokens = content.get('total_tokens', 0)
                    inference_time = content.get('inference_time', None)  # Allow None
                    
                    data[model_name][method].append({
                        'gold': None,  # Placeholder, filled later
                        'pred': pred_json,
                        'filename': filename,
                        'language': language,
                        'total_cost': total_cost,
                        'input_tokens': input_tokens,
                        'output_tokens': output_tokens,
                        'total_tokens': total_tokens,
                        'inference_time': inference_time
                    })

    # Pair gold data with predictions
    for model_name in data:
        for method in data[model_name]:
            for sample in data[model_name][method]:
                filename = sample['filename']
                if filename in gold_data:
                    sample['gold'] = gold_data[filename]

    return data

def evaluate_models(data: Dict[str, Dict[str, List[Dict[str, Dict]]]], fields_to_include: List[str]) -> Dict[str, Dict[str, Dict[str, Dict[str, float]]]]:
    """Evaluate each model-method-language combination and compute macro F1 scores and averages for cost, tokens, and inference time."""
    results = {}
    languages = ['bn', 'en', 'tbn']

    for model_name, methods in data.items():
        results[model_name] = {}
        for method, samples in methods.items():
            # Filter out samples without gold data
            valid_samples = [s for s in samples if s['gold'] is not None]
            if not valid_samples:
                continue

            # Group samples by language
            samples_by_lang = defaultdict(list)
            for sample in valid_samples:
                lang = sample['language']
                samples_by_lang[lang].append(sample)
                samples_by_lang['total'].append(sample)  # Add to total as well

            # Compute metrics for each language and total
            results[model_name][method] = {}
            for lang in languages + ['total']:
                lang_samples = samples_by_lang.get(lang, [])
                if lang_samples:
                    # Compute macro F1
                    macro_f1_scores = compute_macro_f1(lang_samples, flexible=True, fields_to_include=fields_to_include)
                    overall_f1 = macro_f1_scores.get('overall', 0.0)
                    
                    # Compute average cost (excluding zeros)
                    valid_costs = [s['total_cost'] for s in lang_samples if s.get('total_cost', 0) > 0]
                    avg_cost = sum(valid_costs) / len(valid_costs) if valid_costs else 0.0
                    
                    # Compute token and inference time averages (excluding None or 0)
                    valid_input_tokens = [s['input_tokens'] for s in lang_samples if s.get('input_tokens', 0) > 0]
                    avg_input_tokens = sum(valid_input_tokens) / len(valid_input_tokens) if valid_input_tokens else 0.0
                    
                    valid_output_tokens = [s['output_tokens'] for s in lang_samples if s.get('output_tokens', 0) > 0]
                    avg_output_tokens = sum(valid_output_tokens) / len(valid_output_tokens) if valid_output_tokens else 0.0
                    
                    valid_total_tokens = [s['total_tokens'] for s in lang_samples if s.get('total_tokens', 0) > 0]
                    avg_total_tokens = sum(valid_total_tokens) / len(valid_total_tokens) if valid_total_tokens else 0.0
                    
                    valid_inference_times = [s['inference_time'] for s in lang_samples if s.get('inference_time') and s['inference_time'] > 0]
                    avg_inference_time = sum(valid_inference_times) / len(valid_inference_times) if valid_inference_times else 0.0
                    
                    results[model_name][method][lang] = {
                        "macro_f1_score": overall_f1,
                        "avg_cost": avg_cost,
                        "avg_input_tokens": avg_input_tokens,
                        "avg_output_tokens": avg_output_tokens,
                        "avg_total_tokens": avg_total_tokens,
                        "avg_inference_time": avg_inference_time
                    }
                else:
                    # Default to 0 if no samples for this language
                    results[model_name][method][lang] = {
                        "macro_f1_score": 0.0,
                        "avg_cost": 0.0,
                        "avg_input_tokens": 0.0,
                        "avg_output_tokens": 0.0,
                        "avg_total_tokens": 0.0,
                        "avg_inference_time": 0.0
                    }

    return results

def main():
    # Base directory
    base_dir = "."

    # Fields to include for evaluation
    fields_to_include = [
        "compensation.",  # All compensation subfields
        "blood_group",
        "bags_needed",
        "location",
        "probable_day",
        "probable_time"
    ]

    # Load predictions and gold data
    data = get_predictions_and_gold(base_dir)

    # Evaluate and compute metrics
    results = evaluate_models(data, fields_to_include)

    # Save results to JSON file
    output_path = os.path.join(base_dir, "evaluation_results_with_cost_tokens_time.json")  # Updated filename for clarity
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"Evaluation results saved to {output_path}")
    print(json.dumps(results, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()