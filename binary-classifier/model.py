import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils import shuffle
import gensim.downloader as api
import numpy as np


df = pd.read_csv('dataset.csv')
df = shuffle(df, random_state=42)  

print(f'non-blood:\n {(df['label']==0).sum()}')
print(f'blood:\n {(df['label']==1).sum()}')

X = df['message']  # Features (text data)
y = df['label']    # Labels (0 or 1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

# Add L2 regularization
model = LogisticRegression(C=1.0, penalty='l2', solver='lbfgs', max_iter=1000)
model.fit(X_train_tfidf, y_train)

y_pred = model.predict(X_test_tfidf)

accuracy = accuracy_score(y_test,y_pred)

print(f'accuracy {accuracy}') # 0.99 % 

print(f'\n----------Word2Vec model--------\n')

w2v_model = api.load('glove-wiki-gigaword-100')

def text_to_vector(text):

    words = text.split()

    word_vectors = []

    for word in words:

        if word in w2v_model:

            print(f' word: {word} , vector : {w2v_model[word]}')
            word_vectors.append(w2v_model[word])
    
    np.mean(word_vectors,axis=1)

text_to_vector("রক্তদান করা প্রয়োজন বন্ধু")


# messages = ["someone needed at uttara, my purse has been stolen by someone, I need to contact to the police",

# "I am bag, ha ha hol hola",
# "আমি তোমাকে ভালোবাসি bag",
# "Emergency"]

# messages_vector = tfidf.transform(messages)

# # print(f'after vectorization: {messages_vector}')

# y_pred = model.predict(messages_vector)

# print(f'predicted: {y_pred}')

