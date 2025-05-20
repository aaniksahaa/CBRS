
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils import shuffle
import json
import os
from llmclient import LLMClient
import time

# Constants
DATASET_PATH = "/kaggle/input/bnet-dataset/pre_parsed_dataset.csv"
DATASET_PATH = "pre_parsed_dataset.csv"
OUTPUT_DIR = "./evaluation_results"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_prompt(message):
    message = message.replace('"', '\\"')
    sample_true = {
        "is_blood_donation_request": True
    }
    sample_false = {
        "is_blood_donation_request": False
    }

    prompt = f"""
    You are an expert in text classification for emergency blood donation requests. Analyze the following text to determine if it is explicitly related to a request for blood donation or an emergency need for blood. The text may be in English, Bengali, or a mix of both. Return your response in JSON format with a single key 'is_blood_donation_request' and a boolean value (true if related to blood donation/emergency, false otherwise). Ensure your analysis is precise and academically sound.

    Samples:

    Input Text: Emergency O+ blood needed. Please help.
    Response:
    ```json
    {json.dumps(sample_true)}
    ```

    Input Text: Blood donation is a great virtue.
    Response:
    ```json
    {json.dumps(sample_false)}
    ```

    Text: "{message}"

    Reminders:
    - Do not include any sort of greetings/fillers etc in the response.
    - Output only the correct JSON properly understanding the meaning of the English / Bengali / Transliterated Bengali Text
    
    """

    return prompt

class TextClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        self.model = LogisticRegression(
            class_weight={0: 15.0, 1: 1.0}, 
            C=1.0, 
            penalty='l2', 
            solver='lbfgs', 
            max_iter=10000
        )
        self.llm_client = LLMClient()
        self.llm_client.set_model("gpt-4o-mini")
    
    def load_and_prepare_data(self, filepath):
        print("Loading dataset...")
        df = pd.read_csv(filepath)
        df = shuffle(df, random_state=42)

        # df = df[:1000]
        
        print(f"non-blood: {(df['label']==0).sum()}")
        print(f"blood: {(df['label']==1).sum()}")
        
        self.X = df['text']
        self.y = df['label']
        
        print("Splitting dataset...")
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
    
    def train(self):
        print("Training vectorizer and model...")
        print("Running vectorizer for train...")
        self.X_train_vec = self.vectorizer.fit_transform(self.X_train)
        print("Running vectorizer for test...")
        self.X_test_vec = self.vectorizer.transform(self.X_test)
        print("Fitting model...")
        self.model.fit(self.X_train_vec, self.y_train)
    
    def evaluate(self):
        print("Evaluating model...")
        start_time = time.perf_counter()
        y_pred_initial = self.model.predict(self.X_test_vec)
        y_pred_final = []
        for idx, (pred, text) in enumerate(zip(y_pred_initial, self.X_test)):
            # if pred == 0:
            if True:
                # If model predicts negative, flag as negative
                y_pred_final.append(pred)
            else:
                # If model predicts positive, verify with gpt-4o-mini
                try:
                    prompt = get_prompt(text)
                    response = self.llm_client.get_response(prompt)
                    parsed_json = response.get('parsed_json', None)
                    
                    if parsed_json and 'is_blood_donation_request' in parsed_json:
                        is_blood_donation_request = parsed_json['is_blood_donation_request']
                        print(f"\nText: {text}\nModel said: positive\nVerdict of LLM:\n is_blood_donation_request: {is_blood_donation_request}")
                        y_pred_final.append(1 if is_blood_donation_request else 0)
                    else:
                        # If LLM response is invalid, default to model's prediction (positive)
                        print(f"Warning: Invalid LLM response for text {idx+1}. Defaulting to model prediction (positive).")
                        y_pred_final.append(1)
                except Exception as e:
                    # If LLM call fails, default to model's prediction (positive)
                    print(f"Error calling LLM for text {idx+1}: {e}. Defaulting to model prediction (positive).")
                    y_pred_final.append(1)
        
        end_time = time.perf_counter()
        num_samples = len(self.y_test)
        total_inference_time = end_time - start_time
        avg_inference_time = total_inference_time / num_samples
        
        accuracy = accuracy_score(self.y_test, y_pred_final)
        report = classification_report(y_pred_final, self.y_test, digits=8, output_dict=True)
        

        # Collect false positives
        false_positives = []
        for idx, (pred, true, text) in enumerate(zip(y_pred_final, self.y_test, self.X_test)):
            if pred == 1 and true == 0:
                false_positives.append({"index": idx, "text": text})

        # Write false positives to a JSON file
        false_positives_file = os.path.join("", "false_positives.json")
        with open(false_positives_file, 'w', encoding='utf-8') as f:
            json.dump(false_positives, f, ensure_ascii=False, indent=4)

        # Inform user
        if false_positives:
            print(f"Saved {len(false_positives)} false positives to {false_positives_file}")
        else:
            print(f"No false positives found. Empty file saved to {false_positives_file}")




        print(f'Accuracy: {accuracy:.8f}')
        print(f'Average Inference Time per Sample: {avg_inference_time:.8f} seconds')
        print('Classification Report:')
        print(classification_report(y_pred_final, self.y_test, digits=8))
        
        # Prepare and save results
        results = {
            'vectorizer': 'tfidf',
            'model': 'logistic-weighted',
            'accuracy': accuracy,
            'avg_inference_time_seconds': avg_inference_time,
            'metrics': report
        }
        
        filename = "tfidf_logistic-weighted_with_gpt-4o-mini.json"
        with open(os.path.join(OUTPUT_DIR, filename), 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Saved results to {os.path.join(OUTPUT_DIR, filename)}")
        
        return accuracy, results
    
    def predict_messages(self, messages):
        messages_vec = self.vectorizer.transform(messages)
        y_pred_initial = self.model.predict(messages_vec)
        for idx, (message, pred) in enumerate(zip(messages, y_pred_initial)):
            if pred == 0:
                final_pred = 0
                print(f'Message: {message}')
                print(f'Prediction: {final_pred} (Negative - Model)\n')
            else:
                try:
                    prompt = get_prompt(message)
                    print(prompt)
                    response = self.llm_client.get_response(prompt)
                    print(response)
                    parsed_json = response.get('parsed_json', None)
                    
                    if parsed_json and 'is_blood_donation_request' in parsed_json:
                        is_blood_donation_request = parsed_json['is_blood_donation_request']
                        final_pred = 1 if is_blood_donation_request else 0
                        print(f'Message: {message}')
                        print(f'Prediction: {final_pred} ({"Positive" if final_pred else "Negative"} - LLM)\n')
                    else:
                        final_pred = 1
                        print(f'Warning: Invalid LLM response for message {idx+1}. Defaulting to model prediction (positive).')
                        print(f'Message: {message}')
                        print(f'Prediction: {final_pred} (Positive - Model Default)\n')
                except Exception as e:
                    final_pred = 1
                    print(f'Error calling LLM for message {idx+1}: {e}. Defaulting to model prediction (positive).')
                    print(f'Message: {message}')
                    print(f'Prediction: {final_pred} (Positive - Model Default)\n')

def main():
    # Initialize classifier
    classifier = TextClassifier()
    
    # Load and prepare data
    classifier.load_and_prepare_data(DATASET_PATH)
    
    # Train the model
    classifier.train()
    
    # Evaluate
    classifier.evaluate()
    
    # Test with custom messages
    messages = [
        "someone needed at uttara, my bag has been stolen by someone, I need to contact to the police",
        "জরুরি ভিত্তিতে রক্ত প্রয়োজন, যোগাযোগ - 01552375331",
        "Please help me. One of my relatives need 2 bags O+ve blood for uterus operation at birdem hospital",
        "Keu ektu shahajjo koren, amar fupir jonno birdem hospital e A-ve rokto proyojon",
    ]
    
    # classifier.predict_messages(messages)

if __name__ == "__main__":
    main()
