# P3 fail-open 修复设计（待批准，未施工）

- **文档类型**：修复设计（含改动范围与测试方案，不施工）
- **任务**：P1-A1 PENDING 3 的 fail-open 缺陷修复候选
- **版本**：以 v14（`2f180cf0…`）为基准；v6（`c4497e04…`）快照保持不变
- **日期**：2026-11-22
- **更新时间**：2026-11-22 12:45（Asia/Shanghai）
- **当前状态**：**设计完成，待复审；未改代码、未新增测试、未部署、未重启**
- **对应 commit**：`zzc` 分支 `p1-a2-v14` @ `91514773b2f04bcb83c20e8a1daaa6cfc359a475`（仅参考基准）

## 一、缺陷回顾

M2 复现：`has_marker(comp.text)` 在 `guard` 的 targets 推导中抛异常时，异常冒出 `guard`；
`ResultDecorateStage` 的 `except BaseException`（`result_decorate/stage.py:181`）吞掉后，
`event.is_stopped()` 为假，stage 继续执行，`RespondStage` 发送**未清洗原文**。
v6/v14 均复现（v6 `_pull/p1a/tool_xml_guard.py:301-306`；v14 同位置）。

根因：targets 推导在清洗 `try` 之外；且 `guard` 没有统一异常边界。

## 二、修复原则

1. 以 v14 为基准建独立修复候选；**v6 历史快照不动**（回滚点保持原样）。
2. 普通 `Exception` 必须 `_stop`，禁止异常后继续发送未清洗文本。
3. `asyncio.CancelledError` 单独处理：先 `_stop`，再 `raise`，不得静默吞掉。
4. 不机械地把所有 `except Exception` 改成吞掉 `BaseException`。
5. 只改插件，不改 AstrBot 核心；核心的 `except BaseException` 行为在文档中说明。

## 三、目标结构

```python
async def guard(self, event):
    try:
        # 1) 读取结果
        result = event.get_result()
        if result is None or not result.chain:
            return
        # 2) targets 推导（has_marker 在这里，纳入异常边界）
        targets = [
            comp for comp in result.chain
            if isinstance(comp, Plain) and has_marker(comp.text or "")
        ]
        if not targets:
            return
        # 3) 文本访问、parse_invokes、save_proposal、finalize_text、链更新
        saved = 0
        for comp in targets:
            text = comp.text or ""
            for call in parse_invokes(_no_code(text)):
                ...
            comp.text = finalize_text(text)
        result.chain = [...]
        # 4) 空链 / 成功日志
        if not result.chain:
            logger.warning(...)
            event.stop_event()
            return
        logger.info(...)
    except asyncio.CancelledError:
        self._stop(event, "清洗被取消")
        raise
    except Exception as e:
        self._stop(event, f"清洗异常（{type(e).__name__}）")
```

要点：

- 读取结果、链遍历、`comp.text`、`has_marker`、`parse_invokes`、`finalize_text`、链更新全部在同一个 `try` 内；
- 只捕获 `Exception` 和 `CancelledError`；`SystemExit` / `KeyboardInterrupt` 等其它 `BaseException` 不捕获，交给运行时（不在插件职责内）；
- `CancelledError` 分支：`_stop` 后 `raise`，让取消继续传播；
- `_stop` 内部每个动作的 `except Exception` 改为 `logger.warning`，不静默 `pass`，且 `_stop` 自身不再抛异常。

## 四、`_stop` 调整

```python
def _stop(self, event, why):
    logger.error(...)
    try:
        result = event.get_result()
        if result is not None:
            result.chain = []
    except Exception as e:
        logger.warning(f"[tool_xml_guard] _stop 清链失败（{type(e).__name__}）")
    try:
        event.stop_event()
    except Exception as e:
        logger.warning(f"[tool_xml_guard] _stop 停止事件失败（{type(e).__name__}）")
```

- 不改变 `_stop` 的对外行为（清链 + stop），只把静默吞掉改为可观测；
- `_stop` 不再向外抛，避免“清理失败导致二次异常”。

## 五、关于核心 `except BaseException`

AstrBot v4.29.4 `ResultDecorateStage.process`（`result_decorate/stage.py:160-189`）：

```python
for handler in handlers:
    try:
        await handler.handler(event)
    except BaseException:
        logger.error(traceback.format_exc())
    if event.is_stopped():
        return
```

影响：

1. 插件抛 `Exception`：若插件已 `_stop`，核心检查 `is_stopped()` 为真 → `return`，不发送；
2. 插件抛 `CancelledError`：`_stop` 后 `raise`，核心的 `except BaseException` 捕获并记日志，然后检查 `is_stopped()` → 已 stop → `return`；
   因此“取消”在插件层表现为“事件停止 + 不发送”，但 asyncio 取消继续传播的语义被核心的 `except BaseException` 截断——这是**核心行为**，修复不改变核心；
3. 若插件没有 `_stop` 就抛异常（当前缺陷），核心吞掉后 `is_stopped()` 为假 → 继续发送未清洗文本。

测试里要覆盖 1 和 2，并明确“核心吞掉取消”是已知边界，不在插件修复范围。

## 六、改动范围

| 文件 | 改动 |
|---|---|
| `astrbot_plugin_tool_xml_guard/main.py` | `guard` 统一异常边界；`_stop` 可观测；新增 `CancelledError` 分支 |
| `测试/test_out_guard.py` | 新增故障注入用例（见第七节） |

不动：`multi_bubble`、`rule_guard`、AstrBot 核心、配置、线上文件；v6 快照不动。

## 七、测试方案（新增故障注入）

| # | 注入点 | 方法 | 期望 |
|---|---|---|---|
| 1 | `get_result` 抛异常 | fake event `get_result` raise | stop + 无出站 |
| 2 | `result.chain` 遍历抛异常 | chain 对象 `__iter__` raise | stop + 无出站 |
| 3 | `comp.text` 访问抛异常 | Plain 子类 property raise | stop + 无出站 |
| 4 | `has_marker` 抛异常 | monkeypatch raise | stop + 无出站（**本次缺陷**） |
| 5 | `parse_invokes` 抛异常 | monkeypatch raise | stop + 无出站 |
| 6 | `finalize_text` 抛异常 | monkeypatch raise | stop + 无出站 |
| 7 | `save_proposal` 抛异常 | monkeypatch raise | 记录 warning，继续清洗（或 stop，需裁定） |
| 8 | `stop_event` 自身抛异常 | fake event raise | `_stop` 不二次抛，记录 warning |
| 9 | `CancelledError` | 注入 `asyncio.CancelledError` | stop + 重新抛出（测试里捕获并断言） |
| 10 | 正常清洗 | 完整标记 | 出站 `前缀A  后缀B`（回归） |

验证方式：用真实 `ResultDecorateStage` + 假发送端（沿用 `harness/p1a1_pipeline_harness.py` 的思路），断言异常后无出站；v14 修复候选跑；v6 只跑现有基准确认未受影响。

## 八、风险

- 修复后“该发未发”的体验风险：fail-closed 是有意行为，需主人接受；
- `CancelledError` 被核心吞掉：插件只能保证 stop，取消传播依赖核心，文档已说明；
- 故障注入测试若用 monkeypatch，需确认测试进程隔离，不影响线上；
- 只改 v14 基准，回滚 v6 时仍存在该缺陷（v6 快照不动，属历史版本）。

## 九、待批准

1. 是否批准按本设计施工（只改 `tool_xml_guard/main.py` + 测试）；
2. `save_proposal` 异常时“继续清洗”还是“stop”，需裁定；
3. `CancelledError` 测试是否要求真实 asyncio 取消（还是注入异常即可）；
4. 修复候选是否单独分支（建议 `p1-a1-v14-failclosed`），不覆盖 v6/v14 快照。
