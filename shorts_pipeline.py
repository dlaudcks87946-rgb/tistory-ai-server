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
    """주제를 20~25초 분량의 바이럴 3단계(후킹-핵심비법-프로필유입) 스토리텔링 대본으로 변환"""

    @staticmethod
    def generate_script(topic: str, blog_url: str = "") -> Dict:
        clean_topic = topic.strip() or "2026 부업 수익화 비밀 꿀팁"
        clean_url = blog_url.strip() or "https://tistory-ai-corp.tistory.com"

        # 1. 정부 지원금 / 바우처 / 청년 / 환수 테마
        if any(k in clean_topic for k in ["바우처", "첫만남", "지원금", "청년", "환수", "소멸", "국민행복카드", "정부"]):
            return {
                "title": f"🚨 {clean_topic[:26]} 기한 지나면 전액 소멸?! #Shorts",
                "tags": ["정부지원금", "바우처혜택", "생활꿀팁", "Shorts", "Reels"],
                "pinned_comment": f"📌 [1초 잔액 조회 & 제휴처 전체 리스트] 지금 바로 프로필 고정 댓글 블로그에서 확인하세요! 👉 {clean_url}",
                "scenes": [
                    {
                        "badge": "🚨 긴급 경고 | 기한 엄수",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "기한 지나면",
                        "hero_line2": "전액 국고 환수?!",
                        "accent": "전액 국고 환수?!",
                        "speech": f"혹시 {clean_topic[:18]} 지원금 받아두고 그냥 까먹고 계신가요? 정해진 기한 넘기면 남은 잔액이 전부 자동 소멸됩니다!"
                    },
                    {
                        "badge": "💡 현금처럼 긁는 꿀팁",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "마트·약국·배민까지",
                        "hero_line2": "전부 결제 가능합니다!",
                        "accent": "전부 결제 가능합니다!",
                        "speech": "병원과 약국은 물론이고 이마트, 백화점, 심지어 쿠팡이나 배달의민족 앱에서도 간편결제 등록해서 현금처럼 쓸 수 있습니다."
                    },
                    {
                        "badge": "👉 프로필 링크 확인",
                        "badge_color": (168, 85, 247),
                        "hero_line1": "내 잔액 1초 조회",
                        "hero_line2": "지금 바로 확인하세요!",
                        "accent": "지금 바로 확인하세요!",
                        "speech": "내 카드에 남은 잔액 실시간 조회법과 온라인 결제처 총정리는, 아래 고정 댓글 블로그 링크에서 지금 바로 확인해 보세요!"
                    }
                ]
            }

        # 2. 블로그 / 부업 / 수익화 / 네이버 / 애드센스 / 재테크 테마
        if any(k in clean_topic for k in ["수익", "부업", "블로그", "네이버", "구독", "애드센스", "돈", "머니", "월", "쿠팡"]):
            return {
                "title": f"🔥 {clean_topic[:26]} 솔직히 나만 몰랐던 수익화 비법 #Shorts",
                "tags": ["부업추천", "수익화", "직장인부업", "Shorts", "Reels"],
                "pinned_comment": f"📌 [100% 무료 가이드] 상세한 0원 시작 세팅법과 꿀팁은 고정 댓글 블로그에서 확인하세요! 👉 {clean_url}",
                "scenes": [
                    {
                        "badge": "🔥 솔직히 나만 몰랐던 비법",
                        "badge_color": (239, 68, 68),
                        "hero_line1": "아직도 하루 몇 백원에",
                        "hero_line2": "현타 오고 계신가요?",
                        "accent": "현타 오고 계신가요?",
                        "speech": f"솔직히 블로그 하루 종일 써서 몇 백원 벌면 현타 오죠? 남들은 지금 {clean_topic[:18]} 이거 하나로 월 150씩 조용히 챙겨가고 있습니다."
                    },
                    {
                        "badge": "💡 0원으로 시작하는 꿀팁",
                        "badge_color": (245, 158, 11),
                        "hero_line1": "딱 2가지만",
                        "hero_line2": "세팅해 두면 끝납니다!",
                        "accent": "딱 2가지만",
                        "speech": "딱 2가지만 기억하세요. 남들 다 쓰는 레드오션 키워드는 버리고, 3분 만에 0원으로 채널을 열어두면 자는 동안에도 수익이 들어옵니다."
                    },
                    {
                        "badge": "👉 프로필 링크 확인",
                        "badge_color": (168, 85, 247),
                        "hero_line1": "100% 무료 가이드",
                        "hero_line2": "지금 바로 확인하세요!",
                        "accent": "100% 무료 가이드",
                        "speech": "더 늦기 전에 막차 타세요! 상세한 첫 달 수익화 세팅 가이드는 프로필 고정 댓글 링크에 모두 남겨뒀으니 지금 바로 확인하세요!"
                    }
                ]
            }

        # 3. AI / 테크 / 생산성 / 일반 생활 꿀팁 테마
        return {
            "title": f"⚡ {clean_topic[:26]} 20초 만에 끝내는 시크릿 꿀팁 #Shorts",
            "tags": ["생활꿀팁", "인생꿀팁", "핵심요약", "Shorts", "Reels"],
            "pinned_comment": f"📌 [상세 가이드 & 바로가기] 고정 댓글 블로그 링크에서 1초 만에 확인하세요! 👉 {clean_url}",
            "scenes": [
                {
                    "badge": "⚡ 3초 시선 집중",
                    "badge_color": (239, 68, 68),
                    "hero_line1": "이거 아직도 모르면",
                    "hero_line2": "매달 30만원씩 손해!",
                    "accent": "매달 30만원씩 손해!",
                    "speech": f"아직도 {clean_topic[:20]}에 대해 제대로 모르고 계셨나요? 이거 하나만 알아도 남들보다 3배 이상 앞서갈 수 있습니다."
                },
                {
                    "badge": "💡 1%만 아는 핵심 비법",
                    "badge_color": (245, 158, 11),
                    "hero_line1": "복잡한 절차 없이",
                    "hero_line2": "딱 3분 만에 해결!",
                    "accent": "딱 3분 만에 해결!",
                    "speech": "핵심은 간단합니다. 뻔한 방식으로 시간 낭비하지 마시고, 전문가들이 검증한 이 지름길 공식 하나만 그대로 따라 해 보세요."
                },
                {
                    "badge": "👉 프로필 링크 확인",
                    "badge_color": (168, 85, 247),
                    "hero_line1": "상세 가이드 배포 중",
                    "hero_line2": "고정 댓글 링크 클릭!",
                    "accent": "고정 댓글 링크 클릭!",
                    "speech": "초보자도 1분 만에 따라 할 수 있는 상세 실행 매뉴얼은, 아래 고정 댓글 블로그 링크에 전부 정리해 뒀으니 지금 확인하세요!"
                }
            ]
        }


class ShortsVideoRenderer:
    """1080x1920 세로형 감성 무빙 캔버스 + 키네틱 타이포그래피 + Lo-Fi BGM 믹싱 렌더러"""

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
            self.font_badge = ImageFont.truetype(font_file, 38)
            self.font_hero = ImageFont.truetype(font_file, 68)
            self.font_accent = ImageFont.truetype(font_file, 74)
            self.font_sub = ImageFont.truetype(font_file, 44)
            self.font_cta = ImageFont.truetype(font_file, 34)
        else:
            self.font_badge = ImageFont.load_default()
            self.font_hero = ImageFont.load_default()
            self.font_accent = ImageFont.load_default()
            self.font_sub = ImageFont.load_default()
            self.font_cta = ImageFont.load_default()

    async def render_shorts(self, script_data: Dict, output_filepath: str) -> Dict:
        temp_dir = os.path.join(os.path.dirname(output_filepath), f"temp_{int(time.time()*1000)}")
        os.makedirs(temp_dir, exist_ok=True)

        # 1. Edge-TTS 음성 생성 (+12% 신속 쾌속 전달)
        audio_files = []
        scene_durations = []
        for idx, scene in enumerate(script_data["scenes"]):
            scene_audio = os.path.join(temp_dir, f"scene_{idx}.mp3")
            communicate = edge_tts.Communicate(scene["speech"], "ko-KR-SunHiNeural", rate="+12%")
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

        # 2. 감성 Lo-Fi BGM 배경음악 자동 믹싱 (BGM 18% 음량)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        lofi_bgm_path = os.path.join(base_dir, "assets", "audio", "lofi_beat.mp3")
        final_audio_path = merged_voice

        if os.path.exists(lofi_bgm_path):
            mixed_audio = os.path.join(temp_dir, "final_mixed.mp3")
            mix_cmd = [
                self.ffmpeg_exe, "-y",
                "-i", merged_voice,
                "-i", lofi_bgm_path,
                "-filter_complex", "[1:a]volume=0.18[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
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

        # 3. 비디오 렌더링 파이프라인
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

        proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        acc = 0
        cumulative_durations = []
        for d in scene_durations:
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

            # 캔버스 렌더링
            img = self._render_frame(scene, progress, current_time, current_scene_idx, len(script_data["scenes"]))
            proc.stdin.write(img.tobytes())

        proc.stdin.close()
        proc.communicate()

        # 임시 정리
        try:
            for f in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)
        except Exception:
            pass

        file_size_mb = os.path.getsize(output_filepath) / (1024 * 1024)
        print(f"✅ [감성 릴스 파이프라인] 1080x1920 MP4 영상 렌더링 완성! ({file_size_mb:.2f} MB, {total_duration:.1f}초)")

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

    def _render_frame(self, scene: Dict, progress: float, time_in_sec: float, scene_idx: int, total_scenes: int) -> Image.Image:
        # 1. 딥 앰비언트 다크 캔버스
        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), color=(15, 17, 26))
        draw = ImageDraw.Draw(img)

        # 부드럽게 움직이는 앰비언트 글로우 오브 (시각적 생동감)
        glow_x = int(540 + 180 * math.sin(time_in_sec * 0.8))
        glow_y = int(700 + 120 * math.cos(time_in_sec * 0.9))
        draw.ellipse([glow_x - 450, glow_y - 450, glow_x + 450, glow_y + 450], fill=(28, 25, 56))

        glow2_x = int(540 - 200 * math.cos(time_in_sec * 0.7))
        glow2_y = int(1200 + 100 * math.sin(time_in_sec * 0.6))
        draw.ellipse([glow2_x - 400, glow2_y - 400, glow2_x + 400, glow2_y + 400], fill=(20, 35, 60))

        # 2. 상단 네온 프로그레스 바 (0~100%)
        prog_w = int(self.WIDTH * progress)
        draw.rectangle([0, 0, prog_w, 10], fill=(244, 63, 94))

        # 3. 상단 바이럴 뱃지 (Pill Capsule)
        badge_color = scene.get("badge_color", (239, 68, 68))
        draw.rounded_rectangle([140, 240, 940, 330], radius=24, fill=(24, 24, 38), outline=badge_color, width=3)
        draw.text((self.WIDTH // 2, 285), scene.get("badge", ""), fill=(255, 255, 255), font=self.font_badge, anchor="mm")

        # 4. 중앙 무대: 시선 강탈 대형 히어로 텍스트 (Center Kinetic Hook)
        hero_y1 = 580
        hero_y2 = 680
        line1 = scene.get("hero_line1", "")
        line2 = scene.get("hero_line2", "")
        accent = scene.get("accent", "")

        # 그림자 효과
        for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 5)]:
            draw.text((self.WIDTH // 2 + ox, hero_y1 + oy), line1, fill=(0, 0, 0), font=self.font_hero, anchor="mm")
            draw.text((self.WIDTH // 2 + ox, hero_y2 + oy), line2, fill=(0, 0, 0), font=self.font_accent if line2 == accent else self.font_hero, anchor="mm")

        # 본문 텍스트 (강조 단어는 옐로우/사이언)
        draw.text((self.WIDTH // 2, hero_y1), line1, fill=(255, 255, 255), font=self.font_hero, anchor="mm")
        accent_color = (250, 204, 21) if line2 == accent else (255, 255, 255)
        draw.text((self.WIDTH // 2, hero_y2), line2, fill=accent_color, font=self.font_accent if line2 == accent else self.font_hero, anchor="mm")

        # 5. 하단 나레이션 자막 글래스 카드 (Clean Modern Glassmorphism Card)
        card_top = 1120
        card_bottom = 1480
        draw.rounded_rectangle([80, card_top, 1000, card_bottom], radius=36, fill=(18, 22, 36), outline=(99, 102, 241), width=3)

        speech = scene.get("speech", "")
        words = speech.split()
        lines = []
        curr = ""
        for w in words:
            if len(curr) + len(w) + 1 <= 15:
                curr = (curr + " " + w).strip()
            else:
                lines.append(curr)
                curr = w
        if curr:
            lines.append(curr)
        lines = lines[:4]

        line_h = 70
        start_y = card_top + (card_bottom - card_top - len(lines) * line_h) // 2 + 35
        for l_idx, line in enumerate(lines):
            ly = start_y + l_idx * line_h
            draw.text((self.WIDTH // 2, ly), line, fill=(241, 245, 249), font=self.font_sub, anchor="mm")

        # 6. 최하단 고정 CTA 배너 (Floating Pill)
        draw.rounded_rectangle([120, 1660, 960, 1760], radius=28, fill=(225, 29, 72), outline=(254, 205, 211), width=2)
        draw.text((self.WIDTH // 2, 1710), "📌 100% 무료 가이드는 프로필 링크 클릭!", fill=(255, 255, 255), font=self.font_cta, anchor="mm")

        return img


def generate_shorts_pipeline(topic: str, blog_url: str = "") -> Dict:
    """단일 진입점: 주제를 받아 20초 바이럴 릴스 MP4 영상과 메타데이터를 일괄 생성"""
    clean_topic = topic.strip() or "2026 정부 지원금 혜택 총정리"
    output_dir = os.path.join(os.getcwd(), "output", "shorts")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = int(time.time())
    safe_topic = re.sub(r'[\s\\/:*?"<>|]+', '_', clean_topic)[:20]
    output_filename = f"shorts_{safe_topic}_{timestamp}.mp4"
    output_filepath = os.path.join(output_dir, output_filename)

    # 1. 바이럴 스크립트 작성
    script_gen = ShortsScriptGenerator()
    script_data = script_gen.generate_script(clean_topic, blog_url)

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
