# 附件 1 · PENDING 1 独立分析（Agent p1a1-dsml）

> 子智能体独立只读分析；完整原文见其会话记录，本文件为归档要点（保留关键证据、结论、方案）。
> 主 Agent 已在正文交叉复核，并以 DB 原文修正了其“推测”为“已证实”。

## 问题定义

v6 在真实 QQ 链路里，对完整标记 `<｜｜DSML｜｜ calls>` 的端到端清理是否成立。2026-11-19 真机：入站含完整标记，cleaner 执行（`req=91584d1eff55`），实发 `前缀A ｜｜ calls 后缀B`（残片）。

## 关键证据

- 线上 2026-11-19 00:15:31 入站完整标记；00:15:40.957 `[tool_xml_guard] 已把控制标记从消息里删掉 req=91584d1eff55`；00:15:40.960 实发 `[引用消息] 前缀A ｜｜ calls 后缀B`；00:15:43.753 已发出（docker logs 行号 124621 附近）。
- v6 对完整多行 DSML 隔离清理 `""`，88 项 ALL PASS（`reviews/P1-A1-v6/测试日志.txt:54,216`）。
- 内存实测（v6 源码，`python -B`）：
  - `前缀A <｜｜DSML｜｜ calls> 后缀B` → `前缀A  后缀B`；
  - v6 完整多行 LEAK → `""`；
  - `前缀A ｜｜DSML｜｜ calls 后缀B` → `前缀A ｜｜ calls 后缀B`（与实发逐字一致）；
  - `前缀A ｜｜ calls 后缀B` → 不变；
  - `前缀A <｜｜DSML｜｜ calls POST`（无 `>`）→ `前缀A `（吞同行后文）。
- v14 实测：完整/裸标记均能清理；裸标记无 `>` → `前缀A   后缀B`。
- 中间层排除：multi_bubble `MIN_LEN=28` 未参与；style_strip 不删 `<>｜DSML`；rule_guard 该轮无重生成；chuanhuatong 未改写。

## 结论（主 Agent 修正后）

- **已证实（DB 补强）**：该轮模型输出是裸标记 `前缀A ｜｜DSML｜｜ calls 后缀B`（无尖括号）；v6 的 `replace("｜DSML｜","")` 必然留下 `｜｜ calls`。完整标记没有以原样到达 cleaner。
- v6 对完整标记的隔离处理是干净的；PENDING 1 的“完整标记真实 E2E 未验证”仍成立，根因是模型输出不可控，不是 cleaner 缺陷。
- 未知：模型为何输出裸标记（provider/解码层）；真实完整标记样本仍无；运行时注册表全集。

## 最小验证方案

L0 纯函数：M1 完整单标记→`前缀A  后缀B`；M2 完整 LEAK→`""`；M3 裸标记→`前缀A ｜｜ calls 后缀B`；M4 残片不变；M5 无 `>` 完整标记吞行（记录）；M6 幂等。

L1 钩子层：裸标记改写；完整 LEAK → stop + 空链；`finalize_text` 抛异常 → stop + 不残留。

L2 管道层：stub provider 固定返回完整标记，捕获出站 payload，跑真实 `ResultDecorateStage → RespondStage`，断言 `前缀A  后缀B`。

## 风险

- 验收对象错位（v6 vs v14）；
- 回滚 v6 会重新引入裸标记残片、无 `>` 吞行；
- 本地测试文件是 v14，对 v6 跑会预期性 FAIL；
- 关键日志未归档，轮转后丢失；
- 把隔离测试写成 E2E 会越界。
