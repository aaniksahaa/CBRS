from samples import *
import json 
from util import *
from typing import List, Dict
import math
from llmclient import *


bn_words = [
    'অপারেশন', 'আগামীকাল', 'আজ', 'এগিয়ে',
    'কলেজ', 'কেউ', 'গ্রুপ', 'জন্য', 'জরুরি', 'জরুরী', 'যোগাযোগ', 'যেন', 'দিতে', 'না',
    'পজেটিভ', 'নেগেটিভ', 'এ পজেটিভ' , 'এ+', 'এ নেগেটিভ', 'বি নেগেটিভ', 'ও পজেটিভ',
    'পারলেও', 'প্রয়োজন', 'ব্লাড', 'ব্যাগ', 'ভিত্তিতে', 'মধ্যে', 'মেডিকেল', 'রক্ত', 'রক্তদানের',
    'রক্তের', 'রোগীর', 'শেয়ার', 'সকাল', 'স্থান', 'হাসপাতাল'
]

en_words = [
    'blood', 'call', 'cc', 'contact', 'donors', 'group', 'hospital',
    'hyderabad', 'need', 'patient', 'please', 'pls',
    'A+', 'B+ve', 'O-', '-ve', 'AB+', 'AB-', 'B-', 'O+',
    'required', 'serious', 'units', 'urgent', 'urgently', 'condition', 'emergency'
]


client = LLMClient()

model = "gemini-2.0-flash"
model = "gpt-4o-mini"
model = "deepseek-ai/DeepSeek-V3"
model = "gpt-4o"

model = "deepseek/deepseek-chat:free"

client.set_model(model)

def load_manual_negatives(file_path: str) -> List[Dict]:
    """Load manually collected negative examples from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Convert the format to match our required structure
        formatted_data = []
        for item in data:
            formatted_data.append(item['text'])
        return formatted_data

def build_anchored_prompt(anchor_examples: List[Dict], num_examples: int = 10) -> str:
    """
    Builds a prompt for generating adversarial examples using anchor examples as inspiration.
    
    Args:
        anchor_examples (list): List of 5 anchor examples to use as inspiration
        num_examples (int): Number of new examples to generate (default: 10)
    
    Returns:
        str: A formatted prompt string
    """
    prompt = f"""

    You are tasked with generating adversarial examples for a text classification model designed to identify blood donation-seeking messages. The goal is to create realistic, diverse, and tricky negative examples that are NOT actual blood donation requests but use vocabulary commonly associated with such requests.

    ### Vocabulary
The following words are frequently found in blood donation-seeking messages. You must incorporate some of these words in each example to make the text appear similar to a blood donation request, but the intent should not be a genuine request for blood donation.

**Bengali Words**: {bn_words}

**English Words**: {en_words}

### Anchor Examples
Here are some examples of the desired style and complexity. 
Use these as inspiration and create similarly realistic but a bit new examples.

{json.dumps(anchor_examples, indent=2)}

### Output Format
Generate {num_examples} new examples in JSON format. Each example must be a JSON object with the following fields:
- **en**: The text in English 
- **bn**: The equivalent text in Bengali 
- **tbn**: The transliterated form of the Bengali text using Latin script

The output should be a JSON array of these objects, properly formatted with double quotes and correct syntax.

### Guidelines
1. **Realistic and Diverse**: The examples should mimic real-world scenarios (e.g., social media posts, conversations, awareness campaigns) but must not be actual blood donation requests
2. **Tricky**: Use several words from the provided lists in each example to make the text resemble a blood donation request, while ensuring the intent is different

### Task
Generate {num_examples} new adversarial examples following the guidelines above. Ensure each example is realistic, similar to the anchor examples but novel and does not represent an actual blood donation request. Output the result as a JSON array.

**Reminders:**
- Adhering strictly to the JSON schema is **mandatory**
- Do **not** include any greetings, explanations, or additional text. Output **only** the correctly formatted JSON
- Your generated samples each must be distinct, diverse, novel, tricky, and challenging

Ensure your output is precise, complete, and formatted in a manner suitable for automated parsing.

Please strictly follow the pattern of the given anchor examples. 
We want such realistic adversarial examples. Feel free to make very similar exammples.

"""
    
    return prompt

def process_sliding_windows(manual_negatives: List[Dict], window_size: int = 5, stride: int = 1) -> List[List[Dict]]:
    """Create sliding windows of anchor examples."""
    windows = []
    for i in range(0, len(manual_negatives) - window_size + 1, stride):
        windows.append(manual_negatives[i:i + window_size])
    return windows

def main():
    # Load manual negatives
    manual_negatives = load_manual_negatives('manually_collected_negatives.json')
    
    # Create sliding windows
    windows = process_sliding_windows(manual_negatives)
    
    # Process each window
    for i, window in enumerate(windows[:]):
        # Generate prompt with current window as anchors
        prompt = build_anchored_prompt(window)

        print(prompt)
        
        # Get response from model
        res = client.get_response(
            prompt=prompt
        )
        j = res.get('parsed_json', [])
        out_path = f'raw/out_with_anchor_{i+1}.json'
        write_json(out_path, j)
        
        print(f"✅ Window {i+1}/{len(windows)} processed and written to {out_path}")

if __name__ == "__main__":
    main() 