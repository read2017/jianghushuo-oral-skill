#!/usr/bin/env python3
"""把 .build/extract/ 的提炼产出加工成可发布的 references/ 文件。

改动：替换内部路径引用、换成发布版头部、去掉仅用于构建的元信息。
用法：python3 prep_refs.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / ".build/extract"
REF = ROOT / "references"
REF.mkdir(exist_ok=True)

HEADERS = {
    "style-dna.md": """# 姜胡说 · 表达风格 DNA

> 基于姜胡说 **431 条**公开口播视频的开场原句统计得出（语料保存在本地分析环境，不随本仓库分发；提取方法见 [`../sources/README.md`](../sources/README.md)）。
> 「」= 逐字原话（保留 ASR 错字未改）；`[视频ID, X.X万赞]` = 出处与热度，可回原片核对。""",

    "methodology.md": """# 姜胡说 · 内容方法论

> 基于 **431 条**视频的结构拆解、**432 条**开场钩子、**392 条**类比素材（共 1084 条）统计得出。
> 所有段长占比均有视频行号可考；`[视频ID, X.X万赞]` 可用于回原片核对。""",

    "quotes.md": """# 姜胡说 · 金句库（精选 60 条）

> 从 **428 条**候选金句里精选，标准：独立成句、有辨识度、观点锋利。
> 「」= 逐字原话（保留 ASR 错字）；`[视频ID, X.X万赞]` = 出处与热度。
>
> **引用前请注意**：语料来自 ASR 转写，存在同音错字。用于公开发布前建议核对原片
> （`python3 scripts/locate.py <视频ID> --text "引文"` 可换算到原片时间点）。""",

    "terms.md": """# 姜胡说 · 自创术语表

> 从 **429 条**卡片中汇总并归并同义写法，共 **108 个**词条。
> 只收他自创或他重新定义的词；借用来的专名（如费曼学习法）与嘉宾自造词不计入。""",

    "final_models.md": """# 姜胡说 · 核心心智模型

> 由 4 个并行提炼 agent 从 431 条视频的论点卡中提出 **67 个候选**，再经三重验证合并收敛而来。
> **三重验证**：跨域复现（在 ≥2 个领域出现）· 生成力（能推断他对新问题的立场）· 排他性（不是所有聪明人都这么想）。
> 「」= 逐字原话（保留 ASR 错字）；`[视频ID, X.X万赞]` = 出处与热度。""",

    "final_tensions.md": """# 姜胡说 · 内在张力

> 一个人物的「自相矛盾」不是缺点而是指纹——**观点高度一致反而说明蒸馏失败了**。
> 本文件保留经核实的矛盾，不调和、不替他圆场。""",

    "asr_corrections.md": """# ASR 校正表

> 语料由 whisper 转写，人名、书名、专业词易错。**引用前先查此表**，避免把转写错误当成他的原话。
> 格式：`转写原文 → 应为`（标注「存疑」的表示无法确认，不要当确定值使用）。""",
}

# 构建期元信息行（发布版删除）
DROP_PAT = re.compile(
    r"^(- 语料来源：|- 输入：|- 样本量：|- 统计口径：|- 引用约定：|- 生成时间：|- 样本基线：|- 覆盖率：).*$",
    re.M)


def prep(src_name, dst_name):
    src = EX / src_name
    if not src.exists():
        return None
    t = src.read_text(encoding="utf-8")
    t = re.sub(r"[（(]?`\.build/[^`]*`[)）]?", "（本地语料库）", t)
    t = re.sub(r"`slices/[^`]*`", "（本地语料分片）", t)
    t = DROP_PAT.sub("", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    # 去掉原有的第一行标题（统一用新头部）
    t = re.sub(r"^#\s+.*?\n", "", t, count=1).lstrip()
    t = re.sub(r"^---\s*\n+", "", t)      # 去掉源文件开头的分隔符
    head = HEADERS.get(dst_name, "")
    out = (head + "\n\n" + t).strip() + "\n"
    (REF / dst_name).write_text(out, encoding="utf-8")
    print("  %-22s %6.1f KB" % (dst_name, len(out) / 1024))
    return True


if __name__ == "__main__":
    pairs = [("style_dna.md", "style-dna.md"), ("method.md", "methodology.md"),
             ("quotes.md", "quotes.md"), ("terms.md", "terms.md"),
             ("final_models.md", "final_models.md"), ("final_tensions.md", "final_tensions.md"),
             ("asr_corrections.md", "asr_corrections.md")]
    done = [p[1] for p in pairs if prep(*p)]
    print("已生成 %d 个 references 文件" % len(done))
