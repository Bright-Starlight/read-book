# CLI 配方

本文件提供最小可运行命令示例。当前版本已经内置 `scripts/extract_book.py` 作为基础提取层：EPUB 可直接抽目录与正文，PDF 可直接抽正文、书签和图像占位。

## 一、初始化一本书的工作目录

```bash
mkdir -p my-book/input
cp /path/to/your-book.pdf my-book/input/source.pdf
bash scripts/run.sh --book-dir ./my-book
```

若输入为 EPUB：

```bash
mkdir -p my-book/input
cp /path/to/your-book.epub my-book/input/source.epub
bash scripts/run.sh --book-dir ./my-book
```

## 二、推荐的真实执行顺序

1. 运行 `bash scripts/run.sh --book-dir ./my-book`
2. 用你偏好的提取器，把正文写入 `work/extracted_text.md`
3. 恢复目录，写入 `work/toc_raw.md`
4. 回填 `work/book_structure.json`、`work/chapter_index.json`、`work/images_manifest.json`
5. 逐章生成 `output/chapters/chNN_章节精读.md`
6. 生成 `output/01_全书结构图.md` 到 `output/06_图表索引.md`
7. 运行 `python scripts/validate_outputs.py --book-dir ./my-book`

## 三、提取器接入建议

### PDF

可接入任何能稳定输出 Markdown 或结构化文本的工具。优先要求：
- 能保留标题层级
- 能尽量保留图注、表头、脚注
- 能暴露页码或定位信息

### EPUB

优先使用能读取目录、spine 和 HTML 结构的工具。要求：
- 合并被拆散的同章 HTML 文件
- 保留标题层级与图注
- 能把目录项映射到正文标题

## 四、图片处理建议

至少做三件事：
- 记录每个视觉对象所在章节
- 保留图题、图注、表头、坐标轴、图例等可确认字段
- 无法可靠识别时写入低置信度占位记录，而不是直接丢弃

## 五、Mermaid 使用约定

一旦需要画图，统一使用 Mermaid。推荐：
- `flowchart TD/LR`：论证链、章节关系、工作流
- `mindmap`：概念网络
- `timeline`：历史书时间线
- `graph TD/LR`：机制图、变量关系

所有 Mermaid 图前后都要有简短中文说明。


## 一键执行推荐

最推荐在 Claude Code CLI 中直接使用：

```bash
bash scripts/run.sh --book-dir ./my-book
```

若已有自己的提取与渲染脚本：

```bash
bash scripts/run.sh --book-dir ./my-book \
  --extract-cmd 'python tools/extract.py --book-dir "$BOOK_DIR"' \
  --index-cmd 'python tools/build_index.py --book-dir "$BOOK_DIR"' \
  --render-cmd 'python tools/render_notes.py --book-dir "$BOOK_DIR"'
```

## 章节骨架生成

当 `work/chapter_index.json` 已经回填后，可单独运行：

```bash
python scripts/scaffold_chapters.py --book-dir ./my-book
```

若想覆盖已存在的章节骨架：

```bash
python scripts/scaffold_chapters.py --book-dir ./my-book --force
```

## 失败排查

- 一键脚本只保证目录规范和最小校验，不代替真正的高质量解析。
- 若 `chapter_index.json` 为空，章节骨架不会生成，这是正常现象。
- 若已列出章节但没有生成章节文件，先检查 `chapter_id`、`chapter_title` 字段是否存在。
- 自定义命令里引用工作目录时，优先使用环境变量 `$BOOK_DIR`。


## 内置基础提取器单独运行

```bash
python scripts/extract_book.py --book-dir ./my-book
```

这个命令会：
- 探测 `input/source.pdf` 或 `input/source.epub`
- 回填 `work/extracted_text.md`
- 回填 `work/toc_raw.md`
- 回填 `work/images_manifest.json`
- 尽可能回填 `work/chapter_index.json` 和 `work/book_structure.json`

## 当前提取能力边界

- EPUB：通常可直接 usable，尤其适合有目录和标准 XHTML 结构的电子书。
- PDF：属于基础提取层；对带书签的数字版 PDF 效果最好。
- 扫描版 PDF、复杂多栏排版、嵌字图片型页面，仍建议后续接入更强的提取器覆盖。


## 内置渲染层单独运行

```bash
python scripts/render_book.py --book-dir ./my-book
```

这个命令会：
- 根据 `chapter_index.json` 自动写出逐章精读草稿
- 自动刷新 `00_readme.md` 到 `06_图表索引.md`
- 默认保留可验证线索，不把不确定内容写成确定结论

若要覆盖已有章节草稿：

```bash
python scripts/render_book.py --book-dir ./my-book --overwrite
```


## 视觉材料增强

- 视觉材料处理补充：`references/visual-processing.md`
- 当前版本默认不启用 OCR，但会回收 figcaption、alt、附近正文引用和 PDF 页面级 caption 候选。
