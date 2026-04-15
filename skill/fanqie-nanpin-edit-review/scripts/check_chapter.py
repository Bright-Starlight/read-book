#!/usr/bin/env python3
"""Lightweight diagnostic helper for Fanqie male-fiction chapter revision."""
from __future__ import annotations
import re
import sys
from pathlib import Path

FILLERS = ["与此同时", "然而", "就在这时", "下一刻", "显然", "不由得", "顿时"]
EMOTION = ["震惊", "愤怒", "惊讶", "不安", "紧张", "狂喜"]
REACTION = ["所有人", "众人", "围观", "满脸震惊", "目瞪口呆"]


def count_hits(text: str, terms: list[str]) -> int:
    return sum(text.count(t) for t in terms)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: check_chapter.py <chapter.txt>")
        return 1
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    avg_len = round(sum(len(p) for p in paragraphs) / max(len(paragraphs), 1), 1)
    print("Fanqie chapter quick diagnostic")
    print(f"paragraphs: {len(paragraphs)}")
    print(f"avg_paragraph_chars: {avg_len}")
    print(f"filler_hits: {count_hits(text, FILLERS)}")
    print(f"emotion_label_hits: {count_hits(text, EMOTION)}")
    print(f"crowd_reaction_hits: {count_hits(text, REACTION)}")
    first = paragraphs[0][:80] if paragraphs else ""
    last = paragraphs[-1][-80:] if paragraphs else ""
    print(f"opening_preview: {first}")
    print(f"ending_preview: {last}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
