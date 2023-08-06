from kafka import KafkaConsumer
from nltk.tokenize import word_tokenize
from json import loads
import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer


class KafkaTwitterAnalyzer:
    def __init__(self, topic_name: str, consumer: str, number_tweets: int):
        self.consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers='34.143.129.50:9092',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=consumer,
            value_deserializer=lambda x: loads(x.decode('utf-8'))
        )
        self.df = pd.DataFrame(columns=['content'])
        self.number_tweets = number_tweets
        self.stopword_file = "./stopwords.txt"
        self.stopword_list = []
        self.to_drop = ["LP LOCKED",
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

    def pre_process(self, text):
        text = re.sub('http://\S+|https://\S+', '', text)
        text = re.sub('http[s]?://\S+', '', text)
        text = re.sub(r"http\S+", "", text)
        text = re.sub('&amp', 'and', text)
        text = re.sub('&lt', '<', text)
        text = re.sub('&gt', '>', text)
        text = re.sub('[\r\n]+', ' ', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        text = re.sub('\s+', ' ', text)
        text = text.lower()
        # print(text)
        return text

    def keywords(self, sentence):
        word_list = re.findall(r'\b\w+_\w+\b|\b\w+\b', sentence)
        result = []
        for word in word_list:
            if '_' in word:
                word = word.replace('_', '')
            result.append(word)
        return result

    def load_stopwords(self):
        with open(self.stopword_file, 'r', encoding='utf-8') as file:
            self.stopword_list = [line.strip() for line in file.readlines()]

    def expand_contractions(self, text):
        try:
            return contractions.fix(text)
        except:
            return text

    def remove_stopwords(self, text):
        stopwords = self.stopword_list
        tokens = word_tokenize(text.lower())
        filtered_tokens = [word for word in tokens if word not in stopwords]
        filtered_text = ' '.join(filtered_tokens)
        return filtered_text

    def get_top_n_bigram(self, corpus, n=None):
        vec = CountVectorizer(ngram_range=(2, 2), stop_words='english').fit(corpus)
        bag_of_words = vec.transform(corpus)
        sum_words = bag_of_words.sum(axis=0)
        words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
        words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
        return words_freq[:n]

    def process_tweets(self, size: int):
        self.load_stopwords()
        i = 1
        result = []  # List to store the text and count objects
        for message in self.consumer:
            content = message.value['content']
            self.df = self.df._append({'content': content}, ignore_index=True)
            if i >= self.number_tweets:
                print("no more message")
                break
            i += 1

        self.consumer.close()
        self.df['expanded_text'] = self.df['content'].apply(self.expand_contractions)
        self.df['processed_text'] = self.df['expanded_text'].apply(self.pre_process)
        self.df['processed_text'] = self.df['processed_text'].apply(self.remove_stopwords)
        print(self.df[self.df['processed_text'].str.contains('https', case=False)]['content'])

        common_words = self.get_top_n_bigram(self.df['processed_text'], size)


        for word, count in common_words:
            result.append({'text': word, 'count': count})

        return result



# Usage

