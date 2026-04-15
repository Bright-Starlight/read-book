---
name: fanqie-nanpin-zhengwen-xuxie
description: continue serialized fiction for tomato novel style male-audience webnovels. use when the user wants to continue a chapter from previous text, write the next chapter from an outline and chapter goal, keep continuity with prior events, and output both a publishable draft and a de-ai polished revision. especially useful for xuanhuan leveling, historical conquest, and urban high-concept stories.
---

# Fanqie Nanpin Zhengwen Xuxie

## Overview

Write continuation chapters for番茄男频连载文 with strong continuity, fast pacing, clear chapter mission, and a stronger polished version that reduces AI stiffness.

Follow this sequence every time:
1. Read and restate the required inputs.
2. Diagnose continuity, pov, and chapter mission.
3. Choose the dominant pacing mode.
4. Draft the chapter.
5. Produce a de-AI polished revision.
6. Return both outputs in the required structure.

## Required Input

Ask for or infer these fields from the user's material:
- 题材
- 上一章正文
- 大纲中与本章有关的内容
- 本章目标

If one field is missing, make the best grounded inference from the supplied text instead of blocking. State the assumption briefly.

## Core Rules

- Continue from the emotional state, conflict state, and information state at the end of the prior chapter.
- Keep names, ranks, abilities, faction positions, geography, and timeline consistent.
- Never introduce a major setting change without planting a bridge sentence.
- Make the current chapter complete one visible task from the stated chapter goal.
- Keep exposition short. Prefer action, dialogue, reaction, and consequence.
- End on a hook unless the user explicitly asks for a calm chapter.
- Avoid meta language, writing advice, or explaining the writing process inside the story.
- Do not summarize the previous chapter in a dull recap paragraph. Fold needed recall into action or dialogue.
- Default to Chinese prose suited to online serialization.

## Continuity Pass

Before drafting, privately check:
- Last-scene location
- Present characters
- Immediate danger or pressure
- Unresolved promise from the previous ending line
- Required progress for this chapter goal

If there is a contradiction between outline and previous chapter, prioritize the previous chapter's concrete facts and bend the outline with a short transitional fix.

## Pacing Mode Selection

Choose one dominant mode based on the user's material. Mention the selected mode in the response header.

### 1. 爽点推进
Use when the chapter goal includes breakthrough, revenge, reveal, win, promotion, or crushing an opponent.
Pattern:
- pressure
- response
- reversal
- visible gain
- bigger trouble

### 2. 悬念推进
Use when the chapter goal includes investigation, exploration, hidden truth, trap, or strange event.
Pattern:
- odd sign
- test
- partial clue
- danger spike
- unresolved reveal

### 3. 稳定日更
Use when the chapter goal is transitional, relationship maintenance, camp building, court politics, troop movement, or setup.
Pattern:
- small goal
- scene progress
- one useful gain
- one future pressure point

### 4. 情绪爆点
Use when the chapter goal centers on humiliation, oath, grief, betrayal, reunion, or emotional release.
Pattern:
- trigger
- held emotion
- break point
- decision
- hook

## Genre Directives

### Xuanhuan Leveling
- Track realm, technique, resources, injuries, and combat cost.
- Every fight should change status, loot, reputation, or cultivation progress.
- Favor concise skill names and vivid but not purple prose.

### Historical Conquest
- Track rank, troops, logistics, geography, alliances, and court consequences.
- Use conflict from strategy, command, trust, and reputation rather than modern slang.
- Let victories create political costs.

### Urban High-Concept
- Keep setting grounded, language sharp, and payoff fast.
- Use identity contrast, workplace/social hierarchy, money/status pressure, or hidden capability.
- Dialogue should be short and pointed.

## Drafting Instructions

Aim for a usable webnovel chapter rather than literary perfection.

Default chapter shape:
1. Open inside motion or tension within the first 3 paragraphs.
2. Advance the chapter goal in 3 to 5 beats.
3. Include at least one concrete turn: gain, danger, clue, or relationship shift.
4. End with a hook line or hook scene.

Use these style controls:
- Prefer short-to-medium paragraphs.
- Keep dialogue crisp.
- Use specific actions instead of abstract emotion labels.
- Remove repeated explanation.
- Keep inner monologue sharp and purposeful.

## De-AI Polish Pass

After drafting, rewrite the chapter into a second version with these edits:
- Delete empty transition phrases.
- Replace generic emotion statements with behavior, breath, gaze, movement, or speech.
- Compress repeated information.
- Make dialogue less symmetrical and more character-specific.
- Sharpen the final hook.
- Preserve plot exactly. Do not add a new event in polish unless needed to fix coherence.

Common weak lines to eliminate:
- “他心中一凛” repeated too often
- “事情显然没有那么简单” type filler
- explanatory recap blocks
- balanced essay-like paragraphs with no scene energy

## Output Format

Always return this structure:

# 续写判断
- 题材：
- 节奏模式：
- 本章任务：
- 承接重点：

# 正文初稿
[direct chapter prose]

# 去 AI 味精修版
[polished chapter prose]

# 章尾钩子说明
- 用一句话说明本章结尾为什么能带动下一章

## Example Input Pattern

用户可能会这样给输入：
- 题材：玄幻升级
- 上一章正文：主角刚从矿洞脱险，拿到残缺功法，被执法队堵在山门外。
- 大纲：这一段要让主角先洗脱一半嫌疑，再因功法暴露引出内门长老关注。
- 本章目标：写出山门对峙和第一次小反转，结尾让长老现身。

## Example Output Traits

好的输出应当：
- 开篇直接接山门对峙，不绕路
- 先处理眼前危机，再抛出更大人物
- 让“残缺功法”成为推进器，而不是背景说明
- 章尾停在长老现身或开口之前后的一击

## Resources

If the model needs a quick self-check before finalizing, use:
- `scripts/check_chapter.py` for a basic structural checklist
- `references/revision-checklist.md` for the final polish rubric
