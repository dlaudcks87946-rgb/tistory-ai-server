FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV HEADLESS=true
ENV RAILWAY_ENVIRONMENT=production
RUN pip install --no-cache-dir requests beautifulsoup4 selenium webdriver-manager
COPY . /app
CMD ["python3", "tistory_bot.py", "--web"]
