import asyncio
import json
from twscrape import API, gather
from twscrape.logger import set_log_level

async def main():
    api = API()  # or API("path-to.db") - default is `accounts.db`
# votienbac831,08032001,fishface832001@gmail.com
    # ADD ACCOUNTS (for CLI usage see BELOW)
    await api.pool.add_account("votienbac831", "08032001", "fishface832001@gmail.com", "B@c12345")
    await api.pool.login_all()
    user_id = 952136206980009985
    # await api.user_by_id(user_id)  # User
    followings = await gather(api.following(user_id))
    following_list = []
    for u in followings:
        following_list.append(u.username)
    with open('following.json', 'w', encoding='utf-8') as json_file:
        json.dump(following_list, json_file)  # list[User]
    # print(followings[0])
    # or add account with COOKIES (with cookies login not required)
    # cookies = "abc=12; ct0=xyz"  # or '{"abc": "12", "ct0": "xyz"}'
    # await api.pool.add_account("user3", "pass3", "u3@mail.com", "mail_pass3", cookies=cookies)

    # add account with PROXY
    # proxy = "http://login:pass@example.com:8080"
    # await api.pool.add_account("user4", "pass4", "u4@mail.com", "mail_pass4", proxy=proxy)

    # API USAGE

    # search (latest tab)
    # total_tweets = 10
    # tweets = await gather(api.search("from:RyanNguyenHC", limit=total_tweets))  # list[Tweet]
    # tweets_list = []
    # # print(tweets[0])
    # for i, tweet in enumerate(tweets):
    #         if i > total_tweets:
    #             break

    #         user = tweet.user
    #         user_dict = {
    #             'id': str(user.id),
    #             'username': user.username,
    #             'name': user.displayname,
    #             'url': user.url,
    #             'verified': user.verified,
    #             'followers_count': user.followersCount,
    #             'following_count': user.friendsCount,
    #             'listed_count': user.listedCount,
    #             'favourites_count': user.favouritesCount,
    #             'statuses_count': user.statusesCount,
    #             'profile_image_url': user.profileImageUrl,
    #             'profile_banner_url': user.profileBannerUrl,
    #         }

    #         mentioned_users = []
    #         if tweet.mentionedUsers:
    #             for user1 in tweet.mentionedUsers:
    #                 mentioned_users.append({
    #                     'username': user1.username,
    #                     'id': user1.id
    #                 })
    #         feature_keywords = []
    #         # if tweet.lang != 'vi':
    #         #     feature_keywords = extract_keywords(pre_process(tweet.rawContent))


    #         is_reply = False
    #         if tweet.inReplyToUser:
    #             is_reply = True
            
    #         url = []
    #         photos = []
    #         if tweet.media:
    #             photos = tweet.media.photos
    #             print(photos)
    #             for variant in photos:
    #                 url.append(variant.url)
    #             videos = tweet.media.videos
    #             for variant in videos:
    #                 url.append(variant.url)
    #             animated = tweet.media.animated
    #             for variant in animated:
    #                 url.append(variant.url)


    #         link_dicts = []
    #         if tweet.links:
    #             link_dicts = [link.url for link in tweet.links]

    #         is_retweet = False
    #         if tweet.retweetedTweet:
    #             is_retweet = True

    #         is_quote = False
    #         if tweet.quotedTweet:
    #             is_quote = False
    #         report_ids = []
    #         # if report_id:
    #         #     report_ids.append(report_id)
    #         tweet_dict = {
    #             'id': str(tweet.id),
    #             'conversation_id': str(tweet.conversationId),
    #             'content': tweet.rawContent,
    #             'feature_keywords': feature_keywords,
    #             'date': tweet.date.strftime('%Y-%m-%d %H:%M:%S'),
    #             'username': user.username,
    #             'user_id': str(user.id),
    #             'author': user_dict,
    #             'quotes': tweet.quoteCount,
    #             'retweets': tweet.retweetCount,
    #             'likes': tweet.likeCount,
    #             'replies': tweet.replyCount,
    #             'views': tweet.viewCount,
    #             # 'bookmarks': tweet.bookmarkCount,
    #             'url': tweet.url,
    #             'language': tweet.lang,
    #             'in_reply_to_tweet_id': tweet.inReplyToTweetId,
    #             'mentioned_users': mentioned_users,
    #             'is_reply': is_reply,
    #             'is_retweet': is_retweet,
    #             'is_quote': is_quote,
    #             'hashtags': tweet.hashtags,
    #             'cashtags': tweet.cashtags,
    #             'links': link_dicts,
    #             'media': url,
    #             # 'report_ids': report_ids,
    #             # "sentiment": detect_sentiment(tweet.rawContent)
        
    #         }

    #         tweets_list.append(tweet_dict)
    # print("__________________________________________")
    # print(tweets[0].media.photos)
    # with open('output.json', 'w', encoding='utf-8') as json_file:
    #     json.dump(tweets_list, json_file)

    # tweet info
    # tweet_id = 20
    # await api.tweet_details(tweet_id)  # Tweet
    # await gather(api.retweeters(tweet_id, limit=20))  # list[User]
    # await gather(api.favoriters(tweet_id, limit=20))  # list[User]

    # get user by login
    # user_login = "twitterdev"
    # await api.user_by_login(user_login)  # User

    # user info
    # user_id = 2244994945
    # await api.user_by_id(user_id)  # User
    # await gather(api.followers(user_id, limit=20))  # list[User]
    # await gather(api.following(user_id, limit=20))  # list[User]
    # await gather(api.user_tweets(user_id, limit=20))  # list[Tweet]
    # await gather(api.user_tweets_and_replies(user_id, limit=20))  # list[Tweet]

    # list info
    # list_id = 123456789
    # await gather(api.list_timeline(list_id))

    # NOTE 1: gather is a helper function to receive all data as list, FOR can be used as well:
    # async for tweet in api.search("elon musk"):
    #     print(tweet.id, tweet.user.username, tweet.rawContent)  # tweet is `Tweet` object

    # NOTE 2: all methods have `raw` version (returns `httpx.Response` object):
    # async for rep in api.search_raw("elon musk"):
    #     print(rep.status_code, rep.json())  # rep is `httpx.Response` object

    # change log level, default info
    set_log_level("DEBUG")

    # Tweet & User model can be converted to regular dict or json, e.g.:
    # doc = await api.user_by_id(user_id)  # User
    # doc.dict()  # -> python dict
    # doc.json()  # -> json string

if __name__ == "__main__":
    asyncio.run(main())