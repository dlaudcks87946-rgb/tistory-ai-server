#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[Tistory AI Corp] 40초 숏폼 영상(YouTube Shorts / Instagram Reels) 자동 제작 파이프라인
- 블로그 원고 & 키워드 기반 5단계 숏폼 대본(Hook - Point - Caution - Tip - CTA) 자동 생성
- Edge-TTS 고음질 한국어 AI 성우 음성(ko-KR-SunHiNeural) 합성
- 1080x1920 9:16 버티컬 고화질 인포그래픽 슬라이드 & 자막 프레임 렌더링
- FFmpeg 파이프라인을 통한 초고속 MP4 인코딩 및 메타데이터(제목, 태그, 고정댓글) 자동 생성
"""

import os
import sys
import time
import json
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
    """주제 및 블로그 내용을 숏폼 5단계 황금 구조(40~45초)로 변환하는 스크립트 엔진"""

    @staticmethod
    def generate_script(topic: str, blog_url: str = "") -> Dict:
        clean_topic = topic.strip()

        # 기본 스크립트 템플릿 (다양한 주제에 맞춤 적응)
        if "바우처" in clean_topic or "첫만남" in clean_topic or "지원금" in clean_topic or "청년" in clean_topic:
            return {
                "title": f"🚨 {clean_topic[:26]} 40초 핵심 총정리! #shorts",
                "tags": ["정부지원금", "바우처", "생활꿀팁", "혜택", "shorts"],
                "pinned_comment": f"📌 상세 잔액 조회 및 온라인 사용처 총정리 블로그 글 확인하기 👉 {blog_url or 'https://tistory.com'}",
                "scenes": [
                    {
                        "badge": "🚨 긴급 지원금 공지",
                        "badge_color": (239, 68, 68),
                        "heading": "기한 지나면 전액 소멸?",
                        "subheading": clean_topic[:28],
                        "points": ["✔ 신청 후 방치 시 국고 환수", "✔ 출생/선정일로부터 사용 기한 엄수"],
                        "speech": f"혹시 {clean_topic[:20]} 지원금을 신청해 두고 그냥 잊고 계신가요? 사용 기한을 넘기면 남은 잔액이 전액 자동 소멸됩니다!"
                    },
                    {
                        "badge": "📍 오프라인 핵심 사용처",
                        "badge_color": (59, 130, 246),
                        "heading": "어디서 현금처럼 쓸까?",
                        "subheading": "생활 밀착형 사용처",
                        "points": ["✔ 병원, 의원, 약국 결제 가능", "✔ 대형마트(이마트, 홈플러스, 롯데마트)", "✔ 백화점 및 유아/생활 매장"],
                        "speech": "바우처 지원금은 병원과 약국은 물론, 대형마트와 백화점 등 일상생활 매장에서 일반 카드처럼 바로 긁어서 결제할 수 있습니다."
                    },
                    {
                        "badge": "⚠️ 절대 결제 불가 업종",
                        "badge_color": (245, 158, 11),
                        "heading": "여기서는 결제 거절됩니다!",
                        "subheading": "주의해야 할 제한 업종",
                        "points": ["✖ 유흥업소 및 사행성 매장", "✖ 상품권, 골드바, 복권 구매", "✖ 국세, 지방세 등 세금 납부 불가"],
                        "speech": "주의할 점도 있습니다. 유흥업소나 사행성 시설, 상품권 구매, 세금 납부에는 승인이 즉시 거절되니 헛걸음하지 않도록 유의하세요."
                    },
                    {
                        "badge": "💡 200% 활용 꿀팁",
                        "badge_color": (168, 85, 247),
                        "heading": "온라인에서도 결제 가능!",
                        "subheading": "집에서 편하게 배달/쇼핑",
                        "points": ["✔ 쿠팡, 배달의민족 간편결제 등록", "✔ 분유, 기저귀, 생필품 로켓배송 주문"],
                        "speech": "특히 쿠팡이나 배달의민족 같은 온라인 앱에서도 국민행복카드를 간편결제에 등록해 두면 집에서 편하게 주문할 수 있습니다!"
                    },
                    {
                        "badge": "👉 블로그 바로가기",
                        "badge_color": (16, 185, 129),
                        "heading": "자세한 신청법 & 잔액조회",
                        "subheading": "고정 댓글 링크 클릭!",
                        "points": ["✔ 실시간 남은 잔액 1초 확인", "✔ 온라인 제휴처 전체 리스트"],
                        "speech": "내 카드에 남은 잔액 실시간 조회 방법과 온라인 등록 상세 가이드는, 아래 고정 댓글 블로그 링크에서 지금 바로 확인해 보세요!"
                    }
                ]
            }

        # 일반 IT/테크/생활 정보형 템플릿
        return {
            "title": f"💡 {clean_topic[:26]} 40초 핵심 가이드 #shorts",
            "tags": ["생활꿀팁", "정보", "꿀팁", "shorts"],
            "pinned_comment": f"📌 더 자세한 상세 가이드 및 꿀팁 블로그 글 바로가기 👉 {blog_url or 'https://tistory.com'}",
            "scenes": [
                {
                    "badge": "🚨 10초 핵심 요약",
                    "badge_color": (239, 68, 68),
                    "heading": "이것 모르면 무조건 손해!",
                    "subheading": clean_topic[:28],
                    "points": ["✔ 알아두면 평생 써먹는 필수 팁", "✔ 40초 만에 완벽 정리"],
                    "speech": f"아직도 {clean_topic[:22]}에 대해 제대로 모르고 계셨나요? 40초 만에 핵심만 쏙쏙 뽑아 정리해 드립니다!"
                },
                {
                    "badge": "📍 필수 핵심 포인트 1",
                    "badge_color": (59, 130, 246),
                    "heading": "가장 중요한 첫 번째 원칙",
                    "subheading": "효율 200% 극대화",
                    "points": ["✔ 복잡한 절차 없이 간편 적용", "✔ 전문가들이 검증한 핵심 노하우"],
                    "speech": "첫 번째로 가장 중요한 것은 정확한 기준과 타이밍입니다. 잘못된 방식으로 접근하면 시간과 비용을 낭비하기 쉽습니다."
                },
                {
                    "badge": "⚠️ 반드시 피해야 할 실수",
                    "badge_color": (245, 158, 11),
                    "heading": "초보자들이 가장 많이 하는 실수",
                    "subheading": "체크리스트 확인 필수",
                    "points": ["✖ 무작정 따라하기 금지", "✖ 공인 가이드라인 미준수"],
                    "speech": "두 번째로 흔히 저지르는 실수를 피해야 합니다. 기본적인 가이드라인을 지키지 않으면 기대했던 결과를 얻기 어렵습니다."
                },
                {
                    "badge": "💡 전문가 실전 시크릿",
                    "badge_color": (168, 85, 247),
                    "heading": "상위 1%가 몰래 쓰는 팁",
                    "subheading": "결과를 바꾸는 핵심 디테일",
                    "points": ["✔ 즉각적인 피드백 적용", "✔ 자동화 및 시간 단축 최적화"],
                    "speech": "상위 전문가들이 활용하는 숨은 꿀팁을 적용하면, 같은 시간과 노력을 들이고도 두 배 이상의 성과를 만들 수 있습니다."
                },
                {
                    "badge": "👉 블로그 원문 바로가기",
                    "badge_color": (16, 185, 129),
                    "heading": "상세 가이드 & 서식 무료 제공",
                    "subheading": "고정 댓글 링크 클릭!",
                    "points": ["✔ 초보자용 단계별 체크리스트", "✔ 1초 바로가기 링크 제공"],
                    "speech": "더 자세한 단계별 실행 가이드와 무료 서식은, 아래 고정 댓글 블로그 링크에서 1초 만에 확인해 보세요!"
                }
            ]
        }


class ShortsVideoRenderer:
    """Pillow 프레임 렌더링 + FFmpeg 고화질 1080x1920 MP4 렌더러"""

    WIDTH = 1080
    HEIGHT = 1920
    FPS = 24

    def __init__(self, font_name: str = "malgunbd.ttf"):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        font_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
        font_path = os.path.join(font_dir, font_name)
        if not os.path.exists(font_path):
            font_path = os.path.join(font_dir, "malgun.ttf")

        try:
            self.font_badge = ImageFont.truetype(font_path, 36)
            self.font_heading = ImageFont.truetype(font_path, 58)
            self.font_subheading = ImageFont.truetype(font_path, 40)
            self.font_point = ImageFont.truetype(font_path, 42)
            self.font_subtitle = ImageFont.truetype(font_path, 46)
            self.font_brand = ImageFont.truetype(font_path, 32)
        except Exception:
            self.font_badge = ImageFont.load_default()
            self.font_heading = ImageFont.load_default()
            self.font_subheading = ImageFont.load_default()
            self.font_point = ImageFont.load_default()
            self.font_subtitle = ImageFont.load_default()
            self.font_brand = ImageFont.load_default()

    async def render_shorts(self, script_data: Dict, output_filepath: str) -> Dict:
        temp_dir = os.path.join(os.path.dirname(output_filepath), "temp_" + str(int(time.time())))
        os.makedirs(temp_dir, exist_ok=True)

        scene_audio_files = []
        scene_durations = []

        # 1. Edge-TTS 음성 생성 및 오디오 길이 측정
        for idx, scene in enumerate(script_data["scenes"]):
            scene_audio_path = os.path.join(temp_dir, f"scene_{idx}.mp3")
            tts = edge_tts.Communicate(scene["speech"], 'ko-KR-SunHiNeural', rate='+8%')
            await tts.save(scene_audio_path)
            scene_audio_files.append(scene_audio_path)

            # ffmpeg로 오디오 길이 측정
            cmd = [self.ffmpeg_exe, '-i', scene_audio_path]
            proc = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors='replace')
            match = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.\d+)', proc.stderr)
            if match:
                h, m, s = match.groups()
                dur = float(h) * 3600 + float(m) * 60 + float(s)
            else:
                dur = 7.0
            scene_durations.append(dur)

        total_duration = sum(scene_durations)
        print(f"🎬 [숏폼 파이프라인] 총 5개 씬 오디오 합성 완료 (총 재생 시간: {total_duration:.1f}초)")

        # 2. 전체 오디오 파일 하나로 병합 (ffmpeg concat)
        concat_list_path = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for fpath in scene_audio_files:
                clean_fpath = fpath.replace("\\", "/")
                f.write(f"file '{clean_fpath}'\n")

        merged_audio_path = os.path.join(temp_dir, "merged_audio.mp3")
        subprocess.run([
            self.ffmpeg_exe, '-y', '-f', 'concat', '-safe', '0',
            '-i', concat_list_path, '-c', 'copy', merged_audio_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 3. 비디오 인코딩 파이프 준비
        total_frames = int(total_duration * self.FPS) + 5
        cmd_ffmpeg = [
            self.ffmpeg_exe,
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f"{self.WIDTH}x{self.HEIGHT}",
            '-pix_fmt', 'rgb24',
            '-r', str(self.FPS),
            '-i', '-',
            '-i', merged_audio_path,
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',
            output_filepath
        ]

        proc = subprocess.Popen(cmd_ffmpeg, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

        # 4. 프레임 렌더링 루프
        current_time = 0.0
        frame_duration = 1.0 / self.FPS

        cumulative_durations = []
        acc = 0.0
        for d in scene_durations:
            acc += d
            cumulative_durations.append(acc)

        for frame_idx in range(total_frames):
            current_time = frame_idx * frame_duration
            progress = min(1.0, current_time / total_duration)

            # 현재 씬 찾기
            current_scene_idx = 0
            for idx, cum_d in enumerate(cumulative_durations):
                if current_time <= cum_d:
                    current_scene_idx = idx
                    break
            else:
                current_scene_idx = len(script_data["scenes"]) - 1

            scene = script_data["scenes"][current_scene_idx]

            # 캔버스 렌더링
            img = self._render_frame(scene, progress, current_scene_idx, len(script_data["scenes"]))
            proc.stdin.write(img.tobytes())

        proc.stdin.close()
        stdout, stderr = proc.communicate()

        # 임시 오디오 파일 정리
        try:
            for f in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)
        except Exception:
            pass

        if proc.returncode != 0:
            err_msg = stderr.decode('utf-8', errors='replace')
            raise RuntimeError(f"FFmpeg encoding error: {err_msg[:400]}")

        file_size_mb = os.path.getsize(output_filepath) / (1024 * 1024)
        print(f"✅ [숏폼 파이프라인] 1080x1920 MP4 영상 렌더링 완성! ({file_size_mb:.2f} MB, {total_duration:.1f}초)")

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

    def _render_frame(self, scene: Dict, progress: float, scene_idx: int, total_scenes: int) -> Image.Image:
        # 배경: 다크 인디고 & 사이버펑크 그래디언트
        img = Image.new('RGB', (self.WIDTH, self.HEIGHT), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)

        # 배경 앰비언트 글로우 원형
        glow_colors = [(30, 27, 75), (49, 46, 129), (30, 41, 59)]
        draw.ellipse([-200, -200, 1280, 800], fill=glow_colors[scene_idx % len(glow_colors)])

        # 1. 상단 브랜드 채널 헤더
        draw.rectangle([60, 100, 1020, 180], fill=(30, 41, 59), outline=(99, 102, 241), width=2)
        draw.text((1080 // 2, 140), "✨ Tistory AI Corp | 40초 숏폼 지식 저장소", fill=(199, 210, 254), font=self.font_brand, anchor="mm")

        # 2. 메인 인포그래픽 카드 (Glassmorphism 3D Card)
        card_top = 240
        card_bottom = 1420
        draw.rounded_rectangle([60, card_top, 1020, card_bottom], radius=44, fill=(24, 32, 53), outline=(129, 140, 248), width=5)

        # 3. 씬 카테고리 뱃지
        badge_bg = scene.get("badge_color", (236, 72, 153))
        badge_text = scene.get("badge", "💡 핵심 요약")
        draw.rounded_rectangle([120, card_top + 50, 960, card_top + 130], radius=24, fill=badge_bg)
        draw.text((1080 // 2, card_top + 90), badge_text, fill=(255, 255, 255), font=self.font_badge, anchor="mm")

        # 4. 헤딩 타이틀
        draw.text((1080 // 2, card_top + 200), scene.get("heading", ""), fill=(254, 240, 138), font=self.font_heading, anchor="mm")
        draw.text((1080 // 2, card_top + 280), scene.get("subheading", ""), fill=(226, 232, 240), font=self.font_subheading, anchor="mm")

        # 5. 핵심 포인트 박스 (체크리스트)
        box_top = card_top + 360
        box_bottom = card_bottom - 60
        draw.rounded_rectangle([100, box_top, 980, box_bottom], radius=32, fill=(15, 23, 42), outline=(56, 189, 248), width=3)

        points = scene.get("points", [])
        start_y = box_top + 70
        spacing = 130
        for p_idx, pt in enumerate(points):
            y = start_y + p_idx * spacing
            color = (52, 211, 153) if "✔" in pt else ((248, 113, 113) if "✖" in pt else (255, 255, 255))
            draw.text((1080 // 2, y), pt, fill=color, font=self.font_point, anchor="mm")

        # 6. 하단 자막(Subtitle) 박스 (네온 골드 하이라이트)
        sub_box_top = 1460
        sub_box_bottom = 1760
        draw.rounded_rectangle([60, sub_box_top, 1020, sub_box_bottom], radius=36, fill=(17, 24, 39), outline=(251, 191, 36), width=4)

        # 씬 나레이션 자막 텍스트 줄바꿈 렌더링
        speech = scene.get("speech", "")
        # 한 줄당 약 20자 내외로 분할
        lines = []
        words = speech.split()
        curr_line = ""
        for w in words:
            if len(curr_line) + len(w) + 1 <= 18:
                curr_line = (curr_line + " " + w).strip()
            else:
                lines.append(curr_line)
                curr_line = w
        if curr_line:
            lines.append(curr_line)

        # 최대 3줄까지만 자막 박스에 큼직하게 렌더링
        lines = lines[:3]
        total_text_h = len(lines) * 65
        text_start_y = sub_box_top + (sub_box_bottom - sub_box_top - total_text_h) // 2 + 30
        for l_idx, line in enumerate(lines):
            ly = text_start_y + l_idx * 65
            draw.text((1080 // 2, ly), line, fill=(255, 255, 255), font=self.font_subtitle, anchor="mm")

        # 7. 최하단 실시간 프로그레스 바 (핑크 & 사이언 그라데이션)
        bar_w = int(960 * progress)
        draw.rectangle([60, 1850, 60 + bar_w, 1872], fill=(236, 72, 153))

        # 씬 번호 표시
        scene_indicator = f"STEP {scene_idx + 1} / {total_scenes}"
        draw.text((1080 // 2, 1815), scene_indicator, fill=(148, 163, 184), font=self.font_brand, anchor="mm")

        return img


def generate_shorts_pipeline(topic: str, blog_url: str = "") -> Dict:
    """단일 진입점: 주제를 받아 40초 숏폼 MP4 영상과 메타데이터를 일괄 생성"""
    clean_topic = topic.strip() or "2026 정부 지원금 혜택 총정리"
    output_dir = os.path.join(os.getcwd(), "output", "shorts")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = int(time.time())
    safe_topic = re.sub(r'[\s\\/:*?"<>|]+', '_', clean_topic)[:20]
    output_filename = f"shorts_{safe_topic}_{timestamp}.mp4"
    output_filepath = os.path.join(output_dir, output_filename)

    # 1. 숏폼 스크립트 작성
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
    parser = argparse.ArgumentParser(description="Tistory AI 숏폼 영상 자동 제작 파이프라인")
    parser.add_argument("--topic", type=str, default="국민행복카드 바우처 혜택 총정리: 첫만남이용권 200만원 사용처", help="영상 제작 주제")
    parser.add_argument("--url", type=str, default="https://your-blog.tistory.com", help="유입용 블로그 포스팅 URL")
    args = parser.parse_args()

    print(f"\n=======================================================")
    print(f"🎬 [Tistory AI Corp] 숏폼(Shorts/Reels) 영상 제작 시작")
    print(f"주제: {args.topic}")
    print(f"=======================================================\n")

    res = generate_shorts_pipeline(args.topic, args.url)

    print(f"\n🎉 숏폼 영상 제작 완료!")
    print(f"📁 파일 경로: {res['filepath']}")
    print(f"⏱️ 재생 시간: {res['duration']}초 | 용량: {res['size_mb']} MB")
    print(f"🏷️ 추천 제목: {res['title']}")
    print(f"📌 고정 댓글: {res['pinned_comment']}")
    print(f"=======================================================\n")
