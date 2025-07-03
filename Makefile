install:
	pip install -r requirements.txt

run:
	python3 news_scraper/main.py

test:
	pytest news_scraper/tests/ 