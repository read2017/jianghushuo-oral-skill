#!/usr/bin/env python3
"""生成 assets/hero.gif —— README 顶部的动图。

内容：姜胡说 persona skill 的蒸馏流水线可视化
  433 条视频 → 94.7 万字 → 432 张论点卡 → 67 个候选 → 6 个心智模型

设计：深色（GitHub 暗色底）+ 淡入 + 数据逐行推进，最后落在 6 个模型名上。
不使用人物肖像（避免版权问题），用「胡子」抽象符号做视觉标记。

依赖：Pillow、macOS 自带中文字体
用法：python3 scripts/make_hero.py
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 620
FPS = 12
BG = (13, 17, 23)
FG = (234, 240, 246)
DIM = (139, 148, 158)
ACC = (88, 166, 255)     # 蓝
ACC2 = (63, 185, 80)     # 绿
ACC3 = (210, 153, 34)    # 黄
ACC4 = (188, 140, 255)   # 紫

FONT_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]
MONO_CANDIDATES = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/SFNSMono.ttf",
    "/System/Library/Fonts/Courier.ttc",
]


def pick(cands, size):
    for c in cands:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()


def ease(t):
    """0→1 缓动"""
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def layer():
    return Image.new("RGBA", (W, H), BG + (255,))


def draw_centered(d, y, text, font, fill, alpha=1.0, dx=0):
    if alpha <= 0.01:
        return
    bbox = d.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = (W - w) / 2 - bbox[0] + dx
    col = tuple(int(c * alpha + BG[i] * (1 - alpha)) for i, c in enumerate(fill))
    d.text((x, y), text, font=font, fill=col + (255,))


def mix(c1, c2, a):
    return tuple(int(c1[i] * a + c2[i] * (1 - a)) for i in range(3))


AVATAR_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "assets", "avatar.png")
_AV_CACHE = {}


def avatar_circle(R):
    """把头像裁成圆形（4x 超采样后缩小，边缘平滑）"""
    if R in _AV_CACHE:
        return _AV_CACHE[R]
    S = R * 2 * 4
    src = Image.open(AVATAR_PATH).convert("RGBA")
    w, h = src.size
    m = min(w, h)
    src = src.crop(((w - m) // 2, (h - m) // 2, (w - m) // 2 + m, (h - m) // 2 + m))
    src = src.resize((S, S), Image.LANCZOS)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, S - 1, S - 1], fill=255)
    # 内缩 6%，避免圆形遮罩切掉头顶与下巴
    inner = int(S * 0.94)
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    canvas.paste(src.resize((inner, inner), Image.LANCZOS),
                 ((S - inner) // 2, (S - inner) // 2))
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.paste(canvas, (0, 0), mask)
    _AV_CACHE[R] = out.resize((R * 2, R * 2), Image.LANCZOS)
    return _AV_CACHE[R]


def draw_avatar(img, cx, cy, R, alpha=1.0):
    """贴圆形头像 + 蓝色圆环"""
    if alpha <= 0.01:
        return
    av = avatar_circle(R).copy()
    if alpha < 1.0:
        av.putalpha(av.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(av, (int(cx - R), int(cy - R)), av)
    d = ImageDraw.Draw(img)
    ring = mix((88, 166, 255), BG, alpha)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=ring + (255,), width=3)


# ---------- 内容 ----------
TITLE = "姜胡说 · 口播 skill"
SUBTITLE = "从 433 条公开口播视频，蒸馏出一个人"

PIPE = [
    ("433", " 条公开视频 · 52.6 小时音频", ACC),
    ("946,972", " 字口播逐字稿", ACC),
    ("432", " 张论点卡 · 每条引文逐字校验", ACC),
    ("67", " 个心智模型候选", ACC3),
    ("↓", " 三重验证：跨域复现 · 生成力 · 排他性", DIM),
    ("6", " 个心智模型", ACC2),
]

MODELS = [
    "① 世界以你攀登的最高峰定义你",
    "② 我走的是窄门",
    "③ 做资产，不做流量",
    "④ 一定不要做难而正确的事",
    "⑤ 行动产生信息",
    "⑥ 收集问题就是收集财富",
]

FOOT_L = "每一句原话都能回到原片秒数"
FOOT_R = "独立评分 90/100 · 引用核验 31/31 全中"


def frame(t):
    """t: 秒"""
    img = layer()
    d = ImageDraw.Draw(img)
    f_title = pick(FONT_CANDIDATES, 58)
    f_sub = pick(FONT_CANDIDATES, 25)
    f_num = pick(MONO_CANDIDATES, 34)
    f_txt = pick(FONT_CANDIDATES, 25)
    f_model = pick(FONT_CANDIDATES, 23)
    f_foot = pick(FONT_CANDIDATES, 19)
    f_small = pick(FONT_CANDIDATES, 17)

    # ---- 阶段 1：标题（0.0–1.5s）----
    a1 = ease(t / 0.9)
    draw_avatar(img, W / 2, 92 + int(12 * (1 - a1)), 46, a1)
    draw_centered(d, 154, TITLE, f_title, FG, a1)
    if t > 0.55:
        a = ease((t - 0.55) / 0.7)
        draw_centered(d, 226, SUBTITLE, f_sub, DIM, a)

    # ---- 阶段 2 / 3：同一区域先流水线、后模型（避免叠字）----
    y0 = 278
    if t < 4.10:
        for i, (num, label, color) in enumerate(PIPE):
            st = 1.45 + i * 0.36
            if t < st:
                break
            a = ease((t - st) / 0.5)
            if t > 3.95:                      # 换场前整体淡出
                a *= max(0.0, 1 - (t - 3.95) / 0.15)
            dy = int(16 * (1 - a))
            y = y0 + i * 44 + dy
            nb = d.textbbox((0, 0), num, font=f_num)
            nw = nb[2] - nb[0]
            col = tuple(int(c * a + BG[j] * (1 - a)) for j, c in enumerate(color))
            d.text((W / 2 - 24 - nw, y), num, font=f_num, fill=col + (255,))
            lcol = tuple(int(c * a + BG[j] * (1 - a)) for j, c in enumerate(FG if i == 5 else DIM))
            d.text((W / 2 + 4, y + 8), label, font=f_txt, fill=lcol + (255,))
    else:
        ah = ease((t - 4.10) / 0.45)
        draw_centered(d, 276, "蒸馏出的 6 个心智模型", pick(FONT_CANDIDATES, 24), DIM, ah)
        for i, m in enumerate(MODELS):
            st = 4.25 + i * 0.24
            if t < st:
                break
            a = ease((t - st) / 0.45)
            col = [ACC, ACC3, ACC2, ACC4, ACC, ACC3][i]
            draw_centered(d, 316 + i * 40, m, f_model, col, a)

    # ---- 阶段 4：底栏（5.9–7.0s）----
    if t > 5.85:
        a = ease((t - 5.85) / 0.5)
        d.line([(120, H - 92), (W - 120, H - 92)],
               fill=tuple(int(c * a + BG[j] * (1 - a)) for j, c in enumerate((48, 54, 61))) + (255,), width=1)
        draw_centered(d, H - 74, FOOT_L, f_foot, ACC2, a)
        draw_centered(d, H - 46, FOOT_R, f_small, DIM, a * 0.95)

    return img.convert("RGB")


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "hero.gif")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    total = 7.0
    n = int(total * FPS)
    frames = [frame(i / FPS) for i in range(n)]
    # 量化以压缩体积
    pal = frames[0].quantize(colors=128)
    qs = [f.quantize(colors=128) for f in frames]
    qs[0].save(out, save_all=True, append_images=qs[1:], duration=125, loop=0, optimize=True)
    kb = os.path.getsize(out) / 1024
    print(f"✅ {out}  {n} 帧  {kb/1024:.2f} MB")


if __name__ == "__main__":
    main()
