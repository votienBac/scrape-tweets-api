from segment_keyword import extract_keywords
import snscrape.modules.twitter as sntwitter
import json
import re
class TwitterStreamer:
    # def __init__(self, bootstrap_servers, topic_name):
    #     self.bootstrap_servers = bootstrap_servers
    #     self.topic_name = topic_name
    #     self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
    #                                   api_version=(0, 10, 1),
    #                                   value_serializer=lambda x: json.dumps(x).encode('utf-8'))

    def stream_tweets(self, keyword, total_tweets, report_id):
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

        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(keyword, mode=sntwitter.TwitterSearchScraperMode.TOP).get_items()):
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
                for media in tweet.media:
                    if "Photo" in str(media):
                        url.append(media.fullUrl)
                    elif "Video" in str(media):
                        for variant in media.variants:
                            url.append(variant.url)

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
                'bookmarks': tweet.bookmarkCount,
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
                'report_ids': report_ids
        
            }

            tweets_list.append(tweet_dict)

        return tweets_list