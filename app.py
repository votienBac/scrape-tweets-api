from flask import Flask, request, jsonify
from kafka import KafkaProducer
from cloudword import KafkaTwitterAnalyzer
from twitter_search import TwitterStreamer
from profile_search import ProfileSearch
import json


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
    consumer = topic_name + '-consumer'
    analyzer = KafkaTwitterAnalyzer(topic_name, consumer, number_tweets)
    cloudwords = analyzer.process_tweets(size)
    # Convert int64 elements to regular integers
    cloudwords = [{'text': word['text'], 'count': int(word['count'])} for word in cloudwords]
    response = jsonify({'cloudwords': cloudwords})  # Create a JSON response
    return response

if __name__ == '__main__':
    app.run()