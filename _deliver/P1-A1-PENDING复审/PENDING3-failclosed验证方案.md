# PENDING 3 fail-closed 验证方案

- **文档类型**：验证方案（待批准，未执行）
- **任务**：P1-A1 PENDING 3「fail-closed 真实线上故障注入未验证」的分层验证
- **版本**：v1
- **日期**：2026-11-22
- **更新时间**：2026-11-22 15:07（Asia/Shanghai）
- **当前状态**：**方案完成，待批准；未执行线上注入/未改线上**
- **线上版本**：`bba95b71…`（P3 修复，基于 v14）

## 一、目标与约束

目标：验证“清洗异常 → 不发送/不补发”的 fail-closed 行为。

约束：

- **禁止线上故障注入**（不 monkeypatch、不调试器、不临时版本、不构造极端输入）；
- 不重启、不改配置；
- 不能把隔离测试写成“真机已验证”。

## 二、已有证据

### M1 合同核对（已完成）

- `ResultDecorateStage` 对 handler 异常 `except BaseException` 后检查 `is_stopped()`；
- `PipelineScheduler` 在 `is_stopped()` 后 break；
- `RespondStage` 空链不发、不触发 `OnAfterMessageSentEvent`；
- 核心文件 SHA 已记录（见 L2/M2 执行报告）。

### M2 隔离微管道（已完成）

- 真实 `ResultDecorateStage` + 假事件/假发送端；
- 覆盖：`get_result`、chain 遍历、`comp.text`、`has_marker`、`parse_invokes`、`finalize_text`、`save_proposal`、`stop_event` 自身、`CancelledError`、`KeyboardInterrupt`、双重故障；
- 修复后 27 项 ALL PASS；v14 原 204 项回归 ALL PASS；
- 曾复现 fail-open（`has_marker` 异常 → 未 stop → 发送未清洗原文），已由 P3 修复并复测。

### 线上被动观察（可继续）

- 巡检 5 类日志：`读取结果失败` / `清洗异常` / `补发清洗失败` / `清洗器不可用` / `预处理清洗失败`；
- 当前 24 小时窗口：0 条；
- 容器日志轮转后不可追溯。

## 三、验证层级设计

| 层 | 内容 | 状态 | 能证明 |
|---|---|---|---|
| L1 合同 | 核心源码 + SHA + 关键行 | 已完成 | “stop/空链 ⇒ 不发、不补发”是核心显式合同 |
| L2 隔离 | 真实 stage + 假事件/假发送端 + 注入 | 已完成（修复后 27 项） | 插件异常时会 stop；修复后无出站 |
| L3 线上被动 | 只读日志巡检 | 进行中（当前 0 条） | 自然触发时才有的真机证据 |
| L4 线上注入 | **禁止** | 不执行 | — |

## 四、验收口径

1. **不能关闭 PENDING 3**：没有真机异常样本，不能写“fail-closed 真机已验证”。
2. 可写“**合同已核对 + 隔离已复现 + 真机样本缺失（已知残余风险）**”。
3. 若主人接受降级：记为“已缓解”，但保留 PENDING 3 未关闭；不写成 PASS。
4. 双重故障边界：清链与 `stop_event` 同时失败时不能宣称绝对 fail-closed；当前只覆盖“stop 失败、清链成功”。
5. `CancelledError` 的传播会被核心 `except BaseException` 截断（核心行为），插件侧只保证 stop + re-raise。

## 五、后续可选（需单独批准）

1. 持续被动观察：每次巡检记录 5 类日志计数、req、上下文；只在自然触发时取证；
2. 隔离环境扩展：真实核心 + 插件副本 + 假事件，覆盖更多注入点（已覆盖主要点）；
3. **不**做：线上 monkeypatch、带异常开关的临时版本、极端输入触发、调试器注入。

## 六、待批准

1. 是否接受“合同 + 隔离 + 真机样本缺失”的当前口径；
2. 是否继续被动观察（只读）；
3. 是否安排隔离环境补充用例（不线上）。
