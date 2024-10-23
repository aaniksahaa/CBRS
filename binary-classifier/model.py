import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils import shuffle
import gensim.downloader as api
import numpy as np


df = pd.read_csv('./data-preprocessing/dataset.csv')
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
model = LogisticRegression(C=1.0, penalty='l2', solver='lbfgs', max_iter=10000)
model.fit(X_train_tfidf, y_train)

y_pred = model.predict(X_test_tfidf)

accuracy = accuracy_score(y_test,y_pred)

print(f'accuracy {accuracy}') # 0.99 % 
print(f'classification report\n {classification_report(y_pred,y_test)}')


def predict_messages(messages):

    y_pred = model.predict(tfidf.transform(messages))

    for i in range(len(messages)):

        print(f'message: {messages[i]}, prediction: {y_pred[i]}')

messages = ["someone needed at uttara, my bag has been stolen by someone, I need to contact to the police",

"জরুরি ভিত্তিতে রক্ত প্রয়োজন, যোগাযোগ - 01552375331",
"Please help me. One of my relatives need 2 bags O+ve blood for uterus operation at birdem hospital",
"Keu ektu shahajjo koren, amar fupir jonno birdem hospital e A-ve rokto proyojon",
"আমি তোমাকে ভালোবাসি bag Emergency",
"Emergency",
"ব্যাগ"]

predict_messages(messages)

# messages_vector = tfidf.transform(messages)

# # print(f'after vectorization: {messages_vector}')

# y_pred = model.predict(messages_vector)

# print(f'predicted: {y_pred}')

