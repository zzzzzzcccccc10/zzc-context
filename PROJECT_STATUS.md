# 项目状态（截至 2026-11-21）

> 状态词：**封版**（验收通过、不再改动）/ **已部署**（线上在跑）/ **施工中** / **待复审** / **独立立项**（未排期）

## 一、总览

| 模块 | 状态 | 部署 | 证据 |
|---|---|---|---|
| P0 安全层（执行门禁 / 状态一致性 / Goal 租约） | 封版 | 是 | 2026-11-16 审查通过 |
| B0.5 工具门禁 | 封版 | 是 | gate harness 通过；白名单 10 工具 |
| B1 请求级信任上下文 + 外部来源标记 | 封版 | 是 | 2026-11-16 封版；harness 60 项 |
| P1-recall_boost（按问句检索 + 权限现查 + 缓存） | 封版 | 是 | 2026-11-17 节点二验收通过；`main.py 65e69d66…` |
| P1-A1 统一输出清洗（v6） | **已部署（部分验收，含 PENDING）** | 是 | 2026-11-19 00:02 部署；`bc04462361e418219da8110f28d6b50377834105`；sha256 与 v6 snapshot 逐字节一致 |
| P1-A2 其余直发点（9 处会把模型正文直发） | 未开始 | 否 | 见 `HANDOFF.md` 遗留项 |
| P1-A2a 裸 DSML 清理 | **v14 复审通过；部署准备完成（未部署）** | 否 | `p1-a2-v14` @ `91514773b2f04bcb83c20e8a1daaa6cfc359a475`；204 项 ALL PASS；部署准备见 `_deliver/P1-A2-v14-部署准备/` |
| `<｜｜ calls>` 残片泄漏 | 独立立项 | 否 | 17:48 实测；`rule_guard` + `tool_xml_guard` 清理尾巴问题 |
| 好友管理权限收紧（严格 OWNER_QQ） | 待办 | — | 维护手册待办 |
| 情绪 / 生活线 / 愿望（人格与生命设计） | 设计阶段 | — | `小恋-人格与生命设计.md` v0.2 |

## 二、线上事实（2026-11-18）

- 环境：腾讯云 Ubuntu 22.04 + Docker；`astrbot`（AstrBot v4.29.4）+ `snowluma`（OneBot v11）+ `ollama`（bge-m3）。
- 插件总数 **106**（全部加载成功），另有 `plugins_off/group_chat_plus` 停用 1 个。
- recall_boost 缓存：`记忆/recall_boost_vectors.json`，跨重启 0 重算（0.2–0.3s 完成预热）。
- 会话白名单 6 条（主人私聊、三个群、3025260592、3669402050）。
- 核心补丁（已登记维护手册 9.1）：waking_check 群唤醒、respond 拦 `[不回]`、web_search 成本封顶、bilibili 记忆桥、whitelist 放行 request 事件。

## 三、P1-A1 v6 部署记录（2026-11-19 00:02）

1. **部署文件与 v6 snapshot 一致**：`tool_xml_guard/main.py` sha256 `c4497e0404dd61a2…`、
   `multi_bubble/main.py` sha256 `5e2519320edac1da…`；与仓库 `p1-a1-v6` 的 `snapshot/` `diff -q` 为空。
   部署前备份 `记忆/备份_20261119_p1a1/`（旧版 `665eabb4ccf3…` / `f368e8ef83db…`）。
2. **插件启动正常**：StartedAt 00:02:39、RestartCount 0、Traceback/ImportError 0、适配器 00:02:54 连接；
   两插件均加载；`recall_boost 预热 docs=136 atoms=240 用时 0.2s`。
3. **真实 QQ 已验证**：普通文本（`今天 19 号，周四` 等）、首条气泡（走管道）、后续气泡（直发 2 条，内容干净）、
   标点与中文正常；4 条入站消息全部有回复，无发送失败、无空消息。
4. **真实 QQ 清洗测试未验证完整标记的端到端清理（PENDING）**：
   模型把 `<｜｜DSML｜｜ calls>` 改写成了不带尖括号的 `｜｜DSML｜｜ calls`；
   清洗器**确实执行**（`req=91584d1eff55`），实发 `前缀A ｜｜ calls 后缀B`。
   用线上代码做的候选验证显示：带尖括号的输入会被清成 `前缀A  后缀B`；
   与实发一致的那个候选正是无尖括号的版本。**这是候选实验，不是真实 QQ 端到端验收。**
5. **fail-closed 不做线上故障注入**：真机异常路径无法人工制造（PENDING）。
   现有证据 = 隔离测试里 88 项中的 fail-closed 用例（清洗异常 → stop_event、链清空）+ 部署后线上代码行为验证；
   覆盖范围仅限这两类，**不包含**线上真实故障注入。
6. **代码块测试受到 `style_strip` 干扰**：隔离实验确认 `style_strip.restyle()` 会把
   `def add(a, b):\n    return a + b` 改成 `def add(a，b):\nreturn a + b`（英文逗号全角化 + 缩进丢失）；
   该轮**没有** `tool_xml_guard` 日志，清洗器未触发；原始 `completion_text` 未取得，
   因此**不能据此归因于 P1-A1**（PENDING：需要拿到模型原始输出才能定位）。
7. **`metadata.yaml` 版本号与代码不一致**：日志显示插件版本 `1.0.0`（来自 `metadata.yaml`），
   代码 `@register` 是 `1.3.0`。低优先级维护事项，未改。

## 四、遗留与独立事项（含 P1-A1 待办、P1-A2a、B 代码保护、维护）

### A. 裸 DSML 标记清理（**v14 复审通过；部署准备完成，未部署**）

- 规范：`DECISIONS/P1-A2-裸DSML清理规范.md`（v7 + 第九节 v8 修订 + 第十节 v11 修订：非法候选隔离）。
- 裁定清单：`DECISIONS/P1-A2-R1边界裁定清单.md`（已填裁定结果）。
- 施工方案：`DECISIONS/P1-A2-施工方案.md`（v4 + 第十一节 v9 + 第十二节 v10 + 第十三节 v11 修订）。
- **已全部裁定**：R2=B、R4=A、R3=A；7.1=B；7.2=A；R1-a=A3、R1-b=B1（栈式配对）、R1-c=C1、
  R1-d=D1、R1-e=E1、R1-f=F1、R1-g=G2（单竖线纳入 + 双竖线优先）、R1-h=H1。
- **v8 复审不通过**：LEAK / DSML 提案整段保留；原包在 `p1-a2-v8` / `reviews/P1-A2-v8/`。
- **v9 复审不通过**：闭合异常分支用 `find(">")` 不感知引号；非法候选仍从 `m["end"]` 继续扫描；
  README 缺建目录步骤。原包在 `p1-a2-v9` / `reviews/P1-A2-v9/`。
- **v10 复审不通过**：非法候选隔离只在 `_match_r1()` 局部；UNCLOSED_SINGLE 后重扫候选内部；
  测试区分力不足。原包在 `p1-a2-v10` / `reviews/P1-A2-v10/`。
- **v11 复审不通过**：`_candidate_regions` 未排除 QUOTE / 外层 SYNTAX 内的伪候选；
  `_syntax_regions` 对无 `>` 候选生成到末尾的区间。原包在 `p1-a2-v11` / `reviews/P1-A2-v11/`。
- **v12 复审不通过**：普通 XML 第二轮 `find(">")` 截断引号属性。原包在 `p1-a2-v12` / `reviews/P1-A2-v12/`。
- **v13 复审不通过**：第二轮普通 XML 扫描没有跳过第一轮已识别的 DSML SYNTAX，
  DSML 属性里的伪 `<invoke>` 会把 SYNTAX 扩展到末尾、吞掉候选隔离。
  原包在 `p1-a2-v13` / `reviews/P1-A2-v13/`。
- **v14 修订**：第二轮尊重 DSML SYNTAX；`_xml_deletions` 只保护 DSML 区间；新增 3 项复审回归。
- **代码施工**：`p1-a2-v14` @ `91514773b2f04bcb83c20e8a1daaa6cfc359a475`；32 组 204 项 ALL PASS（5KB 5.62ms）。
- **v14 复审通过**（2026-11-21 ChatGPT 独立复审），进入部署准备阶段。
- **未部署、未重启**；线上 `main.py` 仍为 `c4497e04…`（v6）。
- 部署准备：核验、备份确认、部署与回滚方案、验证清单已完成。
  正式报告：`zzzzzzcccccc10/zzc-context`，分支 `main`，commit `25bcac98e9255b95b58ab61f486ccc5ca08a5f31`，
  路径 `_deliver/P1-A2-v14-部署准备/部署准备报告.md`，
  https://github.com/zzzzzzcccccc10/zzc-context/blob/25bcac98e9255b95b58ab61f486ccc5ca08a5f31/_deliver/P1-A2-v14-部署准备/部署准备报告.md
- 状态：**部署准备完成，等待部署批准**。
- 证据边界：隔离 Event 测试证明 stop_event / 链清空，不等于真实发送管道；未部署，无真机 E2E。

### B. `style_strip` 代码内容保护（独立问题）

- 线上代码隔离实验确认：`style_strip` 会修改代码样式文本（英文逗号全角化、缩进丢失）。
- QQ 测试的 `completion_text` 未取得，**不能确认这次实际变形完全由 `style_strip` 引起**。
- fenced code block 内部是否同样受影响，**尚未独立验证**。
- 目标：格式化插件应识别并保护代码块，保留代码标点、缩进、换行和围栏。
- 状态：**独立问题，待只读完整调用链审查和测试设计**。

### C. 维护事项（低优先级）

- `tool_xml_guard/metadata.yaml` 的 version 与新代码不一致（见第三节第 7 条）。

## 五、P1-recall_boost 节点二部署（2026-11-17）

- 部署后 `main.py 65e69d66…`、`vec_cache.py e8b6f3d0…`，独立备份在 `记忆/备份_20261117_recall_boost/`。
- 冷缓存：首轮 5 条失败未发布 READY，60 秒重试补全后发布（fail-closed 生效）。
- 请求级注入窗：0.18–9.4 秒（旧版分钟级）。
- 隐私：私聊 `r1=False`、群/非主人私聊只拿 public 原子 + 本会话文档；canary 8 项通过。

## 六、未完成的观测项（不阻断封版）

1. 线上满载并发（两个 query 槽位）未压满：单会话有 session lock + `msg_merge` 合并。
2. 请求级 LRU 命中缺线上计数（短问句 embed 仅 0.10s，耗时差异在噪声内）。
3. `_qlru_get_locked` 命中不刷新时间戳（实际是 TTL+容量缓存，非严格 LRU）。
4. `VectorCache._save()` 返回值未参与 READY 判定。
