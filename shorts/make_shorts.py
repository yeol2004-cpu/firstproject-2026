"""산곡역자이힐스테이트&하늘채 홍보용 숏폼(릴스) 5편 생성기.

사용법:
    python3 shorts/make_shorts.py          # 5편 모두 생성
    python3 shorts/make_shorts.py 2        # 2번 영상만 생성

결과물: shorts/output/*.mp4 (1080x1920, 30fps, 세로형)
"""

import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ─────────────────────────────────────────────
# 1. 기본 설정 (여기만 바꿔도 전체 영상에 반영돼요)
# ─────────────────────────────────────────────
COMPLEX_NAME = "산곡역자이힐스테이트&하늘채"
CONTACT = "분양 상담 ☎ 0000-0000"  # ← 실제 상담 번호로 바꿔주세요
MODEL_HOUSE = "견본주택 · 인천 부평구 산곡동 43-2"
DISCLAIMER = (
    "※ 본 영상은 이해를 돕기 위한 홍보물로 실제와 다를 수 있으며,\n"
    "세부 내용은 반드시 입주자모집공고를 확인하시기 바랍니다."
)

W, H, FPS = 1080, 1920, 30
OUT_DIR = Path(__file__).parent / "output"

FONT_DIR = "/usr/share/fonts/opentype/noto/"
BOLD = (FONT_DIR + "NotoSansCJK-Bold.ttc", 1)
REGULAR = (FONT_DIR + "NotoSansCJK-Regular.ttc", 1)

NAVY_TOP = (9, 24, 48)
NAVY_BOTTOM = (22, 56, 102)
GOLD = (232, 194, 122)
WHITE = (255, 255, 255)
SOFT = (201, 211, 227)

# 각 줄 스타일: (폰트, 크기, 색, 아래 여백)
STYLES = {
    "kicker": (BOLD, 54, GOLD, 34),
    "title": (BOLD, 118, WHITE, 40),
    "body": (REGULAR, 50, SOFT, 26),
    "note": (REGULAR, 34, SOFT, 20),
    "count": (BOLD, 210, GOLD, 10),
}

# ─────────────────────────────────────────────
# 2. 영상 5편의 내용
#    장면(scene)마다 길이(초)와 보여줄 줄(items)을 적어요.
# ─────────────────────────────────────────────
VIDEOS = [
    {
        "file": "01_station.mp4",
        "tag": "#1 초역세권",
        "scenes": [
            {"dur": 3.0, "items": [("kicker", "출퇴근 스트레스, 이제 그만"),
                                   ("title", "문 열고 나가면\n바로 지하철")]},
            {"dur": 3.4, "items": [("kicker", "지하철 7호선"),
                                   ("title", "산곡역\n초역세권"),
                                   ("body", "산곡역 5·6번 출구 바로 앞")]},
            {"dur": 3.4, "items": [("kicker", "환승 없이 한 번에"),
                                   ("title", "7호선 타고\n강남권까지"),
                                   ("body", "청라 연장선 개통 예정")]},
        ],
    },
    {
        "file": "02_scale.mp4",
        "tag": "#2 매머드급 대단지",
        "scenes": [
            {"dur": 2.8, "items": [("kicker", "인천 부평구 산곡동"),
                                   ("title", "이 규모,\n실화인가요?")]},
            {"dur": 3.2, "items": [("kicker", "총 세대수"),
                                   ("count", 2706, "세대"),
                                   ("body", "산곡6구역 재개발 대단지")]},
            {"dur": 3.0, "items": [("kicker", "단지 규모"),
                                   ("title", "20개 동\n최고 33층"),
                                   ("body", "지하 3층 ~ 지상 33층")]},
            {"dur": 3.6, "items": [("kicker", "대형 건설사 3곳이 함께"),
                                   ("title", "3개 브랜드\n한 단지에"),
                                   ("chips", ["GS건설 자이", "현대건설 힐스테이트",
                                              "코오롱글로벌 하늘채"])]},
        ],
    },
    {
        "file": "03_design.mp4",
        "tag": "#3 특화 설계",
        "scenes": [
            {"dur": 2.8, "items": [("kicker", "집은 결국 구조입니다"),
                                   ("title", "살아보면 아는\n설계의 차이")]},
            {"dur": 3.2, "items": [("kicker", "다양한 선택지"),
                                   ("title", "전용\n50~84㎡"),
                                   ("body", "신혼부부부터 4인 가족까지")]},
            {"dur": 3.0, "items": [("kicker", "햇살 가득"),
                                   ("title", "남향 위주\n단지 배치")]},
            {"dur": 3.6, "items": [("kicker", "공간을 넓히는"),
                                   ("title", "특화 설계"),
                                   ("chips", ["4베이", "팬트리", "드레스룸"]),
                                   ("note", "*일부 타입 적용")]},
        ],
    },
    {
        "file": "04_lifestyle.mp4",
        "tag": "#4 단지 라이프",
        "scenes": [
            {"dur": 3.2, "items": [("kicker", "아이 키우는 집이라면"),
                                   ("title", "차 없는\n공원형 단지"),
                                   ("body", "지상에 차가 다니지 않는 설계")]},
            {"dur": 3.8, "items": [("kicker", "멀리 갈 필요 없이"),
                                   ("title", "단지 안에서\n누리는 일상"),
                                   ("chips", ["피트니스", "골프연습장", "사우나",
                                              "게스트하우스", "카페라운지"])]},
            {"dur": 3.2, "items": [("kicker", "자연과 학교를 가까이"),
                                   ("title", "원적산공원\n가까운 숲세권"),
                                   ("body", "초·중·고교가 가까운 입지")]},
        ],
    },
    {
        "file": "05_summary.mp4",
        "tag": "#5 한눈에 정리",
        "scenes": [
            {"dur": 2.8, "items": [("kicker", "산곡동이 바뀝니다"),
                                   ("title", "15초 만에\n핵심 정리")]},
            {"dur": 4.2, "items": [("kicker", "이 단지를 봐야 하는 이유"),
                                   ("checks", ["7호선 산곡역 초역세권",
                                               "총 2,706세대 대단지",
                                               "자이·힐스테이트·하늘채",
                                               "전용 50~84㎡ 다양한 평면",
                                               "차 없는 공원형 단지"])]},
            {"dur": 3.0, "items": [("kicker", "입주 예정"),
                                   ("title", "2029년\n12월")]},
        ],
    },
]

END_CARD_DUR = 4.0
FADE_OUT = 0.3


# ─────────────────────────────────────────────
# 3. 그리기 도구
# ─────────────────────────────────────────────
_font_cache = {}


def font(spec, size):
    key = (spec, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(spec[0], size, index=spec[1])
    return _font_cache[key]


def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def text_block(text, spec, size, color, max_w=940, align="center"):
    """여러 줄 텍스트를 투명 배경 이미지로 만든다. 너무 넓으면 글자 크기를 줄인다."""
    while True:
        f = font(spec, size)
        lines = text.split("\n")
        widths = [f.getbbox(l)[2] - f.getbbox(l)[0] for l in lines]
        if max(widths) <= max_w or size <= 20:
            break
        size -= 4
    line_h = int(size * 1.22)
    img = Image.new("RGBA", (max(widths) + 20, line_h * len(lines) + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, (l, w) in enumerate(zip(lines, widths)):
        x = (img.width - w) // 2 if align == "center" else 0
        d.text((x - f.getbbox(l)[0] + 10 if align != "center" else x, i * line_h),
               l, font=f, fill=color)
    return img


def chips_block(labels):
    """둥근 배지 여러 개를 줄바꿈하며 배치한다."""
    f = font(BOLD, 44)
    pad_x, pad_y, gap, chip_h = 34, 18, 18, 44 + 18 * 2 + 8
    sizes = [f.getbbox(t)[2] - f.getbbox(t)[0] + pad_x * 2 for t in labels]
    rows, row, row_w = [], [], 0
    for lab, w in zip(labels, sizes):
        if row and row_w + gap + w > 960:
            rows.append(row)
            row, row_w = [], 0
        row.append((lab, w))
        row_w += w + (gap if len(row) > 1 else 0)
    rows.append(row)
    img = Image.new("RGBA", (980, len(rows) * (chip_h + gap)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for r, row in enumerate(rows):
        total = sum(w for _, w in row) + gap * (len(row) - 1)
        x = (980 - total) // 2
        y = r * (chip_h + gap)
        for lab, w in row:
            d.rounded_rectangle([x, y, x + w, y + chip_h], radius=chip_h // 2,
                                fill=(232, 194, 122, 38), outline=GOLD, width=3)
            d.text((x + pad_x, y + pad_y - 6), lab, font=f, fill=WHITE)
            x += w + gap
    return img


def checks_block(labels):
    """금색 체크 표시가 붙은 목록."""
    f = font(BOLD, 52)
    row_h = 104
    img = Image.new("RGBA", (960, row_h * len(labels)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, lab in enumerate(labels):
        y = i * row_h
        cx, cy, r = 70, y + 42, 30
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD)
        d.line([(cx - 14, cy + 1), (cx - 3, cy + 12), (cx + 15, cy - 11)],
               fill=NAVY_TOP, width=7, joint="curve")
        d.text((130, y + 8), lab, font=f, fill=WHITE)
    return img


def with_alpha(img, a):
    if a >= 0.999:
        return img
    out = img.copy()
    alpha = out.getchannel("A").point(lambda v: int(v * a))
    out.putalpha(alpha)
    return out


def make_background():
    """그라데이션 + 은은한 빛 + 아래쪽 도시 실루엣 (특정 단지를 그린 것이 아닌 일반 이미지)."""
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t)
                                            for a, b in zip(NAVY_TOP, NAVY_BOTTOM)))
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([W * 0.05, H * 0.28, W * 0.95, H * 0.62], fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    bg.paste(Image.new("RGB", (W, H), (60, 110, 180)), mask=glow)
    return bg


def make_skyline():
    """가로로 긴 도시 실루엣 레이어 (천천히 흐르도록 넓게 만든다)."""
    sw = W * 2
    sky = Image.new("RGBA", (sw, 520), (0, 0, 0, 0))
    d = ImageDraw.Draw(sky)
    x, seed = 0, 7
    while x < sw:
        seed = (seed * 1103515245 + 12345) % (2 ** 31)
        bw = 90 + seed % 80
        bh = 220 + (seed // 97) % 280
        top = 520 - bh
        d.rectangle([x, top, x + bw, 520], fill=(6, 16, 34, 235))
        for wy in range(top + 24, 500, 34):
            for wx in range(x + 16, x + bw - 16, 26):
                seed = (seed * 1103515245 + 12345) % (2 ** 31)
                if seed % 5 == 0:
                    d.rectangle([wx, wy, wx + 10, wy + 14], fill=GOLD + (120,))
        x += bw + 6
    return sky


# ─────────────────────────────────────────────
# 4. 장면 구성
# ─────────────────────────────────────────────
def build_items(items):
    """장면의 각 줄을 이미지로 미리 만들어 둔다. count는 프레임마다 다시 그린다."""
    built = []
    for it in items:
        kind = it[0]
        if kind == "chips":
            built.append({"kind": kind, "img": chips_block(it[1]), "gap": 24})
        elif kind == "checks":
            built.append({"kind": kind, "img": checks_block(it[1]), "gap": 10})
        elif kind == "count":
            spec, size, color, gap = STYLES["count"]
            sample = text_block(f"{it[1]:,}", spec, size, color)
            built.append({"kind": kind, "value": it[1], "unit": it[2],
                          "h": sample.height + 70, "gap": gap})
        else:
            spec, size, color, gap = STYLES[kind]
            built.append({"kind": kind, "img": text_block(it[1], spec, size, color),
                          "gap": gap})
    return built


def item_height(b):
    return b["h"] if b["kind"] == "count" else b["img"].height


def draw_count(frame, b, y, progress, alpha):
    value = int(round(b["value"] * ease_out(progress)))
    spec, size, color, _ = STYLES["count"]
    num = text_block(f"{value:,}", spec, size, color)
    unit = text_block(b["unit"], BOLD, 72, WHITE)
    total = num.width + unit.width - 10
    x = (W - total) // 2
    frame.alpha_composite(with_alpha(num, alpha), (x, y))
    frame.alpha_composite(with_alpha(unit, alpha),
                          (x + num.width - 10, y + num.height - unit.height - 30))


def render_scene(frame, built, t, dur):
    """t: 장면 안에서의 경과 시간(초)."""
    total_h = sum(item_height(b) + b["gap"] for b in built)
    y = int(H * 0.47 - total_h / 2)
    exit_a = 1.0 - ease_out((t - (dur - FADE_OUT)) / FADE_OUT) if t > dur - FADE_OUT else 1.0
    for i, b in enumerate(built):
        start = 0.12 + i * 0.2
        p = ease_out((t - start) / 0.5)
        a = p * exit_a
        if a > 0.01:
            dy = int((1 - p) * 70)
            if b["kind"] == "count":
                draw_count(frame, b, y + dy, (t - start) / 1.3, a)
            else:
                img = b["img"]
                frame.alpha_composite(with_alpha(img, a), ((W - img.width) // 2, y + dy))
        y += item_height(b) + b["gap"]


def end_card_items():
    return build_items([
        ("kicker", COMPLEX_NAME),
        ("title", "지금 바로\n상담하세요"),
        ("body", CONTACT),
        ("note", MODEL_HOUSE),
    ])


def render_video(video):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / video["file"]
    scenes = [(s["dur"], build_items(s["items"])) for s in video["scenes"]]
    scenes.append((END_CARD_DUR, end_card_items()))
    total = sum(d for d, _ in scenes)
    n_frames = int(total * FPS)

    bg = make_background()
    sky = make_skyline()
    header = text_block(COMPLEX_NAME, BOLD, 40, WHITE)
    tag = text_block(video["tag"], BOLD, 40, GOLD)
    disclaimer = text_block(DISCLAIMER, REGULAR, 26, (170, 182, 204))

    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
           "-shortest", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    for fi in range(n_frames):
        t = fi / FPS
        frame = bg.copy().convert("RGBA")
        # 천천히 흐르는 도시 실루엣
        shift = int((t * 22) % W)
        frame.alpha_composite(sky.crop((shift, 0, shift + W, sky.height)), (0, H - sky.height))
        # 상단: 진행 막대 + 단지명 + 회차 태그
        d = ImageDraw.Draw(frame)
        d.rectangle([60, 150, W - 60, 156], fill=(255, 255, 255, 50))
        d.rectangle([60, 150, 60 + int((W - 120) * t / total), 156], fill=GOLD)
        frame.alpha_composite(header, ((W - header.width) // 2, 200))
        frame.alpha_composite(tag, ((W - tag.width) // 2, 262))
        # 현재 장면
        acc = 0.0
        for idx, (dur, built) in enumerate(scenes):
            if t < acc + dur or idx == len(scenes) - 1:
                render_scene(frame, built, t - acc, dur + (1 if idx == len(scenes) - 1 else 0))
                if idx == len(scenes) - 1:
                    a = ease_out((t - acc - 0.8) / 0.5)
                    if a > 0.01:
                        frame.alpha_composite(with_alpha(disclaimer, a),
                                              ((W - disclaimer.width) // 2, 1330))
                break
            acc += dur
        proc.stdin.write(frame.convert("RGB").tobytes())

    proc.stdin.close()
    proc.wait()
    print(f"완성: {out} ({total:.1f}초)")


if __name__ == "__main__":
    picks = [int(a) for a in sys.argv[1:]] or range(1, len(VIDEOS) + 1)
    for n in picks:
        render_video(VIDEOS[n - 1])
