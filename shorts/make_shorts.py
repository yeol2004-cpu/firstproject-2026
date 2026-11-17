"""산곡역자이힐스테이트&하늘채 홍보용 숏폼(릴스) 5편 생성기.

사용법:
    python3 shorts/make_shorts.py          # 5편 모두 생성
    python3 shorts/make_shorts.py 2        # 2번 영상만 생성

결과물: shorts/output/*.mp4 (1080x1920, 30fps, 세로형, 배경음악·효과음 포함)
이미지: shorts/assets/ (조감도·항공뷰·입지도·배치도)
"""

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from audio import make_audio

# ─────────────────────────────────────────────
# 1. 기본 설정 (여기만 바꿔도 전체 영상에 반영돼요)
# ─────────────────────────────────────────────
COMPLEX_NAME = "산곡역자이힐스테이트&하늘채"
CONTACT = "분양 상담 ☎ 1666-3007"
MODEL_HOUSE = "견본주택 · 인천 부평구 산곡동 43-2"
DISCLAIMER = (
    "※ 본 영상의 이미지는 소비자의 이해를 돕기 위한 것으로 실제와 다를 수 있으며,\n"
    "세부 내용은 반드시 입주자모집공고를 확인하시기 바랍니다."
)

W, H, FPS = 1080, 1920, 30
HERE = Path(__file__).parent
OUT_DIR = HERE / "output"
ASSET_DIR = HERE / "assets"

FONT_DIR = "/usr/share/fonts/opentype/noto/"
BOLD = (FONT_DIR + "NotoSansCJK-Bold.ttc", 1)
REGULAR = (FONT_DIR + "NotoSansCJK-Regular.ttc", 1)

NAVY_TOP = (9, 24, 48)
NAVY_BOTTOM = (18, 44, 82)
GOLD = (232, 194, 122)
WHITE = (255, 255, 255)
SOFT = (201, 211, 227)

IMG_TOP = 330      # 이미지 영역 시작 위치(위에서부터 px)
IMG_H = 860        # 이미지 영역 기본 높이

# 각 줄 스타일: (폰트, 크기, 색, 아래 여백)
STYLES = {
    "kicker": (BOLD, 52, GOLD, 26),
    "title": (BOLD, 104, WHITE, 30),
    "body": (REGULAR, 46, SOFT, 20),
    "note": (REGULAR, 34, SOFT, 16),
    "count": (BOLD, 190, GOLD, 6),
}

# ─────────────────────────────────────────────
# 2. 이미지 속 위치 (원본 이미지 픽셀 좌표)
# ─────────────────────────────────────────────
# 입지도(map.png)
P_COMPLEX = (352, 312)
P_SANGOK = (378, 343)
LINE7 = [(533, 343), (621, 350), (720, 357), (828, 365), (951, 383)]  # 부평구청~부천시청
SCHOOLS = [(300, 300), (370, 293), (405, 300)]  # 인천마곡초, 인천산곡북초, 청천중

# ─────────────────────────────────────────────
# 3. 영상 5편의 내용
#    img: 사용할 이미지, view: 이미지에서 보여줄 부분 (중심x, 중심y, 폭)의 시작→끝
#    marks: 반짝이는 표시를 할 위치
# ─────────────────────────────────────────────
VIDEOS = [
    {
        "file": "01_station.mp4",
        "tag": "#1 초역세권",
        "scenes": [
            {"dur": 3.0, "img": "aerial", "view": ((503, 330, 980), (500, 420, 720)),
             "items": [("kicker", "출퇴근 스트레스, 이제 그만"),
                       ("title", "문 열고 나가면\n바로 지하철")]},
            {"dur": 3.6, "img": "map", "view": ((545, 338, 1040), (368, 330, 440)),
             "marks": [P_COMPLEX, P_SANGOK],
             "items": [("kicker", "지하철 7호선"),
                       ("title", "산곡역 초역세권"),
                       ("body", "산곡역 5·6번 출구 바로 앞")]},
            {"dur": 3.6, "img": "map", "view": ((400, 345, 460), (690, 360, 760)),
             "marks": [P_SANGOK] + LINE7,
             "items": [("kicker", "환승 없이 한 번에"),
                       ("title", "7호선 타고\n강남권까지"),
                       ("body", "부평구청 · 굴포천 · 상동 · 부천시청 방면"),
                       ("note", "청라 연장선 개통 예정")]},
        ],
    },
    {
        "file": "02_scale.mp4",
        "tag": "#2 매머드급 대단지",
        "scenes": [
            {"dur": 2.8, "img": "front", "view": ((550, 309, 953), (560, 330, 720)),
             "items": [("kicker", "인천 부평구 산곡동"),
                       ("title", "이 규모,\n실화인가요?")]},
            {"dur": 3.2, "img": "aerial", "view": ((500, 400, 700), (503, 330, 980)),
             "items": [("kicker", "총 세대수"),
                       ("count", 2706, "세대"),
                       ("body", "산곡6구역 재개발 대단지")]},
            {"dur": 3.0, "img": "front", "view": ((460, 309, 900), (640, 309, 900)),
             "items": [("kicker", "단지 규모"),
                       ("title", "20개 동 · 최고 33층"),
                       ("body", "지하 3층 ~ 지상 33층")]},
            {"dur": 3.8, "img": "siteplan", "view": ((544, 382, 1089), (544, 375, 960)),
             "items": [("kicker", "대형 건설사 3곳이 함께"),
                       ("title", "3개 브랜드 한 단지에"),
                       ("chips", ["GS건설 101~106·115~116동", "현대건설 107~114동",
                                  "코오롱글로벌 117~120동"])]},
        ],
    },
    {
        "file": "03_design.mp4",
        "tag": "#3 특화 설계",
        "scenes": [
            {"dur": 2.8, "img": "front", "view": ((640, 330, 600), (560, 309, 900)),
             "items": [("kicker", "집은 결국 구조입니다"),
                       ("title", "살아보면 아는\n설계의 차이")]},
            {"dur": 3.2, "img": "aerial", "view": ((420, 380, 640), (600, 380, 640)),
             "items": [("kicker", "다양한 선택지"),
                       ("title", "전용 50~84㎡"),
                       ("body", "신혼부부부터 4인 가족까지")]},
            {"dur": 3.0, "img": "front", "view": ((550, 250, 953), (580, 290, 760)),
             "items": [("kicker", "햇살 가득"),
                       ("title", "남향 위주\n단지 배치")]},
            {"dur": 3.6, "img": "front", "view": ((600, 360, 560), (530, 340, 680)),
             "items": [("kicker", "공간을 넓히는"),
                       ("title", "특화 설계"),
                       ("chips", ["4베이", "팬트리", "드레스룸"]),
                       ("note", "*일부 타입 적용")]},
        ],
    },
    {
        "file": "04_lifestyle.mp4",
        "tag": "#4 단지 라이프",
        "scenes": [
            {"dur": 3.6, "img": "siteplan", "view": ((544, 382, 1089), (470, 390, 600)),
             "items": [("kicker", "아이 키우는 집이라면"),
                       ("title", "차 없는\n공원형 단지"),
                       ("chips", ["어린이놀이터", "생태연못", "주민운동시설", "스쿨버스존"])]},
            {"dur": 3.8, "img": "siteplan", "view": ((480, 350, 620), (478, 350, 430)),
             "items": [("kicker", "멀리 갈 필요 없이"),
                       ("title", "단지 안에서\n누리는 일상"),
                       ("chips", ["피트니스", "골프연습장", "사우나",
                                  "게스트하우스", "카페라운지"])]},
            {"dur": 3.4, "img": "map", "view": ((360, 320, 620), (320, 315, 400)),
             "marks": [P_COMPLEX] + SCHOOLS,
             "items": [("kicker", "자연과 학교를 가까이"),
                       ("title", "원적산공원\n가까운 숲세권"),
                       ("body", "인천마곡초 · 산곡북초 · 청천중 인근")]},
        ],
    },
    {
        "file": "05_summary.mp4",
        "tag": "#5 한눈에 정리",
        "scenes": [
            {"dur": 2.8, "img": "aerial", "view": ((503, 330, 980), (480, 400, 700)),
             "items": [("kicker", "산곡동이 바뀝니다"),
                       ("title", "15초 만에\n핵심 정리")]},
            {"dur": 4.4, "img": "front", "img_h": 600, "view": ((470, 309, 900), (630, 309, 900)),
             "items": [("kicker", "이 단지를 봐야 하는 이유"),
                       ("checks", ["7호선 산곡역 초역세권",
                                   "총 2,706세대 대단지",
                                   "자이·힐스테이트·하늘채",
                                   "전용 50~84㎡ 다양한 평면",
                                   "차 없는 공원형 단지"])]},
            {"dur": 3.0, "img": "front", "view": ((560, 330, 700), (550, 309, 953)),
             "items": [("kicker", "입주 예정"),
                       ("title", "2029년 12월")]},
        ],
    },
]

END_CARD = {"dur": 4.0, "img": "aerial", "view": ((503, 330, 980), (503, 340, 880))}
FADE_OUT = 0.3


# ─────────────────────────────────────────────
# 4. 그리기 도구
# ─────────────────────────────────────────────
_font_cache = {}
_img_cache = {}


def font(spec, size):
    key = (spec, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(spec[0], size, index=spec[1])
    return _font_cache[key]


def asset(name):
    if name not in _img_cache:
        path = next(ASSET_DIR.glob(name + ".*"))
        _img_cache[name] = Image.open(path).convert("RGB")
    return _img_cache[name]


def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def text_block(text, spec, size, color, max_w=960):
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
        d.text(((img.width - w) // 2 - f.getbbox(l)[0], i * line_h), l, font=f, fill=color)
    return img


def chips_block(labels):
    """둥근 배지 여러 개를 줄바꿈하며 배치한다."""
    f = font(BOLD, 40)
    pad_x, pad_y, gap, chip_h = 30, 16, 16, 40 + 16 * 2 + 8
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
    f = font(BOLD, 50)
    row_h = 96
    img = Image.new("RGBA", (900, row_h * len(labels)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, lab in enumerate(labels):
        y = i * row_h
        cx, cy, r = 70, y + 40, 28
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD)
        d.line([(cx - 13, cy + 1), (cx - 3, cy + 11), (cx + 14, cy - 10)],
               fill=NAVY_TOP, width=7, joint="curve")
        d.text((125, y + 6), lab, font=f, fill=WHITE)
    return img


def with_alpha(img, a):
    if a >= 0.999:
        return img
    out = img.copy()
    out.putalpha(out.getchannel("A").point(lambda v: int(v * a)))
    return out


def make_background():
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t)
                                            for a, b in zip(NAVY_TOP, NAVY_BOTTOM)))
    return bg.convert("RGBA")


_fade_cache = {}


def band_fade(h):
    """이미지 영역 위·아래를 배경색으로 부드럽게 녹이는 마스크."""
    if h not in _fade_cache:
        m = Image.new("L", (W, h), 255)
        d = ImageDraw.Draw(m)
        top, bottom = 40, 240
        for y in range(top):
            d.line([(0, y), (W, y)], fill=int(255 * y / top))
        for y in range(bottom):
            d.line([(0, h - 1 - y), (W, h - 1 - y)], fill=int(255 * (y / bottom) ** 1.4))
        _fade_cache[h] = m
    return _fade_cache[h]


def view_rect(src, cx, cy, w, h_px):
    """원본 이미지에서 잘라낼 영역(비율 유지, 이미지 밖으로 안 나가게)."""
    aspect = W / h_px
    w = min(w, src.width, src.height * aspect)
    h = w / aspect
    cx = min(max(cx, w / 2), src.width - w / 2)
    cy = min(max(cy, h / 2), src.height - h / 2)
    return cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2


def draw_image_band(frame, scene, t, dur, alpha):
    src = asset(scene["img"])
    h_px = scene.get("img_h", IMG_H)
    (c0, c1) = scene["view"]
    p = ease_in_out(t / dur)
    cx, cy, w = (a + (b - a) * p for a, b in zip(c0, c1))
    x0, y0, x1, y1 = view_rect(src, cx, cy, w, h_px)
    band = src.transform((W, h_px), Image.EXTENT, (x0, y0, x1, y1), Image.BICUBIC)
    band = band.convert("RGBA")

    # 위치 표시: 금색 링이 퍼지며 반짝인다
    marks = scene.get("marks", [])
    if marks:
        d = ImageDraw.Draw(band)
        sx = W / (x1 - x0)
        for i, (mx, my) in enumerate(marks):
            px, py = (mx - x0) * sx, (my - y0) * sx
            if not (0 <= px < W and 0 <= py < h_px):
                continue
            phase = ((t * 1.2) - i * 0.15) % 1.0
            r = 14 + phase * 46
            d.ellipse([px - r, py - r, px + r, py + r],
                      outline=GOLD + (int(255 * (1 - phase)),), width=5)
            d.ellipse([px - 13, py - 13, px + 13, py + 13], fill=GOLD + (255,),
                      outline=(255, 255, 255, 255), width=4)

    mask = band_fade(h_px)
    if alpha < 0.999:
        mask = mask.point(lambda v: int(v * alpha))
    band.putalpha(mask)
    frame.alpha_composite(band, (0, IMG_TOP))
    return IMG_TOP + h_px


# ─────────────────────────────────────────────
# 5. 장면 구성
# ─────────────────────────────────────────────
def build_items(items):
    built = []
    for it in items:
        kind = it[0]
        if kind == "chips":
            built.append({"kind": kind, "img": chips_block(it[1]), "gap": 14})
        elif kind == "checks":
            built.append({"kind": kind, "img": checks_block(it[1]), "gap": 6})
        elif kind == "count":
            spec, size, color, gap = STYLES["count"]
            sample = text_block(f"{it[1]:,}", spec, size, color)
            built.append({"kind": kind, "value": it[1], "unit": it[2],
                          "h": sample.height + 50, "gap": gap})
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
    unit = text_block(b["unit"], BOLD, 68, WHITE)
    total = num.width + unit.width - 10
    x = (W - total) // 2
    frame.alpha_composite(with_alpha(num, alpha), (x, y))
    frame.alpha_composite(with_alpha(unit, alpha),
                          (x + num.width - 10, y + num.height - unit.height - 28))


def render_text(frame, built, t, dur, top):
    """이미지 아래쪽에 글자를 차례로 띄운다. top: 글자 시작 위치."""
    y = top
    exit_a = 1.0 - ease_out((t - (dur - FADE_OUT)) / FADE_OUT) if t > dur - FADE_OUT else 1.0
    for i, b in enumerate(built):
        start = 0.12 + i * 0.2
        p = ease_out((t - start) / 0.5)
        a = p * exit_a
        if a > 0.01:
            dy = int((1 - p) * 60)
            if b["kind"] == "count":
                draw_count(frame, b, y + dy, (t - start) / 1.3, a)
            else:
                img = b["img"]
                frame.alpha_composite(with_alpha(img, a), ((W - img.width) // 2, y + dy))
        y += item_height(b) + b["gap"]
    return y


def end_card():
    scene = dict(END_CARD)
    scene["items"] = [("kicker", COMPLEX_NAME), ("title", "지금 바로 상담하세요"),
                      ("body", CONTACT), ("note", MODEL_HOUSE)]
    scene["last"] = True
    return scene


def render_video(video):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / video["file"]
    scenes = video["scenes"] + [end_card()]
    built_all = [build_items(s["items"]) for s in scenes]
    total = sum(s["dur"] for s in scenes)
    n_frames = int(total * FPS)

    bg = make_background()
    header = text_block(COMPLEX_NAME, BOLD, 44, WHITE)
    tag = text_block(video["tag"], BOLD, 42, GOLD)
    disclaimer = text_block(DISCLAIMER, REGULAR, 25, (170, 182, 204), max_w=1000)

    # 소리: 장면이 바뀔 때 '휙', 숫자가 다 올라가거나 마지막 화면이 뜰 때 '띵'
    starts, dings, acc = [], [], 0.0
    for s, built in zip(scenes, built_all):
        starts.append(acc)
        for i, b in enumerate(built):
            if b["kind"] == "count":
                dings.append(acc + 0.12 + i * 0.2 + 1.3)
        acc += s["dur"]
    dings.append(starts[-1] + 0.35)
    wav = OUT_DIR / (video["file"] + ".wav")
    make_audio(wav, total, starts, dings, VIDEOS.index(video))

    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(wav), "-b:a", "192k",
           "-shortest", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    for fi in range(n_frames):
        t = fi / FPS
        frame = bg.copy()
        # 현재 장면 찾기
        acc = 0.0
        for idx, s in enumerate(scenes):
            if t < acc + s["dur"] or idx == len(scenes) - 1:
                break
            acc += s["dur"]
        st = t - acc
        last = s.get("last", False)
        img_alpha = ease_out(st / 0.35) if idx == 0 else 1.0
        bottom = draw_image_band(frame, s, st, s["dur"], img_alpha)
        text_end = render_text(frame, built_all[idx], st,
                               s["dur"] + (5 if last else 0), bottom - 40)
        if last:
            a = ease_out((st - 0.8) / 0.5)
            if a > 0.01:
                frame.alpha_composite(with_alpha(disclaimer, a),
                                      ((W - disclaimer.width) // 2, text_end + 30))
        # 상단: 진행 막대 + 단지명 + 회차 태그 (항상 맨 위에)
        d = ImageDraw.Draw(frame)
        d.rectangle([60, 150, W - 60, 156], fill=(255, 255, 255, 50))
        d.rectangle([60, 150, 60 + int((W - 120) * t / total), 156], fill=GOLD)
        frame.alpha_composite(header, ((W - header.width) // 2, 196))
        frame.alpha_composite(tag, ((W - tag.width) // 2, 258))
        proc.stdin.write(frame.convert("RGB").tobytes())

    proc.stdin.close()
    proc.wait()
    wav.unlink()
    print(f"완성: {out} ({total:.1f}초)")


if __name__ == "__main__":
    picks = [int(a) for a in sys.argv[1:]] or range(1, len(VIDEOS) + 1)
    for n in picks:
        render_video(VIDEOS[n - 1])
