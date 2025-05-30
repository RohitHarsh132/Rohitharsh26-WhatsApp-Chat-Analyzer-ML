import re
import pandas as pd

def preprocess(data):
    # Patterns for both 2-digit and 4-digit years, and both AM/PM and am/pm
    pattern_2d = r'\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}\s[apAP][mM]\s-\s'
    pattern_4d = r'\d{1,2}/\d{1,2}/\d{4},\s\d{1,2}:\d{2}\s[apAP][mM]\s-\s'

    # Detect which pattern is present
    if re.findall(pattern_2d, data):
        pattern = pattern_2d
        date_format = '%d/%m/%y, %I:%M %p - '
    elif re.findall(pattern_4d, data):
        pattern = pattern_4d
        date_format = '%d/%m/%Y, %I:%M %p - '
    else:
        raise ValueError("Date pattern not recognized. Please check your chat file format.")

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    df['message_date'] = pd.to_datetime(df['message_date'], format=date_format, errors='coerce')
    df = df.dropna(subset=['message_date'])  # Drop lines that couldn't be parsed
    df.rename(columns={'message_date': 'date'}, inplace=True)

    users, messages = [], []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(str(hour) + "-00")
        elif hour == 0:
            period.append("00-01")
        else:
            period.append(str(hour).zfill(2) + "-" + str(hour + 1).zfill(2))
    df['period'] = period

    return df
