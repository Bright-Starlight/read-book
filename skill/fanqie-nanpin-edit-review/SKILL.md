---
name: fanqie-nanpin-edit-review
description: revise and review fanqie male-fiction chapters for xuanhuan progression, historical power struggle, and urban brain-hole stories. use when the user wants chapter polishing, revision, line editing, quality review, ai-tone reduction, pacing diagnosis, hook strengthening, scene compression, dialogue tightening, continuity checks, or a publish-ready rewrite for tomato-style webnovel chapters.
---

# Fanqie Nanpin Edit Review

## Overview

Use this skill to turn rough or overly artificial webnovel chapters into tighter, more publishable Fanqie male-fiction prose. Prioritize readable momentum, clean payoff, chapter-end pursuit value, and human-sounding delivery over decorative language.

## Workflow decision

Follow this order every time:

1. **Identify the task mode**
   - If the user gives a full chapter and asks to fix or polish it, use **full-chapter revision**.
   - If the user gives a short passage and asks what is wrong, use **diagnosis-first review**.
   - If the user gives a chapter plus concerns such as "too much ai flavor" or "no爽点", use **targeted repair**.
2. **Extract hard constraints**
   - Preserve character names, realm/stage names, faction names, timeline facts, and key plot outcomes unless the user asks for structural changes.
   - Preserve the intended genre lane: xuanhuan progression, historical power struggle, or urban brain-hole.
3. **Diagnose before rewriting**
   - Briefly identify the main issues in priority order.
4. **Rewrite only after deciding the fix path**
   - Fix the few most damaging problems first: weak opening, flat conflict, repetitive explanation, fake-sounding dialogue, no chapter-end hook.
5. **Return usable output**
   - Always provide a clean revised chapter or revised excerpt.
   - When the user asks for review, include concise notes before the revision.

## Inputs to expect

Typical useful inputs are:
- Current chapter text
- Previous chapter summary or previous chapter ending
- Brief outline for this chapter
- User goal such as "go harder on爽点" or "remove ai flavor"

If some context is missing, proceed with the provided text and preserve as much continuity as possible instead of stalling.

## Output modes

Choose the lightest output that satisfies the request.

### Mode A: diagnosis-first review

Use when the user asks what is wrong or asks for审稿意见.

Default structure:

```markdown
## 核心问题
- [Issue 1]
- [Issue 2]
- [Issue 3]

## 修改方向
- [Fix 1]
- [Fix 2]

## 精修示例
[Rewrite only the most relevant excerpt or the whole section if short]
```

### Mode B: full-chapter revision

Use when the user wants a whole chapter polished.

Default structure:

```markdown
## 审稿结论
[1 short paragraph]

## 改后正文
[Rewritten chapter]
```

### Mode C: targeted repair

Use when the user names a specific issue such as 节奏慢、对话假、像AI写的.

Default structure:

```markdown
## 定向处理
- [What was targeted]

## 改后正文
[Rewritten text]
```

## Genre-specific revision rules

### 1. Xuanhuan progression

Emphasize:
- Clear hierarchy pressure
- Visible resource stakes
- Immediate humiliation or danger before payoff
- Step-by-step gain, not vague power inflation
- Harder line endings and cleaner combat beats

Prefer:
- Shorter internal monologue
- Concrete sensory/action verbs
- Distinct cultivation/resource nouns
- Endings that point to the next fight, next breakthrough, or next suppression attempt

Avoid:
- Repeating the same awe reaction from side characters
- Abstract power descriptions without cost or comparison
- Explaining mechanics twice in the same scene

### 2. Historical power struggle

Emphasize:
- Position, leverage, coalition, reputation, military or court consequence
- Strategy hidden inside conversation
- Cause and effect between one move and later backlash
- Restraint in language; sharper subtext than shouting

Prefer:
- Dialogue with layered motive
- Short political observations tied to advantage or risk
- Chapter endings that reveal a counter-move, decree, betrayal, or military shift

Avoid:
- Modern slang that breaks period texture unless the setting explicitly allows it
- Everyone stating motives directly
- Empty grand speeches with no tactical value

### 3. Urban brain-hole

Emphasize:
- Fast hook in the first screen
- Everyday setting smashed by absurd/clever twist
- Strong contrast between ordinary social reality and the protagonist's abnormal advantage
- Crisp face-slapping and instantly legible gains

Prefer:
- Short scene turns
- Punchy dialogue
- Concrete social stakes: money, status, embarrassment, traffic, school, workplace, livestream, family expectations

Avoid:
- Long worldbuilding dumps
- Re-explaining the gimmick every scene
- Soft endings with no next-click impulse

## Fanqie male-fiction quality bar

Check these in order:

1. **Opening pull**
   - Does the first paragraph create pressure, conflict, or curiosity?
   - If not, cut setup and enter later.
2. **Conflict clarity**
   - Can the reader tell what the protagonist wants in this chapter and what blocks it?
3. **Payoff density**
   - Is there at least one meaningful gain, reversal, or reveal?
4. **Dialogue credibility**
   - Do different characters sound different?
   - Remove speech that only exists to explain the plot to the reader.
5. **Narrative compression**
   - Delete repeated explanation, repeated emotion labels, and repeated recap.
6. **Ending force**
   - End on danger, reversal, discovery, vow, or imminent confrontation.

## Anti-ai-flavor rules

When the user asks to去ai味, enforce these aggressively:

- Replace generic emotional explanation with physical reaction or choice.
- Cut transition fillers such as "与此同时" "然而" "就在这时" when overused.
- Break overly symmetrical sentence patterns.
- Reduce stacked abstract adjectives.
- Replace summary statements with one concrete detail.
- Shorten dialogue; make characters interrupt, evade, mock, threaten, or test each other.
- Remove redundant moralizing and reader-facing explanation.
- Keep some roughness if it improves human feel; do not over-polish into formal prose.

### Common weak-to-strong transformations

Weak:
- He felt extremely shocked.
- Everyone was very surprised.
- The atmosphere became tense.

Better:
- His fingers stopped on the cup rim.
- The room went quiet enough to hear sleeves drag across the table.
- No one answered him. That silence was the answer.

Weak:
- He knew this matter was not simple.

Better:
- He glanced at the seal a second time and did not reach for it.

## What to cut first

When compression is needed, cut in this order:

1. Repeated recap
2. Empty emotion labels
3. Generic scenery not tied to action or mood pressure
4. On-the-nose explanation of motives
5. Side-character amazement loops

## Chapter-end hook rules

If the ending is weak, rebuild it around one of these:
- A stronger enemy arrives
- A hidden cost appears
- A key identity is exposed
- The protagonist makes a dangerous decision
- A previous victory turns unstable
- A new rule, decree, or system prompt changes the game

Endings should make the next click feel necessary, not merely possible.

## Review language rules

When giving critique:
- Be direct, not academic.
- Focus on what hurts retention and satisfaction.
- Keep notes short unless the user asked for a detailed breakdown.
- Pair every major criticism with a concrete revision move.

## Safe default behavior

If the user gives only raw chapter text and says "改", do this by default:

1. Provide a 2-4 bullet diagnosis.
2. Output a full revised version.
3. Preserve plot facts and names.
4. Strengthen the first paragraph and the last paragraph.
5. Reduce explanation by at least one visible layer.

## Mini examples

### Example 1: xuanhuan pacing fix

Input intent:
- "这章太水了，帮我改得更有升级爽感。"

Good response behavior:
- Say the problem is delayed conflict, repetitive reactions, and vague gain description.
- Rewrite so the protagonist faces pressure earlier, obtains a specific resource or breakthrough, and ends with a bigger enemy or consequence.

### Example 2: historical dialogue fix

Input intent:
- "朝堂戏太像现代人聊天，帮我修。"

Good response behavior:
- Keep motives indirect.
- Put status and leverage inside phrasing.
- Reduce direct explanation and use subtext.

### Example 3: urban brain-hole ai-flavor fix

Input intent:
- "帮我去ai味，顺便把结尾钩子做强。"

Good response behavior:
- Tighten sentence rhythm.
- Make dialogue more pointed.
- Replace generic surprise statements with concrete reactions.
- End on a reveal, trap, or imminent public embarrassment.
