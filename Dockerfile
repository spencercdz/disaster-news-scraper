FROM python:3.11-slim

# Install Chrome and ChromeDriver
RUN apt-get update && \
    apt-get install -y wget unzip curl gnupg && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "news_scraper.api.app:app", "--host", "0.0.0.0", "--port", "8000"] 