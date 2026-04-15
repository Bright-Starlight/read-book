#!/usr/bin/env python3
"""基于提取文本与章节索引生成可读的章节/全书 Markdown 草稿。

说明：
- 这是一个“模型渲染层”的最小本地实现，目标是让 CLI 流程默认生成可读草稿。
- 若用户已有更强的模型调用脚本，可用 run.sh 的 --render-cmd 覆盖本脚本。
- 本脚本不会伪装为真正的高质量学术精读器；它会在能自动生成的地方尽量填充，
  在不确定处保留可验证的原文线索与明确的提醒。
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from collections import Counter
from textwrap import shorten
from typing import List, Dict, Any

STOPWORDS = set("我们你们他们以及因为所以但是然而如果一个一些这种这个那个可以需要已经进行对于通过没有不是并且或者其中这里那里然后还有以及为了由于可以可能非常很多不同之间".split())

SECTION_TEMPLATE = [
    "本章在全书中的位置",
    "本章要回答的核心问题",
    "本章的核心主张",
    "论证链条拆解",
    "关键概念与概念区分",
    "证据、案例与材料",
    "图像、图表与表格信息",
    "前提、限制与例外",
    "容易被忽略的细节",
    "一分钟回看",
]


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def clean_text(text: str) -> str:
    text = text.replace("\r", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_paragraphs(text: str) -> List[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", clean_text(text))]
    return [p for p in paras if len(p) >= 20]


def split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[。！？；])", text)
    return [p.strip() for p in parts if len(p.strip()) >= 12]


def chapter_markers(chapters: List[Dict[str, Any]]) -> List[str]:
    markers = []
    for ch in chapters:
        t = (ch.get("chapter_title") or ch.get("title") or "").strip()
        if t:
            markers.append(t)
            markers.append(f"# {t}")
            markers.append(f"## {t}")
    return markers


def find_chapter_slice(text: str, chapters: List[Dict[str, Any]], idx: int) -> str:
    title = (chapters[idx].get("chapter_title") or chapters[idx].get("title") or "").strip()
    if not title:
        return text
    candidates = [title, f"# {title}", f"## {title}"]
    starts = [text.find(c) for c in candidates if text.find(c) != -1]
    start = min(starts) if starts else -1
    if start == -1:
        # fallback: even partition
        size = max(1, len(text) // max(1, len(chapters)))
        return text[idx * size:(idx + 1) * size] if idx < len(chapters) - 1 else text[idx * size:]
    end = len(text)
    for nxt in chapters[idx + 1:]:
        nt = (nxt.get("chapter_title") or nxt.get("title") or "").strip()
        if not nt:
            continue
        next_candidates = [nt, f"# {nt}", f"## {nt}"]
        poss = [text.find(c, start + 1) for c in next_candidates if text.find(c, start + 1) != -1]
        if poss:
            end = min(poss)
            break
    return text[start:end].strip()


def extract_candidate_question(title: str, paras: List[str]) -> str:
    first = paras[0] if paras else ""
    sents = split_sentences(first)
    if sents:
        lead = sents[0]
        return f"结合标题“{title}”与开篇内容，本章主要追问的是：{lead[:80]}" + ("……" if len(lead) > 80 else "")
    return f"本章围绕“{title}”展开，核心问题需结合原文进一步校正。"


def pick_signals(paras: List[str], limit: int = 6) -> List[str]:
    scored = []
    for p in paras:
        score = 0
        if re.search(r"因此|所以|由此|说明|表明|意味着", p):
            score += 2
        if re.search(r"然而|但是|不过|相反|反而", p):
            score += 2
        if re.search(r"例如|比如|个案|案例|访谈|数据|图|表|统计", p):
            score += 1
        score += min(len(p) // 80, 3)
        scored.append((score, p))
    scored.sort(key=lambda x: (-x[0], -len(x[1])))
    out = []
    for _, p in scored:
        if p not in out:
            out.append(p)
        if len(out) >= limit:
            break
    return out


def extract_terms(text: str, n: int = 12) -> List[str]:
    cands = re.findall(r"[\u4e00-\u9fff]{2,6}", text)
    counts = Counter(w for w in cands if w not in STOPWORDS and len(w) >= 2)
    return [w for w, _ in counts.most_common(n)]


def build_mermaid_chapters(chapters: List[Dict[str, Any]]) -> str:
    lines = ["```mermaid", "flowchart TD"]
    prev = None
    for i, ch in enumerate(chapters, start=1):
        cid = ch.get("chapter_id") or f"ch{i:02d}"
        title = (ch.get("chapter_title") or ch.get("title") or f"第{i}章").strip().replace('"', "")
        label = title[:18] + ("…" if len(title) > 18 else "")
        node = f"{cid}[{i}. {label}]"
        if prev is None:
            lines.append(f"  {node}")
        else:
            lines.append(f"  {prev} --> {node}")
        prev = cid
    lines.append("```")
    return "\n".join(lines)


def update_readme(output_dir: Path, source_name: str, source_type: str, book_type: str, chapter_count: int, visual_count: int, confidence: str) -> None:
    content = f"""# 阅读说明

- 源文件名：{source_name}
- 文件类型：{source_type.upper()}
- 书型判断：{book_type}
- 判断依据：当前由章节标题、提取文本风格与索引信息自动初判，建议人工再确认。
- 实际启用的分支关注点：默认按“{book_type}”近似处理；如不符，请在后续精修时切换分支。
- 结构恢复置信度：{confidence}
- 识别到的章节数量：{chapter_count}
- 预处理中的主要问题：自动提取已完成，但 PDF/EPUB 复杂版式、脚注和图片仍可能存在遗漏。
- 图片/图表保留情况说明：当前共记录 {visual_count} 个视觉对象，并尽量回收了图注/alt/正文提及等可验证线索；关键图像仍建议人工回看原书。

## 文件使用建议

1. 先读 `01_全书结构图.md` 把握主线。
2. 再读 `02_核心论证.md` 与 `03_关键概念.md` 建立框架。
3. 回到 `output/chapters/` 做逐章精读。
4. 用 `05_复习问题.md` 做二刷和讨论。
"""
    (output_dir / "00_readme.md").write_text(content, encoding="utf-8")


def infer_book_type(chapters: List[Dict[str, Any]], text: str) -> str:
    sample = (" ".join((ch.get("chapter_title") or "") for ch in chapters) + "\n" + text[:4000]).lower()
    if re.search(r"访谈|田野|口述|观察| ethnography ", sample):
        return "访谈 / 田野材料型作品"
    if re.search(r"历史|年代|世纪|战争|帝国|革命|档案|史料|年", sample):
        return "历史书"
    if re.search(r"理论|概念|范畴|命题|规范|批判|本体|认识论", sample):
        return "理论书"
    return "社会学 / 政治学书"


def summarize_visual(v: Dict[str, Any]) -> list[str]:
    fields = v.get("extractable_fields", {}) or {}
    lines = [f"- {v.get('visual_id','未编号')}｜类型：{v.get('type','视觉对象')}｜标题/图注：{v.get('title_or_caption','无')}｜置信度：{v.get('confidence','unknown')}"]
    if fields.get('alt'):
        lines.append(f"  - alt：{shorten(str(fields.get('alt')), width=120, placeholder='…')}")
    if fields.get('title_attr'):
        lines.append(f"  - title：{shorten(str(fields.get('title_attr')), width=120, placeholder='…')}")
    if fields.get('caption_candidates'):
        vals = '; '.join(str(x) for x in fields.get('caption_candidates')[:3])
        lines.append(f"  - 图注候选：{shorten(vals, width=160, placeholder='…')}")
    if fields.get('nearby_references'):
        vals = '; '.join(str(x) for x in fields.get('nearby_references')[:2])
        lines.append(f"  - 正文提及：{shorten(vals, width=160, placeholder='…')}")
    if fields.get('src'):
        lines.append(f"  - 源路径：{fields.get('src')}")
    return lines


def build_chapter_md(ch: Dict[str, Any], idx: int, total: int, text: str, visuals: List[Dict[str, Any]]) -> str:
    title = (ch.get("chapter_title") or ch.get("title") or f"第{idx}章").strip()
    paras = split_paragraphs(text)
    signals = pick_signals(paras, limit=6)
    sents = split_sentences(text)
    terms = extract_terms(text, 8)
    visual_lines = []
    for v in visuals[:6]:
        visual_lines.extend(summarize_visual(v))
    if not visual_lines:
        visual_lines.append('- 本章暂未自动识别到可靠的关键视觉对象；如原书中有图表，请人工回看。')

    argument_bits = signals[:4] if signals else paras[:4]
    evidence_bits = [p for p in signals if re.search(r"例如|比如|案例|数据|图|表|访谈|材料|统计", p)] or signals[:3]
    hidden_bits = [p for p in paras if re.search(r"注|脚注|不过|仅在|除非|并不|未必|限制|边界", p)]
    hidden_bits = hidden_bits[:3] if hidden_bits else (signals[-2:] if len(signals) >= 2 else paras[:2])

    position = "开篇奠基章" if idx == 1 else ("结尾收束章" if idx == total else "中段推进章")
    if idx > 1 and idx < total and re.search(r"案例|个案|历史|田野|访谈", title):
        position = "中段案例/材料章"

    md = [f"# {title}", "", "## 本章在全书中的位置", f"本章位于全书第 {idx}/{total} 章，当前自动判断它更接近“{position}”。它与前后章节的具体衔接仍建议结合全书结构再校正。", "",
          "## 本章要回答的核心问题", extract_candidate_question(title, paras), "",
          "## 本章的核心主张", "以下内容基于自动提取文本生成，属于可读草稿，建议后续用更强模型深化：", ]
    for s in (sents[:3] or ["当前无法从提取文本中稳定恢复本章主张。"]):
        md.append(f"- {s}")
    md += ["", "## 论证链条拆解", "本节先保留自动挑出的关键论证片段，供后续精修时追踪作者如何从前提走向结论："]
    for i, p in enumerate(argument_bits, start=1):
        md.append(f"{i}. {p}")
    if not argument_bits:
        md.append("1. 当前提取文本不足，需人工回看本章正文。")

    md += ["", "## 关键概念与概念区分"]
    if terms:
        for t in terms[:6]:
            md.append(f"- **{t}**：当前由词频与上下文自动提取，建议结合原文确认定义、边界和与相邻概念的区别。")
    else:
        md.append("- 暂未可靠提取到高置信度关键概念。")

    md += ["", "## 证据、案例与材料"]
    if evidence_bits:
        for p in evidence_bits[:4]:
            md.append(f"- {p}")
    else:
        md.append("- 当前自动提取未找到明显的案例/数据/材料信号，请人工补充。")

    md += ["", "## 图像、图表与表格信息"] + visual_lines

    md += ["", "## 前提、限制与例外", "以下片段更可能包含限定条件、转折、例外或边界："]
    for p in hidden_bits[:3]:
        md.append(f"- {p}")

    md += ["", "## 容易被忽略的细节", "建议重点回看以下容易在普通摘要中丢失的线索："]
    for p in hidden_bits[:3]:
        md.append(f"- {p}")

    recap = signals[0] if signals else (paras[0] if paras else "当前无稳定文本可供总结。")
    md += ["", "## 一分钟回看", recap[:300] + ("……" if len(recap) > 300 else "")]
    return "\n".join(md).strip() + "\n"


def build_core_arguments(chapters: List[Dict[str, Any]]) -> str:
    lines = ["# 核心论证", "", "## 自动汇总说明", "以下为基于章节标题与索引生成的第一版全书论证草图，适合作为后续模型精修的起点。", "", "## 章节推动关系"]
    for i, ch in enumerate(chapters, start=1):
        title = ch.get("chapter_title") or ch.get("title") or f"第{i}章"
        role = "提出问题/搭框架" if i == 1 else ("收束/回应" if i == len(chapters) else "推进主线")
        lines.append(f"- 第{i}章《{title}》：{role}")
    lines += ["", "## 论证推进图（Mermaid）", build_mermaid_chapters(chapters)]
    return "\n".join(lines) + "\n"


def build_key_concepts(text: str, chapters: List[Dict[str, Any]]) -> str:
    terms = extract_terms(text, 20)
    lines = ["# 关键概念", ""]
    if not terms:
        lines.append("暂未可靠提取到关键概念，请结合章节文本手动补充。")
        return "\n".join(lines) + "\n"
    for term in terms[:15]:
        appears = []
        for i, ch in enumerate(chapters, start=1):
            title = ch.get("chapter_title") or ch.get("title") or f"第{i}章"
            if term in title:
                appears.append(f"第{i}章")
        lines += [f"## {term}", f"- 中文解释：自动候选概念，需结合原文定义确认。", f"- 作者如何使用它：建议回到含有“{term}”的原文段落核对其功能。", f"- 容易混淆：请与相邻概念比较边界。", f"- 关键章节：{', '.join(appears) if appears else '待结合正文确认'}", ""]
    return "\n".join(lines).strip() + "\n"


def build_misreadings(book_structure: Dict[str, Any], visuals: List[Dict[str, Any]]) -> str:
    conf = book_structure.get("structure_confidence", "low")
    lines = ["# 易误读与限制", "", "## 自动提取层面的限制", f"- 当前结构恢复置信度：{conf}", "- 自动草稿能提供阅读起点，但不能替代对论证链的人工复核。", "- 对复杂 PDF、扫描版、密集脚注页，仍可能漏掉关键细节。", "", "## 最容易被误读的地方", "- 章节标题并不等于章节结论，必须回到正文检查推理步骤。", "- 自动提取出的高频词并不天然等于关键概念，仍需看作者定义。", "- 图表与图片只建立了索引，不等于已经完成视觉论证分析。", ""]
    if visuals:
        lines.append("## 视觉材料提醒")
        for v in visuals[:10]:
            lines.append(f"- {v.get('visual_id','未编号')}：{v.get('title_or_caption','无标题')}（{v.get('type','视觉对象')}）")
    return "\n".join(lines) + "\n"


def build_review_questions(chapters: List[Dict[str, Any]]) -> str:
    groups = [
        ("基础理解", 5),
        ("论证追踪", 5),
        ("概念辨析", 5),
        ("批判思考", 5),
        ("迁移应用", 5),
    ]
    titles = [ch.get("chapter_title") or ch.get("title") or f"第{i}章" for i, ch in enumerate(chapters, start=1)]
    lines = ["# 复习问题", ""]
    for group, n in groups:
        lines.append(f"## {group}")
        for i in range(n):
            t = titles[i % len(titles)] if titles else f"第{i+1}章"
            if group == "基础理解":
                q = f"{t} 主要想回答什么问题？它在全书里承担什么作用？"
            elif group == "论证追踪":
                q = f"{t} 是如何从前提推进到结论的？中间最关键的转折在哪？"
            elif group == "概念辨析":
                q = f"{t} 中最关键的概念与其相邻概念有什么区别？"
            elif group == "批判思考":
                q = f"如果质疑 {t} 的核心判断，最可能从哪些证据、前提或范围限制入手？"
            else:
                q = f"把 {t} 的洞见迁移到现实分析时，哪些条件必须保留，哪些不能直接外推？"
            lines.append(f"{i+1}. {q}")
        lines.append("")
    lines += ["## 记忆锚点"]
    for t in titles[:10]:
        lines.append(f"- 记住《{t}》在全书中的位置与一个核心判断。")
    lines += ["", "## 二刷路径图（Mermaid）", "```mermaid", "flowchart LR", "  A[先看全书核心问题] --> B[再看核心概念]", "  B --> C[回到关键章节]", "  C --> D[核对论证链]", "  D --> E[最后检查易误读点]", "```", ""]
    return "\n".join(lines)


def build_visual_index(visuals: List[Dict[str, Any]]) -> str:
    lines = ["# 图表索引", "", "## 视觉对象总览"]
    if not visuals:
        lines.append("当前未自动识别到可靠视觉对象。")
    else:
        for v in visuals:
            line = f"- {v.get('visual_id','未编号')}｜章节：{v.get('chapter_id','未知')}｜类型：{v.get('type','视觉对象')}｜标题：{v.get('title_or_caption','无标题')}｜作用：{v.get('notes','待补充')}"
            lines.append(line)
            for extra in summarize_visual(v)[1:]:
                lines.append(extra)
    lines += ["", "## 视觉证据分布图（Mermaid)", "```mermaid", "flowchart TD"]
    by_ch = Counter(v.get('chapter_id', '未知') for v in visuals)
    if by_ch:
        for ch, c in by_ch.items():
            lines.append(f"  {re.sub(r'[^A-Za-z0-9_]', '_', ch)}[{ch}] --> V{c}[{c} 个视觉对象]")
    else:
        lines.append("  A[暂无可靠视觉对象] --> B[建议人工补录]")
    lines.append("```")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book-dir", required=True)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    book_dir = Path(args.book_dir).resolve()
    work = book_dir / "work"
    output = book_dir / "output"
    chapters_dir = output / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    extracted = (work / "extracted_text.md").read_text(encoding="utf-8") if (work / "extracted_text.md").exists() else ""
    book_structure = read_json(work / "book_structure.json", {})
    chapter_index = read_json(work / "chapter_index.json", {"chapters": []})
    chapters = chapter_index.get("chapters", [])
    visuals = read_json(work / "images_manifest.json", {"visuals": []}).get("visuals", [])

    source_type = book_structure.get("source_type", "unknown")
    source_name = f"source.{source_type}" if source_type in {"pdf", "epub"} else "source"
    book_type = infer_book_type(chapters, extracted)
    confidence = book_structure.get("structure_confidence", "medium")

    update_readme(output, source_name, source_type, book_type, len(chapters), len(visuals), confidence)
    (output / "01_全书结构图.md").write_text("# 全书结构图\n\n## 全书核心问题\n待结合正文进一步精修。\n\n## 全书主论题\n当前由章节推进关系自动估计。\n\n## 逐章功能图\n" + "\n".join([f"- 第{i}章《{(ch.get('chapter_title') or ch.get('title') or f'第{i}章')}》" for i, ch in enumerate(chapters, start=1)]) + "\n\n## 章节关系图（Mermaid）\n" + build_mermaid_chapters(chapters) + "\n", encoding="utf-8")
    (output / "02_核心论证.md").write_text(build_core_arguments(chapters), encoding="utf-8")
    (output / "03_关键概念.md").write_text(build_key_concepts(extracted, chapters), encoding="utf-8")
    (output / "04_易误读与限制.md").write_text(build_misreadings(book_structure, visuals), encoding="utf-8")
    (output / "05_复习问题.md").write_text(build_review_questions(chapters), encoding="utf-8")
    (output / "06_图表索引.md").write_text(build_visual_index(visuals), encoding="utf-8")

    visuals_by_ch: Dict[str, List[Dict[str, Any]]] = {}
    for v in visuals:
        visuals_by_ch.setdefault(v.get("chapter_id", ""), []).append(v)

    for i, ch in enumerate(chapters, start=1):
        cid = ch.get("chapter_id") or f"ch{i:02d}"
        title = ch.get("chapter_title") or ch.get("title") or f"第{i}章"
        out = chapters_dir / f"{cid}_章节精读.md"
        if out.exists() and not args.overwrite:
            existing = out.read_text(encoding="utf-8")
            if "待填写" not in existing and len(existing.strip()) > 300:
                continue
        chapter_text = find_chapter_slice(extracted, chapters, i - 1) if extracted else ""
        out.write_text(build_chapter_md(ch, i, max(1, len(chapters)), chapter_text, visuals_by_ch.get(cid, [])), encoding="utf-8")

    print(f"[OK] 已生成渲染草稿: chapters={len(chapters)}, visuals={len(visuals)}")


if __name__ == "__main__":
    main()
