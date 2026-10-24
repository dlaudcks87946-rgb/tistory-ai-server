@echo off
chcp 65001 > nul
title 티스토리 AI 오피스 봇 서버
echo ===================================================
echo [Tistory AI Corp] 티스토리 봇 서버를 실행합니다...
echo 브라우저에서 버튼을 누르면 크롬 창이 자동 실행됩니다.
echo ===================================================
echo.
python run_web.py
pause
