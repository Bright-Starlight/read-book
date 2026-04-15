#!/usr/bin/env python3
"""校验 output/ 与 work/ 是否符合本 skill 的最小交付规范。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_OUTPUTS = [
    "00_readme.md",
    "01_全书结构图.md",
    "02_核心论证.md",
    "03_关键概念.md",
    "04_易误读与限制.md",
    "05_复习问题.md",
    "06_图表索引.md",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book-dir", required=True)
    args = parser.parse_args()
    book_dir = Path(args.book_dir).resolve()
    work_dir = book_dir / "work"
    output_dir = book_dir / "output"
    chapters_dir = output_dir / "chapters"

    missing: list[str] = []
    for name in REQUIRED_OUTPUTS:
        if not (output_dir / name).exists():
            missing.append(f"output/{name}")
    for name in ["book_structure.json", "chapter_index.json", "images_manifest.json"]:
        if not (work_dir / name).exists():
            missing.append(f"work/{name}")
    if not chapters_dir.exists():
        missing.append("output/chapters/")

    if missing:
        print("[FAIL] 缺少以下文件或目录:")
        for item in missing:
            print(" -", item)
        raise SystemExit(1)

    chapter_index = json.loads((work_dir / "chapter_index.json").read_text(encoding="utf-8"))
    chapters = chapter_index.get("chapters", [])
    if chapters and not any(chapters_dir.glob("ch*_章节精读.md")):
        print("[FAIL] chapter_index.json 已列出章节，但 output/chapters/ 中没有章节精读文件")
        raise SystemExit(1)

    print("[OK] 输出目录通过最小校验")


if __name__ == "__main__":
    main()
