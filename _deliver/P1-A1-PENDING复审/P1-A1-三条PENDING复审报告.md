# P1-A1 三条 PENDING 独立复审报告

- **文档类型**：只读复审报告（含验证方案，未施工）
- **任务**：P1-A1 三条 PENDING 的独立复审
- **版本**：评审对象 P1-A1 v6（`c4497e04…`）；当前线上 P1-A2 v14（`2f180cf0…`）
- **日期**：2026-11-22
- **更新时间**：2026-11-22 02:20（Asia/Shanghai）
- **当前状态**：**只读复审完成；未修改代码/配置/线上；未新增测试；等待主人批准后续**
- **对应 commit**：`zzc` 分支 `p1-a1-v6` @ `bc04462361e418219da8110f28d6b50377834105`（P1-A1 v6 部署 commit）；线上 v14 `2f180cf0…`

## 〇、上下文校验与前提纠正

按 `COOPERATION.md` 启动校验读取了：

- `zzc-context` 最新 `HANDOFF.md`、`PROJECT_STATUS.md`、`_deliver/README.md`；
- `DECISIONS/P1-A2-施工方案.md`、`P1-A2-裸DSML清理规范.md`、`P1-A2-R1边界裁定清单.md`；
- `_ctx/P1-A1-v5-交付报告.md`、`_ctx/P1-A1-v6-交付报告.md`、`审查-P1-A0-输出清洗与发送边界.md`、`审查-P1-A2-输出格式与代码块边界.md`；
- `_pull/p1a/tool_xml_guard.py`（v6）、`_pull/p1a/multi_bubble.py`、线上 `style_strip` 源码与配置；
- 线上只读日志、`data_v4.db`（`mode=ro`）与容器内核心源码。

三个前提需要先纠正：

1. **线上当前是 v14，不是 v6。** 2026-11-21 22:30 部署 v14（`2f180cf0…`，38021 字节）；`c4497e04…`（v6）是回滚备份。P1-A1 三条 PENDING 的验收对象是 **v6 历史部署**；不能说“线上 v6 未修”，也不能拿 v14 的行为当 v6 已验证。
2. **`审查-P1-A1-输出清洗与发送边界.md` 不存在。** 工作区实际是 `审查-P1-A0-输出清洗与发送边界.md`（P1-A1 的前置只读审查），以及 `审查-P1-A2-输出格式与代码块边界.md`。本报告引用时按实际文件名。
3. **“原始 completion_text 不可得”这一旧前提被部分推翻。** `data_v4.db` 的 `conversations.content` 保存了 `run_context.messages`，即 **LLM 响应 append 之后、装饰钩子之前** 的 assistant 文本；本轮只读复核拿到了 2026-11-19 00:15 那轮的两条原文（见 PENDING 1/2 节）。但 DB 只到 AstrBot 收到的文本，**provider/模型解码层**仍不可得；两者不能混为一谈。

## 一、方法与证据等级

- 三个子智能体并行只读分析，各自独立提交结果（见附件）；
- 主 Agent 交叉复核：DB 原文、v6/v14 源码 SHA、线上 SHA、历史日志窗口、`style_strip` SHA；
- 证据等级按「已证实 / 推测 / 未知」标注，不把子智能体的推测当事实；
- 有分歧的地方保留在第九节，不强行合并。

本轮未修改代码、测试、配置、文档或线上状态；未部署、未重启、未发送消息。

## 二、PENDING 1：完整 DSML 标记端到端清理未验证

### 2.1 问题定义

待证命题：v6 在真实 QQ 链路里，对**完整标记**（带尖括号的 `<｜｜DSML｜｜ calls>`）做端到端清理。
2026-11-19 真机结果是：入站提示词含完整标记，cleaner 日志执行（`req=91584d1eff55`），最终发送却是 `前缀A ｜｜ calls 后缀B`（残片）。所以问题不是“cleaner 有没有跑”，而是：完整标记有没有到达 cleaner / 到达后是否被清干净 / 最终发送能否证明由 cleaner 造成。

### 2.2 现有证据（含本轮新取证）

**新证据（主 Agent 只读复核，DB `mode=ro`）**：会话 `176b02ad-bd0c-45e6-9a92-b2272837cc58` 的 `conversations.content` 是 60 条消息的 JSON 数组；其中：

- msg 34（user）：`请逐字复述下面这一整行…前缀A <｜｜DSML｜｜ calls> 后缀B`；
- **msg 35（assistant）：`前缀A ｜｜DSML｜｜ calls 后缀B`（无尖括号）**；
- msg 36（user）：代码块复述请求；
- **msg 37（assistant）：`def add(a, b):\n    result = a + b\n    return result\n\nprint(add(2, 3))`（69 字符，格式完好）**。

msg 35 仍含 `｜｜DSML｜｜`，而最终实发是 `前缀A ｜｜ calls 后缀B`（v6 会删掉 `｜DSML｜`），这说明 msg 35 是**清洗前**的文本。也就是说：**模型输出本身就是裸标记，没有 `<`/`>`；v6 把 `｜｜DSML｜｜` 挖成 `｜｜`，留下 `｜｜ calls` 残片。**

其他证据：

- 最终发送：`[01:06? 实为 00:15:40.960] Prepare to send - …: [引用消息] 前缀A ｜｜ calls 后缀B`（历史日志；Agent 1 复核原始 docker logs，行号 124621 附近）；
- v6 对完整多行 DSML 的隔离清理为 `""`，v6 测试 88 项 ALL PASS（`reviews/P1-A1-v6/测试日志.txt:54,216`；测试源码 `:38-43`）；
- 本轮内存实测（Agent 1，用 v6 源码、AstrBot venv、`python -B`）：完整单标记 → `前缀A  后缀B`；裸标记 `前缀A ｜｜DSML｜｜ calls 后缀B` → `前缀A ｜｜ calls 后缀B`（与实发逐字一致）；裸标记无 `>` → `前缀A   后缀B`（v14）。
- `style_strip` 不删除 `<`/`>`/`｜`/`DSML`（线上源码 `:31-56`）；`multi_bubble` 因 `MIN_LEN=28` 未参与该请求（`_pull/p1a/multi_bubble.py:42,243`）；`rule_guard` 该请求无重生成日志。

### 2.3 根因判断

- **已证实**：该轮模型输出是裸标记（DB msg 35），完整标记**没有以原样到达 cleaner**；v6 对裸标记的 `replace("｜DSML｜","")` 必然留下 `｜｜ calls`（源码 `:186`）。所以“实发残片”的机制已闭合，不是推测。
- **已证实**：v6 对完整标记的隔离清理是干净的（测试 + 实测）；PENDING 1 的“完整标记 E2E 未验证”仍然成立，但根因不是 cleaner 不会清完整标记，而是**模型输出不可控（生成了裸标记）**。
- **未知**：模型为什么输出裸标记（解码层/provider 层/特殊 token 处理），DB 只到 AstrBot 收到的文本；完整标记的真实 QQ E2E 仍没有。
- **不能写**：把 v14 的裸标记冒烟当作 P1-A1 完整标记 E2E 的证据；v14 冒烟已自限“completion 不可得、非完整 E2E 原文取证”。

### 2.4 证据缺口

1. provider/模型解码层的原始响应（DB 不可得）；
2. 完整标记真正原样到达 cleaner 的真实样本（当前没有任何一次）；
3. 运行时 handler 注册表全集（静态扫描自认不覆盖动态注册）；
4. 候选实验的原始脚本/日志（`PROJECT_STATUS.md` 只有摘要）；
5. v6 原始 88 项测试日志在本地不可得，只在 `zzc` 的 `reviews/P1-A1-v6/`。

### 2.5 最小验证方案（不依赖模型随机输出）

**L0 纯函数隔离**（本轮已完成，0 风险）：

| # | 输入 | 期望（v6） | 证明 |
|---|---|---|---|
| M1 | `前缀A <｜｜DSML｜｜ calls> 后缀B` | `前缀A  后缀B` | 完整单标记被删净 |
| M2 | v6 测试的完整多行 LEAK | `""` | 完整嵌套结构整段删除 |
| M3 | `前缀A ｜｜DSML｜｜ calls 后缀B` | `前缀A ｜｜ calls 后缀B` | 逐字复现实发，证明裸标记必留残片 |
| M4 | `前缀A ｜｜ calls 后缀B` | 原样 | 残片不自愈 |
| M5 | `前缀A <｜｜DSML｜｜ calls POST`（无 `>`） | `前缀A ` | v6 过删边界，必须记录 |
| M6 | M1 连续两次 | 第二次 == 第一次 | 幂等 |

**L1 钩子层**（0 线上，fake event）：H1 裸标记 → chain 改写；H2 完整 LEAK → stop + 空链；H3 `finalize_text` 抛异常 → stop + 不残留。

**L2 管道层 E2E**（不依赖模型，需单独批准）：stub provider 固定返回含完整标记的 `completion_text`，捕获出站 payload，跑真实 `ResultDecorateStage → RespondStage`，断言出站 `前缀A  后缀B`。这是唯一能叫“端到端”又不依赖模型随机性的做法。

**能证明/不能证明**：L0/L1 证明 cleaner 与钩子的确定性行为；L2 证明整条 pipeline + 出站；都不能证明模型实际输出、真实 OneBot/客户端、运行时注册表全集。

### 2.6 风险

- 验收对象错位（v6 vs v14）→ 高；
- 回滚到 v6 会重新引入裸标记残片与无 `>` 吞行 → 中；
- 本地 `测试/test_out_guard.py` 是 v14 测试，对 v6 跑会预期性 FAIL → 中；
- 关键日志在 docker logs，未归档，轮转后丢失 → 中；
- 把 L0 写成 E2E → 违反证据边界 → 中。

## 三、PENDING 2：style_strip 对代码块的影响

### 3.1 调用链（按实际执行顺序）

AstrBot v4.29.4 排序：`handlers.sort(key=lambda h: -priority)` → **priority 降序**（大的先执行）。装饰阶段 8 个注册点实际顺序：

```
meme_manager(99999) → style_strip(90) → face_map(80) → rule_guard(80)
→ recall_guard(70) → quote_reply(60) → chuanhuatong(-10) → tool_xml_guard(-1000000)
```

完整链路：LLM provider → `completion_text` → `on_llm_response`（rule_guard/multi_bubble 等，可改写）→ `internal.py` 构建 chain → `ResultDecorateStage`（上面 8 个钩子）→ `RespondStage`（去重/Prepare to send/event.send）→ `after_sent`（multi_bubble 补发直发）。

**材料更正**：`审查-P1-A0-输出清洗与发送边界.md:36-37` 写成“priority 升序”，方向反了；`审查-P1-A2-输出格式与代码块边界.md` 的钩子顺序表也把 `rule_guard(80)` 排在 `style_strip(90)` 前，也是反的。正确顺序以上面源码与 Agent 2 的运行时核对为准。

### 3.2 归因（已闭合）

**已证实**：2026-11-19 00:15 代码块那轮：

- 原始 completion（DB msg 37）：`def add(a, b):\n    result = a + b\n    return result\n\nprint(add(2, 3))`（69 字符，格式完好）；
- 最终实发（AstrBot `Prepare to send` 00:15:58.936）：`def add(a，b):\nresult = a + b\nreturn result\nprint(add(2，3))`（58 字符）；
- 用线上 `style_strip` 源码（SHA `bb2e9984…`）重放 `fix_quotes(restyle(squash_blank(raw), 400))`，输出与实发**逐字节相等**；
- `rule_guard.strip_stage` 输出（半角逗号、1 空格缩进、保留空行）、`multi_bubble._tidy` 输出（1 空格缩进、保留空行）、`tool_xml_guard.finalize_text` 输出（原样）均≠实发；把 style_strip 输出再喂 rule_guard 仍不变（不动点）；
- 该轮 `multi_bubble` 只有“想 1.8s”，没有“首条走管道，排队…”日志 → 未拆分；`tool_xml_guard` 无日志 → 无 marker，未改文本；
- 各插件版本钉住：style_strip `bb2e9984…`、tool_xml_guard v6 `c4497e04…`、multi_bubble `5e2519…`。

**变化环节**：`astrbot_plugin_style_strip/main.py` 的 `on_decorating`（priority=90），具体是 `squash_blank()`（删空行）+ `restyle()`（`,→，`；`[ \t]{2,}→1`；行首空白清零 → 0 缩进）。

### 3.3 与 B 的关系

同一根因、两个不同验收对象：

- PENDING 2 是“归因/取证”验收（谁改坏的、证据是否充分），本报告可闭合；
- B 是“修复/代码保护”验收（style_strip 如何保护代码内容），未开工；
- 不能互相替代：B 上线不能证明 PENDING 2，PENDING 2 归因也不能证明 B 达标；
- **B 的范围警告**：本轮真实样本是**无围栏的纯文本代码**（缩进行），不是 ``` 围栏块。B 若只保护围栏，会漏掉这次真实失败形态。B 的验收至少应覆盖：fenced ```/~~~（含 CRLF、未闭合、四反引号）、无围栏多行缩进代码、行内 `code`、代码内 `, ; 、 。 「」`、空行、URL/数字逗号；受保护区域逐字节不变，围栏外仍正常 restyle。
- 相邻通道（建议独立，不混进 B 验收）：`multi_bubble._tidy` 直发同样 `,→，`、双空格压缩；`rule_guard.strip_stage` 也压双空格；`meme_manager`/`face_map` 对 Plain 的 strip/拆链。

### 3.4 已证实 / 推测 / 未知

- 已证实：上面的原文对照、逐字节重放、排除项、版本钉住；
- 推测：链上其它钩子对这段文本恒等（由“最终==style_strip(raw)”反推+逐插件源码），未做运行时 dump；
- 未知：QQ 客户端渲染；历史其它轮次是否有同类变形（未全量扫描）；`max_len=400` 是否合理（产品问题）。

### 3.5 最小验证方案

- 方案 A（已执行，只读取证）：DB 钩子前原文 + 历史日志最终发送 + 离线纯函数重放 + 版本钉住；
- 方案 B（离线钩子链重放）：加载线上插件源码，按 priority 顺序跑 8 个装饰钩子 + 前置逻辑，断言 `final == observed`；B 修复后断言 `final == raw`；
- 方案 C（未来只读观测，需批准）：记录 `hash(raw)` / `hash(style_strip(raw))` / `hash(final)` 三哈希，不落正文。

## 四、PENDING 3：fail-closed 真实线上故障注入未验证

### 4.1 现有隔离测试覆盖

v6 一代（及 v14 保留）fail-closed 用例覆盖：

- 主路径：清洗抛异常 → `stop_event`（`测试/test_out_guard.py:253-267`）；链清空（`:265`）；读取结果失败 → `stop_event`（`:499-512`）；清洗后为空 → stop + 空链（`:248-251`）；
- multi_bubble：补发清洗异常 → 中止剩余（`:380-382`）；空内容跳过（`:373-375`）；发送失败中止（`:415-417`）；日志脱敏（`:385-430`）；预处理异常不排队（`:437-441`）。

测试替身边界（项目自己写明）：`GuardEv` 只置 bool、清空 chain，不证明线上适配器不发字节；`MBCtx` 是假 Context。

### 4.2 真实缺口（只有真实链路或真实核心能证明）

1. 真实 `AstrMessageEvent.stop_event()` 的语义被核心阶段尊重；
2. `ResultDecorateStage` 在 hook 异常/停止后真的 return；
3. `PipelineScheduler` 在 `is_stopped()` 后 break；
4. `RespondStage` 空链不发、也不触发 `OnAfterMessageSentEvent`（补发气泡的关键）；
5. 真实进程 handler 注册表；
6. 真实模型输出能否触发 `finalize_text` 异常（线上 24h 零 fail-closed 日志）；
7. 真实 OneBot/适配器“不发”时的行为；
8. `asyncio.CancelledError`/`BaseException` 路径；
9. 多气泡首条被 stop 后 `_pending_parts` 残留、下一轮补发旧气泡（静态推测）。

### 4.3 代码路径与不一致

- `_stop`（`tool_xml_guard.py:276-287`）：日志 + 清链 + `stop_event`；但 `except Exception: pass` 吞掉自身失败；读取结果失败路径上第二次 `get_result()` 大概率再失败，链清空不成立（只剩 stop_event）——文案“链清空”只对清洗异常路径成立。
- `guard`（`:291-344`）：`targets` 列表推导在 try 之外；`result.chain` 非可迭代/`comp.text` 抛异常会冒出 guard，核心 `except BaseException` 后若 `is_stopped()` 为假会继续发送未清洗正文 → **fail-open 风险**（低概率、高影响）。
- `except Exception` 不覆盖 `asyncio.CancelledError`（Python 3.12 属 BaseException）→ 同样可能绕过。
- `multi_bubble._send_rest`（`:185-211`）：清洗器缺失/清洗异常/发送异常都会中止；`_tidy` 在 try 外；`_finalize_text is None` 路径无测试。
- 核心合同（只读核对）：`result_decorate/stage.py:163-189` stop 后 return；`scheduler.py:46-82` break；`respond/stage.py:198-212` 空链早返回且不触发 after_sent。

### 4.4 最小验证方案

- **M1 合同核对**（零风险，推荐先做）：记录 AstrBot 核心 5 个文件的 SHA 与关键行，证明“stop/空链 ⇒ 不发、不补发”是核心显式合同；
- **M2 隔离微管道**（证据最强，需批准）：容器内 `/tmp` 临时目录，加载插件副本 + 真实核心 stage + 假事件，注入 `finalize_text` 异常，断言不发送、不触发 after_sent；对 v6 备份字节与 v14 线上字节各跑一遍；
- **M3 被动观察**（零副作用）：只读日志巡检 5 类 fail-closed 日志，挂账；当前 24h 为 0 条，不能保证何时出现。

**明确排除**：线上进程 monkeypatch/调试器注入、部署带异常开关的临时版本、构造极端输入“碰巧”抛异常。

### 4.5 已证实 / 推测 / 未知

- 已证实：隔离测试覆盖的动作；核心合同（静态）；线上 24h 无 fail-closed 日志；v14 的 `_stop`/`guard` 控制流与 v6 一致；
- 推测：try 外 fail-open、BaseException 绕过、`_pending_parts` 跨轮残留（静态推理，未真机）；
- 未知：真实异常概率、运行时注册表、OneBot 行为、更早日志窗口。

**结论**：PENDING 3 不能关闭；在禁止线上注入的前提下，最多降级为“合同已核对 + 隔离链路已复现 + 真实样本缺失（已知残余风险）”，不能写成“fail-closed 真机已验证”。

## 五、依赖关系与 B 的关系

| 关系 | 判断 |
|---|---|
| PENDING 1 ↔ PENDING 2 | 机制独立（清理效果 vs 标点/缩进变形）；共享“原始 completion 取证”通道（DB 可回溯，已部分解决） |
| PENDING 1 ↔ PENDING 3 | 独立（清洗效果 vs 出错不发送）；共享“发送前原文捕获”需求，但捕获不解决 PENDING 3 的异常源问题 |
| PENDING 2 ↔ B | 同一根因（style_strip）、不同验收对象；B 修复必须覆盖“无围栏代码”，否则原样复发 |
| PENDING 3 ↔ B | 弱耦合：B 改代码块保护/`_code_regions` 会改变 `finalize_text` 的异常面与保护面；届时需重跑 fail-closed 与 M2 |
| PENDING 1/2 ↔ v14 | v14 已覆盖裸标记清理；P1-A1 的验收对象仍是 v6；v14 不能替代 P1-A1 的证据 |

不能笼统写成“三条互不依赖”：P1/P2 共享取证通道，P2/B 同根因，P3/B 有代码面耦合。

## 六、推荐优先级（不修改源码）

1. **PENDING 2 先结案**：证据已闭合（DB 原文 + 最终发送 + 逐字节重放 + 排除项 + 版本钉住），只需主人接受“DB + 历史日志”作为证据类型；同时启动 B 的范围裁定（无围栏代码是必测项）。
2. **PENDING 1 补 L2**：L0/L1 已有；要真正叫“端到端”，需隔离环境 stub provider + 捕获出站；成本中等，可与 PENDING 3 的 M2 共用 harness。
3. **PENDING 3 做 M1 + M2**：M1 零风险；M2 需主人批准在容器 `/tmp` 写临时文件（不碰线上插件目录、不重启）；M3 长期挂账。
4. **B 独立立项**：不与 PENDING 2 合并验收；先裁定保护范围（围栏/无围栏/行内/URL/引号），再施工。

## 七、风险

- 版本漂移（v6 vs v14）导致证据错位 → 高；
- 把隔离测试/DB 回溯写成“完整 E2E 原文取证” → 高（违反证据边界）；
- B 只保护围栏，漏掉无围栏真实形态 → 高；
- 线上故障注入被误批准 → 高（红线）；
- 关键日志/DB 证据未归档，轮转后丢失 → 中；
- 钩子顺序旧材料方向错误，后续复审继续引用 → 中；
- `_pending_parts` 跨轮残留（推测）若属实，会造成旧气泡补发 → 中。

## 八、需要主人批准的事项

1. 是否接受 **DB `conversations`（钩子前原文）+ 历史 `docker logs`（最终发送）** 作为 PENDING 2 的有效证据类型，并据此结案；
2. 是否批准 **B 独立立项**，并裁定保护范围（围栏/无围栏/行内/URL/引号；是否把 `multi_bubble._tidy`、`rule_guard` 纳入）；
3. 是否批准 **PENDING 1 的 L2 注入式管道测试**（隔离环境，不改线上）；
4. 是否批准 **PENDING 3 的 M1 + M2**（M2 需在容器 `/tmp` 写临时文件，不碰线上插件、不重启）；
5. 是否把三条 PENDING 的目标版本明确标注为 **v6 历史部署 / v14 当前部署**，避免下一轮混淆；
6. 是否把本轮历史日志/DB 摘录归档进 `zzc`（写操作，需批准）。

## 九、分歧与未合并结论

1. **“completion_text 不可得” vs “DB 可回溯”**：Agent 1、Agent 3 以既有材料为前提写“不可得”；Agent 2 用 DB 推翻。主 Agent 复核 DB 后确认：AstrBot 内**钩子前**文本可回溯（msg 35/37）；**provider/模型解码层**仍不可得。两种说法各对一半，最终报告按“分层不可得”表述。
2. **PENDING 1 根因**：Agent 1 原为“模型输出裸标记（强推断）”；DB msg 35 把它升级为“已证实”。Agent 1 报告中的“推测”标签在本报告中按已证实处理，并注明升级依据。
3. **PENDING 3 的 `_pending_parts` 残留**：Agent 3 标为“推测（静态）”；主 Agent 未做真机验证，保留为推测，不并入已证实。
4. **B 的范围**：Agent 2 建议覆盖无围栏/行内/URL/引号；是否全部纳入，需主人裁定，本报告不替主人决定。
5. **钩子顺序旧材料错误**：Agent 2 指出 A0/A2 审查表方向反了；主 Agent 采信源码排序（priority 降序），但旧材料未修改（本轮不改文档），列为待更正项。

## 十、附件（智能体独立结果）

- `附件/agent1-dsml.md`：PENDING 1 完整分析（含 v6/v14 内存实测、日志行号、最小验证方案）；
- `附件/agent2-style-strip.md`：PENDING 2 完整分析（含调用链、DB 证据、逐字节重放、B 清单）；
- `附件/agent3-fail-closed.md`：PENDING 3 完整分析（含测试覆盖表、核心合同、M1/M2/M3、代码不一致）。

附件为子智能体独立分析，主 Agent 已在正文交叉复核；两者不一致处以正文“已证实/推测/未知”标注为准。
