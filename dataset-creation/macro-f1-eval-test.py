from typing import Dict, List, Any
from collections import defaultdict

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


from typing import List, Dict
from collections import defaultdict

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


if __name__ == "__main__":
    # Example usage
    gold_json = {
        "blood_group": "B+",
        "bags_needed": "2",
        "patient": {"name": "", "gender": "", "age_group": ""},
        "condition": "Dengue, ICU",
        "location": "সমরিতা হাসপাতাল, তেজগাঁও, লিফ্টের ৪ এ",
        "hospital_name": "সমরিতা হাসপাতাল",
        "location_markers": ["তেজগাঁও"],
        "probable_day": "today",
        "probable_time": "now",
        "contacts": [{"name": "Plabon Asad", "contact_numbers": ["+8801719474127"], "relation_with_patient": "friend"}],
        "compensation": {"transportation": "", "allowance": ""}
    }

    pred_json = {
        "blood_group": "B+",
        "bags_needed": "2",
        "patient": {"name": "", "gender": "", "age_group": "adult"},
        "condition": "Dengue",
        "location": "সমরিতা হাসপাতাল, তেজগাঁও",
        "hospital_name": "সমরিতা হাসপাতাল",
        "location_markers": ["তেজগাঁও"],
        "probable_day": "today",
        "probable_time": "now",
        "contacts": [{"name": "Plabon", "contact_numbers": ["+8801719474127"], "relation_with_patient": ""}],
        "compensation": {"transportation": "N", "allowance": ""}
    }

    # Single sample evaluation
    # f1_scores = evaluate_json(gold_json, pred_json, flexible=True)
    # print("Field-wise F1 scores:", f1_scores)

    # Multiple samples (example dataset)
    samples = [
        {"gold": gold_json, "pred": pred_json},
        {"gold": gold_json, "pred": pred_json},
        # Add more samples here (e.g., 2K samples)
    ]

    # Compute macro F1 for all fields
    result_all = compute_macro_f1(samples, flexible=True)
    print("Macro F1 for All fields:", result_all)

    # Compute macro F1 for specific fields only
    fields = ["compensation.", "blood_group", "bags_needed", "location", "probable_day", "probable_time"]
    result_filtered = compute_macro_f1(samples, flexible=True, fields_to_include=fields)
    print("Macro F1 for Filtered fields:", result_filtered)