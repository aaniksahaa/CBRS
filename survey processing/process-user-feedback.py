import pandas as pd

def convert_survey_responses(df):
    # Define mapping dictionaries for each question type
    freq_scale = {
        'Almost always': 5,
        'Often': 4,
        'Sometimes': 3,
        'Seldom': 2,
        'Never': 1
    }
    
    satisfaction_scale = {
        'Very satisfied': 5,
        'Satisfied': 4,
        'Neither': 3,
        'Dissatisfied': 2,
        'Very dissatisfied': 1
    }
    
    ease_scale = {
        'Extremely easy': 5,
        'Very easy': 4,
        'Moderately easy': 3,
        'Slightly easy': 2,
        'Not at all': 1
    }
    
    intuitive_scale = {
        'Extremely intuitive': 5,
        'Very intuitive': 4,
        'Moderately intuitive': 3,
        'Slightly intuitive': 2,
        'Not at all': 1
    }
    
    functionality_scale = {
        'Excellent': 5,
        'Above Average': 4,
        'Average': 3,
        'Below Average': 2,
        'Very Poor': 1
    }
    
    effectiveness_scale = {
        'Much better': 5,
        'Somewhat better': 4,
        'Stayed the same': 3,
        'Somewhat worse': 2,
        'Much worse': 1,
        'Not applicable (I have never used any such app before)': None
    }
    
    # Create a copy of the dataframe
    df_numeric = df.copy()
    
    # Convert each column based on its corresponding scale
    # Q1: Social media blood donation request frequency
    df_numeric.iloc[:, 2] = df_numeric.iloc[:, 2].map(freq_scale)
    
    # Q2: Timely responses before BNet
    df_numeric.iloc[:, 3] = df_numeric.iloc[:, 3].map(freq_scale)
    
    # Q3: Satisfaction with BNet response time
    df_numeric.iloc[:, 4] = df_numeric.iloc[:, 4].map(satisfaction_scale)
    
    # Q4: Success in connecting with donors through BNet
    df_numeric.iloc[:, 5] = df_numeric.iloc[:, 5].map(freq_scale)
    
    # Q5: Ease of using BNet command-line prompts
    df_numeric.iloc[:, 6] = df_numeric.iloc[:, 6].map(ease_scale)
    
    # Q6: Interface intuitiveness
    df_numeric.iloc[:, 7] = df_numeric.iloc[:, 7].map(intuitive_scale)
    
    # Q7: Overall functionality
    df_numeric.iloc[:, 8] = df_numeric.iloc[:, 8].map(functionality_scale)
    
    # Q8: Effectiveness compared to other apps
    df_numeric.iloc[:, 9] = df_numeric.iloc[:, 9].map(effectiveness_scale)
    
    # Q9 and Q10 are open-ended responses, so we leave them as is
    
    return df_numeric

filename = "user-feedback-BNet.csv"

# Read the CSV file
df = pd.read_csv(f"./data/{filename}")

# Convert to numeric format
df_numeric = convert_survey_responses(df)

# Save the converted data to a new CSV file
df_numeric.to_csv(f"./processed/{filename.split('.')[0]}-numeric.csv", index=False)