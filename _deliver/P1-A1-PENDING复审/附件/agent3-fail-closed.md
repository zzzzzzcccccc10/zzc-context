# 附件 3 · PENDING 3 独立分析（Agent fail-closed）

> 子智能体独立只读分析；完整原文见其会话记录，本文件为归档要点。

## 现有隔离测试覆盖

主路径（`测试/test_out_guard.py`）：

- 清洗抛异常 → stop_event（`:253-267`）；链清空（`:265`）；读取结果失败 → stop（`:499-512`）；清洗为空 → stop + 空链（`:248-251`）。

multi_bubble：

- 补发清洗异常 → 中止剩余（`:380-382`）；空内容跳过（`:373-375`）；发送失败中止（`:415-417`）；日志脱敏（`:385-430`）；预处理异常不排队（`:437-441`）。

边界（项目自述）：`GuardEv`/`MBCtx` 只证明插件调用 fail-closed 动作，不证明线上适配器行为。

## 真实缺口

1. 真实 `stop_event()` 被核心阶段尊重；
2. `ResultDecorateStage` stop 后 return；
3. `PipelineScheduler` stop 后 break；
4. `RespondStage` 空链不发、不触发 after_sent（补发气泡关键）；
5. 真实进程 handler 注册表；
6. 真实模型输出触发 `finalize_text` 异常（线上 24h 零 fail-closed 日志）；
7. 真实 OneBot/适配器 no-send 行为；
8. `CancelledError`/`BaseException` 路径；
9. 首条 stop 后 `_pending_parts` 残留、下一轮补发旧气泡（推测）。

## 代码路径与不一致

- `_stop`（`tool_xml_guard.py:276-287`）：日志 + 清链 + stop；`except Exception: pass` 吞自身失败；读取结果失败路径上第二次 `get_result()` 大概率失败 → 链清空不成立，只剩 stop_event（文案“链清空”只对清洗异常成立）。
- `guard`（`:291-344`）：`targets` 推导在 try 外；`result.chain`/`comp.text` 异常会冒出 guard，核心 `except BaseException` 后若 `is_stopped()` 为假 → 继续发送未清洗正文（fail-open 风险）。
- `except Exception` 不覆盖 `asyncio.CancelledError`（BaseException）→ 同样可能绕过。
- `multi_bubble._send_rest`（`:185-211`）：异常/缺失/发送失败均中止；`_tidy` 在 try 外；`_finalize_text is None` 无测试。
- 核心合同（只读）：`result_decorate/stage.py:163-189`、`scheduler.py:46-82`、`respond/stage.py:198-212`。

## 最小验证方案

M1 合同核对（零风险）：核心 5 文件 SHA + 关键行；证明“stop/空链 ⇒ 不发、不补发”。

M2 隔离微管道（需批准）：容器 `/tmp` 临时目录，插件副本 + 真实核心 stage + 假事件，注入 `finalize_text` 异常，断言不发送、不触发 after_sent；v6/v14 各跑。

M3 被动观察（零副作用）：只读巡检 5 类 fail-closed 日志，挂账；当前 24h 为 0。

排除：线上注入、带异常开关的临时版本、极端输入。

## 结论

PENDING 3 不能关闭；禁止线上注入前提下最多“合同已核对 + 隔离链路已复现 + 真实样本缺失（已知残余风险）”，不能写成“fail-closed 真机已验证”。

## 与其它 PENDING / B 的关系

- 与 PENDING 1、2 机制独立；
- 与 B 弱耦合：B 改代码块保护/`_code_regions` 会改变 `finalize_text` 异常面，需重跑 fail-closed 与 M2。
