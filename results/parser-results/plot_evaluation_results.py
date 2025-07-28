import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict

# Configuration
N = 6  # Number of top combinations to show
SCORE_METRIC = 'final_score'  # Metric to use for scoring and sorting

# Use a sophisticated, modern color palette with excellent visual harmony
colors = ['#4A90E2', '#F5A623', '#7ED321']  # Sophisticated blue, warm amber, vibrant green

colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # blue, orange, green (Color Universal Design - CUD compliant)

# colors = ['#3E8EDE', '#EF6C00', '#00C853']  # bright blue, deep orange, emerald green



def load_json_data(filename):
    """Load JSON data from file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filename} not found, skipping...")
        return {}

def extract_combinations(data):
    """Extract model+setting combinations with scores for each language"""
    combinations = []
    
    for model_name, model_data in data.items():
        # Skip deepseek models
        if 'deepseek' in model_name.lower():
            continue
            
        for setting, setting_data in model_data.items():
            if setting in ['few_shot', 'zero_shot']:
                # Get scores for each language
                scores = {}
                for lang in ['en', 'bn', 'tbn']:
                    if lang in setting_data and SCORE_METRIC in setting_data[lang]:
                        scores[lang] = setting_data[lang][SCORE_METRIC]
                
                # Only include if we have scores for all three languages
                if len(scores) == 3:
                    # Calculate average score for sorting
                    avg_score = sum(scores.values()) / len(scores)
                    
                    combinations.append({
                        'model': model_name,
                        'setting': setting,
                        'combination': f"{model_name}_{setting}",
                        'scores': scores,
                        'avg_score': avg_score
                    })
    
    return combinations

def extract_lora_combinations(data):
    """Extract combinations from LoRA finetuned results"""
    combinations = []
    
    for model_name, model_data in data.items():
        # Skip deepseek models
        if 'deepseek' in model_name.lower():
            continue
            
        for setting, setting_data in model_data.items():
            if setting in ['few_shot', 'zero_shot']:
                # First try to get individual language scores (preferred)
                scores = {}
                for lang in ['en', 'bn', 'tbn']:
                    if lang in setting_data and SCORE_METRIC in setting_data[lang]:
                        scores[lang] = setting_data[lang][SCORE_METRIC]
                
                # If we have scores for all three languages, use them
                if len(scores) == 3:
                    avg_score = sum(scores.values()) / len(scores)
                    
                    combinations.append({
                        'model': model_name,
                        'setting': setting,
                        'combination': f"{model_name}_{setting}",
                        'scores': scores,
                        'avg_score': avg_score,
                        'is_lora': True  # Flag to indicate this is LoRA data
                    })
                # Fallback to total score if individual scores not available
                elif 'total' in setting_data:
                    score_key = 'final_score' if 'final_score' in setting_data['total'] else SCORE_METRIC
                    total_score = setting_data['total'].get(score_key, 0)
                    
                    if total_score > 0:
                        # Use the same score for all languages as fallback
                        scores = {
                            'en': total_score,
                            'bn': total_score, 
                            'tbn': total_score
                        }
                        
                        combinations.append({
                            'model': model_name,
                            'setting': setting,
                            'combination': f"{model_name}_{setting}",
                            'scores': scores,
                            'avg_score': total_score,
                            'is_lora': True  # Flag to indicate this is LoRA data
                        })
    
    return combinations

def create_bar_chart(combinations):
    """Create grouped bar chart"""
    # Sort combinations by average score and take top N
    combinations = sorted(combinations, key=lambda x: x['avg_score'], reverse=True)[:N]
    
    # Prepare cleaner labels
    labels = []
    for combo in combinations:
        # Clean up model names
        model_clean = combo['model'].replace('meta-llama-', '').replace('-instruct', '').replace('-it', '')
        model_clean = model_clean.replace('gemini-2.0-flash', 'gemini-2.0').replace('claude-3-haiku', 'claude-3')
        
        setting_clean = 'Few-Shot' if combo['setting'] == 'few_shot' else 'Zero-Shot'
        lora_indicator = " (LoRA)" if combo.get('is_lora', False) else ""
        labels.append(f"{model_clean}\n{setting_clean}{lora_indicator}")
    
    en_scores = [combo['scores']['en'] for combo in combinations]
    bn_scores = [combo['scores']['bn'] for combo in combinations]
    tbn_scores = [combo['scores']['tbn'] for combo in combinations]
    
    # Set up modern, clean styling
    plt.style.use('default')  # Reset to default first
    sns.set_palette("husl")
    
    # Create figure with better proportions
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    fig.patch.set_facecolor('white')
    
    x = np.arange(len(labels))
    width = 0.26
    
    # Create bars with clean styling
    bars1 = ax.bar(x - width, en_scores, width, label='English', 
                   color=colors[0], alpha=0.9, edgecolor='white', linewidth=1.2)
    bars2 = ax.bar(x, bn_scores, width, label='Bengali', 
                   color=colors[1], alpha=0.9, edgecolor='white', linewidth=1.2)
    bars3 = ax.bar(x + width, tbn_scores, width, label='Transliterated Bengali', 
                   color=colors[2], alpha=0.9, edgecolor='white', linewidth=1.2)
    
    # Clean up the chart appearance
    ax.set_xlabel('Model and Setting', fontsize=13, fontweight='600', labelpad=15)
    ax.set_ylabel('Parsing Accuracy', fontsize=13, fontweight='600', labelpad=15)
    ax.set_title('Parsing Performance Across Languages', fontsize=16, fontweight='700', pad=25)
    
    # Set x-axis
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11, ha='center')
    
    # Set y-axis with better limits and formatting
    max_score = max(max(en_scores), max(bn_scores), max(tbn_scores))
    ax.set_ylim(0, max_score * 1.08)
    ax.tick_params(axis='y', labelsize=11)
    
    # Clean legend positioned at top right
    legend = ax.legend(loc='upper right', fontsize=11, frameon=True, 
                      fancybox=False, shadow=False, framealpha=0.95,
                      edgecolor='gray', facecolor='white')
    legend.get_frame().set_linewidth(0.8)
    
    # Minimal grid
    ax.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Clean up spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)
    
    # # Add subtle note about LoRA data if present
    # if any(combo.get('is_lora', False) for combo in combinations):
    #     ax.text(0.02, 0.98, '* LoRA indicates LoRA fine-tuned models', 
    #             transform=ax.transAxes, fontsize=9, verticalalignment='top',
    #             bbox=dict(boxstyle='round,pad=0.4', facecolor='#f0f0f0', alpha=0.8, 
    #                      edgecolor='#cccccc', linewidth=0.5))
    
    plt.tight_layout()
    plt.savefig('parsing-performace-across-language-comparison.png', dpi=600, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.show()
    
    # Print top combinations
    print(f"\nTop {N} Model + Setting Combinations (by average {SCORE_METRIC}):")
    print("-" * 100)
    for i, combo in enumerate(combinations, 1):
        lora_note = " (LoRA)" if combo.get('is_lora', False) else ""
        print(f"{i:2d}. {combo['combination']:<40} | Avg: {combo['avg_score']:.4f} | "
              f"EN: {combo['scores']['en']:.4f} | BN: {combo['scores']['bn']:.4f} | "
              f"TBN: {combo['scores']['tbn']:.4f}{lora_note}")

def main():
    # Load data from JSON files
    print("Loading evaluation results...")
    
    parser_data = load_json_data('parser_evaluation_results_with_cost_tokens_time.json')
    lora_data = load_json_data('lora_finetuned_llama_evaluation_results.json')
    
    # Extract combinations from both datasets
    combinations = []
    
    if parser_data:
        parser_combinations = extract_combinations(parser_data)
        combinations.extend(parser_combinations)
        print(f"Found {len(parser_combinations)} combinations from parser evaluation results")
    
    if lora_data:
        lora_combinations = extract_lora_combinations(lora_data)
        combinations.extend(lora_combinations)
        print(f"Found {len(lora_combinations)} combinations from LoRA evaluation results")
    
    if not combinations:
        print("No valid combinations found in the data!")
        return
    
    print(f"Total combinations found: {len(combinations)}")
    print(f"Showing top {N} combinations...")
    
    # Create the bar chart
    create_bar_chart(combinations)

if __name__ == "__main__":
    main() 