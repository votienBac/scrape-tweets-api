from flask import Flask, request, jsonify
from kafka import KafkaProducer
from cloudword import KafkaTwitterAnalyzer
from twitter_search import TwitterStreamer
from profile_search import ProfileSearch
from Scweet.follower import ScweetScraper
import json
import random
import string


app = Flask(__name__)
bootstrap_servers = ['34.125.143.12:9092']
producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                      api_version=(0, 10, 1),
                                      value_serializer=lambda x: json.dumps(x).encode('utf-8'))

@app.route('/report/get-tweets', methods=['POST'])
def getTweetsReport():
    data = request.get_json()
    query = data.get('query')
    report_id = data.get('report_id')
    size = data.get('size')
    topic_name = 'topic-report-'+str(report_id)

    streamer = TwitterStreamer()
    tweets = streamer.stream_tweets(query, size, report_id)

    sendTweetsToTopic(producer=producer, tweets= tweets, topic_name=topic_name)
    response = jsonify({'tweets_count': len(tweets)})  # Create a JSON response
    return response
@app.route('/projects/get-tweets', methods=['POST'])
def getTweetsForProject():
    data = request.get_json()
    query = data.get('query')
    size = data.get('size')
    topic_name = 'project-tweets'

    streamer = TwitterStreamer()
    tweets = streamer.stream_tweets(query, size, None)

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
def scrape_following_route():
    print("start")
    data = request.json  # Get the JSON data from the request body
    
    if not data or 'users' not in data:
        return jsonify({'error': 'No users data provided'})

    users = data['users']
    if not isinstance(users, dict):
        return jsonify({'error': 'Invalid users data format'})

    scraper = ScweetScraper()
    following = scraper.scrape_following(users=users, verbose=0, headless=True, wait=2)

    return jsonify(following)
def generate_random_string(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string
if __name__ == '__main__':
    app.run(app.run(host='0.0.0.0', port=5000 ))