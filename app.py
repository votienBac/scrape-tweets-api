from flask import Flask, request, jsonify
from kafka import KafkaProducer
# from aiokafka import AIOKafkaProducer
from cloudword import KafkaTwitterAnalyzer
from twitter_search import TwitterStreamer
from profile_search import ProfileSearch
from backjob_tracker_follower import TwitterDataProcessor
from apscheduler.schedulers.background import BackgroundScheduler
from parallel_search import ParallelSearch
from follower import ScweetScraper
from account_crawler import AccountCrawler
import time
import json
import random
import string
import asyncio
import os
import twscrape


app = Flask(__name__)
bootstrap_servers = ['34.143.129.50:9092']
producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                      api_version=(0, 10, 1),
                                      value_serializer=lambda x: json.dumps(x).encode('utf-8'))


@app.route('/report/get-tweets', methods=['POST'])
async def getTweetsReport():
    data = request.get_json()
    query = data.get('query')
    report_id = data.get('report_id')
    size = data.get('size')
    topic_name = 'topic-report-'+str(report_id)

    streamer = TwitterStreamer()
    tweets = await streamer.stream_tweets(query, size, report_id)
    print(len(tweets))
    sendTweetsToTopic(producer=producer, tweets= tweets, topic_name=topic_name)
    response = jsonify({'tweets_count': len(tweets)})  # Create a JSON response
    return response
@app.route('/projects/get-tweets', methods=['POST'])
async def getTweetsForProject():
    data = request.get_json()
    query = data.get('query')
    size = data.get('size', 200)
    topic_name = 'project-tweets'
    queries = query.split(',') if isinstance(query, str) else []
    parallel_search = ParallelSearch()
    # Call the main function asynchronously
    # loop = asyncio.get_event_loop()
    tweets = await parallel_search.parallel_search(queries, size)

    sendTweetsToTopic(producer=producer, tweets= tweets, topic_name=topic_name)
    response = jsonify({'tweets_count': len(tweets)})  # Create a JSON response
    return response
@app.route('/user/get-profile', methods=['POST'])
def getProfile():
    data = request.get_json()
    username = data.get('username')
    profile = ProfileSearch()
    user = profile.getProfileByUsername(username)

    if user is None:
        return jsonify({'error': 'Account with username does not exist'}), 400

    response = jsonify(user)  # Create a JSON response
    return response
def sendTweetsToTopic(producer, tweets, topic_name):
    
    for tweet in tweets:
        producer.send(topic=topic_name, value=tweet)
    producer.flush()

@app.route('/report/get-cloudword', methods=['POST'])
def getCloudwordReport():
    data = request.get_json()
    report_id = data.get('report_id')
    size = data.get('size')
    number_tweets = data.get('number_tweets')
    topic_name = 'topic-report-'+str(report_id)
    consumer = topic_name + '-consumer' + generate_random_string(5)
    analyzer = KafkaTwitterAnalyzer(topic_name, consumer, number_tweets)
    cloudwords = analyzer.process_tweets(size)
    # Convert int64 elements to regular integers
    cloudwords = [{'text': word['text'], 'count': int(word['count'])} for word in cloudwords]
    response = jsonify({'cloudwords': cloudwords})  # Create a JSON response
    return response
@app.route('/scrape_following', methods=['POST'])
async def scrape_following_route():
    data = request.json  # Get the JSON data from the request body
    
    if not data or 'users' not in data:
        return jsonify({'error': 'No users data provided'})

    users = data['users']
    # if not isinstance(users, dict):
    #     return jsonify({'error': 'Invalid users data format'})

    scraper = ScweetScraper()
    following = await scraper.scrape_following(users=users)
    sendProfilesToTopic(producer, following, "following_tracker")

    return jsonify({'count': len(following)})
def generate_random_string(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

async def cron_job():
    print("start cron job")
    # Sử dụng lớp TwitterDataProcessor
    host = '34.143.129.50'
    port = 5432
    database = 'insightweets'
    user = 'datn'
    password = '08032001'
    processor = TwitterDataProcessor(host, port, database, user, password)
    results = await processor.process_data()
    sendProfilesToTopic(producer, results, "following_tracker")

def sendProfilesToTopic(producer, profiles, topic_name):
    for profile in profiles:
        producer.send(topic=topic_name, value=profile)
    producer.flush()

# Create an instance of BackgroundScheduler
scheduler = BackgroundScheduler()

# Add a synchronous wrapper function for the async cron_job
def cron_job_wrapper():
    asyncio.run(cron_job())

# Add the cron_job_wrapper as a job to the scheduler
scheduler.add_job(cron_job_wrapper, 'interval', hours=24)
@app.route('/api/import-accounts', methods=['POST'])
async def import_accounts():
    # data = request.text  # Get the JSON data from the request body
    
    # if not data or 'line_format' not in data:
    #     return jsonify({'error': 'No users data provided'})

    # line_format = data['line_format']
    line_format = "username|password|email|email_password"
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if file:
        file_path = os.path.join('./uploads', file.filename)
        file.save(file_path)
        api = twscrape.API()
        await api.pool.load_from_file(file_path, line_format)
        os.remove(file_path)
        return jsonify({"message": "Accounts imported successfully"}), 200
@app.route('/api/get-accounts', methods=['GET'])
async def get_accounts():
    api = twscrape.API()
    account_list = await api.pool.accounts_info()
    return jsonify(account_list)
if __name__ == '__main__':
    # Khởi động scheduler
    scheduler.start()
    app.run(app.run(host='0.0.0.0', port=5000 ))