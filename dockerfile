FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HEADLESS=true
ENV RAILWAY_ENVIRONMENT=production
ENV RND_CRAWL_INTERVAL=600

WORKDIR /app

requirements.txt 파일 누락이나 이름 오류에도 무조건 성공하도록 직접 설치

RUN pip install --no-cache-dir requests beautifulsoup4 selenium webdriver-manager

COPY . /app

CMD ["python3", "tistory_bot.py", "--web"]
