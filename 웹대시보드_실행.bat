@echo off
chcp 65001 > nul
title 티스토리 AI 오피스 실행기
echo ===================================================
echo [Tistory AI Corp] 웹 그래픽 대시보드 서버를 시작합니다...
echo 크롬 브라우저 자동 포스팅 연동이 준비됩니다.
echo ===================================================
echo.
python tistory_bot.py --web
pause
