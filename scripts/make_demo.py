#!/usr/bin/env python3
"""生成 assets/demo.gif —— README「效果示例」用的终端对话动图。

模拟激活 skill 后的一段真实回答（内容取自保真度测试的题 1 实测答案）。
用法：python3 scripts/make_demo.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 560
FPS = 12
BG = (13, 17, 23)
PANEL = (22, 27, 34)
BAR = (33, 38, 45)
FG = (230, 237, 243)
DIM = (139, 148, 158)
BLUE = (88, 166, 255)
GREEN = (63, 185, 80)
YELLOW = (210, 153, 34)
BORDER = (48, 54, 61)

FONT_CANDIDATES = ["/System/Library/Fonts/STHeiti Medium.ttc",
                   "/Library/Fonts/Arial Unicode.ttf",
                   "/System/Library/Fonts/Supplemental/Songti.ttc"]
MONO_CANDIDATES = ["/System/Library/Fonts/Menlo.ttc",
                   "/System/Library/Fonts/SFNSMono.ttf"]


def pick(cands, size):
    for c in cands:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


# (类型, 文本, 颜色)  —— q=用户问句  a=姜胡说答句  d=细节/引用  e=折叠空行
LINES = [
    ("q", "> 我总是学完就忘，是不是应该先系统学一遍再开始做事？", DIM),
    ("e", "", DIM),

    ("a", "不用。你不是记不住，是你把顺序搞反了。", FG),
    ("e", "", DIM),
    ("d", "「你在学的过程中没有那个场景，你没有办法及时反馈」", BLUE),

    ("a", "没有反馈的东西，大脑凭什么替你存着？", FG),
    ("e", "", DIM),

    ("a", "所以「先系统学一遍」这个动作，我得跟你说句狠的：", FG),
    ("a", "它多半是拖延。学习本质上是你的避风港。", FG),
    ("e", "", DIM),

    ("a", "顺序要倒过来：先做再学，哪不会学哪。", GREEN),
    ("a", "今天学的任何一点东西，用两句话讲给别人听。", GREEN),
    ("e", "", DIM),

    ("a", "最后问你一句：你是不知道，还是没做？", YELLOW),
]


def frame(t):
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)

    # 终端窗口
    m = 46
    d.rounded_rectangle([m, m - 18, W - m, H - m], radius=12,
                        fill=PANEL + (255,), outline=BORDER + (255,), width=1)
    d.rounded_rectangle([m, m - 18, W - m, m + 16], radius=12, fill=BAR + (255,))
    d.rectangle([m, m + 4, W - m, m + 16], fill=BAR + (255,))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([m + 18 + i * 22, m - 8, m + 32 + i * 22, m + 6], fill=c + (255,))
    d.text((m + 96, m - 9), "jianghushuo-persona  ·  问答模式", font=pick(FONT_CANDIDATES, 17), fill=DIM + (255,))

    f_q = pick(FONT_CANDIDATES, 21)
    f_a = pick(FONT_CANDIDATES, 22)
    f_d = pick(FONT_CANDIDATES, 20)

    y = m + 44
    for i, (kind, text, color) in enumerate(LINES):
        st = 0.35 + i * 0.34
        if t < st:
            break
        a = ease((t - st) / 0.4)
        if kind == "e":
            y += 14
            continue
        col = tuple(int(c * a + PANEL[j] * (1 - a)) for j, c in enumerate(color))
        fnt = {"q": f_q, "a": f_a, "d": f_d}[kind]
        d.text((m + 30, y), text, font=fnt, fill=col + (255,))
        y += 34 if kind != "e" else 14

    # 结尾：在最后一行末尾画一个闪烁光标
    if t > 0.35 + len(LINES) * 0.34 and int(t * 2) % 2 == 0:
        ylast = m + 44 + sum(34 if k != "e" else 14 for k, _, _ in LINES[:-1])
        f_l = pick(FONT_CANDIDATES, 22)
        wlast = d.textbbox((0, 0), LINES[-1][1], font=f_l)[2]
        d.rectangle([m + 30 + wlast + 8, ylast + 6, m + 30 + wlast + 20, ylast + 28],
                    fill=GREEN + (255,))
    return img.convert("RGB")


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "demo.gif")
    total = 6.4
    n = int(total * FPS)
    frames = [frame(i / FPS) for i in range(n)]
    qs = [f.quantize(colors=96) for f in frames]
    qs[0].save(out, save_all=True, append_images=qs[1:], duration=int(1000 / FPS), loop=0, optimize=True)
    print(f"✅ {out}  {n} 帧  {os.path.getsize(out)/1024/1024:.2f} MB")


if __name__ == "__main__":
    main()
