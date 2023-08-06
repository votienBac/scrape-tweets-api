docker stop -f docker stop scrape-tweets-api-4
docker rm scrape-tweets-api-4
docker rmi scrape-tweets-api:v1.1.1
docker build -t scrape-tweets-api:v1.1.1 .
docker run --shm-size=2g -d -p 5000:5000 --name scrape-tweets-api-4 scrape-tweets-api:v1.1.1

