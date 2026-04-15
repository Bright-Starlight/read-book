# 视觉材料处理补充

本文件补充说明如何在不默认启用 OCR 的前提下，提高视觉材料的可用性。

## 优先回收的线索

1. EPUB/HTML
- `figure > figcaption`
- `img[alt]`
- `img[title]`
- `aria-label`
- 图片前后相邻段落中出现的“图/表/Figure/Table”字样

2. PDF
- 同页文本中以“图 / 表 / Figure / Table”开头的 caption 候选行
- 同页正文中“见图”“如下表”“如图所示”这类提及
- 图像对象文件名或对象名中的线索

## 字段解释

- `title_or_caption`：首选图注，其次 alt/title/aria 等可验证说明。
- `extractable_fields.nearby_references`：附近正文对该视觉对象的提及。
- `extractable_fields.caption_candidates`：PDF 页面级恢复出的 caption 候选。
- `is_key_evidence`：只表示当前已发现图注或正文提及线索，不等于已完成论证判断。

## 使用建议

- 先看 `work/images_manifest.json`，确认有没有高价值视觉对象。
- 再看 `output/06_图表索引.md`，快速浏览标题、线索和章节归属。
- 最后回到对应 `chapters/chNN_章节精读.md`，把视觉对象与正文论证绑起来。
