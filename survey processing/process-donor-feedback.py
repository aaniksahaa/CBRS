import pandas as pd

def convert_donor_survey_responses(df):
    # Define mapping dictionaries for each question type
    donation_frequency = {
        'Never': 1,
        '1 time': 2,
        '2 times': 3,
        '3 times': 4,
        '4 or more': 5
    }
    
    trouble_finding = {
        'Almost always': 1,  # Note: Reversed scale since this is a negative question
        'Often': 2,
        'Sometimes': 3,
        'Seldom': 4,
        'Never': 5
    }
    
    convenience_scale = {
        'Extremely convenient': 5,
        'Very convenient': 4,
        'Moderately convenient': 3,
        'Slightly convenient': 2,
        'Not at all': 1
    }
    
    message_frequency = {
        '1-5': 1,
        '6-10': 2,
        '11-15': 3,
        '16-20': 4,
        '21 or more': 5
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
        'Not applicable': None,
        'Not applicable  (I have never used any such app before)': None  # Note: handling both formats
    }
    
    # Create a copy of the dataframe
    df_numeric = df.copy()
    
    # Convert each column based on its corresponding scale
    # Q1: Blood donation frequency
    df_numeric.iloc[:, 2] = df_numeric.iloc[:, 2].map(donation_frequency)
    
    # Q2: Trouble finding blood donation requests
    df_numeric.iloc[:, 3] = df_numeric.iloc[:, 3].map(trouble_finding)
    
    # Q3: Convenience of BNet notifications
    df_numeric.iloc[:, 4] = df_numeric.iloc[:, 4].map(convenience_scale)
    
    # Q4: Comfortable message frequency
    df_numeric.iloc[:, 5] = df_numeric.iloc[:, 5].map(message_frequency)
    
    # Q5: Overall functionality
    df_numeric.iloc[:, 6] = df_numeric.iloc[:, 6].map(functionality_scale)
    
    # Q6: Effectiveness compared to other apps
    df_numeric.iloc[:, 7] = df_numeric.iloc[:, 7].map(effectiveness_scale)
    
    # Q7 and Q8 are open-ended responses, so we leave them as is
    
    return df_numeric

filename = "donor-feedback-BNet.csv"

# Read the CSV file
df = pd.read_csv(f"./data/{filename}")

# Convert to numeric format
df_numeric = convert_donor_survey_responses(df)

# Save the converted data to a new CSV file
df_numeric.to_csv(f"./processed/{filename.split('.')[0]}-numeric.csv", index=False)