"""
JSON Evaluation Utilities
Common functions for comparing and evaluating JSON structures.
"""

import json
import logging
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import zss

# ============================================================================
# TREE EDIT DISTANCE FUNCTIONS
# ============================================================================

class JSONNode:
    """Simple node class for JSON tree representation."""
    def __init__(self, label: str, value: Any = None):
        self.label = label
        self.value = value
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)
    
    def __str__(self):
        return self.label

def json_to_tree(obj: Any, key: str = "root") -> JSONNode:
    """Convert JSON object to tree structure for zss."""
    if obj is None:
        return JSONNode(f"{key}:null")
    
    if isinstance(obj, dict):
        node = JSONNode(f"{key}:dict")
        for k, v in obj.items():
            child = json_to_tree(v, k)
            node.add_child(child)
        return node
    
    elif isinstance(obj, list):
        node = JSONNode(f"{key}:list")
        for i, item in enumerate(obj):
            child = json_to_tree(item, f"item_{i}")
            node.add_child(child)
        return node
    
    else:
        # Leaf node with value
        return JSONNode(f"{key}:{str(obj).lower().strip()}")

def get_children(node: JSONNode) -> List[JSONNode]:
    """Get children of a node for zss."""
    return node.children

def get_label(node: JSONNode) -> str:
    """Get label of a node for zss."""
    return node.label

def label_distance(label1: str, label2: str) -> float:
    """Calculate distance between two labels."""
    if label1 == label2:
        return 0.0
    
    # Extract key and type/value parts
    parts1 = label1.split(':', 1)
    parts2 = label2.split(':', 1)
    
    if len(parts1) != 2 or len(parts2) != 2:
        return 1.0
    
    key1, type_val1 = parts1
    key2, type_val2 = parts2
    
    # Different keys = high cost
    if key1 != key2:
        return 1.0
    
    # Same key, different type/value = medium cost
    if type_val1 != type_val2:
        return 0.5
    
    return 0.0

def calculate_tree_edit_distance(gold_json: Dict, pred_json: Dict) -> float:
    """Calculate normalized tree edit distance between two JSON structures."""
    try:
        # Convert JSONs to trees
        gold_tree = json_to_tree(gold_json, "root")
        pred_tree = json_to_tree(pred_json, "root")
        
        # Calculate tree edit distance
        distance = zss.simple_distance(
            gold_tree, pred_tree,
            get_children=get_children,
            get_label=get_label,
            label_dist=label_distance
        )
        
        # Normalize by the maximum possible distance
        # Max distance is roughly the sum of nodes in both trees
        def count_nodes(node):
            return 1 + sum(count_nodes(child) for child in node.children)
        
        gold_nodes = count_nodes(gold_tree)
        pred_nodes = count_nodes(pred_tree)
        max_distance = gold_nodes + pred_nodes
        
        if max_distance == 0:
            return 0.0
        
        normalized_distance = distance / max_distance
        return min(normalized_distance, 1.0)  # Cap at 1.0
        
    except Exception as e:
        logging.warning(f"Error calculating tree edit distance: {e}")
        return 1.0

# ============================================================================
# FIELD-LEVEL COMPARISON FUNCTIONS (from original eval-llama.py)
# ============================================================================

def normalize_value(value: Any, flexible: bool = True) -> Any:
    """Normalize a string value for flexible matching."""
    if isinstance(value, str):
        return value.strip().lower() if flexible else value
    return value

def compare_fields(gold: Any, pred: Any, flexible: bool = True) -> Tuple[int, int, int]:
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

def evaluate_json_field_level(gold: Dict, pred: Dict, flexible: bool = True) -> Dict[str, float]:
    """Evaluate a single pair of gold and predicted JSONs, returning field-wise F1 scores."""
    tp, fp, fn = defaultdict(int), defaultdict(int), defaultdict(int)

    def recursive_compare(gold_val: Any, pred_val: Any, prefix: str = "") -> Tuple[int, int, int]:
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

# ============================================================================
# COMBINED EVALUATION FUNCTIONS
# ============================================================================

def evaluate_json_combined(gold: Dict, pred: Dict, flexible: bool = True, 
                          tree_weight: float = 0.5, field_weight: float = 0.5) -> Dict[str, Any]:
    """
    Evaluate JSON pair using both tree edit distance and field-level F1 scores.
    
    Args:
        gold: Gold standard JSON
        pred: Predicted JSON
        flexible: Whether to use flexible string matching
        tree_weight: Weight for tree edit distance (0-1)
        field_weight: Weight for field-level F1 (0-1)
    
    Returns:
        Dictionary containing both metrics and combined score
    """
    # Calculate tree edit distance (0 = perfect, 1 = worst)
    tree_distance = calculate_tree_edit_distance(gold, pred)
    tree_accuracy = 1 - tree_distance  # Convert to accuracy (1 = perfect, 0 = worst)
    
    # Calculate field-level F1 scores
    field_f1_scores = evaluate_json_field_level(gold, pred, flexible)
    
    # Calculate overall field F1 (average of all field F1 scores)
    if field_f1_scores:
        overall_field_f1 = sum(field_f1_scores.values()) / len(field_f1_scores)
    else:
        overall_field_f1 = 0.0
    
    # Calculate combined score (weighted average)
    combined_score = (tree_weight * tree_accuracy) + (field_weight * overall_field_f1)
    
    return {
        'tree_edit_distance': tree_distance,
        'tree_accuracy': tree_accuracy,
        'field_f1_scores': field_f1_scores,
        'overall_field_f1': overall_field_f1,
        'combined_score': combined_score,
        'weights': {'tree_weight': tree_weight, 'field_weight': field_weight}
    }

def is_field_included(field: str, fields_to_include: List[str]) -> bool:
    """Check if a field should be included based on exact match or prefix pattern."""
    if not fields_to_include:  # If no fields specified, include all
        return True
    for pattern in fields_to_include:
        if field == pattern or (pattern.endswith(".") and field.startswith(pattern)):
            return True
    return False

def compute_macro_metrics(samples: List[Dict[str, Dict]], flexible: bool = True, 
                         fields_to_include: List[str] = None,
                         tree_weight: float = 0.5, field_weight: float = 0.5) -> Dict[str, Any]:
    """
    Compute macro metrics across multiple samples using both tree edit distance and field-level F1.
    """
    # Store all individual results
    all_tree_distances = []
    all_tree_accuracies = []
    all_field_f1_scores = defaultdict(list)
    all_overall_field_f1 = []
    all_combined_scores = []
    
    for sample in samples:
        gold = sample["gold"]
        pred = sample["pred"]
        
        # Get combined evaluation
        result = evaluate_json_combined(gold, pred, flexible, tree_weight, field_weight)
        
        all_tree_distances.append(result['tree_edit_distance'])
        all_tree_accuracies.append(result['tree_accuracy'])
        all_overall_field_f1.append(result['overall_field_f1'])
        all_combined_scores.append(result['combined_score'])
        
        # Collect field-level F1 scores
        for field, score in result['field_f1_scores'].items():
            if is_field_included(field, fields_to_include):
                all_field_f1_scores[field].append(score)
    
    # Calculate macro averages
    macro_results = {
        'avg_tree_edit_distance': sum(all_tree_distances) / len(all_tree_distances),
        'avg_tree_accuracy': sum(all_tree_accuracies) / len(all_tree_accuracies),
        'avg_overall_field_f1': sum(all_overall_field_f1) / len(all_overall_field_f1),
        'avg_combined_score': sum(all_combined_scores) / len(all_combined_scores),
        'macro_field_f1': {},
        'weights': {'tree_weight': tree_weight, 'field_weight': field_weight}
    }
    
    # Calculate macro F1 for each field
    for field, scores in all_field_f1_scores.items():
        macro_results['macro_field_f1'][field] = sum(scores) / len(scores)
    
    # Overall macro F1 (average across included fields only)
    if macro_results['macro_field_f1']:
        macro_results['overall_macro_f1'] = sum(macro_results['macro_field_f1'].values()) / len(macro_results['macro_field_f1'])
    else:
        macro_results['overall_macro_f1'] = 0.0
    
    return macro_results 