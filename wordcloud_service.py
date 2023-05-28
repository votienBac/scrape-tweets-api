from kafka import KafkaConsumer
from py_vncorenlp import VnCoreNLP
import nltk

from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from json import loads
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image
import numpy as np
import pandas as pd
from nltk.stem import WordNetLemmatizer

def pre_process(text):
    # Remove links
    text = re.sub('http://\S+|https://\S+', '', text)
    text = re.sub('http[s]?://\S+', '', text)
    text = re.sub(r"http\S+", "", text)

    text = re.sub('&amp', 'and', text)
    text = re.sub('&lt', '<', text)
    text = re.sub('&gt', '>', text)

    # Remove new line characters
    text = re.sub('[\r\n]+', ' ', text)

    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    # # Remove hashtags
    # text = re.sub(r'#\w+', '', text)
    # # Remove cashtags
    # text = re.sub(r'\$\w+', '', text)
    # Remove multiple space characters
    text = re.sub('\s+',' ', text)
    
    # Convert to lowercase
    text = text.lower()
    return text
def keywords(sentence: str):
  word_list = re.findall(r'\b\w+_\w+\b|\b\w+\b', sentence)
  result = []
  for word in word_list:
      if '_' in word:
          word = word.replace('_', '')
      result.append(word)
  return result
# Thiết lập Kafka consumer
consumer = KafkaConsumer('topic-report-1', bootstrap_servers='datn:9092',     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='test5',
     value_deserializer=lambda x: loads(x.decode('utf-8')))

# Đọc message từ Kafka
df = pd.DataFrame(columns=['content'])
number_tweets = 196
is_complete = False  # Flag variable
i=1
for message in consumer:
    content = message.value['content']
    df = df._append({'content': content}, ignore_index=True) 
    print(i)
    if i >= number_tweets:
        break
    i=i+1

# Close the Kafka consumer
consumer.close()

stopword_file = "./stopwords.txt"
stopword_list = []

df['processed_text'] = df['content'].apply(pre_process)
to_drop = ["LP LOCKED",
  "This guy accumulated over $100K",
  "accumulated 1 ETH",
  "help me sell a nickname",
  "As A Big **** *** To The SEC",
  "Wanna be TOP G", 
  "#walv",
  "#NFTProject", 
  "#1000xgem",
  "$GALI",
  "NFT",
  "What the Soul of USA is",
  "#BUSD",
  "$FXMS",
  "#fxms",
  "#Floki",
  "#FLOKIXMAS",
  "#memecoin",
  "#lowcapgem",
  "#frogxmas",
  "Xmas token",
  "crypto space",
  "Busd Rewards",
  "TRUMPLON", 
  "NO PRESALE",
  "#MIKOTO",
  "$HATI", 
  "$SKOLL", 
  "#ebaydeals",
  "CHRISTMAS RABBIT", 
  "@cz_binance", 
  "NFT Airdrop", 
  "#NFT",
  "$btc",
  "retweet",
  "usd",
  "pin",
  "1",
  "tweets", 
  "hey",
  "retweets",
  "pinned",
  "btc",
  "eth",
  "1y",
  "1d",
  "3m",
  "1w",
  "1m",
  "https"]
# Đọc nội dung từ tệp tin stopword.txt
with open(stopword_file, 'r', encoding='utf-8') as file:
    stopword_list = [line.strip() for line in file.readlines()]

stopwords = list(STOPWORDS) + stopword_list + to_drop
def expand_contractions(text):
  try:
    return contractions.fix(text)
  except:
    return text
  
def remove_stopwords(text):
    # Tiền xử lý văn bản
    tokens = word_tokenize(text.lower())

    # Xóa stopword
    filtered_tokens = [word for word in tokens if word not in stopwords]

    # Kết hợp các từ lại thành văn bản
    filtered_text = ' '.join(filtered_tokens)

    return filtered_text
df['expanded_text'] = df['content'].apply(expand_contractions)
df['processed_text'] = df['expanded_text'].apply(pre_process)

df['processed_text'] = df['expanded_text'].apply(remove_stopwords)

from sklearn.feature_extraction.text import CountVectorizer
def get_top_n_bigram(corpus, n=None):
    vec = CountVectorizer(ngram_range=(2, 2), stop_words='english').fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0) 
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key = lambda x: x[1], reverse=True)
    return words_freq[:n]

common_words = get_top_n_bigram(df['processed_text'], 40)
print(common_words)
import plotly.express as px

df1 = pd.DataFrame(common_words, columns=['TweetText', 'count'])
top_20_bigrams = df1.groupby('TweetText').sum()['count'].sort_values(ascending=False).head(40)

fig = px.bar(x=top_20_bigrams.index, y=top_20_bigrams.values, title='Top 20 bigrams in Tweet before removing spams')
fig.update_xaxes(title='Bigram')
fig.update_yaxes(title='Count')
fig.show()


