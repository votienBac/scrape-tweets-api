import twscrape
import asyncio
import sqlite3

class AccountCrawler:
    async def addAccount(self, file_path):
        api = twscrape.API()  # Use your desired database path here
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    fields = line.split(',')
                    if len(fields) >= 4:
                        username, password, mail, mail_password = fields[:4]
                        cookies = fields[4] if len(fields) > 4 else None
                        proxy = fields[5] if len(fields) > 5 else None
                        await api.pool.add_account(username, password, mail, mail_password, cookies=cookies, proxy=proxy)
    def get_accounts(self, page=1, size=10):
        offset = (page - 1) * size

        conn = sqlite3.connect("./accounts.db")
        cursor = conn.cursor()

        # Read accounts from the 'accounts' table with pagination
        cursor.execute("SELECT * FROM accounts LIMIT ? OFFSET ?", (size, offset))
        rows = cursor.fetchall()
        
        # Close the connection
        conn.close()

        return rows        
    # async def addAccount(self, account):
    #     api = API()  # or API("path-to.db") - default is `accounts.db`
    #     # votienbac831,08032001,fishface832001@gmail.com
    #     # ADD ACCOUNTS (for CLI usage see BELOW)
    #     await api.pool.add_account("votienbac831", "08032001", "fishface832001@gmail.com", "B@c12345")


    #     print(followings[0])
    #     # or add account with COOKIES (with cookies login not required)
    #     cookies = "abc=12; ct0=xyz"  # or '{"abc": "12", "ct0": "xyz"}'
    #     await api.pool.add_account("user3", "pass3", "u3@mail.com", "mail_pass3", cookies=cookies)

    #     # add account with PROXY
    #     proxy = "http://login:pass@example.com:8080"
    #     await api.pool.add_account("user4", "pass4", "u4@mail.com", "mail_pass4", proxy=proxy)
    
