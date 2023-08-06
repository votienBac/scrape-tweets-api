# from Scweet.user import get_users_following
import json
import random
import asyncio
import twscrape

# file_credentials_path = ".\Scweet\credentials.txt"
# # file_credentials_path = "/app/credentials.txt"
class ScweetScraper:
    async def worker(self, api: twscrape.API, user_id: int):

        followings = []
        try:
            async for u in api.following(user_id):
                followings.append(u.username)
        except Exception as e:
            print(e)
        finally:         
            following_dict = {
                'user_id': str(user_id),
                'followings': followings,
                'count': len(followings)
            }
            return following_dict
    async def scrape_following(self, users):
        api = twscrape.API()
        await api.pool.login_all()
        results = await asyncio.gather(*(self.worker(api, u) for u in users))
        return results


