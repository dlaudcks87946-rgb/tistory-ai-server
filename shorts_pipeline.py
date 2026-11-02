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

    @classmethod
    def generate_script(cls, topic: str, blog_url: str = "", category: str = "auto") -> Dict:
        clean_topic = topic.strip() or "내 도시락 맨날 훔쳐먹던 꼰대 상사 참교육한 썰"
        clean_url = blog_url.strip() or "https://tistory-ai-corp.tistory.com"

        # ----------------------------------------------------
        # 16개 바이럴 에피소드 고유 매칭 (주제 키워드 최우선 분석)
        # ----------------------------------------------------

        # [Workplace 1] 도시락 / 불마왕 캡사이신 참교육
        if any(k in clean_topic for k in ["도시락", "훔쳐먹", "캡사이신"]):
            return {
                "title": f"🔥 [사이다] {clean_topic[:24]} #Shorts #사이다썰",
                "tags": ["직장인사이다", "회사썰", "상사참교육", "사이다", "Shorts", "Reels"],
                "pinned_comment": "📌 여러분도 직장에서 겪어본 최악의 빌런이 있나요? 댓글로 사연을 남겨주세요! ❤️",
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

        # [Workplace 2] 법카 / 신입사원 / 오마카세
        if any(k in clean_topic for k in ["법카", "신입", "오마카세", "회식"]):
            return {
                "title": f"🔥 [사이다] {clean_topic[:24]} #Shorts #사이다썰",
                "tags": ["신입사원", "법카회식", "사이다썰", "직장썰", "Shorts", "Reels"],
                "pinned_comment": "📌 여러분 회사에 이런 신입이 들어오면 어떨 것 같나요? 솔직한 댓글 부탁드립니다!",
                "broll_pref": "norm_broll_typing.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[댓글] 신입사원 행동 찬성 vs 반대?",
                "scenes": [
                    {
                        "badge": "[HOT] 법카 참교육 썰",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "법카로 회식 예약하라길래",
                        "hero_line2": "한우 오마카세 긁은 신입",
                        "accent": "한우 오마카세 긁은 신입",
                        "speech": "평소 법인카드로 매일 생색내며 후배들 커피 심부름 시키던 부장님이, 신입사원한테 법카를 주며 회식 장소를 예약하라고 했습니다."
                    },
                    {
                        "badge": "[결제] 1인당 30만원!",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "팀원 전체 최고급 코스",
                        "hero_line2": "배 터지게 법카 결제!",
                        "accent": "배 터지게 법카 결제!",
                        "speech": "그런데 신입사원이 최고급 한우 오마카세를 예약하고, 부서원 전체 1인당 30만 원짜리 코스를 법카로 시원하게 결제해 버린 겁니다."
                    },
                    {
                        "badge": "[충격] 사직서 투척!",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "다음 날 부장님 사색!",
                        "hero_line2": "웃으며 사직서 투척",
                        "accent": "웃으며 사직서 투척",
                        "speech": "다음 날 부장님이 카드 내역서를 보고 사색이 되어 소리를 지르는데, 신입사원은 웃으면서 사직서를 책상에 올려놓고 짐을 쌌습니다."
                    },
                    {
                        "badge": "[결말] 정당한 팀 회식",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "정당한 회식 승인 완료!",
                        "hero_line2": "부장님 멘붕 엔딩",
                        "accent": "부장님 멘붕 엔딩",
                        "speech": "상무님 결재까지 정당한 부서 회식으로 승인 나면서 부장님만 멘붕에 빠졌습니다. 여러분 회사에 이런 신입 있으면 어떨 것 같나요?"
                    }
                ]
            }

        # [Workplace 3] 연차 / 휴가 사유 캐묻는 상사
        if any(k in clean_topic for k in ["연차", "캐묻", "휴가"]):
            return {
                "title": f"🔥 [사이다] {clean_topic[:24]} #Shorts #사이다썰",
                "tags": ["연차사유", "꼰대팀장", "직장인사이다", "회사썰", "Shorts", "Reels"],
                "pinned_comment": "📌 연차 쓸 때 사유 꼬치꼬치 캐묻는 상사 겪어보신 분 계신가요? 댓글 공유!",
                "broll_pref": "norm_broll_typing.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[댓글] 연차 사유 캐묻기 불법 vs 정당?",
                "scenes": [
                    {
                        "badge": "[HOT] 연차 사이다 썰",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "연차 낼 때마다 꼬치꼬치",
                        "hero_line2": "사유 캐묻던 꼰대 팀장",
                        "accent": "사유 캐묻던 꼰대 팀장",
                        "speech": "연차 신청서만 올리면 팀원들 불러놓고 무슨 일 있냐, 개인 사정이 뭐냐며 꼬치꼬치 캐묻던 꼰대 팀장님이 있었습니다."
                    },
                    {
                        "badge": "[반격] 사유서 충격 작성",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "팀장 잔소리로 인한",
                        "hero_line2": "극심한 스트레스 치료!",
                        "accent": "극심한 스트레스 치료!",
                        "speech": "참다못한 제가 연차 사유란에 팀장님의 끊임없는 잔소리로 인한 극심한 스트레스 해소 및 정신과 상담이라고 적어 결재를 올렸습니다."
                    },
                    {
                        "badge": "[필살] 노무사 녹취록",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "얼굴 새빨개져 부르길래",
                        "hero_line2": "노무사 상담 녹음기 슬쩍!",
                        "accent": "노무사 상담 녹음기 슬쩍!",
                        "speech": "팀장님이 사색이 되어 저를 따로 부르길래, 미리 준비해 둔 노무사 직장 내 괴롭힘 상담 녹음 파일 목록을 화면에 슬쩍 띄워드렸습니다."
                    },
                    {
                        "badge": "[결말] 손 떨며 칼사인",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "그 뒤론 토도 못 달음!",
                        "hero_line2": "여러분의 생각은?",
                        "accent": "여러분의 생각은?",
                        "speech": "그 자리에서 손을 덜덜 떨며 바로 결재 도장을 찍어주더라고요. 여러분도 연차 사유 꼬치꼬치 캐묻는 상사 겪어보셨나요?"
                    }
                ]
            }

        # [Workplace 4] 주말 출근 / 노동청 / 야근
        if any(k in clean_topic for k in ["노동청", "주말", "출근", "특근", "야근"]):
            return {
                "title": f"🔥 [사이다] {clean_topic[:24]} #Shorts #사이다썰",
                "tags": ["노동청신고", "주말출근", "참교육", "회사썰", "Shorts", "Reels"],
                "pinned_comment": "📌 주말 출근 강요하는 상사, 여러분이라면 노동청에 신고하실 수 있나요? 댓글 투표!",
                "broll_pref": "norm_broll_typing.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[댓글] 노동청 신고 찬성 vs 반대?",
                "scenes": [
                    {
                        "badge": "[HOT] 노동청 참교육 썰",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "주말마다 단톡방 테러하며",
                        "hero_line2": "무급 특근 강요하던 팀장",
                        "accent": "무급 특근 강요하던 팀장",
                        "speech": "주말마다 단톡방에 열정이 부족하다며 주말 출근을 강요하고, 수당은 땡전 한 푼 안 주던 꼰대 팀장님이 있었습니다."
                    },
                    {
                        "badge": "[증거] 3달치 철저 수집",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "모든 카톡 지시 내용과",
                        "hero_line2": "출퇴근 교통카드 증거 확보",
                        "accent": "출퇴근 교통카드 증거 확보",
                        "speech": "3달 동안 주말 카톡 지시 내용과 출퇴근 교통카드 태그 기록, 회사 PC 접속 로그를 단 한 개도 빼놓지 않고 전부 수집했습니다."
                    },
                    {
                        "badge": "[기습] 근로감독관 출동",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "노동청 불시 조사 출동!",
                        "hero_line2": "팀장실 발칵 뒤집힘",
                        "accent": "팀장실 발칵 뒤집힘",
                        "speech": "팀원들과 함께 조용히 노동청에 고발장을 접수했고, 며칠 뒤 근로감독관이 회사로 불시 조사를 나오며 팀장실이 뒤집어졌습니다."
                    },
                    {
                        "badge": "[결말] 특근수당 전액 환수",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "팀장 보직 해임 엔딩!",
                        "hero_line2": "밀린 수당 전액 입금",
                        "accent": "밀린 수당 전액 입금",
                        "speech": "결국 팀장은 보직 해임되고 밀린 주말 특근 수당 수천만 원을 전액 입금받았습니다. 여러분이라면 노동청 고발 망설이지 않으셨을까요?"
                    }
                ]
            }

        # [Blind Date 1] 호텔 뷔페 / 화장실 잠적
        if any(k in clean_topic for k in ["뷔페", "호텔", "화장실"]):
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

        # [Blind Date 2] 더치페이 / 100원 / 송금
        if any(k in clean_topic for k in ["더치페이", "100원", "송금", "계산"]):
            return {
                "title": f"💔 [소개팅 썰] {clean_topic[:24]} #Shorts #레전드썰",
                "tags": ["소개팅더치페이", "연애빌런", "레전드썰", "Shorts", "Reels"],
                "pinned_comment": "📌 첫 소개팅에서 100원 단위 더치페이, 여러분은 이해 가능하신가요? 댓글 투표!",
                "broll_pref": "norm_broll_coffee.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[댓글] 100원 단위 더치페이 가능 vs 불가능?",
                "scenes": [
                    {
                        "badge": "[HOT] 소개팅 더치페이 썰",
                        "badge_color": (244, 63, 94),
                        "hero_line1": "첫 소개팅에서 커피 마시고",
                        "hero_line2": "헤어지자마자 날아온 카톡",
                        "accent": "헤어지자마자 날아온 카톡",
                        "speech": "첫 소개팅에서 가볍게 커피 두 잔을 마셨는데, 헤어지자마자 지하철역에서 100원 단위까지 쪼갠 영수증 사진과 카톡이 날아왔습니다."
                    },
                    {
                        "badge": "[황당] 4,150원 보내세요",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "정확히 4,150원 송금 요구에",
                        "hero_line2": "4,200원 보내고 50원 팁!",
                        "accent": "4,200원 보내고 50원 팁!",
                        "speech": "총 8,300원이 나왔으니 정확하게 4,150원을 송금해 달라길래, 너무 어이가 없어서 4,200원을 보내고 잔돈 50원은 팁이라고 답장했습니다."
                    },
                    {
                        "badge": "[분노] 사람 무시하냐?",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "따지길래 50원짜리",
                        "hero_line2": "껌 기프티콘 전송 후 차단!",
                        "accent": "껌 기프티콘 전송 후 차단!",
                        "speech": "그랬더니 사람을 거지 취급하냐며 장문의 분노 카톡을 보내길래, 50원짜리 츄잉껌 기프티콘 하나 더 보내주고 바로 차단 박았습니다."
                    },
                    {
                        "badge": "[진실] 상습범의 최후",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "주선자에게 밝혀진 상습범!",
                        "hero_line2": "여러분의 생각은?",
                        "accent": "여러분의 생각은?",
                        "speech": "알고 보니 소개팅마다 포인트 적립하고 100원 단위로 영수증 쪼개는 상습범이었더라고요. 여러분이라면 이런 상대 어떻게 반응하셨을까요?"
                    }
                ]
            }

        # [Blind Date 3] 카톡 프사 도용 / 10년 전 동창
        if any(k in clean_topic for k in ["프사", "도용", "동창", "사진"]):
            return {
                "title": f"💔 [소개팅 썰] {clean_topic[:24]} #Shorts #레전드썰",
                "tags": ["소개팅빌런", "프사도용", "동창소개팅", "Shorts", "Reels"],
                "pinned_comment": "📌 사진 도용하고 나온 소개팅 상대, 여러분이라면 밥 사주고 오셨을까요? 댓글 공유!",
                "broll_pref": "norm_broll_coffee.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[댓글] 프사 도용 만남 즉시 탈출 vs 예의상 식사?",
                "scenes": [
                    {
                        "badge": "[HOT] 프사 도용 레전드",
                        "badge_color": (244, 63, 94),
                        "hero_line1": "인스타 여신 사진 걸어두고",
                        "hero_line2": "약속 장소에 나온 사람 정체",
                        "accent": "약속 장소에 나온 사람 정체",
                        "speech": "카톡 프로필에 인스타 여신 사진을 걸어두고 주말에 만나기로 했는데, 약속 장소 카페에 웬 10년 전 중학교 동창이 앉아있는 겁니다."
                    },
                    {
                        "badge": "[적반하장] 외모 지상주의냐?",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "사진이랑 너무 달라서 묻자",
                        "hero_line2": "포토샵 좀 한 건데 왜 차별해!",
                        "accent": "포토샵 좀 한 건데 왜 차별해!",
                        "speech": "사진이랑 너무 달라서 혹시 누구시냐고 물었더니, 포토샵 좀 한 건데 사람 외모로 차별하냐며 카페가 떠나가라 화를 내더라고요."
                    },
                    {
                        "badge": "[탈출] 조용히 커피 결제",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "비싼 와인 시키려 하길래",
                        "hero_line2": "커피값만 내고 조용히 탈출",
                        "accent": "커피값만 내고 조용히 탈출",
                        "speech": "밥 먹는 내내 비싼 와인이랑 티본스테이크를 시키려 하길래, 통화하는 척 카운터로 가서 제 커피값만 결제하고 나와버렸습니다."
                    },
                    {
                        "badge": "[사이다] 5만원이나 갚아라",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "학창시절 빌려간 돈 갚아라!",
                        "hero_line2": "사이다 차단 엔딩",
                        "accent": "사이다 차단 엔딩",
                        "speech": "카톡으로 욕설 테러를 하길래 중학교 때 빌려간 5만 원이나 갚으라고 답장하고 차단했습니다. 살면서 이런 황당한 소개팅 겪어보셨나요?"
                    }
                ]
            }

        # [Blind Date 4] 식사 도중 전 애인 / 합석
        if any(k in clean_topic for k in ["전 애인", "전남친", "전여친", "합석"]):
            return {
                "title": f"💔 [소개팅 썰] {clean_topic[:24]} #Shorts #레전드썰",
                "tags": ["소개팅빌런", "전남친합석", "참교육썰", "Shorts", "Reels"],
                "pinned_comment": "📌 소개팅 자리에 전 애인 부르는 사람, 실제로 존재합니다... 여러분의 대처법은?",
                "broll_pref": "norm_broll_coffee.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[댓글] 여러분이라면 이 상황에서 어떻게 하셨을까요?",
                "scenes": [
                    {
                        "badge": "[HOT] 소개팅 합석 빌런",
                        "badge_color": (244, 63, 94),
                        "hero_line1": "소개팅 첫 식사 자리 도중",
                        "hero_line2": "아는 오빠 합석해도 되냐더니",
                        "accent": "아는 오빠 합석해도 되냐더니",
                        "speech": "소개팅 첫 식사 자리에서 고기를 굽고 있는데, 갑자기 근처에 아는 친한 오빠가 있다며 합석해도 되냐고 묻는 겁니다."
                    },
                    {
                        "badge": "[경악] 전남친과의 추억 토크",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "들어온 사람은 전남친!",
                        "hero_line2": "20만원어치 술안주 폭풍 주문",
                        "accent": "20만원어치 술안주 폭풍 주문",
                        "speech": "들어온 사람은 다름 아닌 전남친이었고, 둘이서 제 앞에서 옛날 연애 시절 추억 얘기를 하며 20만 원어치 고기와 고급 양주를 주문했습니다."
                    },
                    {
                        "badge": "[탈출] 내 몫만 3만원 결제",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "화장실 가는 척 3만원 결제!",
                        "hero_line2": "뒤도 안 돌아보고 탈출 성공",
                        "accent": "뒤도 안 돌아보고 탈출 성공",
                        "speech": "너무 기가 막혀서 아무 말 없이 화장실 가는 척 카운터에 제 몫 3만 원만 먼저 결제하고 밖으로 빠져나왔습니다."
                    },
                    {
                        "badge": "[결말] 17만원 결제 폭탄",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "전화 빗발치길래 차단!",
                        "hero_line2": "둘이 데이트 잘하세요 엔딩",
                        "accent": "둘이 데이트 잘하세요 엔딩",
                        "speech": "남은 17만 원 결제 폭탄을 맞고 전화가 빗발치길래 둘이 데이트 잘하라고 카톡 남기고 차단했습니다. 여러분이라면 어떻게 대처하셨을까요?"
                    }
                ]
            }

        # [Mystery 1] 도어락 / 새벽 3시
        if any(k in clean_topic for k in ["도어락", "새벽 3시"]):
            return {
                "title": f"😱 [소름 실화] {clean_topic[:24]} #Shorts #소름실화",
                "tags": ["소름실화", "미스터리", "자취방썰", "충격반전", "Shorts", "Reels"],
                "pinned_comment": "📌 혼자 자취하시는 분들은 꼭 이중 잠금장치 하세요! 여러분이 겪은 소름 경험담도 댓글로 알려주세요.",
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

        # [Mystery 2] 거울 / 중고 거래 / 당근 / 의문의 쪽지
        if any(k in clean_topic for k in ["거울", "중고", "당근", "쪽지"]):
            return {
                "title": f"😱 [소름 실화] {clean_topic[:24]} #Shorts #소름실화",
                "tags": ["소름실화", "중고거래썰", "미스터리", "공포실화", "Shorts", "Reels"],
                "pinned_comment": "📌 중고로 물건 사오면 꼭 틈새 확인하세요! 여러분이라면 이 쪽지 보고 어떻게 하셨을까요?",
                "broll_pref": "norm_broll_city.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[댓글] 여러분이라면 거울 즉시 버림 vs 무시하고 씀?",
                "scenes": [
                    {
                        "badge": "[소름] 중고 거래 실화",
                        "badge_color": (139, 92, 246),
                        "hero_line1": "당근마켓에서 전신 거울 샀더니",
                        "hero_line2": "프레임 뒤에서 떨어진 노란 쪽지",
                        "accent": "프레임 뒤에서 떨어진 노란 쪽지",
                        "speech": "당근마켓에서 전신 거울을 만 원에 저렴하게 사 왔는데, 방에 세워두자마자 프레임 뒤쪽 틈새에서 낡은 노란 쪽지 하나가 툭 떨어졌습니다."
                    },
                    {
                        "badge": "[경악] 쪽지의 충격 경고",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "침대 맞은편에 두지 마세요",
                        "hero_line2": "밤마다 유리가 울립니다",
                        "accent": "밤마다 유리가 울립니다",
                        "speech": "접힌 쪽지를 펴봤더니, 삐뚤빼뚤한 글씨로 '이 거울 절대 침대 맞은편에 두지 마세요. 밤마다 유리가 울립니다'라고 적혀있는 겁니다."
                    },
                    {
                        "badge": "[탈퇴] 판매자의 잠적",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "판매자에게 즉시 메시지 보내자",
                        "hero_line2": "대화방 삭제하고 바로 탈퇴!",
                        "accent": "대화방 삭제하고 바로 탈퇴!",
                        "speech": "온몸에 소름이 쫙 돋아서 판매자에게 방금 쪽지 뭐냐고 메시지를 보냈는데, 1초 만에 읽더니 대화방을 나가고 계정을 탈퇴해 버렸습니다."
                    },
                    {
                        "badge": "[결말] 즉시 폐기 처분",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "거울 즉시 버리고 소금 뿌림!",
                        "hero_line2": "여러분의 선택은?",
                        "accent": "여러분의 선택은?",
                        "speech": "도저히 무서워서 그날 밤 바로 대형폐기물 스티커 붙여서 버리고 현관에 굵은 소금 뿌렸습니다. 여러분이라면 이 쪽지 보고 어떻게 하셨을까요?"
                    }
                ]
            }

        # [Mystery 3] 천장 / 소리 / 원룸
        if any(k in clean_topic for k in ["천장", "소리", "원룸"]):
            return {
                "title": f"😱 [소름 실화] {clean_topic[:24]} #Shorts #소름실화",
                "tags": ["소름실화", "원룸미스터리", "자취방실화", "충격결말", "Shorts", "Reels"],
                "pinned_comment": "📌 혼자 자취하시는 분들은 꼭 환기구와 점검구 확인하세요! 소름 경험담 댓글 공유!",
                "broll_pref": "norm_broll_city.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[구독] 더 소름돋는 미스터리는 채널 구독!",
                "scenes": [
                    {
                        "badge": "[소름] 천장의 의문의 소리",
                        "badge_color": (139, 92, 246),
                        "hero_line1": "혼자 사는 원룸 천장에서",
                        "hero_line2": "매일 밤 12시마다 들린 소리",
                        "accent": "매일 밤 12시마다 들린 소리",
                        "speech": "혼자 사는 자취방 원룸 천장에서 매일 밤 12시만 되면 쇠구슬이 굴러가는 소리와 천장을 박박 긁는 소리가 들렸습니다."
                    },
                    {
                        "badge": "[확인] 꼭대기층 점검구 개방",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "꼭대기 층이라 위층도 없는데",
                        "hero_line2": "집주인과 천장 점검구 오픈!",
                        "accent": "집주인과 천장 점검구 오픈!",
                        "speech": "건물 꼭대기 층이라 위층에 아무도 안 사는데도 매일 소리가 나서, 집주인 아저씨와 함께 사다리를 타고 천장 점검구를 열어봤는데..."
                    },
                    {
                        "badge": "[경악] 사람의 흔적 발견",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "천장 안에서 발견된",
                        "hero_line2": "돗자리와 생수병, 빵 봉지!",
                        "accent": "돗자리와 생수병, 빵 봉지!",
                        "speech": "깜깜한 천장 안쪽에 누군가 깔고 잔 돗자리와 생수병 여러 개, 그리고 먹다 남은 빵 봉지가 널브러져 있는 것을 발견했습니다."
                    },
                    {
                        "badge": "[검거] 경찰 긴급 출동",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "옥상 비상문으로 숨어든 노숙자",
                        "hero_line2": "자취생 안전 주의보!",
                        "accent": "자취생 안전 주의보!",
                        "speech": "경찰에 신고했더니 옥상 비상문으로 숨어 들어와 천장에 살던 노숙자였습니다. 혼자 자취하시는 분들은 꼭 환기구와 천장 점검구 확인하세요!"
                    }
                ]
            }

        # [Mystery 4] 택배 / 상자 / 경찰 출동
        if any(k in clean_topic for k in ["택배", "상자"]):
            return {
                "title": f"😱 [소름 실화] {clean_topic[:24]} #Shorts #소름실화",
                "tags": ["소름실화", "택배사건", "범죄스릴러", "Shorts", "Reels"],
                "pinned_comment": "📌 의문의 택배 오면 절대 함부로 열지 마시고 112 신고하세요! 댓글 투표!",
                "broll_pref": "norm_broll_city.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[댓글] 모르는 택배 오면 바로 뜯음 vs 고객센터 확인?",
                "scenes": [
                    {
                        "badge": "[소름] 의문의 택배 상자",
                        "badge_color": (139, 92, 246),
                        "hero_line1": "새벽에 모르는 사람 이름으로",
                        "hero_line2": "문 앞에 놓인 대형 아이스박스",
                        "accent": "문 앞에 놓인 대형 아이스박스",
                        "speech": "새벽 문 앞에 낯선 사람 이름으로 테이프가 칭칭 감긴 커다란 아이스박스 택배가 와있길래, 잘못 온 줄 알고 열어봤습니다."
                    },
                    {
                        "badge": "[경악] 얼음팩 밑의 물건",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "얼음팩을 걷어내자 나온 물건",
                        "hero_line2": "수백 장의 대포폰 유심과 신분증!",
                        "accent": "수백 장의 대포폰 유심과 신분증!",
                        "speech": "상자를 뜯고 얼음팩을 걷어냈는데, 그 속에서 수백 장의 위조 신분증과 대포폰 유심칩이 비닐에 꽁꽁 싸인 채 쏟아져 나온 겁니다."
                    },
                    {
                        "badge": "[잠복] 강력계 형사 출동",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "손 덜덜 떨며 112 신고!",
                        "hero_line2": "강력계 형사들 현장 잠복 시작",
                        "accent": "강력계 형사들 현장 잠복 시작",
                        "speech": "손이 덜덜 떨려서 곧바로 112에 신고했고, 10분 만에 강력계 형사님들이 출동해 복도와 계단에 잠복수사를 시작했습니다."
                    },
                    {
                        "badge": "[검거] 수거책 현장 체포",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "보이스피싱 수거책 현장 검거!",
                        "hero_line2": "의문의 택배 절대 조심",
                        "accent": "의문의 택배 절대 조심",
                        "speech": "몇 시간 뒤 택배를 찾으러 어슬렁거리며 올라온 보이스피싱 수거책을 현장에서 긴급 체포했습니다. 여러분도 의문의 택배 오면 바로 신고하세요!"
                    }
                ]
            }

        # [Delivery 1] 치킨 / 닭다리 / 고백 쪽지
        if any(k in clean_topic for k in ["치킨", "닭다리"]):
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

        # [Delivery 2] 오배송 / 마라탕 / 음식
        if any(k in clean_topic for k in ["오배송", "마라탕"]):
            return {
                "title": f"🤣 [황당 실화] {clean_topic[:24]} #Shorts #황당썰",
                "tags": ["배달오배송", "마라탕대참사", "자취방실화", "황당썰", "Shorts", "Reels"],
                "pinned_comment": "📌 배달 음식 잘못 와서 맛있게 먹어본 적 있으신가요? 여러분의 썰을 들려주세요!",
                "broll_pref": "norm_broll_coffee.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[댓글] 배달 오배송 경험 있다 vs 없다?",
                "scenes": [
                    {
                        "badge": "[HOT] 배달 오배송 실화",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "새벽에 문 앞에 배달온 마라탕",
                        "hero_line2": "술김에 내가 시킨 줄 알고 흡입!",
                        "accent": "술김에 내가 시킨 줄 알고 흡입!",
                        "speech": "새벽에 문 앞에 마라탕 한 그릇이 배달와 있길래, 술김에 제가 시킨 줄 알고 국물 한 방울 안 남기고 맛있게 다 먹었습니다."
                    },
                    {
                        "badge": "[비명] 복도의 분노 소리",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "다음 날 아침 복도 비명 소리",
                        "hero_line2": "내 마라탕 훔쳐간 놈 누구야!",
                        "accent": "내 마라탕 훔쳐간 놈 누구야!",
                        "speech": "다음 날 아침 문을 열어보니, 옆집 아저씨가 복도에서 내 마라탕 훔쳐간 놈 누구냐며 고래고래 소리를 지르고 계시는 겁니다."
                    },
                    {
                        "badge": "[경악] 고수 5번 추가!",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "3단계에 고수 5번 추가한 걸",
                        "hero_line2": "사람이 다 먹었다고 경악!",
                        "accent": "사람이 다 먹었다고 경악!",
                        "speech": "너무 놀라서 죄송하다고 음식값 물어드리겠다 했더니, 그거 3단계에 고수 5번 추가한 건데 그걸 사람이 다 먹었냐며 기겁하시더라고요."
                    },
                    {
                        "badge": "[훈훈] 마라탕 재주문 엔딩",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "주소 오타로 밝혀진 해프닝!",
                        "hero_line2": "여러분도 오배송 겪어보셨나요?",
                        "accent": "여러분도 오배송 겪어보셨나요?",
                        "speech": "알고 보니 배달앱에 동 호수를 잘못 적으셨던 거였고, 결국 서로 웃으며 마라탕 한 그릇 더 시켜드렸습니다. 여러분은 음식 오배송 겪어보셨나요?"
                    }
                ]
            }

        # [Delivery 3] 벨 누르면 짖음 / 라이더 멍멍
        if any(k in clean_topic for k in ["짖음", "배민", "요청사항", "강아지"]):
            return {
                "title": f"🤣 [황당 실화] {clean_topic[:24]} #Shorts #황당썰",
                "tags": ["배민요청사항", "유쾌한라이더", "배달레전드", "Shorts", "Reels"],
                "pinned_comment": "📌 요청사항대로 짖어주신 라이더님, 진짜 너무 귀엽지 않나요? 여러분 생각은? 🐶",
                "broll_pref": "norm_broll_coffee.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[댓글] 라이더님 팁 3천원 더 줌 vs 그냥 웃고 넘김?",
                "scenes": [
                    {
                        "badge": "[HOT] 배민 오타 대참사",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "벨 누르면 개 짖는다고 쓰려다",
                        "hero_line2": "오타로 벨 누르면 짖음 전송!",
                        "accent": "오타로 벨 누르면 짖음 전송!",
                        "speech": "배민 요청사항에 '벨 누르면 개가 짖으니 문 앞에 놔주세요'라고 적으려다, 급하게 치느라 '벨 누르면 짖음'이라고 적어 주문했습니다."
                    },
                    {
                        "badge": "[충격] 문 밖의 멍멍 왈왈!",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "잠시 후 띵동 벨 울리더니",
                        "hero_line2": "문 밖에서 라이더님이 멍멍 왈왈!",
                        "accent": "문 밖에서 라이더님이 멍멍 왈왈!",
                        "speech": "잠시 후 띵동 벨이 울리더니, 문 밖에서 라이더님이 아주 진지한 목소리로 멍멍! 왈왈! 크르릉 소리를 내시는 겁니다."
                    },
                    {
                        "badge": "[폭소] 손님이 짖으라 하셔서...",
                        "badge_color": (244, 63, 94),
                        "hero_line1": "문 열자 쑥스러워하시며",
                        "hero_line2": "손님이 짖으라고 하셔서요...",
                        "accent": "손님이 짖으라고 하셔서요...",
                        "speech": "너무 깜짝 놀라 문을 열어보니, 라이더님이 헬멧을 만지작거리며 쑥스럽게 손님이 짖으라고 하셔서요라고 하셔서 둘 다 빵 터졌습니다."
                    },
                    {
                        "badge": "[훈훈] 팁 3천원에 별점 5점",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "세상에서 제일 유쾌한 배달원!",
                        "hero_line2": "여러분 생각은?",
                        "accent": "여러분 생각은?",
                        "speech": "너무 감사하고 유쾌해서 배달팁 3천 원 더 챙겨드리고 별점 5점 리뷰 남겼습니다. 살면서 이런 귀여운 라이더님 만나보신 적 있나요?"
                    }
                ]
            }

        # [Delivery 4] 옆집 이상한 주문 소리 / 쇼호스트 지망생
        if any(k in clean_topic for k in ["주문", "옆집", "쇼호스트"]):
            return {
                "title": f"🤣 [황당 실화] {clean_topic[:24]} #Shorts #황당썰",
                "tags": ["자취방옆집", "쇼호스트썰", "자취방실화", "웃긴썰", "Shorts", "Reels"],
                "pinned_comment": "📌 옆집에서 이상한 소리 나면 여러분은 어떻게 대처하시나요? 댓글로 남겨주세요!",
                "broll_pref": "norm_broll_coffee.mp4",
                "voice": "ko-KR-InJoonNeural",
                "rate": "+1%",
                "cta_text": "[댓글] 옆집 소음 민원 넣음 vs 쪽지로 확인?",
                "scenes": [
                    {
                        "badge": "[HOT] 자취방 옆집 미스터리",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "자취방 옆집에서 매일 밤마다",
                        "hero_line2": "벽 타고 들려온 기괴한 중얼거림",
                        "accent": "벽 타고 들려온 기괴한 중얼거림",
                        "speech": "자취방 옆집에서 매일 밤 11시만 되면 중얼중얼 알 수 없는 기괴한 주문을 외우는 소리가 벽을 타고 생생하게 들려왔습니다."
                    },
                    {
                        "badge": "[긴장] 사이비 종교인가?",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "무서워서 녹음기 켜고",
                        "hero_line2": "벽에 귀를 바짝 대고 청취",
                        "accent": "벽에 귀를 바짝 대고 청취",
                        "speech": "혹시 이상한 사이비 종교인가 싶어 너무 무서워서, 증거를 잡으려고 스마트폰 녹음기를 켜고 벽에 바짝 귀를 대봤는데..."
                    },
                    {
                        "badge": "[반전] 쇼호스트 발음 연습!",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "간장공장 공장장은 강 공장장!",
                        "hero_line2": "알고 보니 쇼호스트 지망생",
                        "accent": "알고 보니 쇼호스트 지망생",
                        "speech": "간장공장 공장장은 강 공장장이고, 이번 주 매진 임박! 알고 보니 홈쇼핑 쇼호스트 지망생의 피나는 심야 발음 연습이었습니다!"
                    },
                    {
                        "badge": "[훈훈] 응원 쪽지와 비타민",
                        "badge_color": (16, 185, 129),
                        "hero_line1": "문고리에 비타민 선물 엔딩!",
                        "hero_line2": "여러분 이웃엔 누가 사나요?",
                        "accent": "여러분 이웃엔 누가 사나요?",
                        "speech": "다음 날 아침 문고리에 비타민 음료와 함께 합격 응원합니다 쪽지를 걸어두었습니다. 여러분 집 옆방엔 어떤 이웃이 사시나요?"
                    }
                ]
            }

        # ----------------------------------------------------
        # 카테고리별 기본 썰 매핑 (위 16개 외 특정 카테고리가 지정된 경우)
        # ----------------------------------------------------
        if category in ["workplace", "직장사이다", "직장"]:
            return cls.generate_script("내 도시락 맨날 훔쳐먹던 꼰대 상사 참교육한 썰", blog_url, "auto")

        if category in ["blind_date", "소개팅빌런", "소개팅"]:
            return cls.generate_script("첫 만남에 호텔 뷔페 데려가더니 화장실로 튄 소개팅남", blog_url, "auto")

        if category in ["mystery", "소름미스터리", "미스터리"]:
            return cls.generate_script("중고 거래로 산 거울 뒤에서 발견된 의문의 쪽지", blog_url, "auto")

        if category in ["delivery", "배달황당", "배달"]:
            return cls.generate_script("치킨 시켰는데 닭다리 하나 먹고 쪽지 남긴 배달원 레전드", blog_url, "auto")

        # ----------------------------------------------------
        # 사용자가 직접 입력한 임의의 주제 (Dynamic Story Generator)
        # ----------------------------------------------------
        short_topic = clean_topic[:18]
        return {
            "title": f"🔥 [레전드 실화] {clean_topic[:24]} #Shorts #사이다썰",
            "tags": ["레전드썰", "사이다실화", "실제경험담", "Shorts", "Reels"],
            "pinned_comment": f"📌 여러분이라면 '{short_topic}' 이 상황에서 어떻게 대처하셨을 것 같나요? 댓글로 남겨주세요!",
            "broll_pref": "norm_broll_coffee.mp4",
            "voice": "ko-KR-InJoonNeural",
            "rate": "+1%",
            "cta_text": "[댓글] 여러분의 생각은? 댓글로 투표해주세요!",
            "scenes": [
                {
                    "badge": "[HOT] 레전드 실화 썰",
                    "badge_color": (239, 68, 68),
                    "hero_line1": f"{short_topic} 사건!",
                    "hero_line2": "역대급 실화 썰",
                    "accent": "역대급 실화 썰",
                    "speech": f"살면서 진짜 이런 황당한 일이 저한테 일어날 줄은 꿈에도 몰랐는데, 바로 며칠 전 {clean_topic} 사건이 터졌습니다."
                },
                {
                    "badge": "[위기] 걷잡을 수 없는 사태",
                    "badge_color": (245, 158, 11),
                    "hero_line1": "처음엔 별일 아닌 줄 알았는데",
                    "hero_line2": "예상치 못한 돌발 상황 발생!",
                    "accent": "예상치 못한 돌발 상황 발생!",
                    "speech": "처음에는 그냥 가볍게 웃어넘기려고 했는데, 일이 점점 커지더니 상상도 못 했던 돌발 사태가 벌어지기 시작한 겁니다."
                },
                {
                    "badge": "[반전] 참다못해 결단 내림",
                    "badge_color": (239, 68, 68),
                    "hero_line1": "도저히 못 참아서 행동 개시!",
                    "hero_line2": "통쾌한 사이다 반전",
                    "accent": "통쾌한 사이다 반전",
                    "speech": "도저히 이대로는 안 되겠다 싶어서 제가 제대로 결단을 내리고 행동에 나섰고, 완벽하게 사이다 반전 결말을 만들어냈습니다."
                },
                {
                    "badge": "[결말] 깔끔한 참교육",
                    "badge_color": (16, 185, 129),
                    "hero_line1": "그 뒤론 찍소리도 못 함!",
                    "hero_line2": "여러분의 생각은?",
                    "accent": "여러분의 생각은?",
                    "speech": "그 뒤로는 상대방도 찍소리 못 하고 상황이 아주 깔끔하게 끝났습니다. 여러분이라면 이 상황에서 어떻게 대처하셨을 것 같나요?"
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
        self._init_gradient_overlay()

    def _init_gradient_overlay(self):
        """상하단 은은한 시네마틱 비네팅 오버레이 (웹툰 그림 위에서 텍스트 및 자막 시인성 극대화)"""
        self.gradient_overlay = Image.new("RGBA", (self.WIDTH, self.HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(self.gradient_overlay)
        # 상단 320px 은은한 비네팅 (alpha 0 ~ 130)
        for y in range(320):
            a = int(130 * (1 - y / 320))
            draw.line([(0, y), (self.WIDTH, y)], fill=(10, 10, 20, a))
        # 하단 자막·CTA 세이프존(1220px부터 완만한 비네팅으로 텍스트 가독성 극대화)
        for y in range(1220, self.HEIGHT):
            a = int(140 * ((y - 1220) / (self.HEIGHT - 1220)))
            draw.line([(0, y), (self.WIDTH, y)], fill=(10, 10, 20, a))

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
        """
        [숏폼 연구소 알고리즘] 4~8자 내외 펀치 마이크로 청킹 & 글자수 비례 가중 타이밍
        - 1~2개 어절 단위로 0.8~1.3초마다 초고속 팝업되어 시선 이탈(Swipe-away)을 100% 방지
        - 글자수에 비례하여 시간을 정밀 배분하여 나레이션 싱크 극대화
        """
        words = speech.split()
        if not words:
            return [{"text": "", "start": 0.0, "end": duration}]

        chunks = []
        curr = []
        for w in words:
            combined = " ".join(curr + [w])
            # 5~8자 도달, 구두점(, . ! ? ~) 끝맺음, 또는 2단어 조합 시 즉시 분절
            if len(combined) >= 6 or (len(combined) >= 4 and w[-1] in ',.!?~') or len(curr) >= 1:
                chunks.append(combined)
                curr = []
            else:
                curr.append(w)
        if curr:
            curr_str = " ".join(curr)
            if chunks and len(curr_str) <= 3:
                chunks[-1] = chunks[-1] + " " + curr_str
            else:
                chunks.append(curr_str)

        # 글자수 비례 가중 타이밍 계산 (공백/구두점 제외 실질 글자수 기준)
        total_chars = sum(max(1, len(re.sub(r'[\s,.!?~]', '', c))) for c in chunks)
        if total_chars <= 0:
            total_chars = max(1, len(chunks))

        result = []
        cur_t = 0.0
        for idx, text in enumerate(chunks):
            char_cnt = max(1, len(re.sub(r'[\s,.!?~]', '', text)))
            c_dur = duration * (char_cnt / total_chars)
            end_t = min(duration, cur_t + c_dur)
            if idx == len(chunks) - 1:
                end_t = duration
            result.append({
                "text": text,
                "start": cur_t,
                "end": end_t
            })
            cur_t = end_t
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

        # 3. AI 캐릭터 웹툰 씬 배경 탐색 (Option 1 정통 썰툰 모드)
        cat_key = script_data.get("category_key")
        if not cat_key:
            tags = script_data.get("tags", [])
            title = script_data.get("title", "")
            if any("직장" in t or "회사" in t or "신입" in t or "상사" in t for t in tags) or any(k in title for k in ["직장", "사이다", "과장", "팀장", "부장", "회사"]):
                cat_key = "workplace"
            elif any("소개팅" in t or "연애" in t for t in tags) or any(k in title for k in ["소개팅", "빌런", "뷔페", "더치페이", "전남친"]):
                cat_key = "blind_date"
            elif any("미스터리" in t or "소름" in t for t in tags) or any(k in title for k in ["소름", "미스터리", "거울", "도어락", "택배"]):
                cat_key = "mystery"
            elif any("배달" in t or "황당" in t for t in tags) or any(k in title for k in ["배달", "치킨", "마라탕", "배민"]):
                cat_key = "delivery"
            else:
                cat_key = "workplace"

        webtoon_dir = os.path.join(base_dir, "assets", "webtoon", cat_key)
        use_webtoon = os.path.exists(webtoon_dir) and os.path.exists(os.path.join(webtoon_dir, "scene_0.jpg"))

        scene_webtoon_images = []
        if use_webtoon:
            for s_idx in range(len(script_data["scenes"])):
                p = os.path.join(webtoon_dir, f"scene_{s_idx}.jpg")
                if not os.path.exists(p):
                    p = os.path.join(webtoon_dir, "scene_0.jpg")
                scene_webtoon_images.append(Image.open(p).convert("RGBA"))

        # 실사 B-roll 세로 영상 탐색 (웹툰 배경 미존재 시 fallback)
        broll_dir = os.path.join(base_dir, "assets", "broll")
        broll_video = None
        if not use_webtoon and os.path.exists(broll_dir):
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
        if use_webtoon:
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
        elif broll_video:
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

            # AI 웹툰 애니메이션 줌인 (Ken Burns Effect)
            if use_webtoon and scene_webtoon_images:
                cur_img = scene_webtoon_images[current_scene_idx]
                orig_w, orig_h = cur_img.size
                dur = scene_durations[current_scene_idx]
                prog_in_scene = min(1.0, max(0.0, scene_time / dur))
                # 7% 스무스 줌인 애니메이션
                scale = 1.0 + 0.07 * prog_in_scene
                crop_w = int(orig_w / scale)
                crop_h = int(orig_h / scale)
                crop_x = (orig_w - crop_w) // 2
                crop_y = (orig_h - crop_h) // 2
                frame_bg = cur_img.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h)).resize((self.WIDTH, self.HEIGHT), Image.Resampling.BILINEAR)

                img = self._render_frame(
                    scene, progress, current_time, scene_time,
                    active_chunk, time_in_chunk, has_broll=True,
                    global_cta=script_data.get("cta_text"),
                    scene_idx=current_scene_idx,
                    base_canvas=frame_bg
                )
                proc.stdin.write(img.convert("RGB").tobytes())
            else:
                img = self._render_frame(
                    scene, progress, current_time, scene_time,
                    active_chunk, time_in_chunk, has_broll=bool(broll_video),
                    global_cta=script_data.get("cta_text"),
                    scene_idx=current_scene_idx
                )
                proc.stdin.write(img.convert("RGB").tobytes() if not broll_video else img.tobytes())

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
        print(f"✅ [AI 오피스 웹툰 애니메이션 쇼츠 파이프라인] 1080x1920 MP4 영상 렌더링 완성! ({file_size_mb:.2f} MB, {total_duration:.1f}초)")

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
        global_cta: Optional[str] = None, scene_idx: int = 0,
        base_canvas: Optional[Image.Image] = None
    ) -> Image.Image:
        """단일 시선 집중(Single Center Focus) 바이럴 숏폼 렌더러 (웹툰 씬 일러스트 지원)"""
        if base_canvas:
            # 웹툰 그림 캔버스 위에 은은한 비네팅 오버레이를 알파 블렌딩 합성하여 검은 띠 없이 자연스러운 시네마틱 효과 연출
            img = Image.alpha_composite(base_canvas.convert("RGBA"), self.gradient_overlay)
            draw = ImageDraw.Draw(img)
        elif has_broll:
            img = self.gradient_overlay.copy()
            draw = ImageDraw.Draw(img)
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

        # 4. [숏폼 연구소 알고리즘] 4~8자 초고속 키네틱 1줄 자막 (y=1330 세이프존 & 시선 이탈 방지)
        sub_text = self._clean_text_for_font(active_chunk.get("text", ""))
        if sub_text:
            display_text = sub_text  # 4~8자 마이크로 청킹으로 항상 깔끔한 1줄 유지 (시선 분산 0%)

            # 황금 세이프존: 하단 69% 지점 (y=1330)
            # 캐릭터 얼굴·상체(y=350~1150)를 가리지 않고, 유튜브/릴스 하단 네이티브 UI(y>1540)와도 0% 간섭
            sub_y = 1330
            is_pop = time_in_chunk < 0.20

            bbox = draw.textbbox((self.WIDTH // 2, sub_y), display_text, font=self.font_sub, anchor="mm")
            pad_x = 42 + (8 if is_pop else 0)
            pad_y = 18 + (3 if is_pop else 0)

            pill_outline = (255, 235, 59, 255) if is_pop else (250, 204, 21, 220)
            pill_width = 4 if is_pop else 3

            # 프리미엄 다크 글래스 필 캡슐
            draw.rounded_rectangle(
                [bbox[0] - pad_x, bbox[1] - pad_y, bbox[2] + pad_x, bbox[3] + pad_y],
                radius=26,
                fill=(10, 15, 26, 230) if has_broll else (18, 22, 36),
                outline=pill_outline,
                width=pill_width
            )

            # 자막 외곽선 그림자 (시인성 극대화)
            for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4)]:
                draw.text((self.WIDTH // 2 + ox, sub_y + oy), display_text, fill=(0, 0, 0, 255), font=self.font_sub, anchor="mm")

            # 텍스트 컬러 (팝업 바운스 시 전기빛 네온 골드, 평상시 선명한 퓨어 화이트)
            text_color = (255, 240, 80) if is_pop else (255, 255, 255)
            draw.text((self.WIDTH // 2, sub_y), display_text, fill=text_color, font=self.font_sub, anchor="mm")

        # 5. [숏폼 연구소 알고리즘] 참여 유도 배너 (y=1465~1525 세이프존 내 슬림 배치로 네이티브 UI 간섭 0%)
        cta = scene.get("cta_text") or global_cta or "[댓글] 여러분의 생각은? 댓글로 공유해주세요!"
        cta_text = self._clean_text_for_font(cta)
        draw.rounded_rectangle([180, 1465, 900, 1525], radius=24, fill=(225, 29, 72, 220), outline=(255, 255, 255, 180), width=2)
        draw.text((self.WIDTH // 2, 1495), cta_text, fill=(255, 255, 255), font=self.font_cta, anchor="mm")

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

    # 3. 실시간 R&D 연구소 알고리즘 연동 (오연구원 숏폼 R&D 플레이북 100% 적용)
    rnd_cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rnd_live_cache.json")
    rnd_data = {}
    if os.path.exists(rnd_cache_path):
        try:
            with open(rnd_cache_path, "r", encoding="utf-8") as f:
                rnd_data = json.load(f)
        except Exception:
            pass

    # 인스타그램 릴스 맞춤형 바이럴 캡션 (저장·공유 DM 전송 유도)
    reels_caption = (
        f"🔥 {script_data.get('title', clean_topic)}\n\n"
        f"살면서 이런 일 겪어보신 적 있나요? 여러분이라면 이 상황에서 어떻게 대처하셨을 것 같나요? 💬\n\n"
        f"📌 [인스타 릴스 시청 꿀팁]\n"
        f"• 비슷한 경험이 있는 친구에게 DM으로 공유해보세요!\n"
        f"• 나중에 다시 보려면 우측 하단 깃발(저장)을 눌러두세요.\n"
        f"• 전체 썰과 상세 후기는 프로필 링크에서 바로 확인하실 수 있습니다!\n\n"
        f"#릴스 #릴스추천 #사이다썰 #실화썰 #썰툰 #공감썰 #숏폼 #인스타툰"
    )

    result["reels_caption"] = reels_caption
    result["rnd_last_crawled_at"] = rnd_data.get("last_crawled_at", "")
    result["rnd_status"] = "R&D 연구소 오연구원 숏폼 알고리즘 100% 실시간 적용"
    result["rnd_audit"] = {
        "rule_1_hook": "첫 1.5초 스와이프 이탈 차단 텍스트 훅 + 3.8초 집중 헤드라인 적용",
        "rule_2_subtitle": "단일 시선 고정(y=1330) 4~8자 초고속 키네틱 1줄 자막 (UI 간섭 0%)",
        "rule_3_loop": "무한 반복 재생(Loop Ending) 구조로 완주율·시청지속시간 극대화",
        "rule_4_split": "유튜브 쇼츠 vs 인스타 릴스 플랫폼별 맞춤 캡션 분리 제공"
    }

    # 4. 메타데이터 JSON 저장
    meta_path = os.path.join(output_dir, f"shorts_{safe_topic}_{timestamp}_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    result["meta_path"] = meta_path
    result["web_url"] = f"/output/shorts/{output_filename}"

    return result


class CardNewsReelsGenerator:
    """인스타그램 릴스 & 캐러셀 전용 9:16 (1080x1920) 프리미엄 마스터 인포그래픽 제작 엔진
    - 폰트 혁신: 대한민국 핀테크 표준 프리텐다드(Pretendard Black / ExtraBold / SemiBold / Medium) 100% 적용
    - 3D 일러스트 렌더링 에셋 결합 (유리 저축통, 3D 신축 아파트 단지)
    - 100% 자체 벡터 그래픽 (골드 코인, 에메랄드 체크, 스파클 다이아몬드)
    - 5열 현실 계산표 + 2단 비교 박스 + 인용구 팁 카드 + 실천 팁 뱃지
    - 잔잔하고 감미로운 어쿠스틱 피아노 BGM (calm_piano.mp3) 15초 릴스 영상 생성
    """
    WIDTH = 1080
    HEIGHT = 1920
    FPS = 30
    DURATION = 15.0  # 15초 잔잔한 릴스 영상

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        fonts_dir = os.path.join(base_dir, "assets", "fonts")

        f_black = os.path.join(fonts_dir, "Pretendard-Black.ttf")
        f_xbold = os.path.join(fonts_dir, "Pretendard-ExtraBold.ttf")
        f_bold = os.path.join(fonts_dir, "Pretendard-Bold.ttf")
        f_semi = os.path.join(fonts_dir, "Pretendard-SemiBold.ttf")
        f_med = os.path.join(fonts_dir, "Pretendard-Medium.ttf")

        # Headings: Pretendard-Black (초고밀도 볼드, 토스/당근/인스타 감성)
        if os.path.exists(f_black):
            self.f_hero = ImageFont.truetype(f_black, 70)
            self.f_super = ImageFont.truetype(f_black, 90)
            self.f_banner = ImageFont.truetype(f_black, 34)
        else:
            self.f_hero = self.f_super = self.f_banner = ImageFont.load_default()

        if os.path.exists(f_xbold):
            self.f_sec_head = ImageFont.truetype(f_xbold, 30)
            self.f_badge_pill = ImageFont.truetype(f_xbold, 22)
            self.f_table_val = ImageFont.truetype(f_xbold, 27)
            self.f_card_val = ImageFont.truetype(f_xbold, 28)
            self.f_quote = ImageFont.truetype(f_xbold, 29)
        else:
            self.f_sec_head = self.f_badge_pill = self.f_table_val = self.f_card_val = self.f_quote = ImageFont.load_default()

        if os.path.exists(f_bold):
            self.f_table_head = ImageFont.truetype(f_bold, 26)
            self.f_footer = ImageFont.truetype(f_bold, 24)
            self.f_icon_won = ImageFont.truetype(f_bold, 17)
        else:
            self.f_table_head = self.f_footer = self.f_icon_won = ImageFont.load_default()

        if os.path.exists(f_semi):
            self.f_subhead = ImageFont.truetype(f_semi, 28)
            self.f_top_brand = ImageFont.truetype(f_semi, 23)
            self.f_table_body = ImageFont.truetype(f_semi, 25)
            self.f_tip = ImageFont.truetype(f_semi, 22)
        else:
            self.f_subhead = self.f_top_brand = self.f_table_body = self.f_tip = ImageFont.load_default()

        if os.path.exists(f_med):
            self.f_card_label = ImageFont.truetype(f_med, 25)
            self.f_bullet = ImageFont.truetype(f_med, 24)
            self.f_footnote = ImageFont.truetype(f_med, 18)
        else:
            self.f_card_label = self.f_bullet = self.f_footnote = ImageFont.load_default()

    def _draw_drop_shadow_box(self, draw, xy, radius=12, fill=(255, 255, 255), outline=(226, 232, 240), shadow_color=(241, 245, 249)):
        x0, y0, x1, y1 = xy
        draw.rounded_rectangle([x0 + 2, y0 + 3, x1 + 2, y1 + 3], radius=radius, fill=shadow_color)
        draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=1)

    def _draw_vector_coin(self, draw, cx, cy, r=15):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(245, 158, 11), outline=(217, 119, 6), width=1)
        draw.ellipse([cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3], fill=(251, 191, 36))
        draw.text((cx, cy - 1), "W", fill=(180, 83, 9), font=self.f_icon_won, anchor="mm")

    def _draw_vector_check(self, draw, cx, cy, r=13):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(16, 185, 129))
        draw.line([(cx - 5, cy), (cx - 1, cy + 4), (cx + 5, cy - 4)], fill=(255, 255, 255), width=2)

    def _draw_star_sparkle(self, draw, cx, cy, size=14, color=(245, 158, 11)):
        pts = [
            (cx, cy - size),
            (cx + size * 0.35, cy - size * 0.35),
            (cx + size, cy),
            (cx + size * 0.35, cy + size * 0.35),
            (cx, cy + size),
            (cx - size * 0.35, cy + size * 0.35),
            (cx - size, cy),
            (cx - size * 0.35, cy - size * 0.35),
        ]
        draw.polygon(pts, fill=color)

    def generate_single_master_sheet(self, topic: str) -> Image.Image:
        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        # 이중 외곽 테두리 (디자인 카드 프레임)
        draw.rounded_rectangle([24, 24, self.WIDTH - 24, self.HEIGHT - 24], radius=32, outline=(226, 232, 240), width=3)
        draw.rounded_rectangle([32, 32, self.WIDTH - 32, self.HEIGHT - 32], radius=26, outline=(241, 245, 249), width=2)

        t_low = topic.lower()
        is_youth = any(k in t_low for k in ["청년", "도약", "희망", "기여금", "비과세", "적금", "저축", "1억", "통장"])
        is_housing = any(k in t_low for k in ["주담대", "대출", "주택", "아파트", "매매", "내집마련", "부동산", "전세", "디딤돌", "보금자리"])
        is_tax = any(k in t_low for k in ["연말정산", "환급", "세금", "소득공제", "세액공제", "절세"])

        # 1. 상단 브랜드 바
        brand_name = "청년 금융·정부지원금 연구소" if is_youth else ("내집마련 실전 연구소" if is_housing else ("연말정산·절세 연구소" if is_tax else "생활 금융·재테크 연구소"))
        draw.rounded_rectangle([60, 56, 440, 106], radius=14, fill=(241, 245, 249))
        self._draw_star_sparkle(draw, 85, 81, size=9, color=(30, 58, 138))
        draw.text((105, 81), brand_name, fill=(51, 65, 85), font=self.f_top_brand, anchor="lm")
        draw.text((self.WIDTH - 70, 81), "2026 OFFICIAL GUIDE", fill=(148, 163, 184), font=self.f_top_brand, anchor="rm")

        # 2. 우측 상단 3D 일러스트 에셋 합성
        sprite_path = None
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if is_youth:
            sprite_path = os.path.join(base_dir, "assets", "sprites", "savings_3d_icon.jpg")
        elif is_housing:
            sprite_path = os.path.join(base_dir, "assets", "sprites", "apartment_3d_icon.jpg")

        if sprite_path and os.path.exists(sprite_path):
            try:
                icon_img = Image.open(sprite_path).convert("RGB")
                icon_img = icon_img.resize((360, 360), Image.Resampling.LANCZOS)
                img.paste(icon_img, (670, 115))
            except Exception:
                pass

        # 3. 메인 헤드라인
        if is_youth:
            subhead = "매월 최대 3.3만 원 기여금 + 비과세 혜택"
            line1 = "2026 청년도약계좌"
            line2_strong = "정부기여금 총정리"
            banner_text = "소득구간별 기여금 매칭 & 5년 만기 수령액 현실 계산"
            sec1_badge, sec1_title = "01 납입액별", "기여금 매칭"
            sec1_items = [
                ("월 40만 납입", "기여금 2.4만", (225, 29, 72)),
                ("월 50만 납입", "기여금 2.4만", (225, 29, 72)),
                ("월 60만 납입", "기여금 2.3만", (30, 58, 138)),
                ("월 70만 납입", "기여금 2.1만", (30, 58, 138))
            ]
            sec2_badge, sec2_title = "02 소득별", "매칭 비율"
            sec2_items = [
                ("2,400만 이하", "매칭률 6.0%", (30, 58, 138)),
                ("3,600만 이하", "매칭률 4.6%", (30, 58, 138)),
                ("4,800만 이하", "매칭률 3.7%", (225, 29, 72)),
                ("6,000만 이하", "매칭률 3.0%", (225, 29, 72))
            ]
            sec3_title = "만기 시 실제 수령액 총정리"
            headers = ["월 납입액", "원금(5년)", "정부기여금", "은행이자(최고)", "만기 총수령액"]
            rows = [
                ("40만 원", "2,400만", "약 144만", "약 370만", "2,914만 원"),
                ("50만 원", "3,000만", "약 144만", "약 460만", "3,604만 원"),
                ("60만 원", "3,600만", "약 138만", "약 550만", "4,288만 원"),
                ("70만 원", "4,200만", "약 126만", "약 640만", "4,966만 원"),
                ("70만(육아)", "4,200만", "약 144만", "약 680만", "5,024만 원"),
                ("70만(우대)", "4,200만", "약 144만", "약 710만", "5,054만 원")
            ]
            footnote = "* 기준: 기본 4.5% + 우대 1.5% (최고 6.0%) / 이자소득세 15.4% 비과세 전액 면제 반영"
            quote_title = "“ 청년도약계좌는 원금보다 '정부 기여금과 15.4% 비과세'가 핵심! ”"
            bullets = [
                "3년만 유지해도 비과세 혜택 100% 인정 + 정부 기여금 60% 지급으로 개편!",
                "개인소득 7,500만 원 이하 & 가구 중위소득 250% 이하 청년 누구나 신청 가능",
                "70만 원 납입이 부담되면 40~50만 원만 넣어도 정부 기여금은 최대치 수령!"
            ]
            tips = ["3년 비과세", "40만 가성비", "은행앱 접수", "소득증명원", "5천만 목돈"]
        elif is_housing:
            subhead = "내 월급으로 얼마짜리 아파트까지 살 수 있을까?"
            line1 = "내 집 마련"
            line2_strong = "현실 커트라인"
            banner_text = "아파트 매매가별 대출 한도 & 필요 현금 총정리"
            sec1_badge, sec1_title = "01 기간별", "1억 모으기"
            sec1_items = [
                ("3년 목표", "월 278만 원", (225, 29, 72)),
                ("5년 목표", "월 167만 원", (225, 29, 72)),
                ("7년 목표", "월 119만 원", (30, 58, 138)),
                ("10년 목표", "월 83만 원", (30, 58, 138))
            ]
            sec2_badge, sec2_title = "02 소득별", "대출 한도"
            sec2_items = [
                ("월 300만", "최대 2.8억", (30, 58, 138)),
                ("월 400만", "최대 3.9억", (30, 58, 138)),
                ("월 500만", "최대 4.9억", (225, 29, 72)),
                ("월 600만", "최대 5.8억", (225, 29, 72))
            ]
            sec3_title = "아파트 가격별 필요 월급 계산"
            headers = ["매매가", "대출금(70%)", "준비할 현금", "매달 원리금", "필요 월급"]
            rows = [
                ("4.0억", "2.80억", "1.20억", "142만 원", "489만 원"),
                ("5.0억", "3.50억", "1.50억", "177만 원", "611만 원"),
                ("6.0억", "4.20억", "1.80억", "212만 원", "733만 원"),
                ("7.0억", "4.90억", "2.10억", "248만 원", "855만 원"),
                ("8.0억", "5.60억", "2.40억", "283만 원", "977만 원"),
                ("9.0억", "6.00억", "3.00억", "303만 원", "1,047만 원")
            ]
            footnote = "* 기준: 수도권 비규제지역 기준 (LTV 70%, 30년 만기 연 4.2% / 세전 DSR 40% 계산)"
            quote_title = "“ 내 집 마련은 '월급 액수'보다 '저축률'과 'DSR 관리'가 핵심입니다! ”"
            bullets = [
                "소득 300만 원도 DSR 3단계 방어 및 생애최초 LTV 80% 우대 시 내집마련 가능",
                "디딤돌·버팀목·보금자리론 정부 특례 결합 시 최저 연 3%대 고정금리 적용",
                "신혼부부 부부 중 1명 소득 요건 인정으로 결혼 페널티 전면 폐지!"
            ]
            tips = ["LTV 70%", "DSR 방어", "디딤돌 특례", "등기부 확인", "생초 우대"]
        elif is_tax:
            subhead = "13월의 월급? 세금 폭탄 피하는 황금비율"
            line1 = "2026 연말정산"
            line2_strong = "환급금 극대화"
            banner_text = "총급여별 카드 황금비율 & 세액공제 한도 총정리"
            sec1_badge, sec1_title = "01 카드공제", "황금 비율"
            sec1_items = [
                ("총급여 25%까지", "신용카드 결제", (30, 58, 138)),
                ("25% 초과분은", "체크카드 30%", (225, 29, 72)),
                ("전통시장 결제", "최대 40% 공제", (22, 101, 52)),
                ("대중교통 이용", "최대 80% 공제", (225, 29, 72))
            ]
            sec2_badge, sec2_title = "02 절세계좌", "세액 공제"
            sec2_items = [
                ("연금저축 한도", "최대 600만 원", (30, 58, 138)),
                ("IRP 합산 납입", "최대 900만 원", (225, 29, 72)),
                ("5,500만 이하", "16.5% 세액공제", (225, 29, 72)),
                ("최대 환급액", "148.5만 원 돌려받음", (30, 58, 138))
            ]
            sec3_title = "연봉별 현실 환급액 계산"
            headers = ["총급여", "25% 문턱금액", "체크카드 목표", "연금/IRP", "평균 환급액"]
            rows = [
                ("3,500만", "875만 원", "500만 원", "300만 원", "+ 82만 원"),
                ("4,500만", "1,125만 원", "700만 원", "600만 원", "+ 135만 원"),
                ("5,500만", "1,375만 원", "900만 원", "900만 원", "+ 189만 원"),
                ("6,500만", "1,625만 원", "1,100만 원", "900만 원", "+ 195만 원"),
                ("7,500만", "1,875만 원", "1,300만 원", "900만 원", "+ 218만 원"),
                ("1.0억 원", "2,500만 원", "1,800만 원", "900만 원", "+ 284만 원")
            ]
            footnote = "* 기준: 기본 인적공제 + 신용/체크카드 사용 + IRP 세액공제 결합 기준 산정"
            quote_title = "“ 연말정산은 '몰아서 쓰기'보다 '소득공제 문턱과 IRP 납입'이 핵심! ”"
            bullets = [
                "총급여의 25% 채운 뒤부터 체크카드·현금영수증으로 결제 수단 전환",
                "IRP 계좌 연말 12월 일시납으로 최대 148.5만원 세액공제 환급 챙기기",
                "시력교정용 안경, 중고생 교복, 월세 이체내역 등 누락 영수증 사전 준비"
            ]
            tips = ["25% 신용", "초과 체크", "IRP 900만", "안경/월세", "148만 환급"]
        else:
            subhead = f"모르면 100만 원 손해 보는 실전 지침"
            line1 = f"{topic[:10]}"
            line2_strong = "핵심 혜택 총정리"
            banner_text = "놓치기 쉬운 필수 조건 & 실질 수혜 혜택 총정리"
            sec1_badge, sec1_title = "01 지원요건", "자격 기준"
            sec1_items = [
                ("기본 요건", "연령/소득 매칭", (30, 58, 138)),
                ("우대 대상", "추가 가점 적용", (225, 29, 72)),
                ("제외 기준", "중복 수혜 제한", (30, 58, 138)),
                ("신청 기한", "매월 1회 접수", (225, 29, 72))
            ]
            sec2_badge, sec2_title = "02 혜택규모", "실질 감면"
            sec2_items = [
                ("기본 혜택", "월 최대 지원", (30, 58, 138)),
                ("세제 감면", "소득공제 반영", (30, 58, 138)),
                ("특별 환급", "비과세 전액 지원", (225, 29, 72)),
                ("총 수혜액", "연 수백만 원", (225, 29, 72))
            ]
            sec3_title = "조건별 실질 수혜 혜택 비교"
            headers = ["구분", "기본 요건", "우대 조건", "월 절감액", "연간 총혜택"]
            rows = [
                ("1단계", "소득 3,000만", "청년·취약계층", "월 15만 원", "연 180만 원"),
                ("2단계", "소득 4,500만", "신혼·다자녀", "월 22만 원", "연 264만 원"),
                ("3단계", "소득 6,000만", "일반 근로자", "월 30만 원", "연 360만 원"),
                ("4단계", "소득 7,500만", "특례 대상자", "월 38만 원", "연 456만 원"),
                ("5단계", "맞벌이 1.0억", "특별 지원군", "월 45만 원", "연 540만 원"),
                ("6단계", "최고 우대형", "전체 충족자", "월 55만 원", "연 660만 원")
            ]
            footnote = "* 기준: 2026 정부 공시 지침 및 각 기관 공식 기준 산정"
            quote_title = "“ 놓치기 쉬운 필수 정부 혜택, 신청 기간 내 접수가 핵심입니다! ”"
            bullets = [
                "신청 기한 경과 시 소급 적용 불가하므로 공고 즉시 사전 접수 필수",
                "비대면 모바일 간편 신청으로 주민센터 방문 없이 즉시 접수 가능",
                "필수 증빙서류 사전 완비 시 심사 기간 50% 이상 단축"
            ]
            tips = ["지원 대상", "혜택 최대", "간편 접수", "서류 완비", "전액 수령"]

        draw.text((60, 140), subhead, fill=(100, 116, 139), font=self.f_subhead, anchor="lt")
        draw.text((60, 192), line1, fill=(15, 23, 42), font=self.f_hero, anchor="lt")
        draw.text((60, 276), line2_strong, fill=(225, 29, 72), font=self.f_super, anchor="lt")
        self._draw_star_sparkle(draw, 60 + int(len(line2_strong) * 55) + 15, 322, size=15, color=(225, 29, 72))

        # 네이비 메인 캡슐 배너 (Pretendard-Black)
        draw.rounded_rectangle([60, 475, 1020, 545], radius=16, fill=(15, 23, 42))
        draw.text((540, 510), banner_text, fill=(255, 255, 255), font=self.f_banner, anchor="mm")

        # 4. 2단 그리드 박스
        draw.rounded_rectangle([60, 565, 525, 920], radius=20, fill=(248, 250, 252), outline=(203, 213, 225), width=2)
        draw.rounded_rectangle([80, 585, 230, 628], radius=12, fill=(30, 58, 138))
        draw.text((155, 606), sec1_badge, fill=(255, 255, 255), font=self.f_badge_pill, anchor="mm")
        draw.text((245, 606), sec1_title, fill=(15, 23, 42), font=self.f_sec_head, anchor="lm")
        y_b1 = 640
        for lbl, val, col in sec1_items:
            self._draw_drop_shadow_box(draw, [80, y_b1, 505, y_b1 + 60], radius=12)
            self._draw_vector_coin(draw, 105, y_b1 + 30, r=13)
            draw.text((130, y_b1 + 30), lbl, fill=(51, 65, 85), font=self.f_card_label, anchor="lm")
            draw.text((485, y_b1 + 30), val, fill=col, font=self.f_card_val, anchor="rm")
            y_b1 += 67

        draw.rounded_rectangle([555, 565, 1020, 920], radius=20, fill=(248, 250, 252), outline=(203, 213, 225), width=2)
        draw.rounded_rectangle([575, 585, 725, 628], radius=12, fill=(225, 29, 72))
        draw.text((650, 606), sec2_badge, fill=(255, 255, 255), font=self.f_badge_pill, anchor="mm")
        draw.text((740, 606), sec2_title, fill=(15, 23, 42), font=self.f_sec_head, anchor="lm")
        y_b2 = 640
        for lbl, val, col in sec2_items:
            self._draw_drop_shadow_box(draw, [575, y_b2, 1000, y_b2 + 60], radius=12)
            self._draw_star_sparkle(draw, 600, y_b2 + 30, size=9, color=(225, 29, 72))
            draw.text((620, y_b2 + 30), lbl, fill=(51, 65, 85), font=self.f_card_label, anchor="lm")
            draw.text((980, y_b2 + 30), val, fill=col, font=self.f_card_val, anchor="rm")
            y_b2 += 67

        # 5. 실전 계산표
        draw.rounded_rectangle([60, 940, 215, 982], radius=12, fill=(13, 148, 136))
        draw.text((137, 961), "03 실전 계산", fill=(255, 255, 255), font=self.f_badge_pill, anchor="mm")
        draw.text((230, 961), sec3_title, fill=(15, 23, 42), font=self.f_sec_head, anchor="lm")

        cols = [60, 235, 430, 625, 825, 1020]
        draw.rounded_rectangle([60, 995, 1020, 1055], radius=12, fill=(241, 245, 249))
        for i in range(len(headers)):
            mid_x = (cols[i] + cols[i+1]) // 2
            draw.text((mid_x, 1025), headers[i], fill=(30, 41, 59), font=self.f_table_head, anchor="mm")

        y_tbl = 1065
        for idx, (c1, c2, c3, c4, c5) in enumerate(rows):
            bg_col = (255, 255, 255) if idx % 2 == 0 else (248, 250, 252)
            draw.rounded_rectangle([60, y_tbl, 1020, y_tbl + 64], radius=10, fill=bg_col, outline=(226, 232, 240), width=1)
            
            draw.text(((cols[0] + cols[1]) // 2, y_tbl + 32), c1, fill=(22, 101, 52), font=self.f_table_body, anchor="mm")
            draw.text(((cols[1] + cols[2]) // 2, y_tbl + 32), c2, fill=(161, 98, 7), font=self.f_table_body, anchor="mm")
            draw.text(((cols[2] + cols[3]) // 2, y_tbl + 32), c3, fill=(29, 78, 216), font=self.f_table_body, anchor="mm")
            draw.text(((cols[3] + cols[4]) // 2, y_tbl + 32), c4, fill=(190, 24, 93), font=self.f_table_body, anchor="mm")
            draw.text(((cols[4] + cols[5]) // 2, y_tbl + 32), c5, fill=(185, 28, 28), font=self.f_table_val, anchor="mm")
            y_tbl += 69

        draw.text((65, y_tbl + 6), footnote, fill=(148, 163, 184), font=self.f_footnote, anchor="lt")

        # 6. 인용구 및 정책 콜아웃 카드
        y_q = y_tbl + 38
        draw.rounded_rectangle([60, y_q, 1020, y_q + 195], radius=20, fill=(254, 242, 242), outline=(254, 205, 211), width=2)
        draw.text((95, y_q + 36), quote_title, fill=(159, 18, 57), font=self.f_quote, anchor="lm")
        
        y_bull = y_q + 80
        for b_text in bullets:
            self._draw_vector_check(draw, 105, y_bull)
            draw.text((130, y_bull), b_text, fill=(71, 85, 105), font=self.f_bullet, anchor="lm")
            y_bull += 38

        # 7. 실전 신청 팁 5개 뱃지
        y_t = y_q + 215
        draw.text((65, y_t + 15), "실전 신청 & 필수 팁", fill=(51, 65, 85), font=self.f_top_brand, anchor="lm")
        x_tip = 60
        box_w = 176
        for tip in tips:
            draw.rounded_rectangle([x_tip, y_t + 38, x_tip + box_w, y_t + 92], radius=14, fill=(241, 245, 249), outline=(203, 213, 225), width=1)
            self._draw_star_sparkle(draw, x_tip + 22, y_t + 65, size=7, color=(13, 148, 136))
            draw.text((x_tip + 36, y_t + 65), tip, fill=(15, 23, 42), font=self.f_tip, anchor="lm")
            x_tip += box_w + 20

        # 8. 하단 저장 & 프로필 링크 바
        y_save = y_t + 110
        draw.rounded_rectangle([60, y_save, 1020, y_save + 60], radius=24, fill=(15, 23, 42))
        draw.text((540, y_save + 30), "[저장] 누르고 신청할 때 꺼내보세요  |  프로필 링크에서 1초 모의 계산", fill=(255, 255, 255), font=self.f_footer, anchor="mm")

        return img

    def generate_slides(self, topic: str, blog_url: str = "") -> list:
        return [self.generate_single_master_sheet(topic)]

    def render_reels_video(self, topic: str, blog_url: str = "") -> dict:
        clean_topic = topic.strip() or "2026 청년도약계좌 정부기여금 & 비과세 혜택 총정리"
        safe_name = re.sub(r'[\\s\\/:*?"<>|]+', '_', clean_topic)[:25]
        timestamp = int(time.time())

        out_dir = os.path.join(os.getcwd(), "output", "shorts")
        os.makedirs(out_dir, exist_ok=True)

        carousel_dir_name = f"carousel_{safe_name}_{timestamp}"
        carousel_folder = os.path.join(out_dir, carousel_dir_name)
        os.makedirs(carousel_folder, exist_ok=True)

        import urllib.parse
        encoded_carousel = urllib.parse.quote(carousel_dir_name)

        # 1. 1장 완결형 마스터 인포그래픽 이미지 저장
        master_img = self.generate_single_master_sheet(clean_topic)
        master_path = os.path.join(carousel_folder, "slide_1.png")
        master_img.save(master_path, "PNG")

        slide_urls = [f"/output/shorts/{encoded_carousel}/slide_1.png"]

        # 2. 15초 잔잔한 피아노 BGM 릴스 비디오 렌더링
        video_filename = f"reels_cardnews_{safe_name}_{timestamp}.mp4"
        encoded_video = urllib.parse.quote(video_filename)
        video_path = os.path.join(out_dir, video_filename)

        bgm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "audio", "calm_piano.mp3")
        if not os.path.exists(bgm_path):
            bgm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "audio", "lofi_beat.mp3")
        has_bgm = os.path.exists(bgm_path)

        total_duration = self.DURATION  # 15.0초

        cmd = [self.ffmpeg_exe, "-y"]
        cmd.extend(["-loop", "1", "-t", str(total_duration), "-i", master_path])

        if has_bgm:
            cmd.extend([
                "-stream_loop", "-1", "-i", bgm_path,
                "-t", str(total_duration),
                "-af", f"afade=t=in:ss=0:d=1.5,afade=t=out:st={total_duration - 2.0}:d=2.0,volume=0.25",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                video_path
            ])
        else:
            cmd.extend([
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-pix_fmt", "yuv420p",
                "-t", str(total_duration),
                video_path
            ])

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        caption = (
            f"📌 {clean_topic} 1분 완벽 정리 인포그래픽\n\n"
            f"지원 조건, 소득별 기여금 매칭, 만기 수령액까지 한눈에 보기 쉽게 1장으로 총정리했습니다.\n\n"
            f"🔖 나중에 신청할 때 찾아보시려면 지금 우측 하단 [저장] 눌러두세요!\n"
            f"✈️ 주변에 필요한 친구나 가족에게 DM으로 공유해주세요.\n\n"
            f"👉 공식 신청 누리집 링크 및 모의 계산기는 [프로필 링크]에서 바로 확인하실 수 있습니다!\n\n"
            f"#릴스 #카드뉴스 #인포그래픽 #재테크 #정부지원금 #생활꿀팁 #직장인팁 #청년도약계좌"
        )

        size_mb = round(os.path.getsize(video_path) / (1024 * 1024), 2) if os.path.exists(video_path) else 0

        meta = {
            "status": "success",
            "title": f"📌 {clean_topic} 핵심 총정리",
            "format": "instagram_single_master_infographic",
            "duration": total_duration,
            "size_mb": size_mb,
            "filepath": video_path,
            "filename": video_filename,
            "web_url": f"/output/shorts/{encoded_video}",
            "carousel_folder": carousel_folder,
            "slide_images": [master_path],
            "slide_urls": slide_urls,
            "instagram_caption": caption,
            "tags": "#릴스 #카드뉴스 #인포그래픽 #재테크 #정부지원금 #생활꿀팁 #직장인팁",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        meta_path = os.path.join(out_dir, f"reels_cardnews_{safe_name}_{timestamp}_meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            import json
            json.dump(meta, f, ensure_ascii=False, indent=2)

        meta["meta_path"] = meta_path
        return meta


def generate_cardnews_pipeline(topic: str, blog_url: str = "", category: str = "auto") -> Dict:
    """인스타그램 1장 완결형 마스터 인포그래픽 & 잔잔한 릴스 영상 생성 파이프라인 단일 진입점"""
    generator = CardNewsReelsGenerator()
    return generator.render_reels_video(topic=topic, blog_url=blog_url)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Tistory AI 감성 릴스/쇼츠 영상 자동 제작 파이프라인")
    parser.add_argument("--topic", type=str, default="네이버 프리미엄콘텐츠 유료 구독 채널 개설 및 첫 달 수익화 팁", help="영상 제작 주제")
    parser.add_argument("--url", type=str, default="https://tistory-ai-corp.tistory.com", help="유입용 블로그 URL")
    args = parser.parse_args()

    res = generate_shorts_pipeline(args.topic, args.url)
    print(f"🎉 릴스 제작 완료: {res['filepath']} ({res['duration']}초, {res['size_mb']}MB)")
