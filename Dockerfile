FROM python:3.8

# Set the working directory inside the Docker container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .
RUN pip install git+https://github.com/JustAnotherArchivist/snscrape.git
# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the port that the Flask app will run on
EXPOSE 5000

# Set the entry point command to run the Flask app
CMD ["python", "app.py"]