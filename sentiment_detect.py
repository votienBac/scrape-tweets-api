import nltk
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer

def detect_sentiment(text):
    # Khởi tạo đối tượng SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    
    # Phân loại cảm xúc của đoạn văn bản
    sentiment_scores = sid.polarity_scores(text)
    
    # Trích xuất độ cảm xúc từ kết quả
    compound_score = sentiment_scores['compound']
    
    # Dựa vào compound score để xác định cảm xúc
    if compound_score >= 0.05:
        sentiment = 'positive'
    elif compound_score <= -0.05:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    return sentiment
