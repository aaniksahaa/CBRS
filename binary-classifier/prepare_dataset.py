import pandas as pd
import numpy as np
import json
import os


def load_data(label_df,df):
     
     for i in range(len(df)):

        label_df.loc[len(label_df)] = [df.loc[i]['English'],0]
        label_df.loc[len(label_df)] = [df.loc[i]['Banglish'],0]
        label_df.loc[len(label_df)] = [df.loc[i]['Bangla'],0]

     return label_df

df1 = pd.read_csv('./negative-samples/random_messages.csv')
df2 = pd.read_csv('./negative-samples/random_messages_new.csv')

label_df = pd.DataFrame(columns=['message','label'])

label_df = load_data(label_df,df1)
label_df = load_data(label_df,df2)

# print(label_df)

# label_df.to_csv('negative.csv',index=False)

# preparing positive samples

START_DIRECTORY = './positive-samples/'

start = 0
end = 701 

for i in range(start,end+1):
    
    file_name = f"{START_DIRECTORY}{i}.json"

    if os.path.exists(file_name):
        
        print(f"{file_name} found")

        with open(file_name,"r",encoding='utf-8') as file:
            
            data = json.load(file)

            print(f"message {data['message']}")

            label_df.loc[len(label_df)] = [data['message'],1]

# print(len(label_df))

label_df.to_csv('dataset.csv',index=False)

