#!/usr/bin/env python3
"""最小可运行的社科书精读流水线脚本。

这个脚本不强绑特定 PDF/EPUB 解析器，优先承担：
1. 统一目录初始化
2. 发现输入文件
3. 生成中间索引骨架
4. 生成最终输出文件骨架
5. 为后续接入真实提取器/模型调用预留稳定接口

用法：
    python scripts/run_book_pipeline.py --book-dir ./my-book
    python scripts/run_book_pipeline.py --book-dir ./my-book --title "想象的共同体"
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


def mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def detect_source(book_dir: Path) -> Path:
    input_dir = book_dir / "input"
    if not input_dir.exists():
        raise FileNotFoundError("缺少 input/ 目录")
    candidates = sorted([p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in {".pdf", ".epub"}])
    if not candidates:
        raise FileNotFoundError("input/ 目录中未找到 pdf 或 epub 文件")
    if len(candidates) > 1:
        raise RuntimeError("input/ 中发现多个书籍文件。请只保留 1 本当前待处理书籍")
    return candidates[0]


def slugify(name: str) -> str:
    name = re.sub(r"\s+", "-", name.strip())
    name = re.sub(r"[^\w\-\u4e00-\u9fff]", "", name)
    return name or "book"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def init_tree(book_dir: Path) -> dict[str, Path]:
    input_dir = book_dir / "input"
    work_dir = book_dir / "work"
    output_dir = book_dir / "output"
    chunks_dir = work_dir / "chapter_chunks"
    chapters_dir = output_dir / "chapters"
    for p in [input_dir, work_dir, output_dir, chunks_dir, chapters_dir]:
        mkdir(p)
    return {
        "input": input_dir,
        "work": work_dir,
        "output": output_dir,
        "chunks": chunks_dir,
        "chapters": chapters_dir,
    }


def build_book_structure(title: str, source_type: str) -> dict[str, Any]:
    return {
        "title": title,
        "source_type": source_type,
        "book_type": "待判断",
        "structure_confidence": "low",
        "chapters": [],
        "front_matter": [],
        "appendix": [],
        "notes_on_extraction": [
            "这是初始化骨架。请在接入真实文本提取和章节识别后回填。"
        ],
    }


def build_readme(source_name: str, source_type: str, title: str) -> str:
    return f"""# 阅读说明

- 源文件名：{source_name}
- 文件类型：{source_type.upper()}
- 暂定书名：{title}
- 书型判断：待判断
- 判断依据：待在完成文本抽取与目录恢复后填写。
- 实际启用的分支关注点：待填写。
- 结构恢复置信度：低
- 识别到的章节数量：0
- 预处理中的主要问题：尚未执行真实提取。
- 图片/图表保留情况说明：尚未建立视觉对象索引。

## 文件使用建议

1. 先检查 `work/book_structure.json` 与 `work/chapter_index.json`。
2. 再补全文本提取与目录恢复。
3. 按章生成 `output/chapters/chNN_章节精读.md`。
4. 最后生成全书级综合文件。
"""


def build_structure_md() -> str:
    return """# 全书结构图

## 全书核心问题
待填写。

## 全书主论题
待填写。

## 逐章功能图
待填写。

## 论证推进路径
待填写。

## 章节关系图（Mermaid）
```mermaid
flowchart TD
  A[导论/问题提出] --> B[概念与框架]
  B --> C[核心论证推进]
  C --> D[案例或经验材料]
  D --> E[结论/回应反对意见]
```
"""


def build_review_md() -> str:
    sections = {
        "基础理解": 6,
        "论证追踪": 6,
        "概念辨析": 6,
        "批判思考": 6,
        "迁移应用": 6,
    }
    parts: list[str] = ["# 复习问题", ""]
    for title, n in sections.items():
        parts.append(f"## {title}")
        for i in range(1, n + 1):
            parts.append(f"{i}. 待填写。")
        parts.append("")
    parts.extend([
        "## 记忆锚点",
        "- 待填写。",
        "- 待填写。",
        "",
        "## 二刷路径图（Mermaid）",
        "```mermaid",
        "flowchart LR",
        "  A[先看全书核心问题] --> B[再看关键概念]",
        "  B --> C[回到核心章节]",
        "  C --> D[核对论证链]",
        "  D --> E[最后检查易误读点]",
        "```",
    ])
    return "\n".join(parts)


def build_empty_md(title: str) -> str:
    return f"# {title}\n\n待填写。\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book-dir", required=True, help="书籍工作目录，内含 input/work/output")
    parser.add_argument("--title", default="", help="可选书名；不传时尝试从文件名推断")
    args = parser.parse_args()

    book_dir = Path(args.book_dir).resolve()
    tree = init_tree(book_dir)
    source = detect_source(book_dir)
    source_type = source.suffix.lower().lstrip(".")
    title = args.title.strip() or source.stem

    book_structure = build_book_structure(title, source_type)
    chapter_index = []
    images_manifest = []

    write_text(tree["work"] / "extracted_text.md", "# 待提取正文\n\n请接入真实 PDF/EPUB 提取器后回填。")
    write_text(tree["work"] / "toc_raw.md", "# 待恢复目录\n\n请从书签、目录页或 EPUB 导航中恢复。")
    write_json(tree["work"] / "book_structure.json", book_structure)
    write_json(tree["work"] / "chapter_index.json", {"chapters": chapter_index})
    write_json(tree["work"] / "images_manifest.json", {"visuals": images_manifest})

    write_text(tree["output"] / "00_readme.md", build_readme(source.name, source_type, title))
    write_text(tree["output"] / "01_全书结构图.md", build_structure_md())
    write_text(tree["output"] / "02_核心论证.md", build_empty_md("核心论证"))
    write_text(tree["output"] / "03_关键概念.md", build_empty_md("关键概念"))
    write_text(tree["output"] / "04_易误读与限制.md", build_empty_md("易误读与限制"))
    write_text(tree["output"] / "05_复习问题.md", build_review_md())
    write_text(tree["output"] / "06_图表索引.md", build_empty_md("图表索引"))

    print(f"[OK] 已初始化书籍目录: {book_dir}")
    print(f"[OK] 输入文件: {source.name}")
    print(f"[OK] 已生成 work/ 与 output/ 骨架文件")


if __name__ == "__main__":
    main()
