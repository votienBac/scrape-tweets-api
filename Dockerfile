FROM python:3.8

# Install Chrome and ChromeDriver dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    libgconf-2-4 \
    libnss3 \
    libgtk-3-0 \
    libx11-xcb1

# Install Chrome
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
RUN apt-get -y update && apt-get -y install google-chrome-stable

# Set ChromeDriver version
ENV CHROMEDRIVER_VERSION 114.0.5735.90

# Install ChromeDriver
RUN curl -sS -o /tmp/chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin
RUN rm /tmp/chromedriver_linux64.zip
RUN chmod +x /usr/local/bin/chromedriver
# set display port to avoid crash
ENV DISPLAY=:99
# Set the working directory inside the Docker container
WORKDIR /app
COPY Scweet/credentials.txt /app/credentials.txt
# Copy the requirements file into the container
COPY requirements.txt .
RUN pip install git+https://github.com/JustAnotherArchivist/snscrape.git
# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Install any required log handlers
RUN pip install logstash
 
# Set the log file path
ENV LOG_FILE /app/logs/app.log
# Copy the application code into the container
COPY . .

# Expose the port that the Flask app will run on
EXPOSE 5000

# Set the entry point command to run the Flask app
CMD ["python", "app.py"]