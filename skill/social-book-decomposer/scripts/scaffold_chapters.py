#!/usr/bin/env python3
"""根据 chapter_index.json 生成逐章精读 Markdown 骨架。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TEMPLATE = """# {title}

## 本章在全书中的位置
待填写。

## 本章要回答的核心问题
待填写。

## 本章的核心主张
待填写。

## 论证链条拆解
待填写。

## 关键概念与概念区分
待填写。

## 证据、案例与材料
待填写。

## 图像、图表与表格信息
待填写。

## 前提、限制与例外
待填写。

## 容易被忽略的细节
待填写。

## 一分钟回看
待填写。
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book-dir", required=True)
    parser.add_argument("--force", action="store_true", help="已存在时覆盖章节骨架")
    args = parser.parse_args()

    book_dir = Path(args.book_dir).resolve()
    index_path = book_dir / "work" / "chapter_index.json"
    chapters_dir = book_dir / "output" / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    if not index_path.exists():
        raise SystemExit("缺少 work/chapter_index.json")

    data = json.loads(index_path.read_text(encoding="utf-8"))
    chapters = data.get("chapters", [])
    created = 0
    skipped = 0
    for i, chapter in enumerate(chapters, start=1):
        cid = chapter.get("chapter_id") or f"ch{i:02d}"
        title = chapter.get("chapter_title") or chapter.get("title") or f"第{i}章"
        out = chapters_dir / f"{cid}_章节精读.md"
        if out.exists() and not args.force:
            skipped += 1
            continue
        out.write_text(TEMPLATE.format(title=title), encoding="utf-8")
        created += 1

    print(f"[OK] 章节骨架生成完成: created={created}, skipped={skipped}, total={len(chapters)}")


if __name__ == "__main__":
    main()
