#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BOOK_DIR=""
TITLE=""
EXTRACT_CMD=""
INDEX_CMD=""
RENDER_CMD=""
FORCE_CHAPTER_STUBS=0

usage() {
  cat <<'EOF'
用法:
  bash scripts/run.sh --book-dir ./my-book [--title "书名"] \
    [--extract-cmd '...'] [--index-cmd '...'] [--render-cmd '...'] [--force-chapter-stubs]

说明:
  1. 初始化目录与骨架文件
  2. 默认执行内置基础提取（scripts/extract_book.py）；也可用 --extract-cmd 覆盖
  3. 可选执行章节索引命令（index-cmd），回填 work/chapter_index.json
  4. 根据 chapter_index.json 生成逐章精读骨架
  5. 默认执行内置渲染草稿（scripts/render_book.py）；也可用 --render-cmd 覆盖
  6. 运行最小产物校验

示例:
  bash scripts/run.sh --book-dir ./my-book
  bash scripts/run.sh --book-dir ./my-book --title "国家与革命"
  bash scripts/run.sh --book-dir ./my-book \
    --extract-cmd 'python tools/extract.py --book-dir "$BOOK_DIR"' \
    --index-cmd 'python tools/build_index.py --book-dir "$BOOK_DIR"' \
    --render-cmd 'python tools/render_notes.py --book-dir "$BOOK_DIR"'
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --book-dir) BOOK_DIR="$2"; shift 2 ;;
    --title) TITLE="$2"; shift 2 ;;
    --extract-cmd) EXTRACT_CMD="$2"; shift 2 ;;
    --index-cmd) INDEX_CMD="$2"; shift 2 ;;
    --render-cmd) RENDER_CMD="$2"; shift 2 ;;
    --force-chapter-stubs) FORCE_CHAPTER_STUBS=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知参数: $1"; usage; exit 1 ;;
  esac
done

if [ -z "$BOOK_DIR" ]; then
  echo "缺少 --book-dir"
  usage
  exit 1
fi

BOOK_DIR="$(cd "$(dirname "$BOOK_DIR")" && pwd)/$(basename "$BOOK_DIR")"
export BOOK_DIR

echo "[1/6] 初始化目录与骨架文件"
if [ -n "$TITLE" ]; then
  python "$SCRIPT_DIR/run_book_pipeline.py" --book-dir "$BOOK_DIR" --title "$TITLE"
else
  python "$SCRIPT_DIR/run_book_pipeline.py" --book-dir "$BOOK_DIR"
fi

if [ -n "$EXTRACT_CMD" ]; then
  echo "[2/6] 执行自定义文本提取命令"
  bash -lc "$EXTRACT_CMD"
else
  echo "[2/6] 执行内置基础提取"
  python "$SCRIPT_DIR/extract_book.py" --book-dir "$BOOK_DIR"
fi

if [ -n "$INDEX_CMD" ]; then
  echo "[3/6] 执行章节索引命令"
  bash -lc "$INDEX_CMD"
else
  echo "[3/6] 跳过章节索引回填（未提供 --index-cmd）"
fi

echo "[4/6] 生成逐章精读骨架"
if [ "$FORCE_CHAPTER_STUBS" -eq 1 ]; then
  python "$SCRIPT_DIR/scaffold_chapters.py" --book-dir "$BOOK_DIR" --force
else
  python "$SCRIPT_DIR/scaffold_chapters.py" --book-dir "$BOOK_DIR"
fi

if [ -n "$RENDER_CMD" ]; then
  echo "[5/6] 执行自定义章节/全书渲染命令"
  bash -lc "$RENDER_CMD"
else
  echo "[5/6] 执行内置渲染草稿"
  python "$SCRIPT_DIR/render_book.py" --book-dir "$BOOK_DIR"
fi

echo "[6/6] 校验产物"
python "$SCRIPT_DIR/validate_outputs.py" --book-dir "$BOOK_DIR"

echo "[OK] 一键流程完成: $BOOK_DIR"
