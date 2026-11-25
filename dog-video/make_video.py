"""강아지 산책 애니메이션 동영상 만들기.

그림(프레임)을 한 장씩 그린 뒤 ffmpeg로 이어 붙여 mp4 파일을 만듭니다.
실행: python3 dog-video/make_video.py
결과: dog-video/dog.mp4
"""

import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720          # 최종 영상 크기
SS = 2                    # 2배로 크게 그린 뒤 줄여서 테두리를 부드럽게
FPS = 30
SECONDS = 9
GROUND = 560              # 땅 높이(y)

OUT = Path(__file__).with_name("dog.mp4")
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

FUR = (226, 172, 108)
FUR_LIGHT = (246, 222, 186)
FUR_DARK = (150, 98, 58)
INK = (40, 30, 30)


def font(size):
    return ImageFont.truetype(FONT_PATH, size * SS)


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


class Canvas:
    """SS배 크기로 그려 주는 작은 도우미."""

    def __init__(self):
        self.img = Image.new("RGB", (W * SS, H * SS))
        self.d = ImageDraw.Draw(self.img)

    def ellipse(self, cx, cy, rx, ry, fill, outline=None, width=0):
        self.d.ellipse(
            [(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS],
            fill=fill, outline=outline, width=width * SS,
        )

    def line(self, x1, y1, x2, y2, fill, width):
        self.d.line([x1 * SS, y1 * SS, x2 * SS, y2 * SS], fill=fill, width=width * SS)
        r = width / 2
        self.ellipse(x1, y1, r, r, fill)
        self.ellipse(x2, y2, r, r, fill)

    def polygon(self, pts, fill):
        self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=fill)

    def text_center(self, text, cx, cy, size, fill, stroke=None):
        f = font(size)
        self.d.text(
            (cx * SS, cy * SS), text, font=f, fill=fill, anchor="mm",
            stroke_width=(4 * SS if stroke else 0), stroke_fill=stroke,
        )

    def result(self):
        return self.img.resize((W, H), Image.LANCZOS)


def draw_background(c, t):
    # 하늘 그라데이션
    for y in range(0, GROUND, 4):
        k = y / GROUND
        col = (int(120 + 90 * k), int(190 + 45 * k), int(250 - 10 * k))
        c.d.rectangle([0, y * SS, W * SS, (y + 4) * SS], fill=col)
    # 해
    c.ellipse(1100, 120, 70, 70, (255, 236, 140))
    c.ellipse(1100, 120, 55, 55, (255, 214, 80))
    # 구름 (천천히 이동)
    for i, (bx, by, s) in enumerate([(150, 110, 1.0), (600, 80, 0.8), (950, 200, 0.7)]):
        x = (bx + t * (18 + 6 * i)) % (W + 300) - 150
        for dx, dy, r in [(0, 0, 40), (45, 10, 32), (-45, 10, 32), (20, -20, 30)]:
            c.ellipse(x + dx * s, by + dy * s, r * s * 1.3, r * s, (255, 255, 255))
    # 언덕
    c.ellipse(250, GROUND + 60, 420, 160, (128, 196, 108))
    c.ellipse(1000, GROUND + 80, 520, 190, (112, 184, 96))
    # 잔디
    c.d.rectangle([0, GROUND * SS, W * SS, H * SS], fill=(98, 170, 80))
    for i in range(0, W, 26):
        h = 10 + (i * 7) % 12
        c.line(i, GROUND + 6, i + 4, GROUND + 6 - h, (80, 150, 64), 3)
    # 꽃
    for fx, fy, col in [(120, 640, (255, 120, 150)), (420, 690, (255, 220, 90)),
                        (880, 650, (255, 255, 255)), (1180, 700, (255, 140, 120))]:
        for a in range(5):
            ang = a * 2 * math.pi / 5
            c.ellipse(fx + 9 * math.cos(ang), fy + 9 * math.sin(ang), 7, 7, col)
        c.ellipse(fx, fy, 5, 5, (255, 200, 40))


def draw_dog(c, x, y, walk_phase, tail_speed, t, happy, squash=1.0):
    """옆을 보고 있는 강아지. (x, y)는 발이 땅에 닿는 기준점."""
    swing = math.sin(walk_phase)
    by = y - 70 * squash  # 몸통 중심 높이

    # 그림자
    c.ellipse(x, GROUND + 4, 90, 12, (70, 130, 60))

    # 꼬리 (흔들기)
    ang = math.radians(55 + 25 * math.sin(t * tail_speed))
    tx, ty = x - 68, by - 10
    c.line(tx, ty, tx - 45 * math.cos(ang), ty - 45 * math.sin(ang), FUR_DARK, 14)

    # 뒤쪽 다리 (조금 어둡게)
    for lx, ph in [(-45, 1), (40, -1)]:
        dx = 14 * swing * ph
        c.line(x + lx + 8, by + 20, x + lx + 8 - dx, y - 6, FUR_DARK, 18)
    # 몸통
    c.ellipse(x, by, 80, 42 * squash, FUR)
    c.ellipse(x + 10, by + 14, 50, 22 * squash, FUR_LIGHT)
    # 앞쪽 다리
    for lx, ph in [(-50, -1), (35, 1)]:
        dx = 14 * swing * ph
        c.line(x + lx, by + 20, x + lx - dx, y - 6, FUR, 18)
        c.ellipse(x + lx - dx + 3, y - 4, 13, 7, FUR_LIGHT)

    # 머리
    hx, hy = x + 78, by - 52 + 3 * math.sin(walk_phase * 2)
    c.ellipse(hx, hy, 46, 44, FUR)
    # 목걸이
    c.line(hx - 34, hy + 34, hx - 6, hy + 44, (220, 50, 60), 10)
    c.ellipse(hx - 14, hy + 52, 7, 7, (255, 210, 60))
    # 주둥이
    c.ellipse(hx + 38, hy + 14, 28, 20, FUR_LIGHT)
    c.ellipse(hx + 62, hy + 6, 10, 8, INK)          # 코
    c.ellipse(hx + 59, hy + 3, 3, 2, (120, 110, 110))
    c.line(hx + 44, hy + 24, hx + 56, hy + 22, INK, 3)  # 입
    if happy:
        c.ellipse(hx + 44, hy + 34, 9, 12, (240, 110, 130))  # 혀
        c.line(hx + 44, hy + 28, hx + 44, hy + 40, (210, 80, 100), 2)
    # 눈 (가끔 깜빡임)
    blink = (t % 3.0) < 0.12
    if blink:
        c.line(hx + 12, hy - 10, hx + 26, hy - 10, INK, 4)
    else:
        c.ellipse(hx + 19, hy - 10, 7, 8, INK)
        c.ellipse(hx + 21, hy - 13, 2.5, 2.5, (255, 255, 255))
    # 볼터치
    c.ellipse(hx + 14, hy + 12, 9, 6, (245, 160, 150))
    # 귀 (축 늘어진 귀, 살짝 흔들림)
    ear = 6 * math.sin(walk_phase + 1)
    c.polygon([(hx - 30, hy - 32), (hx - 2, hy - 40), (hx - 10 + ear, hy + 18),
               (hx - 34 + ear, hy + 8)], FUR_DARK)
    c.ellipse(hx - 22 + ear, hy + 12, 13, 9, FUR_DARK)


def draw_heart(c, x, y, s, col=(255, 90, 120)):
    c.ellipse(x - 9 * s, y - 5 * s, 10 * s, 10 * s, col)
    c.ellipse(x + 9 * s, y - 5 * s, 10 * s, 10 * s, col)
    c.polygon([(x - 18.5 * s, y - 1 * s), (x + 18.5 * s, y - 1 * s), (x, y + 20 * s)], col)


def draw_bubble(c, x, y, text):
    c.ellipse(x, y, 90, 48, (255, 255, 255), outline=INK, width=3)
    c.polygon([(x - 50, y + 30), (x - 25, y + 40), (x - 75, y + 70)], (255, 255, 255))
    c.text_center(text, x, y, 40, INK)


def frame(t):
    c = Canvas()
    draw_background(c, t)

    center = 560
    happy = False
    squash = 1.0
    jump = 0.0
    tail_speed = 10

    if t < 4.0:                         # 1) 걸어 들어오기
        x = -150 + (center + 150) * ease(t / 4.0)
        walk = t * 9 * (1 - ease((t - 3.2) / 0.8) * 0.9)
    elif t < 5.5:                       # 2) 멈춰서 꼬리 흔들기
        x, walk, happy, tail_speed = center, 0, True, 22
    elif t < 6.6:                       # 3) 신나서 점프
        x, walk, happy, tail_speed = center, 0, True, 26
        k = (t - 5.5) / 1.1
        jump = 4 * k * (1 - k) * 150
        squash = 0.9 if k < 0.08 or k > 0.92 else 1.05
    else:                               # 4) 인사
        x, walk, happy, tail_speed = center, 0, True, 18

    draw_dog(c, x, GROUND - jump, walk, tail_speed, t, happy, squash)

    # 말풍선
    if 4.2 < t < 5.6:
        draw_bubble(c, center + 220, 300, "멍멍!")
    # 하트
    if t > 5.6:
        for i, (ox, delay) in enumerate([(-40, 0), (60, 0.25), (150, 0.5)]):
            k = (t - 5.6 - delay) / 2.2
            if 0 < k < 1:
                draw_heart(c, center + 80 + ox + 12 * math.sin(k * 8 + i),
                           380 - 220 * k, 0.8 + 0.6 * k)
    # 제목
    if t < 2.2:
        if t < 1.9:
            c.text_center("멍멍이의 산책", W / 2, 140, 72, (255, 255, 255), stroke=(90, 60, 40))
    # 마지막 인사 문구
    if t > 6.8:
        c.text_center("안녕! 나는 멍멍이야", W / 2, 120, 64, (255, 255, 255), stroke=(90, 60, 40))
    return c.result()


def main():
    total = FPS * SECONDS
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart",
        str(OUT),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(total):
        proc.stdin.write(frame(i / FPS).tobytes())
    proc.stdin.close()
    proc.wait()
    print(f"완료: {OUT}")


if __name__ == "__main__":
    main()
