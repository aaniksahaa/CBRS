import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils import shuffle
import gensim.downloader as api
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
from tqdm import tqdm
import json
import os
import time
import torch

# Constants
DATASET_PATH = "/kaggle/input/bnet-dataset/pre_parsed_dataset.csv"
OUTPUT_DIR = "./evaluation_results"  # Directory to save JSON files

HUGGINGFACE_EMBEDDING_MODELS = [
    "distilbert-base-uncased",  # Focus on DistilBERT
    "google/mobilebert-uncased"  # Focus on MobileBERT
]

# Define available vectorizers
VECTORIZERS = {
    'tfidf': lambda: TfidfVectorizer(max_features=5000, ngram_range=(1, 2)),
    'count': lambda: CountVectorizer(max_features=5000, ngram_range=(1, 2)),
    'word2vec': lambda: Word2VecVectorizer(),
    'huggingface': lambda: HuggingfaceVectorizer(model_name=HUGGINGFACE_EMBEDDING_MODELS[0])
}

# Define available models for traditional classifiers
MODELS = {
    'logistic': lambda: LogisticRegression(C=1.0, penalty='l2', solver='lbfgs', max_iter=10000),
    'svm': lambda: SVC(kernel='linear', probability=True),
    'random_forest': lambda: RandomForestClassifier(n_estimators=100, random_state=42),
    'naive_bayes': lambda: MultinomialNB(),
    'logistic-weighted': lambda: LogisticRegression(class_weight={0: 12.0, 1: 1.0}, C=1.0, penalty='l2', solver='lbfgs', max_iter=10000),
}

class Word2VecVectorizer:
    def __init__(self):
        self.word2vec = api.load('word2vec-google-news-300')
        self.vector_size = 300
    
    def fit_transform(self, X):
        return self._transform(X)
    
    def transform(self, X):
        return self._transform(X)
    
    def _transform(self, X):
        vectors = []
        for text in tqdm(X, desc="Vectorizing with Word2Vec"):
            words = text.split()
            word_vectors = [self.word2vec[word] for word in words if word in self.word2vec]
            if word_vectors:
                vectors.append(np.mean(word_vectors, axis=0))
            else:
                vectors.append(np.zeros(self.vector_size))
        return np.array(vectors)

class HuggingfaceVectorizer:
    def __init__(self, model_name=HUGGINGFACE_EMBEDDING_MODELS[0]):
        self.model_name = model_name
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True).to(self.device)
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            raise
        dummy_text = "test"
        dummy_embedding = self._get_embedding(dummy_text)
        self.vector_size = len(dummy_embedding)
    
    def _get_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        if "bert" in self.model_name.lower():
            embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy().flatten()  # CLS token
        else:
            embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy().flatten()  # Mean pooling
        return embedding
    
    def fit_transform(self, X):
        return self._transform(X)
    
    def transform(self, X):
        return self._transform(X)
    
    def _transform(self, X):
        if isinstance(X, pd.Series):
            X = X.tolist()
        embeddings = []
        for text in tqdm(X, desc=f"Vectorizing with {self.model_name}"):
            embedding = self._get_embedding(text)
            embeddings.append(embedding)
        return np.array(embeddings)

class BERTClassifier:
    def __init__(self, model_name=HUGGINGFACE_EMBEDDING_MODELS[0]):
        self.model_name = model_name
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2, trust_remote_code=True).to(self.device)
        self.vectorizer_type = 'bert-end-to-end'
        self.model_type = 'bert'
        self.embedding_model = model_name
    
    def load_and_prepare_data(self, filepath):
        print("Loading dataset...")
        df = pd.read_csv(filepath)
        df = shuffle(df, random_state=42)
        
        print(f"non-blood: {(df['label']==0).sum()}")
        print(f"blood: {(df['label']==1).sum()}")
        
        self.X = df['text']
        self.y = df['label']
        
        print("Splitting dataset...")
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
        
        # Convert to HuggingFace Dataset
        train_data = {'text': self.X_train.tolist(), 'label': self.y_train.tolist()}
        test_data = {'text': self.X_test.tolist(), 'label': self.y_test.tolist()}
        self.train_dataset = Dataset.from_dict(train_data)
        self.test_dataset = Dataset.from_dict(test_data)
    
    def tokenize_function(self, examples):
        return self.tokenizer(examples['text'], padding="max_length", truncation=True, max_length=512)
    
    def train(self):
        print(f"Training {self.model_name} end-to-end...")
        self.train_dataset = self.train_dataset.map(self.tokenize_function, batched=True)
        self.test_dataset = self.test_dataset.map(self.tokenize_function, batched=True)
        
        # Set format for PyTorch
        self.train_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
        self.test_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
        
        training_args = TrainingArguments(
            output_dir=os.path.join(OUTPUT_DIR, f"{self.model_name.replace('/', '_')}_checkpoint"),
            num_train_epochs=3,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=os.path.join(OUTPUT_DIR, 'logs'),
            logging_steps=10,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.test_dataset,
            compute_metrics=lambda eval_pred: {
                'accuracy': accuracy_score(eval_pred.label_ids, np.argmax(eval_pred.predictions, axis=1))
            }
        )
        
        trainer.train()
        self.trainer = trainer
    
    def evaluate(self):
        print(f"Evaluating {self.model_name}...")
        start_time = time.perf_counter()
        eval_results = self.trainer.predict(self.test_dataset)
        end_time = time.perf_counter()
        
        y_pred = np.argmax(eval_results.predictions, axis=1)
        y_true = eval_results.label_ids
        
        num_samples = len(y_true)
        total_inference_time = end_time - start_time
        avg_inference_time = total_inference_time / num_samples
        
        accuracy = accuracy_score(y_true, y_pred)
        report = classification_report(y_true, y_pred, digits=8, output_dict=True)
        
        print(f'Accuracy: {accuracy:.8f}')
        print(f'Average Inference Time per Sample: {avg_inference_time:.8f} seconds')
        print('Classification Report:')
        print(classification_report(y_true, y_pred, digits=8))
        
        results = {
            'vectorizer': self.vectorizer_type,
            'model': self.model_type,
            'embedding_model': self.embedding_model,
            'accuracy': accuracy,
            'avg_inference_time_seconds': avg_inference_time,
            'metrics': report
        }
        
        filename = f"{self.vectorizer_type}_{self.embedding_model}_{self.model_type}.json".replace('/', '_')
        with open(os.path.join(OUTPUT_DIR, filename), 'w') as f:
            json.dump(results, f, indent=4)
        
        return accuracy, results
    
    def predict_messages(self, messages):
        dataset = Dataset.from_dict({'text': messages})
        dataset = dataset.map(self.tokenize_function, batched=True)
        dataset.set_format('torch', columns=['input_ids', 'attention_mask'])
        predictions = self.trainer.predict(dataset).predictions
        predictions = np.argmax(predictions, axis=1)
        
        for message, pred in zip(messages, predictions):
            print(f'Message: {message}')
            print(f'Prediction: {pred}\n')

class TextClassifier:
    def __init__(self, vectorizer_type='tfidf', model_type='logistic', embedding_model=None):
        if vectorizer_type == 'huggingface' and embedding_model:
            self.vectorizer = HuggingfaceVectorizer(model_name=embedding_model)
        else:
            self.vectorizer = VECTORIZERS[vectorizer_type]()
        self.model = MODELS[model_type]()
        self.vectorizer_type = vectorizer_type
        self.model_type = model_type
        self.embedding_model = embedding_model if vectorizer_type == 'huggingface' else None
    
    def load_and_prepare_data(self, filepath):
        print("Loading dataset...")
        df = pd.read_csv(filepath)
        df = shuffle(df, random_state=42)
        
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
        return self.X_train_vec, self.X_test_vec
    
    def evaluate(self):
        start_time = time.perf_counter()
        y_pred = self.model.predict(self.X_test_vec)
        end_time = time.perf_counter()
        
        num_samples = len(self.y_test)
        total_inference_time = end_time - start_time
        avg_inference_time = total_inference_time / num_samples
        
        accuracy = accuracy_score(self.y_test, y_pred)
        report = classification_report(y_pred, self.y_test, digits=8, output_dict=True)
        
        print(f'Accuracy: {accuracy:.8f}')
        print(f'Average Inference Time per Sample: {avg_inference_time:.8f} seconds')
        print('Classification Report:')
        print(classification_report(y_pred, self.y_test, digits=8))
        
        results = {
            'vectorizer': self.vectorizer_type,
            'model': self.model_type,
            'embedding_model': self.embedding_model if self.embedding_model else 'N/A',
            'accuracy': accuracy,
            'avg_inference_time_seconds': avg_inference_time,
            'metrics': report
        }
        
        filename = f"{self.vectorizer_type}_{self.embedding_model if self.embedding_model else ''}_{self.model_type}.json".replace('/', '_')
        with open(os.path.join(OUTPUT_DIR, filename), 'w') as f:
            json.dump(results, f, indent=4)
        
        return accuracy, results
    
    def predict_messages(self, messages):
        messages_vec = self.vectorizer.transform(messages)
        predictions = self.model.predict(messages_vec)
        
        for message, pred in zip(messages, predictions):
            print(f'Message: {message}')
            print(f'Prediction: {pred}\n')

def run_all_combinations():
    print("Starting bulk evaluation...")
    all_results = {}
    
    try:
        df = pd.read_csv(DATASET_PATH)
        df = shuffle(df, random_state=42)
        X = df['text']
        y = df['label']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    except Exception as e:
        print(f"Error loading or splitting dataset: {e}")
        return
    
    # Evaluate BERT end-to-end models
    for emb_model in HUGGINGFACE_EMBEDDING_MODELS:
        print(f"\nEvaluating end-to-end BERT with {emb_model}")
        try:
            classifier = BERTClassifier(model_name=emb_model)
            classifier.load_and_prepare_data(DATASET_PATH)
            classifier.train()
            accuracy, results = classifier.evaluate()
            key = f"bert-end-to-end_{emb_model}_bert"
            all_results[key] = results
            filename = f"{key}.json".replace('/', '_')
            with open(os.path.join(OUTPUT_DIR, filename), 'w') as f:
                json.dump(results, f, indent=4)
            print(f"Saved individual result to {os.path.join(OUTPUT_DIR, filename)}")
        except Exception as e:
            print(f"Error evaluating end-to-end BERT with {emb_model}: {e}")
            continue
    
    # Evaluate traditional vectorizers and models
    for vec_type in VECTORIZERS.keys():
        if vec_type == 'huggingface':
            for emb_model in HUGGINGFACE_EMBEDDING_MODELS:
                print(f"\nVectorizing with {vec_type} - {emb_model}")
                try:
                    classifier = TextClassifier(vectorizer_type=vec_type, model_type='logistic', embedding_model=emb_model)
                    classifier.X_train, classifier.X_test, classifier.y_train, classifier.y_test = X_train, X_test, y_train, y_test
                    X_train_vec, X_test_vec = classifier.train()
                except Exception as e:
                    print(f"Error vectorizing with {vec_type} - {emb_model}: {e}")
                    continue
                
                for model_type in MODELS.keys():
                    print(f"Evaluating {model_type} with {vec_type} - {emb_model}")
                    try:
                        classifier = TextClassifier(vectorizer_type=vec_type, model_type=model_type, embedding_model=emb_model)
                        classifier.X_train, classifier.X_test, classifier.y_train, classifier.y_test = X_train, X_test, y_train, y_test
                        classifier.X_train_vec, classifier.X_test_vec = X_train_vec, X_test_vec
                        classifier.model.fit(X_train_vec, y_train)
                        accuracy, results = classifier.evaluate()
                        key = f"{vec_type}_{emb_model}_{model_type}"
                        all_results[key] = results
                        filename = f"{key}.json".replace('/', '_')
                        with open(os.path.join(OUTPUT_DIR, filename), 'w') as f:
                            json.dump(results, f, indent=4)
                        print(f"Saved individual result to {os.path.join(OUTPUT_DIR, filename)}")
                    except Exception as e:
                        print(f"Error evaluating {model_type} with {vec_type} - {emb_model}: {e}")
                        continue
        else:
            print(f"\nVectorizing with {vec_type}")
            try:
                classifier = TextClassifier(vectorizer_type=vec_type, model_type='logistic')
                classifier.X_train, classifier.X_test, classifier.y_train, classifier.y_test = X_train, X_test, y_train, y_test
                X_train_vec, X_test_vec = classifier.train()
            except Exception as e:
                print(f"Error vectorizing with {vec_type}: {e}")
                continue
            
            for model_type in MODELS.keys():
                print(f"Evaluating {model_type} with {vec_type}")
                try:
                    classifier = TextClassifier(vectorizer_type=vec_type, model_type=model_type)
                    classifier.X_train, classifier.X_test, classifier.y_train, classifier.y_test = X_train, X_test, y_train, y_test
                    classifier.X_train_vec, classifier.X_test_vec = X_train_vec, X_test_vec
                    classifier.model.fit(X_train_vec, y_train)
                    accuracy, results = classifier.evaluate()
                    key = f"{vec_type}_{model_type}"
                    all_results[key] = results
                    filename = f"{key}.json".replace('/', '_')
                    with open(os.path.join(OUTPUT_DIR, filename), 'w') as f:
                        json.dump(results, f, indent=4)
                    print(f"Saved individual result to {os.path.join(OUTPUT_DIR, filename)}")
                except Exception as e:
                    print(f"Error evaluating {model_type} with {vec_type}: {e}")
                    continue
    
    OUTPUT_PATH = 'bnet_classifier_all_combinations_results.json'
    full_output_path = os.path.join(OUTPUT_DIR, OUTPUT_PATH)
    try:
        with open(full_output_path, 'w') as f:
            json.dump(all_results, f, indent=4)
        print(f"All results saved to {full_output_path}")
    except Exception as e:
        print(f"Error saving combined results: {e}")

def main():
    # Test end-to-end BERT
    model_name = 'distilbert-base-uncased'
    classifier = BERTClassifier(model_name=model_name)
    classifier.load_and_prepare_data(DATASET_PATH)
    classifier.train()
    classifier.evaluate()
    
    messages = [
        "someone needed at uttara, my bag has been stolen by someone, I need to contact to the police",
        "জরুরি ভিত্তিতে রক্ত প্রয়োজন, যোগাযোগ - 01552375331",
        "Please help me. One of my relatives need 2 bags O+ve blood for uterus operation at birdem hospital",
        "Keu ektu shahajjo koren, amar fupir jonno birdem hospital e A-ve rokto proyojon",
    ]
    
    classifier.predict_messages(messages)

if __name__ == "__main__":
    main()  # Run single end-to-end BERT evaluation
    # run_all_combinations()  # Run all combinations including end-to-end BERT