# 附件 2 · PENDING 2 独立分析（Agent style-strip）

> 子智能体独立只读分析；完整原文见其会话记录，本文件为归档要点。

## 调用链（实际顺序）

AstrBot v4.29.4：`handlers.sort(key=lambda h: -priority)` → **priority 降序**。装饰阶段 8 个注册点：

`meme_manager(99999) → style_strip(90) → face_map(80) → rule_guard(80) → recall_guard(70) → quote_reply(60) → chuanhuatong(-10) → tool_xml_guard(-1000000)`。

（旧材料 `审查-P1-A0…:36-37` 写“升序”、`审查-P1-A2…` 的顺序表把 rule_guard 排在 style_strip 前，均错误。）

链路：provider → `completion_text` → `on_llm_response` → `internal.py` 构建 chain → `ResultDecorateStage`（8 钩子）→ `RespondStage` → `after_sent`（multi_bubble 补发直发）。

## 关键证据（DB 只读 + 日志）

- 会话 `176b02ad-bd0c-45e6-9a92-b2272837cc58` 的 `conversations.content`：
  - msg 36 user：代码块复述请求；
  - **msg 37 assistant：`def add(a, b):\n    result = a + b\n    return result\n\nprint(add(2, 3))`（69 字符，格式完好）**。
- 最终实发（AstrBot `Prepare to send` 00:15:58.936）：`def add(a，b):\nresult = a + b\nreturn result\nprint(add(2，3))`（58 字符）。
- SnowLuma 协议端 00:16:02 发送日志同形（截断尾部略）。
- 确定性重放（线上 style_strip SHA `bb2e9984…`）：`fix_quotes(restyle(squash_blank(raw), 400))` 输出与实发**逐字节相等**；rule_guard/multi_bubble/tool_xml_guard 的输出均不符；style_strip 输出再喂 rule_guard 不变（不动点）。
- 该轮 multi_bubble 只有 `想 1.8s`，无“首条走管道，排队…”日志 → 未拆分；tool_xml_guard 无 marker 未改；rule_guard 无日志。
- 版本钉住：style_strip `bb2e9984…`、tool_xml_guard v6 `c4497e04…`、multi_bubble `5e2519…`。

## 归因结论

变化环节 = `style_strip.on_decorating`（priority=90）的 `squash_blank()`（删空行）+ `restyle()`（`,→，`；`[ \t]{2,}→1`；行首空白清零 → 0 缩进）。**归因已闭合**（针对这一轮）。

## 与 B 的关系

同根因、不同验收：PENDING 2 是归因；B 是修复。不能互相替代。B 必须覆盖**无围栏的纯文本代码**（本轮真实形态），否则原样复发。相邻通道（`multi_bubble._tidy`、`rule_guard.strip_stage`）建议独立立项，不混进 B 验收。

## 已证实 / 推测 / 未知

- 已证实：DB 原文、最终实发、逐字节重放、排除项、版本钉住；
- 推测：链上其它钩子对这段文本恒等（未运行时 dump）；
- 未知：QQ 客户端渲染、历史其它轮次、`max_len=400` 是否合理。

## 最小验证方案

A：DB + 历史日志 + 重放（已执行）；
B：离线钩子链重放（B 修复后断言 `final == raw`）；
C：只读观测三哈希（`hash(raw)`/`hash(style_strip(raw))`/`hash(final)`），需批准。

## 风险

- 证据时效（docker logs/DB 可能被清理）；
- 旧材料钩子顺序错误，可能污染后续推理；
- B 只保护围栏 → 漏掉真实形态；
- 保护范围未裁定（围栏/无围栏/行内/URL/引号）。
