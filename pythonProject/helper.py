from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
from textblob import TextBlob


extract = URLExtract()

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]
    words = [word for message in df['message'] for word in message.split()]
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    links = [url for message in df['message'] for url in extract.find_urls(message)]

    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df_percent = (df['user'].value_counts() / df.shape[0] * 100).reset_index()
    df_percent.columns = ['name', 'percent']
    return x, df_percent

def create_wordcloud(selected_user, df):
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[(df['user'] != 'group_notification') & (df['message'] != '<Media omitted>\n')]

    def remove_stop_words(message):
        return " ".join([word for word in message.lower().split() if word not in stop_words])

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    return wc.generate(temp['message'].str.cat(sep=" "))

def most_common_words(selected_user, df):
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[(df['user'] != 'group_notification') & (df['message'] != '<Media omitted>\n')]

    words = [word for message in temp['message'] for word in message.lower().split() if word not in stop_words]
    return pd.DataFrame(Counter(words).most_common(20))

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Updated logic to detect emojis using the new `emoji` library
    emojis = [c for message in df['message'] for c in message if emoji.is_emoji(c)]

    return pd.DataFrame(Counter(emojis).most_common(), columns=['emoji', 'count'])


def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)
    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df.groupby('only_date').count()['message'].reset_index()

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)





def create_pdf_summary(df, filename="whatsapp_summary.pdf"):
    # Create instance of FPDF class
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set font for the PDF
    pdf.set_font("Arial", size=12)

    # Add a title to the PDF
    pdf.cell(200, 10, txt="WhatsApp Chat Summary", ln=True, align='C')

    # Add some space
    pdf.ln(10)

    # Add summary information to the PDF
    pdf.cell(200, 10, txt=f"Total messages: {df.shape[0]}", ln=True)
    pdf.cell(200, 10, txt=f"Total users: {df['user'].nunique()}", ln=True)
    pdf.cell(200, 10, txt=f"Start date: {df['date'].min()}", ln=True)
    pdf.cell(200, 10, txt=f"End date: {df['date'].max()}", ln=True)

    # Optionally, you can add more details, such as top users, common words, etc.
    top_users = df['user'].value_counts().head(5)
    pdf.cell(200, 10, txt="Top 5 users:", ln=True)
    for user, count in top_users.items():
        pdf.cell(200, 10, txt=f"{user}: {count} messages", ln=True)

    # Save the PDF file
    pdf.output(filename)

    return filename  # Returning filename to be used for download

def sentiment_analysis(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    sentiments = []
    for message in df['message']:
        blob = TextBlob(message)
        polarity = blob.sentiment.polarity
        if polarity > 0:
            sentiment = 'Positive'
        elif polarity == 0:
            sentiment = 'Neutral'
        else:
            sentiment = 'Negative'
        sentiments.append(sentiment)

    df['sentiment'] = sentiments
    return df

