# ==============================================================================
# [Tistory AI Corp] Railway 24/7 실시간 키워드·상위글 R&D 서버 & 웹 대시보드 Dockerfile
# ==============================================================================
FROM python:3.11-slim

# 시스템 패키지 및 헤드리스 크로미움 설치 (선택적 셀레니움 분석 및 한글 폰트 지원)
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    fonts-nanum \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 환경변수 설정 (Railway 클라우드 모드 및 버퍼링 해제)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HEADLESS=true
ENV RAILWAY_ENVIRONMENT=production
ENV RND_CRAWL_INTERVAL=600

WORKDIR /app

# 파이썬 의존성 설치
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 복사 (tistory_bot.py, tistory_ai_office.html 등)
COPY . /app

# Railway가 동적으로 할당하는 $PORT로 웹 대시보드 & 24/7 실시간 R&D 크롤러 실행
CMD ["python3", "tistory_bot.py", "--web"]
