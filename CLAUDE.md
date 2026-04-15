# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在本仓库中工作时提供指导。

## 项目概述

这是一个**中文网文创作项目**（番茄男频小说创作）。

当前项目：《道韵之眼》—— 东方玄幻·升级流，主角觉醒能看穿万物"道韵"的特殊眼睛，经典废柴逆袭设定。

## 仓库结构

```
read-book/
├── 道韵之眼/                    # 当前小说项目
│   ├── 第*章_*.md             # 各章节正文
│   └── setting/                # 世界观设定文档
│       ├── 01_Rules.md         # 世界规则、修炼体系
│       ├── 02_Characters.md     # 人物卡
│       ├── 06_Timeline.md      # 绝对时间线
│       ├── 07_Plotlines.md     # 主线、伏笔、回收状态
│       ├── 09_Chapters.md      # 章节摘要、已发生事件、未解决问题
│       └── 10_Recaps.md        # 阶段总结、世界观沉淀
│
├── skill/                      # 小说创作技能
│   ├── fanqie-male-outline/    # 番茄男频大纲生成
│   ├── fanqie-nanpin-zhengwen-xuxie/  # 正文续写
│   ├── fanqie-nanpin-edit-review/     # 改稿审稿
│   └── social-book-decomposer/ # 书籍拆解/资料收集
│
├── novel-com.md                # 番茄男频三件套提示词合集
├── fanqie-nanpin-zhengwen-xuxie.skill  # 快速调用文件
└── fanqie-nanpin-edit-review.skill      # 快速调用文件
```

## 核心工作流

番茄男频小说标准三件套流程：

1. **大纲版** → `fanqie-male-outline` — 确定结构、大纲、章节目标
2. **正文续写版** → `fanqie-nanpin-zhengwen-xuxie` — 起草各章节
3. **改稿审稿版** → `fanqie-nanpin-edit-review` — 打磨、去AI味

提示词模板见 `novel-com.md`。

## 《道韵之眼》维护规范

续写新章节前：
1. 查看 `道韵之眼/setting/` 目录确认设定一致：
   - `09_Chapters.md` — 前章已发生事件、未解决线索
   - `07_Plotlines.md` — 当前伏笔状态、待回收悬念
   - `02_Characters.md` — 角色当前状态和关系

2. 章节文件命名格式：`第X章_章节名.md`，保存在 `道韵之眼/` 下

3. 使用技能 `/fanqie-nanpin-zhengwen-xuxie` 按大纲续写正文

4. 写完新章节后更新 `setting/` 下对应文件：
   - `09_Chapters.md` — 追加本章摘要和未解决问题
   - `10_Recaps.md` — 更新阶段总结

## 写作规范

- **每章字数**：4000+ 字符（中文）
- **节奏模式**：爽点推进、悬念推进、稳定日更、情绪爆点
- **输出格式**：每章单独一个 `.md` 文件
- **去AI味**：删除"他心中一凛"类公式化表达；压缩重复信息；对话更短更自然
- **章尾钩子**：每章结尾必须留钩子，除非明确要求写平静收尾

## 创作自由度说明

小说中的**世界观设定**（人物卡、关系、状态、秘密、世界规则、修炼体系、硬限制）可以自由发挥，不拘束于大纲原始设定。

当发现大纲设定有更好的发挥空间时，直接扩展或调整，无需死守原大纲。这些设定文件是活的文档，随创作推进持续更新。

---

## 重要约定

- `fanqie-nanpin-zhengwen-xuxie` 技能已更新，**只输出最终精修版**，不输出初稿/精修版对比
- 设定文件用数字前缀（01_、02_等）保证更新顺序
- 角色秘密和伏笔在 `07_Plotlines.md` 中标注"已回收/未回收"状态
- 写完每章自动将信息同步到/setting中的相关文件
