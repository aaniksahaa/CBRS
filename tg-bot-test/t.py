import calendar
from datetime import datetime

# Get full month names
full_month_names = [calendar.month_name[i] for i in range(1, 13)]
print(full_month_names)  # ['January', 'February', 'March', 'April', ...]

# Get abbreviated month names
short_month_names = [calendar.month_abbr[i] for i in range(1, 13)]
print(short_month_names)  # ['Jan', 'Feb', 'Mar', 'Apr', ...]

# Current date and time
now = datetime.now()
print(now.strftime("%B %d, %Y"))  # Full month name, day, year

print(calendar.month_abbr[0])
