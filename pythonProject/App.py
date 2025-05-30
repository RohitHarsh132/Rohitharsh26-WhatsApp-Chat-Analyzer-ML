import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from fpdf import FPDF
import tempfile
import os
import numpy as np

# Enhanced WhatsApp-like UI with patterned background
st.markdown("""
<style>
    .stApp {
        background-color: #111b21;
        color: #e9edef;
        background-image: url('https://raw.githubusercontent.com/WhatsApp/whatsapp-brand/master/backgrounds/whatsapp-bg-dark.png');
        background-size: cover;
        background-repeat: repeat;
    }
    .stSidebar {
        background-color: #202c33 !important;
        border-radius: 0 20px 20px 0;
    }
    .stButton>button {
        background-color: #00a884;
        color: white;
        border-radius: 20px;
        font-weight: bold;
    }
    .stSelectbox>div>div>select {
        background-color: #202c33;
        color: #e9edef;
        border-radius: 10px;
    }
    .stFileUploader>div>div>button {
        background-color: #00a884;
        color: white;
        border-radius: 20px;
    }
    .stDataFrame {
        background-color: #202c33;
        color: #e9edef;
        border-radius: 10px;
    }
    .stTitle, .stHeader {
        color: #e9edef;
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }
    .css-1d391kg, .css-1v0mbdj, .css-1kyxreq {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    # Only clear figures and reset PDF state if a new file is uploaded
    if 'last_uploaded_file' not in st.session_state or st.session_state['last_uploaded_file'] != uploaded_file.name:
        st.session_state['figures'] = []
        st.session_state['pdf_ready'] = False
        base_name = uploaded_file.name.rsplit('.', 1)[0]
        pdf_file_name = base_name + ".pdf"
        st.session_state['pdf_file_name'] = pdf_file_name
        st.session_state['last_uploaded_file'] = uploaded_file.name
    # Convert the uploaded file to string
    data = uploaded_file.getvalue().decode("utf-8")

    # Preprocess the data with your preprocessor function
    df = preprocessor.preprocess(data)

    # Fetch unique users
    user_list = df['user'].unique().tolist()

    # Remove 'group_notification' if it exists
    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis with respect to", user_list)

    if st.sidebar.button("Show Analysis"):
        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # Place this after all your figures are created in the analysis section
        figures = []

        # Collect figures as (title, fig) tuples
        # Example: after each chart, add to the list
        # Monthly Timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig1, ax1 = plt.subplots()
        ax1.bar(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Message Count')
        ax1.set_title('Monthly Timeline')
        st.pyplot(fig1)
        st.session_state['figures'].append(("Monthly Timeline", fig1))

        # Daily Timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig2, ax2 = plt.subplots()
        ax2.hist(daily_timeline['only_date'], bins=30, color='red', edgecolor='black')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Message Count')
        ax2.set_title('Daily Timeline')
        plt.xticks(rotation='vertical')
        st.pyplot(fig2)
        st.session_state['figures'].append(("Daily Timeline", fig2))

        # Activity Map
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig3, ax3 = plt.subplots()
            ax3.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig3)
            st.session_state['figures'].append(("Most Busy Day", fig3))

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig4, ax4 = plt.subplots()
            ax4.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig4)
            st.session_state['figures'].append(("Most Busy Month", fig4))

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig5, ax5 = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax5)
        st.pyplot(fig5)
        st.session_state['figures'].append(("Weekly Activity Map", fig5))

        # Most Busy Users
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig6, ax6 = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax6.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig6)
                st.session_state['figures'].append(("Most Busy Users", fig6))
            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig7, ax7 = plt.subplots()
        ax7.imshow(df_wc)
        st.pyplot(fig7)
        st.session_state['figures'].append(("Wordcloud", fig7))

        # Most Common Words
        most_common_df = helper.most_common_words(selected_user, df)
        fig8, ax8 = plt.subplots()
        ax8.barh(most_common_df[0], most_common_df[1], color='blue')
        plt.xticks(rotation='vertical')
        st.title('Most Common Words')
        st.pyplot(fig8)
        st.session_state['figures'].append(("Most Common Words", fig8))

        # Emoji Analysis
        emoji_df = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig9, ax9 = plt.subplots()
            ax9.pie(emoji_df['count'].head(), labels=emoji_df['emoji'].head(), autopct="%0.2f")
            st.pyplot(fig9)
            st.session_state['figures'].append(("Emoji Analysis", fig9))

        # Sentiment Analysis
        st.title("Sentiment Analysis")
        df = helper.sentiment_analysis(selected_user, df)
        st.write("Sentiment scores range from -1 (negative) to 1 (positive).")
        st.dataframe(df[['user', 'message', 'sentiment']])
        # Optionally, you can add a chart for sentiment distribution
        sentiment_counts = df['sentiment'].value_counts()
        fig10, ax10 = plt.subplots()
        ax10.bar(sentiment_counts.index, sentiment_counts.values, color=['green', 'red', 'gray'])
        ax10.set_title('Sentiment Distribution')
        st.pyplot(fig10)
        st.session_state['figures'].append(("Sentiment Distribution", fig10))

        # If the user uploaded a file, you can process and show a sample of it
        st.title("Sample Data")
        st.dataframe(df.head())

        # After all your analysis and chart creation code
        st.write("Number of charts to include in PDF:", len(figures))

        if not figures:
            st.warning("Please upload a chat file and run the analysis before generating the PDF.")
        else:
            if st.button("Generate PDF Report"):
                st.session_state['pdf_bytes'] = generate_pdf(figures)
                st.session_state['pdf_ready'] = True

        if st.session_state.get('pdf_ready', False):
            st.download_button(
                label="Download PDF",
                data=st.session_state['pdf_bytes'],
                file_name=st.session_state.get('pdf_file_name', 'dashboard.pdf'),
                mime="application/pdf"
            )

def generate_pdf(figures):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="WhatsApp Chat Analysis Dashboard", ln=True, align='C')
    pdf.ln(10)
    image_paths = []
    for title, fig in figures:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as imgfile:
            fig.savefig(imgfile.name, bbox_inches='tight')
            image_paths.append((title, imgfile.name))
    for title, img_path in image_paths:
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=title, ln=True)
        pdf.image(img_path, w=180)
        pdf.ln(10)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)
        tmpfile.flush()
        tmpfile.seek(0)
        pdf_bytes = tmpfile.read()
    # Now delete all image files
    for _, img_path in image_paths:
        try:
            os.unlink(img_path)
        except Exception:
            pass
    os.unlink(tmpfile.name)
    return pdf_bytes

plt.rcParams['font.family'] = 'Segoe UI Emoji'

# Ensure session state for figures and PDF bytes
if 'figures' not in st.session_state:
    st.session_state['figures'] = []
if 'pdf_bytes' not in st.session_state:
    st.session_state['pdf_bytes'] = None
if 'pdf_ready' not in st.session_state:
    st.session_state['pdf_ready'] = False

# ... your analysis and chart creation code ...
# After creating each figure, add it to st.session_state['figures']
# Example:
# st.session_state['figures'].append(("Monthly Timeline", fig1))

# At the end, show the number of charts
st.write("Number of charts to include in PDF:", len(st.session_state['figures']))

if len(st.session_state['figures']) == 0:
    st.warning("Please upload a chat file and run the analysis before generating the PDF.")
else:
    if st.button("Generate PDF Report"):
        st.session_state['pdf_bytes'] = generate_pdf(st.session_state['figures'])
        st.session_state['pdf_ready'] = True

if st.session_state['pdf_ready'] and st.session_state['pdf_bytes']:
    st.download_button(
        label="Download PDF",
        data=st.session_state['pdf_bytes'],
        file_name=st.session_state.get('pdf_file_name', 'dashboard.pdf'),
        mime="application/pdf"
    )


