import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils import shuffle


df = pd.read_csv('dataset.csv')
df = shuffle(df, random_state=42)  

X = df['message']  # Features (text data)
y = df['label']    # Labels (0 or 1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


tfidf = TfidfVectorizer(max_features=5000)  
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)


model = LogisticRegression()
model.fit(X_train_tfidf, y_train)


y_pred = model.predict(X_test_tfidf)


accuracy = accuracy_score(y_test, y_pred)
classification_rep = classification_report(y_test, y_pred,target_names=['Not blood request','Blood request'])

# Print the results
print(f"Accuracy: {accuracy}")
print("Classification Report:")
print(classification_rep)
