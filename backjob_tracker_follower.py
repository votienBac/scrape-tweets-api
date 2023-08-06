from query_database import DatabaseQuery
from follower import ScweetScraper
import asyncio

class TwitterDataProcessor:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.query = DatabaseQuery(host, port, database, user, password)
        self.scraper = ScweetScraper()

    async def process_data(self):
        # Kết nối đến cơ sở dữ liệu
        self.query.connect()

        # Thực thi truy vấn
        db_query = """
        SELECT twitter_user.id
        FROM tweetnalysis.tracker
        LEFT JOIN tweetnalysis.twitter_user ON twitter_user.id = tracker.uid
        """
        results = self.query.execute_query(db_query)

        users = []
        # Xử lý và sử dụng kết quả truy vấn
        for row in results:
            # Xử lý từng hàng kết quả
            users.append(row[0])

        # Ngắt kết nối với cơ sở dữ liệu
        self.query.disconnect()

        # Scrape dữ liệu từ danh sách người dùng
        followings = await self.scraper.scrape_following(users=users)
        # followings = []
        # Xử lý dữ liệu
        # ...

        # Trả về kết quả xử lý
        return followings


