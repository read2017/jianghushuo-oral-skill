#!/usr/bin/env python3
"""把引文／行号定位回原视频的时间点。

用法：
  python3 locate.py <视频ID> --line 217
  python3 locate.py <视频ID> --text "这个世界是以你攀登的最高峰来定义你的"
  python3 locate.py <视频ID> --lines 217,245,281

语料由 douyin-creator-research / douyin-video-transcript 提取，默认路径见 CORPUS，
可用环境变量 JHS_CORPUS 覆盖。
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

CORPUS = Path(os.environ.get(
    "JHS_CORPUS",
    Path.home() / "workspace/media-crawler/data/creator_jianghushuo/corpus_transcripts",
))


def norm(s):
    return re.sub(r"[\s，。、！？；：「」『』,.!?;:\"'（）()]", "", s or "")


def load_segments(vid):
    f = CORPUS / vid / "segments.json"
    if not f.exists():
        sys.exit("找不到语料：%s" % f)
    return json.loads(f.read_text(encoding="utf-8"))


def fmt(t):
    return "%d:%02d（第 %d 秒）" % (int(t // 60), int(t % 60), int(t))


def by_line(segs, line):
    i = line - 1
    if not (0 <= i < len(segs)):
        return None
    s = segs[i]
    return s.get("start"), s.get("end"), (s.get("text") or "").strip()


def by_text(segs, text):
    """全文归一化后查找，再把命中位置映射回所属分段（避免窗口首段偏移）。"""
    key = norm(text)
    if not key:
        return None
    full, spans = "", []
    for i, s in enumerate(segs):
        t = norm(s.get("text") or "")
        spans.append((len(full), len(full) + len(t), i))
        full += t
    pos = full.find(key[:14])
    if pos < 0:
        return None
    for a, b, i in spans:
        if a <= pos < b:
            s = segs[i]
            return s.get("start"), s.get("end"), (s.get("text") or "").strip()
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video_id")
    ap.add_argument("--line", type=int)
    ap.add_argument("--lines", default="")
    ap.add_argument("--text", default="")
    a = ap.parse_args()

    segs = load_segments(a.video_id)
    print("视频 %s（语料 %d 段）" % (a.video_id, len(segs)))
    tasks = []
    if a.lines:
        tasks += [("line", int(x)) for x in a.lines.split(",") if x.strip()]
    if a.line:
        tasks.append(("line", a.line))
    if a.text:
        tasks.append(("text", a.text))
    if not tasks:
        tasks.append(("line", 1))

    for kind, v in tasks:
        r = by_line(segs, v) if kind == "line" else by_text(segs, v)
        if not r:
            print("  ✗ 定位失败：%s" % v)
            continue
        st, en, txt = r
        label = "L%s" % v if kind == "line" else "「%s…」" % v[:16]
        print("  %-24s → %s～%s  %s" % (label, fmt(st), fmt(en), txt[:48]))


if __name__ == "__main__":
    main()
