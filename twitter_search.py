import twscrape
import asyncio
from segment_keyword import extract_keywords
from sentiment_detect import detect_sentiment
import re

class TwitterStreamer:
    # def __init__(self, bootstrap_servers, topic_name):
    #     self.bootstrap_servers = bootstrap_servers
    #     self.topic_name = topic_name
    #     self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
    #                                   api_version=(0, 10, 1),
    #                                   value_serializer=lambda x: json.dumps(x).encode('utf-8'))
 
    async def stream_tweets(self, query, total_tweets, report_id):
        async def worker(api: twscrape.API, q: str, limit: 20):
            tweets = []
            try:
                async for doc in api.search(q, limit):
                    tweets.append(doc)
            except Exception as e:
                print(e)
            finally:
                return tweets
        def textlink_to_dict(textlink):
            return textlink.url
        def pre_process(text):
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
            text = re.sub(r'[^\x00-\x7F]+', '', text)
            text = re.sub(r'\d{1,3}(,\d{3})*', '', text)
            text = re.sub(r'#[^\s]+', '', text)  # Xóa hashtag
            text = re.sub(r'\$\w+', '', text)
            text = text.lower()
            return text
        tweets_list = []
        api = twscrape.API()
        # add accounts here or before from cli (see README.md for examples)
        await api.pool.add_account("BacManucians", "B@c08032001", "bacspm@gmail.com", "B@c08032001")
        await api.pool.login_all()

        # queries = ["elon musk", "tesla", "spacex", "neuralink", "boring company"]
        # list_list_tweets = await asyncio.gather(*(worker(api, q, total_tweets) for q in queries))
        # tweets_list = []
        # # print(tweets[0])
        # for j, tweets in enumerate(list_list_tweets):
        #     if j >= len(list_list_tweets):
        #         break
            # for i, tweet in enumerate(sntwitter.TwitterSearchScraper(keyword, mode=sntwitter.TwitterSearchScraperMode.TOP).get_items()):
        tweets = await worker(api, query, total_tweets)
        for i, tweet in enumerate(tweets):
            if i > total_tweets:
                break
            user = tweet.user
            user_dict = {
                'id': str(user.id),
                'username': user.username,
                'name': user.displayname,
                'url': user.url,
                'verified': user.verified,
                'followers_count': user.followersCount,
                'following_count': user.friendsCount,
                'listed_count': user.listedCount,
                'favourites_count': user.favouritesCount,
                'statuses_count': user.statusesCount,
                'profile_image_url': user.profileImageUrl,
                'profile_banner_url': user.profileBannerUrl,
            }

            mentioned_users = []
            if tweet.mentionedUsers:
                for user1 in tweet.mentionedUsers:
                    mentioned_users.append({
                        'username': user1.username,
                        'id': user1.id
                    })
            feature_keywords = []
            if tweet.lang != 'vi':
                feature_keywords = extract_keywords(pre_process(tweet.rawContent))


            is_reply = False
            if tweet.inReplyToUser:
                is_reply = True
            
            url = []
            if tweet.media:
                photos = tweet.media.photos
                for variant in photos:
                    url.append(variant.url)
                videos = tweet.media.videos
                for variant in videos:
                    url.append(variant.thumbnailUrl)
                animated = tweet.media.animated
                for variant in animated:
                    url.append(variant.thumbnailUrl)

            link_dicts = []
            if tweet.links:
                link_dicts = [textlink_to_dict(link) for link in tweet.links]

            is_retweet = False
            if tweet.retweetedTweet:
                is_retweet = True

            is_quote = False
            if tweet.quotedTweet:
                is_quote = False
            report_ids = []
            if report_id:
                report_ids.append(report_id)
            tweet_dict = {
                'id': str(tweet.id),
                'conversation_id': str(tweet.conversationId),
                'content': tweet.rawContent,
                'feature_keywords': feature_keywords,
                'date': tweet.date.strftime('%Y-%m-%d %H:%M:%S'),
                'username': user.username,
                'user_id': str(user.id),
                'author': user_dict,
                'quotes': tweet.quoteCount,
                'retweets': tweet.retweetCount,
                'likes': tweet.likeCount,
                'replies': tweet.replyCount,
                'views': tweet.viewCount,
                'bookmarks': 0,
                'url': tweet.url,
                'language': tweet.lang,
                'in_reply_to_tweet_id': tweet.inReplyToTweetId,
                'mentioned_users': mentioned_users,
                'is_reply': is_reply,
                'is_retweet': is_retweet,
                'is_quote': is_quote,
                'hashtags': tweet.hashtags,
                'cashtags': tweet.cashtags,
                'links': link_dicts,
                'media': url,
                'report_ids': report_ids,
                "sentiment": detect_sentiment(tweet.rawContent)
        
            }

            tweets_list.append(tweet_dict)

        return tweets_list
    