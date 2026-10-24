#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[Tistory AI Corp] 감성 B-Roll 영상 + 로파이(Lo-Fi) 비트 바이럴 숏폼(Shorts / Reels) 렌더링 파이프라인
- 지루한 강의식 말투 100% 제거 ➔ 20초 압축 도파민/호기심/시크릿 스토리텔링 대본 엔진
- MS Edge-TTS 고음질 AI 성우(ko-KR-SunHiNeural) + 12% 쾌속 비트 전달
- 감성 로파이 힙합 BGM(assets/audio/lofi_beat.mp3) 자동 믹싱 (Voice 100% + BGM 18%)
- 1080x1920 세로형 9:16 시선 강탈 키네틱 타이포그래피 & 글래스모피즘 자막
- FFmpeg 무손실 파이프라인으로 15초 만에 초고속 렌더링
"""

import os
import sys
import time
import json
import math
import asyncio
import subprocess
import re
from typing import Dict, List, Optional
from PIL import Image, ImageDraw, ImageFont
import edge_tts
import imageio_ffmpeg

# Windows 콘솔 인코딩 방어
if sys.platform.startswith("win"):
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


class ShortsScriptGenerator:
    """주제를 20~25초 분량의 바이럴 3단계(후킹-갈등/전개-사이다/반전/댓글유도) 스토리텔링 대본으로 변환"""

    @staticmethod
    def generate_script(topic: str, blog_url: str = "", category: str = "auto") -> Dict:
        clean_topic = topic.strip() or "내 도시락 맨날 훔쳐먹던 꼰대 상사 참교육한 썰"
        clean_url = blog_url.strip() or "https://tistory-ai-corp.tistory.com"

        # ==========================================
        # [썰 쇼츠 1] 직장 상사 참교육 사이다 썰
        # ==========================================
        if category in ["workplace", "직장사이다", "직장"] or (
            category == "auto" and any(k in clean_topic for k in ["직장", "상사", "꼰대", "회사", "과장", "부장", "월급", "퇴사", "사이다", "참교육", "법카", "도시락"])
        ):
            return {
                "title": f"🔥 [사이다] {clean_topic[:24]} #Shorts #사이다썰",
                "tags": ["직장인사이다", "회사썰", "상사참교육", "사이다", "Shorts", "Reels"],
                "pinned_comment": "📌 여러분도 직장에서 겪어본 최악의 빌런이 있나요? 댓글로 사연을 남겨주세요! (채널 구독 & 좋아요는 큰 힘이 됩니다 ❤️)",
                "broll_pref": "norm_broll_typing.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[댓글] 여러분의 생각은? 댓글로 남겨주세요!",
                "scenes": [
                    {
                        "badge": "[HOT] 직장 사이다 썰",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "내 도시락 훔쳐먹던",
                        "hero_line2": "꼰대 과장 참교육!",
                        "accent": "꼰대 과장 참교육!",
                        "speech": "회사에서 매일 제 도시락을 한두 입씩 뺏어먹던 꼰대 과장님, 참다못해 제가 결단을 내렸습니다."
                    },
                    {
                        "badge": "[작전] 비밀 작전 개시",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "불마왕 캡사이신 소스",
                        "hero_line2": "도시락에 듬뿍 투하!",
                        "accent": "도시락에 듬뿍 투하!",
                        "speech": "점심시간 직전에 세상에서 가장 매운 불마왕 캡사이신 소스를 밥 속에 듬뿍 숨겨두고 모른 척 자리를 비웠습니다."
                    },
                    {
                        "badge": "[폭발] 탕비실 대참사",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "탕비실 비명 소리!",
                        "hero_line2": "우유 찾고 난리법석",
                        "accent": "우유 찾고 난리법석",
                        "speech": "잠시 후 탕비실에서 과장님 비명이 터지더니, 얼굴이 새빨개져서 땀을 뻘뻘 흘리며 정수기 물을 들이켜더라고요."
                    },
                    {
                        "badge": "[결말] 통쾌한 사이다",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "그 뒤로 손도 못 댐!",
                        "hero_line2": "여러분 생각은?",
                        "accent": "여러분 생각은?",
                        "speech": "그 뒤로는 제 도시락 근처에도 얼씬 못 하고 있습니다. 여러분이라면 이 상황에서 어떻게 하셨을 것 같나요?"
                    }
                ]
            }

        # ==========================================
        # [썰 쇼츠 2] 소개팅 역대급 레전드 빌런 썰
        # ==========================================
        if category in ["blind_date", "소개팅빌런", "소개팅"] or (
            category == "auto" and any(k in clean_topic for k in ["소개팅", "데이트", "연애", "빌런", "뷔페", "더치페이", "남친", "여친", "카톡", "바람", "결혼"])
        ):
            return {
                "title": f"💔 [소개팅 썰] {clean_topic[:24]} #Shorts #레전드썰",
                "tags": ["소개팅썰", "연애빌런", "레전드썰", "더치페이", "Shorts", "Reels"],
                "pinned_comment": "📌 여러분이 겪었던 가장 황당했던 소개팅은 무엇인가요? 댓글로 공유해 주세요! 💬",
                "broll_pref": "norm_broll_coffee.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[댓글] 이런 사람 만나보셨나요? 댓글 공유!",
                "scenes": [
                    {
                        "badge": "[HOT] 소개팅 레전드 썰",
                        "badge_color": (244, 63, 94),
                        "hero_line1": "소개팅 첫 만남에",
                        "hero_line2": "화장실로 튄 소개팅남",
                        "accent": "화장실로 튄 소개팅남",
                        "speech": "주말에 소개팅을 나갔는데, 첫 만남부터 비싼 호텔 뷔페를 가자더니 계산할 때 지갑을 안 가져왔다는 겁니다."
                    },
                    {
                        "badge": "[위기] 30분째 잠적",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "화장실 간다더니",
                        "hero_line2": "황당한 카톡 한 통",
                        "accent": "황당한 카톡 한 통",
                        "speech": "화장실 다녀온다더니 30분째 안 오길래 전화했더니, 급한 약속이 생겨서 먼저 갔다며 톡이 오더라고요."
                    },
                    {
                        "badge": "[응징] 경찰 신고 접수",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "CCTV 즉시 확보 후",
                        "hero_line2": "경찰에 무전취식 신고!",
                        "accent": "경찰에 무전취식 신고!",
                        "speech": "너무 어이가 없어서 매니저님과 함께 CCTV를 확보하고, 곧바로 경찰서에 무전취식으로 신고 접수했습니다."
                    },
                    {
                        "badge": "[결말] 사이다 칼송금",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "경찰 연락 가자마자",
                        "hero_line2": "1분 만에 전액 입금!",
                        "accent": "1분 만에 전액 입금!",
                        "speech": "경찰관 연락을 받자마자 1분 만에 싹싹 빌며 전액을 칼송금하더라고요. 진짜 여러분은 살면서 이런 황당한 사람 만나보셨나요?"
                    }
                ]
            }

        # ==========================================
        # [썰 쇼츠 3] 소름돋는 현실 미스터리/반전 썰
        # ==========================================
        if category in ["mystery", "소름미스터리", "미스터리"] or (
            category == "auto" and any(k in clean_topic for k in ["소름", "미스터리", "도어락", "새벽", "원룸", "공포", "실화", "자취방", "쪽지", "비밀번호", "귀신"])
        ):
            return {
                "title": f"😱 [소름 실화] {clean_topic[:24]} #Shorts #소름실화",
                "tags": ["소름실화", "미스터리", "자취방썰", "충격반전", "Shorts", "Reels"],
                "pinned_comment": "📌 혼자 자취하시는 분들은 꼭 이중 잠금장치 하세요! 여러분이 겪은 소름돋는 경험담도 댓글로 알려주세요.",
                "broll_pref": "norm_broll_city.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[구독] 더 소름돋는 실화는 채널 구독!",
                "scenes": [
                    {
                        "badge": "[소름] 미스터리 실화",
                        "badge_color": (139, 92, 246),
                        "hero_line1": "새벽 3시마다 울리는",
                        "hero_line2": "우리 집 도어락 소리",
                        "accent": "우리 집 도어락 소리",
                        "speech": "자취방으로 이사 온 첫날부터, 매일 새벽 3시만 되면 도어락 번호 누르는 삐빅 소리가 들렸습니다."
                    },
                    {
                        "badge": "[추적] 새벽의 감시",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "문 틈새 공기계로",
                        "hero_line2": "현관문 밤샘 촬영",
                        "accent": "현관문 밤샘 촬영",
                        "speech": "너무 공포스러워서 다음 날 현관문 틈 사이에 공기계를 켜두고 촬영을 시작했는데, 아침에 영상을 돌려보고 얼어붙었습니다."
                    },
                    {
                        "badge": "[충격] 의문의 정체",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "촬영된 영상 속",
                        "hero_line2": "충격적인 남성의 정체",
                        "accent": "충격적인 남성의 정체",
                        "speech": "알고 보니 윗집 사람이 매일 술에 취해 층수를 헷갈려 저희 집 도어락에 자기 집 비밀번호를 눌렀던 거였습니다."
                    },
                    {
                        "badge": "[주의] 문단속 필수",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "이중 잠금장치 설치!",
                        "hero_line2": "자취생 문단속 주의",
                        "accent": "자취생 문단속 주의",
                        "speech": "바로 건물 관리실에 항의해서 사과받고 이중 잠금장치 달았습니다. 혼자 자취하시는 분들은 꼭 문단속 조심하세요!"
                    }
                ]
            }

        # ==========================================
        # [썰 쇼츠 4] 자취방 배달 레전드 황당 썰
        # ==========================================
        if category in ["delivery", "배달황당", "배달"] or (
            category == "auto" and any(k in clean_topic for k in ["배달", "치킨", "라이더", "황당", "음식", "배민", "식당", "포장", "쿠폰", "오배송", "피자"])
        ):
            return {
                "title": f"🤣 [황당 실화] {clean_topic[:24]} #Shorts #황당썰",
                "tags": ["배달썰", "황당실화", "자취방썰", "웃긴썰", "Shorts", "Reels"],
                "pinned_comment": "📌 여러분이라면 배달원이 닭다리 하나 먹고 쪽지 남겼을 때 용서 가능하신가요? 댓글 투표! 🍗",
                "broll_pref": "norm_broll_coffee.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[댓글] 여러분이라면 용서 가능? 댓글 투표!",
                "scenes": [
                    {
                        "badge": "[HOT] 황당 배달 실화",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "야식으로 치킨 시켰더니",
                        "hero_line2": "봉투 속 의문의 쪽지?",
                        "accent": "봉투 속 의문의 쪽지?",
                        "speech": "야식으로 치킨 한 마리를 시켰는데, 배달 봉투 안쪽에 웬 작은 포스트잇 쪽지가 하나 붙어있는 겁니다."
                    },
                    {
                        "badge": "[고백] 황당한 자백",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "냄새가 너무 좋아서",
                        "hero_line2": "닭다리 하나 먹었습니다",
                        "accent": "닭다리 하나 먹었습니다",
                        "speech": "쪽지를 펴보니까, 냄새가 너무 맛있어 보여서 참지 못하고 닭다리 하나를 먹었습니다. 정말 죄송합니다라고 적혀있더라고요."
                    },
                    {
                        "badge": "[보상] 전액 환불 처리",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "치킨값 전액 환불에",
                        "hero_line2": "3만원 쿠폰까지 지급!",
                        "accent": "3만원 쿠폰까지 지급!",
                        "speech": "어이가 없어서 고객센터에 사진을 보냈더니, 치킨값 전액 환불에 3만 원 상당의 상품권까지 즉시 지급해 줬습니다."
                    },
                    {
                        "badge": "[투표] 황당한 결말",
                        "badge_color": (244, 63, 94),
                        "hero_line1": "솔직한 쪽지 고백",
                        "hero_line2": "여러분은 용서 가능?",
                        "accent": "여러분은 용서 가능?",
                        "speech": "그래도 쪽지까지 솔직하게 남겨두고 간 게 너무 황당하고 웃겼습니다. 여러분이라면 닭다리 하나 용서 가능하신가요?"
                    }
                ]
            }

        # ==========================================
        # [정보성 1] 정부 지원금 / 바우처 / 청년 테마
        # ==========================================
        if any(k in clean_topic for k in ["바우처", "첫만남", "지원금", "청년", "환수", "소멸", "국민행복카드", "정부"]):
            return {
                "title": f"🚨 {clean_topic[:26]} 기한 지나면 전액 소멸?! #Shorts",
                "tags": ["정부지원금", "바우처혜택", "생활꿀팁", "Shorts", "Reels"],
                "pinned_comment": f"📌 [1초 잔액 조회 & 제휴처 전체 리스트] 지금 바로 프로필 고정 댓글 블로그에서 확인하세요! 👉 {clean_url}",
                "broll_pref": "norm_broll_city.mp4",
                "cta_text": "[TIP] 무료 꿀팁 가이드북은 프로필 링크 클릭!",
                "scenes": [
                    {
                        "badge": "[경고] 긴급 기한 엄수",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "기한 지나면",
                        "hero_line2": "전액 국고 환수?!",
                        "accent": "전액 국고 환수?!",
                        "speech": f"혹시 {clean_topic[:18]} 지원금 받아두고 그냥 까먹고 계신가요? 정해진 기한 넘기면 남은 잔액이 전부 자동 소멸됩니다!"
                    },
                    {
                        "badge": "[꿀팁] 현금처럼 결제",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "마트·약국·배민까지",
                        "hero_line2": "전부 결제 가능합니다!",
                        "accent": "전부 결제 가능합니다!",
                        "speech": "병원과 약국은 물론이고 이마트, 백화점, 심지어 쿠팡이나 배달의민족 앱에서도 간편결제 등록해서 현금처럼 쓸 수 있습니다."
                    },
                    {
                        "badge": "[확인] 프로필 링크 확인",
                        "badge_color": (168, 85, 247),
                        "hero_line1": "내 잔액 1초 조회",
                        "hero_line2": "지금 바로 확인하세요!",
                        "accent": "지금 바로 확인하세요!",
                        "speech": "내 카드에 남은 잔액 실시간 조회법과 온라인 결제처 총정리는, 아래 고정 댓글 블로그 링크에서 지금 바로 확인해 보세요!"
                    }
                ]
            }

        # ==========================================
        # [정보성 2] 블로그 / 부업 / 수익화 테마
        # ==========================================
        if any(k in clean_topic for k in ["수익", "부업", "블로그", "네이버", "구독", "애드센스", "돈", "머니", "월", "쿠팡"]):
            return {
                "title": f"🔥 {clean_topic[:26]} 솔직히 나만 몰랐던 수익화 비법 #Shorts",
                "tags": ["부업추천", "수익화", "직장인부업", "Shorts", "Reels"],
                "pinned_comment": f"📌 [100% 무료 가이드] 상세한 0원 시작 세팅법과 꿀팁은 고정 댓글 블로그에서 확인하세요! 👉 {clean_url}",
                "broll_pref": "norm_broll_typing.mp4",
                "cta_text": "[TIP] 무료 꿀팁 가이드북은 프로필 링크 클릭!",
                "scenes": [
                    {
                        "badge": "[HOT] 나만 몰랐던 비법",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "아직도 하루 몇 백원에",
                        "hero_line2": "현타 오고 계신가요?",
                        "accent": "현타 오고 계신가요?",
                        "speech": f"솔직히 블로그 하루 종일 써서 몇 백원 벌면 현타 오죠? 남들은 지금 {clean_topic[:18]} 이거 하나로 월 150씩 조용히 챙겨가고 있습니다."
                    },
                    {
                        "badge": "[꿀팁] 0원 시작 가이드",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "딱 2가지만",
                        "hero_line2": "세팅해 두면 끝납니다!",
                        "accent": "딱 2가지만",
                        "speech": "딱 2가지만 기억하세요. 남들 다 쓰는 레드오션 키워드는 버리고, 3분 만에 0원으로 채널을 열어두면 자는 동안에도 수익이 들어옵니다."
                    },
                    {
                        "badge": "[확인] 프로필 링크 확인",
                        "badge_color": (168, 85, 247),
                        "hero_line1": "100% 무료 가이드",
                        "hero_line2": "지금 바로 확인하세요!",
                        "accent": "100% 무료 가이드",
                        "speech": "더 늦기 전에 막차 타세요! 상세한 첫 달 수익화 세팅 가이드는 프로필 고정 댓글 링크에 모두 남겨뒀으니 지금 바로 확인하세요!"
                    }
                ]
            }

        # ==========================================
        # [기본 테마] 일반 생활 꿀팁 / AI 테크
        # ==========================================
        return {
            "title": f"⚡ {clean_topic[:26]} 20초 만에 끝내는 시크릿 꿀팁 #Shorts",
            "tags": ["생활꿀팁", "인생꿀팁", "핵심요약", "Shorts", "Reels"],
            "pinned_comment": f"📌 [상세 가이드 & 바로가기] 고정 댓글 링크에서 1초 만에 확인하세요! 👉 {clean_url}",
            "broll_pref": "norm_broll_typing.mp4",
            "cta_text": "[TIP] 무료 꿀팁 가이드북은 프로필 링크 클릭!",
            "scenes": [
                {
                    "badge": "[속보] 3초 시선 집중",
                    "badge_color": (239, 68, 68),
                    "hero_line1": "이거 아직도 모르면",
                    "hero_line2": "매달 30만원씩 손해!",
                    "accent": "매달 30만원씩 손해!",
                    "speech": f"아직도 {clean_topic[:20]}에 대해 제대로 모르고 계셨나요? 이거 하나만 알아도 남들보다 3배 이상 앞서갈 수 있습니다."
                },
                {
                    "badge": "[TIP] 1%만 아는 비법",
                    "badge_color": (245, 158, 11),
                    "hero_line1": "복잡한 절차 없이",
                    "hero_line2": "딱 3분 만에 해결!",
                    "accent": "딱 3분 만에 해결!",
                    "speech": "핵심은 간단합니다. 뻔한 방식으로 시간 낭비하지 마시고, 전문가들이 검증한 이 지름길 공식 하나만 그대로 따라 해 보세요."
                },
                {
                    "badge": "[확인] 프로필 링크 확인",
                    "badge_color": (168, 85, 247),
                    "hero_line1": "상세 가이드 배포 중",
                    "hero_line2": "고정 댓글 링크 클릭!",
                    "accent": "고정 댓글 링크 클릭!",
                    "speech": "초보자도 1분 만에 따라 할 수 있는 상세 실행 매뉴얼은, 아래 고정 댓글 링크에 전부 정리해 뒀으니 지금 확인하세요!"
                }
            ]
        }


class ShortsVideoRenderer:
    """1080x1920 세로형 9:16 바이럴 비디오 렌더러 (실사 B-Roll 비디오 루프 + 키네틱 팝업 자막 + Lo-Fi BGM)"""

    WIDTH = 1080
    HEIGHT = 1920
    FPS = 24

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self._init_fonts()

    def _init_fonts(self):
        font_candidates = [
            "C:\\Windows\\Fonts\\malgunbd.ttf",
            "C:\\Windows\\Fonts\\malgun.ttf",
            "C:\\Windows\\Fonts\\gulim.ttc",
            "C:\\Windows\\Fonts\\arial.ttf"
        ]
        font_file = None
        for fc in font_candidates:
            if os.path.exists(fc):
                font_file = fc
                break

        if font_file:
            self.font_badge = ImageFont.truetype(font_file, 34)
            self.font_hero = ImageFont.truetype(font_file, 64)
            self.font_accent = ImageFont.truetype(font_file, 72)
            self.font_sub = ImageFont.truetype(font_file, 58)
            self.font_cta = ImageFont.truetype(font_file, 32)
        else:
            self.font_badge = ImageFont.load_default()
            self.font_hero = ImageFont.load_default()
            self.font_accent = ImageFont.load_default()
            self.font_sub = ImageFont.load_default()
            self.font_cta = ImageFont.load_default()

    @staticmethod
    def _clean_text_for_font(text: str) -> str:
        """한글 폰트(malgunbd.ttf)에서 지원하지 않는 이모지로 인한 두부(□) 현상 방지"""
        if not text:
            return ""
        replacements = {
            "🔥": "[HOT]",
            "📌": "▶",
            "⚡": "[속보]",
            "💡": "[TIP]",
            "🚀": "[GO!]",
            "⚠️": "[필독]",
            "💰": "[수익]",
            "👉": "▶",
            "✅": "✓",
            "🕒": "[NOW]",
            "🎯": "[핵심]",
            "👑": "[TOP]",
            "💔": "[실화]",
            "😱": "[소름]",
            "🤣": "[황당]",
            "💬": "[댓글]",
            "🍗": "[치킨]",
        }
        for emo, sym in replacements.items():
            text = text.replace(emo, sym)
        # 4바이트 유니코드 이모지 제거
        text = re.sub(r'[\U00010000-\U0010ffff]', '', text).strip()
        return text

    def _calculate_kinetic_chunks(self, speech: str, duration: float) -> List[Dict]:
        """나레이션 대본을 자연스러운 호흡 단위(12~18자, ~2.2초)로 분절하여 가독성과 몰입도 극대화"""
        words = speech.split()
        if not words:
            return [{"text": "", "start": 0.0, "end": duration}]

        chunks = []
        curr = []
        for w in words:
            curr.append(w)
            curr_str = " ".join(curr)
            # 자연스러운 의미 단위(13~18자 또는 쉼표/마침표 구두점 끝맺음)
            if (len(curr_str) >= 13 or (len(curr_str) >= 9 and curr_str[-1] in ',.!?~')) and len(curr) >= 2:
                chunks.append(curr_str)
                curr = []
        if curr:
            curr_str = " ".join(curr)
            # 자투리 단어가 너무 짧으면 이전 청크에 자연스럽게 병합
            if chunks and len(curr_str) < 8:
                chunks[-1] = chunks[-1] + " " + curr_str
            else:
                chunks.append(curr_str)

        num_chunks = max(1, len(chunks))
        chunk_dur = duration / num_chunks
        result = []
        for idx, text in enumerate(chunks):
            result.append({
                "text": text,
                "start": idx * chunk_dur,
                "end": (idx + 1) * chunk_dur
            })
        return result

    async def render_shorts(self, script_data: Dict, output_filepath: str) -> Dict:
        temp_dir = os.path.join(os.path.dirname(output_filepath), f"temp_{int(time.time()*1000)}")
        os.makedirs(temp_dir, exist_ok=True)

        # 1. Edge-TTS 음성 생성 (자연스러운 템포 & 진솔한 스토리텔러 음성)
        audio_files = []
        scene_durations = []
        voice_name = script_data.get("voice", "ko-KR-InJoonNeural")
        rate_val = script_data.get("rate", "+1%")
        for idx, scene in enumerate(script_data["scenes"]):
            scene_audio = os.path.join(temp_dir, f"scene_{idx}.mp3")
            communicate = edge_tts.Communicate(scene["speech"], voice_name, rate=rate_val)
            await communicate.save(scene_audio)
            audio_files.append(scene_audio)

            # ffmpeg 로 재생 시간 측정
            cmd = [self.ffmpeg_exe, "-i", scene_audio]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            dur_match = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", proc.stderr.decode('utf-8', errors='ignore'))
            if dur_match:
                h, m, s = dur_match.groups()
                duration = int(h) * 3600 + int(m) * 60 + float(s)
            else:
                duration = 7.0
            scene_durations.append(duration)

        # 음성 파일 하나로 병합
        concat_list = os.path.join(temp_dir, "concat.txt")
        with open(concat_list, "w", encoding="utf-8") as f:
            for af in audio_files:
                abs_p = os.path.abspath(af).replace("\\", "/")
                f.write(f"file '{abs_p}'\n")

        merged_voice = os.path.join(temp_dir, "merged_voice.mp3")
        subprocess.run([
            self.ffmpeg_exe, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list,
            "-c", "copy",
            merged_voice
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # 2. 감성 Lo-Fi BGM 배경음악 자동 믹싱 (음성 전달력 최적화: BGM 13% 음량)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        lofi_bgm_path = os.path.join(base_dir, "assets", "audio", "lofi_beat.mp3")
        final_audio_path = merged_voice

        if os.path.exists(lofi_bgm_path):
            mixed_audio = os.path.join(temp_dir, "final_mixed.mp3")
            mix_cmd = [
                self.ffmpeg_exe, "-y",
                "-i", merged_voice,
                "-i", lofi_bgm_path,
                "-filter_complex", "[1:a]volume=0.13[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
                "-map", "[aout]",
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                mixed_audio
            ]
            mix_proc = subprocess.run(mix_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if mix_proc.returncode == 0 and os.path.exists(mixed_audio):
                final_audio_path = mixed_audio

        total_duration = sum(scene_durations)
        total_frames = int(total_duration * self.FPS)

        # 3. 실사 B-roll 세로 영상 탐색
        broll_dir = os.path.join(base_dir, "assets", "broll")
        broll_video = None
        if os.path.exists(broll_dir):
            candidates = [
                os.path.join(broll_dir, f) for f in os.listdir(broll_dir)
                if (f.startswith("norm_") or f.startswith("broll_")) and f.endswith(".mp4")
            ]
            if candidates:
                pref_name = script_data.get("broll_pref")
                pref_path = os.path.join(broll_dir, pref_name) if pref_name else None
                if pref_path and os.path.exists(pref_path):
                    broll_video = pref_path
                else:
                    norm_candidates = [c for c in candidates if "norm_" in os.path.basename(c)]
                    broll_video = norm_candidates[0] if norm_candidates else candidates[0]

        # 4. 각 씬별 키네틱 자막 청크 사전 계산
        scene_kinetic_chunks = []
        for s_idx, scene in enumerate(script_data["scenes"]):
            dur = scene_durations[s_idx]
            chunks = self._calculate_kinetic_chunks(scene.get("speech", ""), dur)
            scene_kinetic_chunks.append(chunks)

        # 5. FFmpeg 비디오 렌더링 파이프라인 구성
        if broll_video:
            ffmpeg_cmd = [
                self.ffmpeg_exe, "-y",
                "-stream_loop", "-1",
                "-i", broll_video,
                "-f", "rawvideo",
                "-vcodec", "rawvideo",
                "-s", f"{self.WIDTH}x{self.HEIGHT}",
                "-pix_fmt", "rgba",
                "-r", str(self.FPS),
                "-i", "-",
                "-i", final_audio_path,
                "-filter_complex", (
                    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                    "crop=1080:1920,setsar=1,"
                    "eq=brightness=-0.18:contrast=1.10:saturation=1.15[bg];"
                    "[bg][1:v]overlay=0:0[vout]"
                ),
                "-map", "[vout]",
                "-map", "2:a",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                output_filepath
            ]
        else:
            ffmpeg_cmd = [
                self.ffmpeg_exe, "-y",
                "-f", "rawvideo",
                "-vcodec", "rawvideo",
                "-s", f"{self.WIDTH}x{self.HEIGHT}",
                "-pix_fmt", "rgb24",
                "-r", str(self.FPS),
                "-i", "-",
                "-i", final_audio_path,
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                output_filepath
            ]

        proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        acc = 0
        cumulative_durations = []
        scene_start_times = []
        for d in scene_durations:
            scene_start_times.append(acc)
            acc += d
            cumulative_durations.append(acc)

        frame_duration = 1.0 / self.FPS
        for frame_idx in range(total_frames):
            current_time = frame_idx * frame_duration
            progress = min(1.0, current_time / total_duration)

            current_scene_idx = 0
            for idx, cum_d in enumerate(cumulative_durations):
                if current_time <= cum_d:
                    current_scene_idx = idx
                    break
            else:
                current_scene_idx = len(script_data["scenes"]) - 1

            scene = script_data["scenes"][current_scene_idx]
            scene_start = scene_start_times[current_scene_idx]
            scene_time = current_time - scene_start

            # 현재 씬에서 활성화된 키네틱 자막 청크 찾기
            chunks = scene_kinetic_chunks[current_scene_idx]
            active_chunk = chunks[0]
            for c in chunks:
                if c["start"] <= scene_time < c["end"]:
                    active_chunk = c
                    break
            else:
                active_chunk = chunks[-1]

            time_in_chunk = scene_time - active_chunk["start"]

            # 프레임 오버레이 렌더링
            img = self._render_frame(
                scene, progress, current_time, scene_time,
                active_chunk, time_in_chunk, has_broll=bool(broll_video),
                global_cta=script_data.get("cta_text"),
                scene_idx=current_scene_idx
            )
            proc.stdin.write(img.tobytes())


        proc.stdin.close()
        proc.wait()

        # 임시 파일 정리
        try:
            for f in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)
        except Exception:
            pass

        file_size_mb = os.path.getsize(output_filepath) / (1024 * 1024)
        print(f"✅ [실사 B-roll + 키네틱 쇼츠 파이프라인] 1080x1920 MP4 영상 렌더링 완성! ({file_size_mb:.2f} MB, {total_duration:.1f}초)")

        return {
            "success": True,
            "filepath": output_filepath,
            "filename": os.path.basename(output_filepath),
            "size_mb": round(file_size_mb, 2),
            "duration": round(total_duration, 1),
            "title": script_data["title"],
            "tags": script_data["tags"],
            "pinned_comment": script_data["pinned_comment"],
            "scenes": script_data.get("scenes", [])
        }

    def _render_frame(
        self, scene: Dict, progress: float, current_time: float, scene_time: float,
        active_chunk: Dict, time_in_chunk: float, has_broll: bool,
        global_cta: Optional[str] = None, scene_idx: int = 0
    ) -> Image.Image:
        """단일 시선 집중(Single Center Focus) 바이럴 숏폼 렌더러 (시선 분산 100% 방지)"""
        if has_broll:
            img = Image.new("RGBA", (self.WIDTH, self.HEIGHT), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # 상단 & 하단 시네마틱 딥 그라데이션 (자막 및 텍스트 시인성 극대화)
            for y in range(320):
                a = int(175 * (1 - y / 320))
                draw.line([(0, y), (self.WIDTH, y)], fill=(10, 10, 20, a))
            for y in range(1420, self.HEIGHT):
                a = int(215 * ((y - 1420) / 500))
                draw.line([(0, y), (self.WIDTH, y)], fill=(10, 10, 20, a))
        else:
            img = Image.new("RGB", (self.WIDTH, self.HEIGHT), color=(15, 17, 26))
            draw = ImageDraw.Draw(img)
            # 앰비언트 글로우 오브
            glow_x = int(540 + 180 * math.sin(current_time * 0.8))
            glow_y = int(700 + 120 * math.cos(current_time * 0.9))
            draw.ellipse([glow_x - 450, glow_y - 450, glow_x + 450, glow_y + 450], fill=(28, 25, 56))

        # 1. 상단 네온 프로그레스 바 (0~100%)
        prog_w = int(60 + (self.WIDTH - 120) * progress)
        draw.rounded_rectangle([60, 40, self.WIDTH - 60, 56], radius=8, fill=(255, 255, 255, 40) if has_broll else (50, 50, 70))
        draw.rounded_rectangle([60, 40, prog_w, 56], radius=8, fill=(244, 63, 94, 255) if has_broll else (244, 63, 94))

        # 2. 상단 카테고리 칩 (Pill Capsule)
        badge_color = scene.get("badge_color", (239, 68, 68))
        badge_text = self._clean_text_for_font(scene.get("badge", "[HOT] 실화 사이다 썰"))
        draw.rounded_rectangle([180, 170, 900, 255], radius=42, fill=(15, 23, 42, 220) if has_broll else (24, 24, 38), outline=badge_color, width=3)
        draw.text((self.WIDTH // 2, 212), badge_text, fill=(255, 255, 255), font=self.font_badge, anchor="mm")

        # 3. 중앙 상단 시선 강탈 헤드라인 (첫 3.8초 훅 구간에만 노출하여 초반 이탈을 완벽 방지하고 이후 시선 집중)
        is_hook_stage = (current_time <= 3.8)
        if is_hook_stage:
            hook_y1 = 460
            hook_y2 = 560
            line1 = self._clean_text_for_font(scene.get("hero_line1", ""))
            line2 = self._clean_text_for_font(scene.get("hero_line2", ""))
            accent = self._clean_text_for_font(scene.get("accent", ""))

            # 텍스트 깊이감 그림자 효과
            for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 5)]:
                draw.text((self.WIDTH // 2 + ox, hook_y1 + oy), line1, fill=(0, 0, 0, 255), font=self.font_hero, anchor="mm")
                draw.text((self.WIDTH // 2 + ox, hook_y2 + oy), line2, fill=(0, 0, 0, 255), font=self.font_accent if line2 == accent else self.font_hero, anchor="mm")

            draw.text((self.WIDTH // 2, hook_y1), line1, fill=(255, 255, 255), font=self.font_hero, anchor="mm")
            accent_color = (250, 204, 21) if line2 == accent else (255, 255, 255)
            draw.text((self.WIDTH // 2, hook_y2), line2, fill=accent_color, font=self.font_accent if line2 == accent else self.font_hero, anchor="mm")

        # 4. 단일 시선 집중(Single Center Focus) 2줄 자동 래핑 자막 (화면 정중앙 배치)
        sub_text = self._clean_text_for_font(active_chunk.get("text", ""))
        if sub_text:
            # 자연스러운 2줄 자동 래핑 (14자 이상이고 양쪽 줄 길이가 균형 잡힐 때만 2줄 정렬)
            words = sub_text.split()
            display_text = sub_text
            if len(words) >= 3 and len(sub_text) >= 14:
                best_mid = -1
                best_diff = 999
                for i in range(1, len(words)):
                    l1 = " ".join(words[:i])
                    l2 = " ".join(words[i:])
                    if len(l1) <= 2 or len(l2) <= 2:
                        continue
                    diff = abs(len(l1) - len(l2))
                    if diff < best_diff:
                        best_diff = diff
                        best_mid = i
                if best_mid != -1:
                    display_text = " ".join(words[:best_mid]) + "\n" + " ".join(words[best_mid:])

            # 도입부 훅(첫 3.8초) 구간은 상단 헤드라인이 있으므로 하단(y=1260), 이후는 시선 고정 정중앙(y=980)
            sub_y = 1260 if is_hook_stage else 980
            is_pop = time_in_chunk < 0.22

            bbox = draw.multiline_textbbox((self.WIDTH // 2, sub_y), display_text, font=self.font_sub, anchor="mm", align="center", spacing=14)
            pad_x = 48 + (10 if is_pop else 0)
            pad_y = 24 + (4 if is_pop else 0)

            pill_outline = (255, 255, 255, 255) if is_pop else (250, 204, 21, 230)
            pill_width = 5 if is_pop else 3

            # 프리미엄 다크 글래스 필 캡슐
            draw.rounded_rectangle(
                [bbox[0] - pad_x, bbox[1] - pad_y, bbox[2] + pad_x, bbox[3] + pad_y],
                radius=32,
                fill=(0, 0, 0, 220) if has_broll else (18, 22, 36),
                outline=pill_outline,
                width=pill_width
            )

            # 자막 외곽선 그림자
            for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4)]:
                draw.multiline_text((self.WIDTH // 2 + ox, sub_y + oy), display_text, fill=(0, 0, 0, 255), font=self.font_sub, anchor="mm", align="center", spacing=14)

            # 텍스트 컬러 (팝업 바운스 시 네온 골드, 평상시 선명한 화이트)
            text_color = (255, 240, 80) if is_pop else (255, 255, 255)
            draw.multiline_text((self.WIDTH // 2, sub_y), display_text, fill=text_color, font=self.font_sub, anchor="mm", align="center", spacing=14)

        # 5. 최하단 참여 유도 / 댓글 투표 배너 (Floating Pill)
        cta = scene.get("cta_text") or global_cta or "[댓글] 여러분의 생각은? 댓글로 공유해주세요!"
        cta_text = self._clean_text_for_font(cta)
        draw.rounded_rectangle([140, 1720, 940, 1820], radius=30, fill=(225, 29, 72, 230), outline=(255, 255, 255, 180), width=2)
        draw.text((self.WIDTH // 2, 1770), cta_text, fill=(255, 255, 255), font=self.font_cta, anchor="mm")

        return img


def generate_shorts_pipeline(topic: str, blog_url: str = "", category: str = "auto") -> Dict:
    """단일 진입점: 주제와 카테고리를 받아 20~25초 바이럴 릴스/쇼츠 MP4 영상과 메타데이터를 일괄 생성"""
    clean_topic = topic.strip() or "내 도시락 맨날 훔쳐먹던 꼰대 상사 참교육한 썰"
    output_dir = os.path.join(os.getcwd(), "output", "shorts")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = int(time.time())
    safe_topic = re.sub(r'[\s\\/:*?"<>|]+', '_', clean_topic)[:20]
    output_filename = f"shorts_{safe_topic}_{timestamp}.mp4"
    output_filepath = os.path.join(output_dir, output_filename)

    # 1. 바이럴 스크립트 작성 (썰 카테고리 지원)
    script_gen = ShortsScriptGenerator()
    script_data = script_gen.generate_script(clean_topic, blog_url, category=category)

    # 2. 비디오 렌더링
    renderer = ShortsVideoRenderer()
    result = asyncio.run(renderer.render_shorts(script_data, output_filepath))

    # 3. 메타데이터 JSON 저장
    meta_path = os.path.join(output_dir, f"shorts_{safe_topic}_{timestamp}_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    result["meta_path"] = meta_path
    result["web_url"] = f"/output/shorts/{output_filename}"

    return result



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Tistory AI 감성 릴스/쇼츠 영상 자동 제작 파이프라인")
    parser.add_argument("--topic", type=str, default="네이버 프리미엄콘텐츠 유료 구독 채널 개설 및 첫 달 수익화 팁", help="영상 제작 주제")
    parser.add_argument("--url", type=str, default="https://tistory-ai-corp.tistory.com", help="유입용 블로그 URL")
    args = parser.parse_args()

    res = generate_shorts_pipeline(args.topic, args.url)
    print(f"🎉 릴스 제작 완료: {res['filepath']} ({res['duration']}초, {res['size_mb']}MB)")
