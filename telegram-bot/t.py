from datetime import datetime

def format_iso_date(iso_date_str):
    # Parse the ISO date string
    date_obj = datetime.fromisoformat(iso_date_str.replace("Z", "+00:00"))
    
    # Format the date as "12 August, 2023"
    formatted_date = date_obj.strftime("%d %B, %Y")
    
    return formatted_date

# Example usage
iso_date = "2023-08-12T00:00:00.000Z"
formatted = format_iso_date(iso_date)
print(formatted)  # Output: 12 August, 2023
