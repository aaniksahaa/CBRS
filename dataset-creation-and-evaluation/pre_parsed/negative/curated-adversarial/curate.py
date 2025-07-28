from samples import *
import json 
from util import *
from llmclient import *

bn_words = [
    'অপারেশন', 'আগামীকাল', 'আজ', 'এগিয়ে',
    'কলেজ', 'কেউ', 'গ্রুপ', 'জন্য', 'জরুরি', 'জরুরী', 'যোগাযোগ', 'যেন', 'দিতে', 'না',
    'পারলেও', 'প্রয়োজন', 'ব্লাড', 'ব্যাগ', 'ভিত্তিতে', 'মধ্যে', 'মেডিকেল', 'রক্ত', 'রক্তদানের',
    'রক্তের', 'রোগীর', 'শেয়ার', 'সকাল', 'স্থান', 'হাসপাতাল'
]

en_words = [
    'blood', 'call', 'cc', 'contact', 'donors', 'group', 'hospital',
    'hyderabad', 'need', 'patient', 'please', 'pls',
    'required', 'serious', 'units', 'urgent', 'urgently', 'condition', 'emergency'
]


def build_adversarial_prompt(num_examples: int = 5) -> str:
    """
    Builds a formal prompt for generating adversarial examples for blood donation-seeking message classification.

    Args:
        bn_words (list): List of frequent Bengali words related to blood donation.
        en_words (list): List of frequent English words related to blood donation.
        num_examples (int): Number of adversarial examples to generate (default: 5).

    Returns:
        str: A formatted prompt string.
    """
    # Introduction and task description
    prompt = f"""
You are tasked with generating adversarial examples for a text classification model designed to identify blood donation-seeking messages. The goal is to create realistic, diverse, and tricky negative examples that are NOT actual blood donation requests but use vocabulary commonly associated with such requests. These examples should challenge the robustness of the model by resembling blood donation-seeking messages while having a different intent (e.g., discussions, awareness messages, or unrelated contexts).

### Vocabulary
The following words are frequently found in blood donation-seeking messages. You must incorporate some of these words in each example to make the text appear similar to a blood donation request, but the intent should not be a genuine request for blood donation.

**Bengali Words**: {bn_words}

**English Words**: {en_words}

### Output Format
Generate {num_examples} examples in JSON format. Each example must be a JSON object with the following fields:
- **en**: The text in English (a realistic sentence or short paragraph, 1-3 sentences long).
- **bn**: The equivalent text in Bengali (a realistic sentence or short paragraph, 1-3 sentences long).
- **tbn**: The tbnliterated form of the Bengali text using Latin script (for readability by non-Bengali speakers).

The output should be a JSON array of these objects, properly formatted with double quotes and correct syntax.

### Guidelines
1. **Realistic and Diverse**: The examples should mimic real-world scenarios (e.g., social media posts, conversations, awareness campaigns) but must not be actual blood donation requests.
2. **Tricky**: Use 1 to 3 words from the provided lists in each example to make the text resemble a blood donation request, while ensuring the intent is different.
3. **Length**: Each example (in both English and Bengali) should be 1-3 sentences long and feel natural.
4. **Cultural Relevance**: Ensure the Bengali examples are culturally appropriate and natural for Bengali speakers.
5. **No Requests**: Avoid phrases that explicitly request blood (e.g., "need blood urgently"). Instead, focus on related contexts like awareness, discussions, or unrelated uses of the words.

### Few-Shot Examples
To guide your generation, here are some examples of the desired output:

{json.dumps(adversarial_samples[:3])}

### Task
Generate {num_examples} new adversarial examples following the guidelines above. Ensure each example uses 1 to 3 words from the provided vocabulary lists, is realistic, and does not represent an actual blood donation request. Output the result as a JSON array.

**Reminders:**
- Adhering strictly to the JSON schema is **mandatory**.
- Do **not** include any greetings, explanations, or additional text. Output **only** the correctly formatted JSON.
- Your generated samples each must be distinct, diverse, novel, tricky, and challenging
- Copying the given examples will be highly penalized.

Ensure your output is precise, complete, and formatted in a manner suitable for automated parsing.

"""

    return prompt

run_id = 7

provider = 'openai'
model = 'gpt-4o'

# provider = 'google'
# model='gemini-2.0-flash'

# provider = 'together'
# model = 'deepseek-ai/DeepSeek-V3'
# model = 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free'
# model = 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo'

# Generate the prompt
prompt = build_adversarial_prompt(num_examples=50)

client = LLMClient()

model = "gemini-2.0-flash"
model = "gpt-4o-mini"
model = "deepseek-ai/DeepSeek-V3"
model = "gpt-4o"

model = "deepseek/deepseek-chat:free"

client.set_model(model)


res = client.get_response(
    prompt=prompt
)

j = res.get('parsed_json', [])

out_path = f'raw/out_{run_id}.json'

write_json(out_path, j)

print(f"✅ JSON successfully parsed and written to {out_path}")