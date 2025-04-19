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

# Define available vectorizers
VECTORIZERS = {
    'tfidf': lambda: TfidfVectorizer(max_features=5000, ngram_range=(1, 2)),
    'count': lambda: CountVectorizer(max_features=5000, ngram_range=(1, 2)),
    'word2vec': lambda: Word2VecVectorizer()  # Custom class defined below
}

# Define available models
MODELS = {
    'logistic': lambda: LogisticRegression(C=1.0, penalty='l2', solver='lbfgs', max_iter=10000),
    'svm': lambda: SVC(kernel='linear', probability=True),
    'random_forest': lambda: RandomForestClassifier(n_estimators=100, random_state=42),
    'naive_bayes': lambda: MultinomialNB()
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
        for text in X:
            words = text.split()
            word_vectors = [self.word2vec[word] for word in words if word in self.word2vec]
            if word_vectors:
                vectors.append(np.mean(word_vectors, axis=0))
            else:
                vectors.append(np.zeros(self.vector_size))
        return np.array(vectors)

class TextClassifier:
    def __init__(self, vectorizer_type='tfidf', model_type='logistic'):
        self.vectorizer = VECTORIZERS[vectorizer_type]()
        self.model = MODELS[model_type]()
        
    def load_and_prepare_data(self, filepath):
        df = pd.read_csv(filepath)
        df = shuffle(df, random_state=42)
        
        print(f"non-blood: {(df['label']==0).sum()}")
        print(f"blood: {(df['label']==1).sum()}")
        
        self.X = df['text']
        self.y = df['label']
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
    
    def train(self):
        self.X_train_vec = self.vectorizer.fit_transform(self.X_train)
        self.X_test_vec = self.vectorizer.transform(self.X_test)
        self.model.fit(self.X_train_vec, self.y_train)
    
    def evaluate(self):
        y_pred = self.model.predict(self.X_test_vec)
        accuracy = accuracy_score(self.y_test, y_pred)
        print(f'Accuracy: {accuracy:.4f}')
        print('Classification Report:')
        print(classification_report(y_pred, self.y_test, digits=8))
        return accuracy
    
    def predict_messages(self, messages):
        messages_vec = self.vectorizer.transform(messages)
        predictions = self.model.predict(messages_vec)
        
        for message, pred in zip(messages, predictions):
            print(f'Message: {message}')
            print(f'Prediction: {pred}\n')

# Usage example
def main():
    # Choose your vectorizer and model
    vectorizer_type = 'word2vec'  # Options: 'tfidf', 'count', 'word2vec'
    model_type = 'random_forest'    # Options: 'logistic', 'svm', 'random_forest', 'naive_bayes'
    
    # Initialize classifier
    classifier = TextClassifier(vectorizer_type=vectorizer_type, model_type=model_type)
    
    # Load and prepare data
    classifier.load_and_prepare_data('./pre_parsed_dataset.csv')
    
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
    
    classifier.predict_messages(messages)

if __name__ == "__main__":
    main()