# P3 fail-open 修复候选交付报告

- **文档类型**：修复候选交付报告
- **任务**：P1-A1 PENDING 3 fail-open 修复候选（v14 基准）
- **版本**：v14 failclosed candidate
- **日期**：2026-11-22
- **更新时间**：2026-11-22 12:55（Asia/Shanghai）
- **当前状态**：**候选已提交，未部署、未重启、未改线上；等待复审**
- **对应 commit**：`zzc` 分支 `p1-a1-v14-failclosed` @ `3ac1c5f400b7e568816981ae1cfd1edfa7416856`（测试修订；初版 `efd66db0…`）

## 一、基线

- 基准：v14 `91514773b2f04bcb83c20e8a1daaa6cfc359a475`；
- 修复候选：`p1-a1-v14-failclosed` @ `3ac1c5f400b7e568816981ae1cfd1edfa7416856`（测试修订）；初版 `efd66db0…`；
- v6 历史快照 `c4497e04…` 未动；v14 基准提交未覆盖。

## 二、改动

| 文件 | 改动 |
|---|---|
| `snapshot/astrbot_plugin_tool_xml_guard/main.py` | `guard` 统一异常边界；`CancelledError` → stop + raise；非 `CancelledError` 的 `BaseException` → stop + raise；`_stop` 失败记 warning；`save_proposal` 异常继续清洗 |
| `snapshot/测试/test_failclosed_v14.py` | 新增 27 项故障注入/集成测试（含双重故障、KeyboardInterrupt） |
| `fix.diff` | v14 → 修复候选的完整 diff |
| `test-log-failclosed.txt` | 新增 19 项日志 |
| `test-log-204.txt` | v14 原 204 项回归日志 |
| `文件SHA.txt` | 源码/测试/diff SHA |

## 三、SHA

| 文件 | SHA256 |
|---|---|
| 修复源码 | `bba95b712d6d0708ed23c34a97f55c2375ea66b4e2bab3b8995bd2fb26de627f` |
| 新增测试 | `23243878bddb34293d9aa45c513bce12ee24cf5cc454d7830a160ac10280ff41` |
| diff | `6a945a714abce9b68ccb2659cc2f55121c7d3f1167af418a0c3570c8077bd4d6` |

## 四、测试结果

### 4.1 新增 27 项（ALL PASS）

| 用例 | 结果 |
|---|---|
| 正常清洗回归（不 stop） | PASS |
| 完整标记 → `前缀A  后缀B` | PASS |
| `get_result` 异常 → stop | PASS |
| `chain` 遍历异常 → stop | PASS |
| `comp.text` 访问异常 → stop | PASS |
| `has_marker` 异常 → stop（本次缺陷） | PASS |
| `parse_invokes` 异常 → stop | PASS |
| `finalize_text` 异常 → stop | PASS |
| `save_proposal` 异常 → 不 stop、标记不泄漏 | PASS |
| `stop_event` 自身异常 → 不二次抛 | PASS |
| `CancelledError` → 先 stop 再抛出 | PASS |
| `KeyboardInterrupt` → 先 stop 再抛出 | PASS |
| 真实 stage + `has_marker` 异常 → stop、无出站 | PASS |
| 真实 stage + `CancelledError` → stop、无出站 | PASS |
| 双重故障（finalize 异常 + stop_event 抛异常）→ `_stop` 被调用、清链成功、无出站 | PASS |
| 真实 stage + 双重故障 → stop 被调用、清链成功、无出站 | PASS |
| 真实 stage + `KeyboardInterrupt` → stop、无出站 | PASS |

### 4.2 v14 原 204 项回归（ALL PASS）

`test-log-204.txt`：无回归。

## 五、核心边界

- `ResultDecorateStage` 仍会 `except BaseException` 捕获插件异常；修复保证插件在抛出前已 `_stop`，核心检查 `is_stopped()` 后返回，不发送；
- `CancelledError` 的传播会被核心的 `except BaseException` 截断（核心行为，未改核心）；插件侧保证 stop + re-raise；
- 测试用真实 `ResultDecorateStage` + 假事件/假发送端，不是真实 QQ/模型 E2E。
- **双重故障边界**：若清链与 `stop_event` 均失败，不能宣称绝对 fail-closed。当前用例覆盖“`stop_event` 失败、清链成功 → 无出站”，未覆盖两者同时失败；该边界已在测试 README 记录。

## 六、未做与待复审

- 未部署、未重启、未改线上；
- 未修改 v6 快照、未覆盖 v14 基准；
- 待复审：分支 diff、测试日志、故障注入覆盖是否足够；是否批准进入部署准备（部署仍需单独批准）。
