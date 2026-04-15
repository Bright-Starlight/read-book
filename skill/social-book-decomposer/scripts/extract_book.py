#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import traceback
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup


CAPTION_RE = re.compile(r'^(图|表|Figure|Fig\.?|Table)\s*[0-9一二三四五六七八九十IVXivx\-\.]*')
REF_RE = re.compile(r'(图|表|Figure|Fig\.?|Table)\s*[0-9一二三四五六七八九十IVXivx\-\.]*')


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding='utf-8')


def detect_source(book_dir: Path) -> Path:
    input_dir = book_dir / 'input'
    candidates = sorted([p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in {'.pdf', '.epub'}])
    if not candidates:
        raise FileNotFoundError('input/ 目录中未找到 pdf 或 epub 文件')
    if len(candidates) > 1:
        raise RuntimeError('input/ 中发现多个书籍文件。请只保留 1 本当前待处理书籍')
    return candidates[0]


def clean_text(text: str) -> str:
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\u00a0', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()


def ensure_dirs(book_dir: Path) -> tuple[Path, Path]:
    work_dir = book_dir / 'work'
    output_dir = book_dir / 'output'
    work_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    return work_dir, output_dir


def parse_epub_container(zf: zipfile.ZipFile) -> str:
    root = ET.fromstring(zf.read('META-INF/container.xml'))
    ns = {'c': 'urn:oasis:names:tc:opendocument:xmlns:container'}
    el = root.find('.//c:rootfile', ns)
    if el is None:
        raise RuntimeError('无法从 container.xml 找到 OPF 路径')
    return el.attrib['full-path']


def strip_html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'nav']):
        tag.decompose()
    for br in soup.find_all('br'):
        br.replace_with('\n')
    text = soup.get_text('\n')
    return clean_text(text)


def classify_visual_type(text: str) -> str:
    t = (text or '').lower()
    if re.search(r'表|table', t):
        return 'table'
    if re.search(r'地图|map', t):
        return 'map'
    if re.search(r'时间线|timeline', t):
        return 'timeline'
    if re.search(r'流程|机制|关系|网络|示意', t):
        return 'diagram'
    if re.search(r'图|figure|fig\.?', t):
        return 'figure'
    return 'image'


def nearby_text(node, limit: int = 2) -> list[str]:
    out: list[str] = []
    for sib in list(node.previous_siblings)[:limit] + list(node.next_siblings)[:limit]:
        text = clean_text(BeautifulSoup(str(sib), 'html.parser').get_text(' '))
        if text:
            out.append(text[:240])
    return out[:limit]


def capture_nearby_refs(lines: list[str], limit: int = 4) -> list[str]:
    refs: list[str] = []
    for line in lines:
        if REF_RE.search(line):
            refs.append(line[:240])
        if len(refs) >= limit:
            break
    return refs


def extract_epub(source: Path, book_dir: Path) -> dict[str, Any]:
    work_dir, _ = ensure_dirs(book_dir)
    notes: list[str] = []
    visuals: list[dict[str, Any]] = []
    chapters: list[dict[str, Any]] = []

    with zipfile.ZipFile(source, 'r') as zf:
        opf_path = parse_epub_container(zf)
        opf_dir = str(Path(opf_path).parent).replace('\\', '/')
        opf = ET.fromstring(zf.read(opf_path))
        ns = {
            'opf': 'http://www.idpf.org/2007/opf',
            'dc': 'http://purl.org/dc/elements/1.1/',
        }
        manifest: dict[str, dict[str, str]] = {}
        for item in opf.findall('.//opf:manifest/opf:item', ns):
            manifest[item.attrib['id']] = {
                'href': item.attrib.get('href', ''),
                'media-type': item.attrib.get('media-type', ''),
                'properties': item.attrib.get('properties', ''),
            }
        spine_ids = [item.attrib.get('idref', '') for item in opf.findall('.//opf:spine/opf:itemref', ns)]
        title = opf.findtext('.//dc:title', default=source.stem, namespaces=ns)

        toc_lines: list[str] = []
        nav_id = None
        for mid, meta in manifest.items():
            if 'nav' in meta.get('properties', ''):
                nav_id = mid
                break
        if nav_id:
            nav_href = manifest[nav_id]['href']
            nav_path = str((Path(opf_dir) / nav_href).as_posix()) if opf_dir != '.' else nav_href
            try:
                nav_html = zf.read(nav_path).decode('utf-8', errors='ignore')
                soup = BeautifulSoup(nav_html, 'html.parser')
                for idx, a in enumerate(soup.select('nav a'), start=1):
                    label = clean_text(a.get_text(' '))
                    href = a.get('href', '')
                    if label:
                        toc_lines.append(f'{idx}. {label} -> {href}')
                        chapters.append({
                            'chapter_id': f'ch{idx:02d}',
                            'chapter_title': label,
                            'chapter_aliases': [],
                            'order': idx,
                            'start_locator': href,
                            'end_locator': '',
                            'subsections': [],
                            'has_visual_material': False,
                            'visual_ids': [],
                            'analysis_status': 'indexed',
                        })
            except Exception as exc:
                notes.append(f'EPUB 导航读取失败: {exc}')
        else:
            notes.append('未找到 EPUB nav，改用 spine 顺序抽取正文。')

        parts: list[str] = [f'# {title}', '']
        chapter_counter = 1
        for idref in spine_ids:
            meta = manifest.get(idref)
            if not meta:
                continue
            href = meta.get('href', '')
            media_type = meta.get('media-type', '')
            if media_type not in {'application/xhtml+xml', 'text/html'}:
                continue
            full_path = str((Path(opf_dir) / href).as_posix()) if opf_dir != '.' else href
            try:
                raw = zf.read(full_path).decode('utf-8', errors='ignore')
            except KeyError:
                notes.append(f'缺少 spine 文件: {full_path}')
                continue
            soup = BeautifulSoup(raw, 'html.parser')
            head = None
            for tag_name in ['h1', 'h2', 'title']:
                tag = soup.find(tag_name)
                if tag and clean_text(tag.get_text(' ')):
                    head = clean_text(tag.get_text(' '))
                    break
            head = head or f'章节 {chapter_counter}'
            text = strip_html_to_text(raw)
            if not text:
                continue
            parts.extend([f'\n\n# {head}\n', text])

            lines = [clean_text(x) for x in soup.get_text('\n').splitlines() if clean_text(x)]
            line_refs = capture_nearby_refs(lines)
            imgs = soup.find_all(['img', 'svg', 'table'])
            visual_ids: list[str] = []
            visual_num = 1
            for node in imgs:
                caption = ''
                fig = node.find_parent('figure')
                if fig:
                    cap = fig.find('figcaption')
                    if cap:
                        caption = clean_text(cap.get_text(' '))
                if not caption:
                    nearby = nearby_text(node)
                    if node.name == 'table':
                        caption = next((t for t in nearby if re.search(r'表|table', t, re.I)), '')
                    else:
                        caption = next((t for t in nearby if CAPTION_RE.search(t)), '')
                alt = node.get('alt', '') if hasattr(node, 'get') else ''
                title_attr = node.get('title', '') if hasattr(node, 'get') else ''
                aria = node.get('aria-label', '') if hasattr(node, 'get') else ''
                kind_hint = ' '.join(x for x in [caption, alt, title_attr, aria, node.name] if x)
                visual_type = 'table' if node.name == 'table' else classify_visual_type(kind_hint)
                vid_prefix = 'tbl' if visual_type == 'table' else 'fig'
                visual_id = f'{vid_prefix}-ch{chapter_counter:02d}-{visual_num:02d}'
                visual_num += 1
                extractable_fields = {
                    'src': node.get('src', '') if hasattr(node, 'get') else '',
                    'alt': alt,
                    'title_attr': title_attr,
                    'aria_label': aria,
                    'nearby_references': [x for x in nearby_text(node, 3) if REF_RE.search(x)],
                }
                note_parts = []
                if caption:
                    note_parts.append('已从 figcaption/附近文本恢复图注')
                if alt or title_attr or aria:
                    note_parts.append('已记录 alt/title/aria 信息')
                if line_refs:
                    note_parts.append('正文存在图表提及线索')
                visuals.append({
                    'visual_id': visual_id,
                    'chapter_id': f'ch{chapter_counter:02d}',
                    'type': visual_type,
                    'title_or_caption': caption or alt or title_attr or aria,
                    'locator': full_path,
                    'is_key_evidence': bool(caption or line_refs),
                    'extractable_fields': extractable_fields,
                    'confidence': 'high' if caption else 'medium' if (alt or title_attr or aria) else 'low',
                    'notes': '；'.join(note_parts) if note_parts else '来自 EPUB HTML 的视觉对象，需要结合正文进一步判断其证据作用。',
                })
                visual_ids.append(visual_id)
            if chapter_counter <= len(chapters):
                chapters[chapter_counter - 1]['has_visual_material'] = bool(visual_ids)
                chapters[chapter_counter - 1]['visual_ids'] = visual_ids
            chapter_counter += 1

    extracted_text = clean_text('\n'.join(parts))
    write_text(work_dir / 'extracted_text.md', extracted_text)
    write_text(work_dir / 'toc_raw.md', '\n'.join(toc_lines) if toc_lines else '# 未恢复到可靠目录\n')
    write_json(work_dir / 'images_manifest.json', {'visuals': visuals})

    book_structure = read_json(work_dir / 'book_structure.json', {})
    book_structure.update({
        'title': book_structure.get('title') or title,
        'source_type': 'epub',
        'structure_confidence': 'high' if chapters else 'medium',
        'chapters': [
            {
                'chapter_id': ch['chapter_id'],
                'title': ch['chapter_title'],
                'order': ch['order'],
                'start_locator': ch['start_locator'],
                'end_locator': ch.get('end_locator', ''),
            }
            for ch in chapters
        ],
        'notes_on_extraction': notes or ['EPUB 已完成基础提取。'],
    })
    write_json(work_dir / 'book_structure.json', book_structure)
    if chapters:
        write_json(work_dir / 'chapter_index.json', {'chapters': chapters})
    return {
        'source_type': 'epub',
        'title': title,
        'chapters_count': len(chapters),
        'visuals_count': len(visuals),
        'notes': notes,
    }


def extract_pdf(source: Path, book_dir: Path) -> dict[str, Any]:
    from pypdf import PdfReader

    work_dir, _ = ensure_dirs(book_dir)
    notes: list[str] = []
    visuals: list[dict[str, Any]] = []
    chapters: list[dict[str, Any]] = []
    reader = PdfReader(str(source))
    title = source.stem
    try:
        if reader.metadata and getattr(reader.metadata, 'title', None):
            title = str(reader.metadata.title).strip() or title
    except Exception:
        pass

    outline_lines: list[str] = []
    try:
        outlines = getattr(reader, 'outline', None) or getattr(reader, 'outlines', None)
        flat: list[tuple[str, Any]] = []

        def walk(items: Any) -> None:
            if isinstance(items, list):
                for item in items:
                    walk(item)
                return
            try:
                if hasattr(items, 'title'):
                    flat.append((str(items.title), items))
                elif isinstance(items, dict) and 'title' in items:
                    flat.append((str(items['title']), items))
            except Exception:
                pass
            if hasattr(items, 'children'):
                try:
                    for child in items.children:
                        walk(child)
                except Exception:
                    pass

        if outlines:
            walk(outlines)
        for idx, (label, item) in enumerate(flat, start=1):
            page_no = ''
            try:
                page_no = reader.get_destination_page_number(item) + 1
            except Exception:
                page_no = ''
            outline_lines.append(f'{idx}. {clean_text(label)}' + (f' -> p.{page_no}' if page_no else ''))
            chapters.append({
                'chapter_id': f'ch{idx:02d}',
                'chapter_title': clean_text(label),
                'chapter_aliases': [],
                'order': idx,
                'start_locator': f'p.{page_no}' if page_no else '',
                'end_locator': '',
                'subsections': [],
                'has_visual_material': False,
                'visual_ids': [],
                'analysis_status': 'indexed',
            })
    except Exception as exc:
        notes.append(f'PDF 书签读取失败: {exc}')

    parts: list[str] = [f'# {title}', '']
    image_counter = 1
    page_count = len(reader.pages)
    page_texts: list[str] = []
    for page_num, page in enumerate(reader.pages, start=1):
        try:
            text = clean_text(page.extract_text() or '')
        except Exception as exc:
            notes.append(f'第 {page_num} 页文本提取失败: {exc}')
            text = ''
        page_texts.append(text)
        parts.append(f'\n\n## 第 {page_num} 页\n')
        parts.append(text or '（该页未提取到可靠文本）')

    for page_num, page in enumerate(reader.pages, start=1):
        page_text = page_texts[page_num - 1]
        lines = [ln.strip() for ln in page_text.splitlines() if ln.strip()]
        caption_candidates = [ln[:240] for ln in lines if CAPTION_RE.search(ln)][:6]
        nearby_refs = capture_nearby_refs(lines)
        page_visual_ids: list[str] = []
        try:
            images = getattr(page, 'images', [])
        except Exception:
            images = []
        for img in images:
            filename = getattr(img, 'name', '') or ''
            name_hint = filename if isinstance(filename, str) else ''
            caption = caption_candidates[0] if caption_candidates else ''
            visual_type = classify_visual_type(caption or name_hint)
            visual_id = f"{'tbl' if visual_type == 'table' else 'fig'}-p{page_num:03d}-{image_counter:02d}"
            image_counter += 1
            visuals.append({
                'visual_id': visual_id,
                'chapter_id': '',
                'type': visual_type,
                'title_or_caption': caption,
                'locator': f'p.{page_num}',
                'is_key_evidence': bool(caption or nearby_refs),
                'extractable_fields': {
                    'filename': name_hint,
                    'caption_candidates': caption_candidates,
                    'nearby_references': nearby_refs,
                },
                'confidence': 'medium' if caption else 'low',
                'notes': 'PDF 页面级恢复：已记录同页 caption 候选与图表正文提及。',
            })
            page_visual_ids.append(visual_id)
        if page_visual_ids and chapters:
            for ch in chapters:
                loc = ch.get('start_locator', '')
                if loc == f'p.{page_num}':
                    ch['has_visual_material'] = True
                    ch['visual_ids'].extend(page_visual_ids)
                    break

    if not chapters:
        notes.append('未读取到 PDF 书签目录，chapter_index.json 暂不自动回填。可后续结合目录页或标题模式补建。')
    if not any(re.search(r'\S', p) for p in page_texts):
        notes.append('PDF 未提取到可靠正文，可能是扫描版或权限限制。')

    write_text(work_dir / 'extracted_text.md', clean_text('\n'.join(parts)))
    write_text(work_dir / 'toc_raw.md', '\n'.join(outline_lines) if outline_lines else '# 未恢复到可靠目录\n')
    write_json(work_dir / 'images_manifest.json', {'visuals': visuals})
    if chapters:
        write_json(work_dir / 'chapter_index.json', {'chapters': chapters})

    book_structure = read_json(work_dir / 'book_structure.json', {})
    book_structure.update({
        'title': title,
        'source_type': 'pdf',
        'structure_confidence': 'medium' if chapters else 'low',
        'chapters': [
            {
                'chapter_id': ch['chapter_id'],
                'title': ch['chapter_title'],
                'order': ch['order'],
                'start_locator': ch['start_locator'],
                'end_locator': ch.get('end_locator', ''),
            }
            for ch in chapters
        ],
        'notes_on_extraction': notes or ['PDF 已完成基础文本提取。'],
    })
    write_json(work_dir / 'book_structure.json', book_structure)
    return {
        'source_type': 'pdf',
        'title': title,
        'pages_count': page_count,
        'chapters_count': len(chapters),
        'visuals_count': len(visuals),
        'notes': notes,
    }


def update_readme(book_dir: Path, summary: dict[str, Any], source_name: str) -> None:
    readme = book_dir / 'output' / '00_readme.md'
    lines = [
        '# 阅读说明',
        '',
        f'- 源文件名：{source_name}',
        f'- 文件类型：{str(summary.get("source_type", "")).upper()}',
        f'- 暂定书名：{summary.get("title", source_name)}',
        '- 书型判断：待判断',
        '- 判断依据：待在完成章节分析后填写。',
        '- 实际启用的分支关注点：待填写。',
        '- 结构恢复置信度：' + ('高' if summary.get('chapters_count', 0) > 0 and summary.get('source_type') == 'epub' else '中' if summary.get('chapters_count', 0) > 0 else '低'),
        f'- 识别到的章节数量：{summary.get("chapters_count", 0)}',
        '- 预处理中的主要问题：' + ('；'.join(summary.get('notes', [])) if summary.get('notes') else '无明显错误。'),
        f'- 图片/图表保留情况说明：已登记 {summary.get("visuals_count", 0)} 个视觉对象，并尽量回收图注/alt/正文引用线索。',
        '',
        '## 文件使用建议',
        '',
        '1. 先检查 `work/extracted_text.md` 与 `work/toc_raw.md`。',
        '2. 再检查 `work/chapter_index.json` 是否需要人工修正。',
        '3. 图片、图表与表格先看 `work/images_manifest.json`。',
        '4. 确认后再生成逐章精读与全书综合文件。',
    ]
    write_text(readme, '\n'.join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--book-dir', required=True)
    args = parser.parse_args()

    book_dir = Path(args.book_dir).resolve()
    source = detect_source(book_dir)
    try:
        summary = extract_epub(source, book_dir) if source.suffix.lower() == '.epub' else extract_pdf(source, book_dir)
        update_readme(book_dir, summary, source.name)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        print('[OK] 已完成基础提取并回填 work/ 中间文件')
    except Exception as exc:
        traceback.print_exc()
        raise SystemExit(f'提取失败: {exc}')


if __name__ == '__main__':
    main()
