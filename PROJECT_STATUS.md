# 项目状态（截至 2026-11-24）

> 状态词：**封版**（验收通过、不再改动）/ **已部署**（线上在跑）/ **施工中** / **待复审** / **独立立项**（未排期）

## 一、总览

| 模块 | 状态 | 部署 | 证据 |
|---|---|---|---|
| P0 安全层（执行门禁 / 状态一致性 / Goal 租约） | 封版 | 是 | 2026-11-16 审查通过 |
| B0.5 工具门禁 | 封版 | 是 | gate harness 通过；白名单 10 工具 |
| B1 请求级信任上下文 + 外部来源标记 | 封版 | 是 | 2026-11-16 封版；harness 60 项 |
| P1-recall_boost（按问句检索 + 权限现查 + 缓存） | 封版 | 是 | 2026-11-17 节点二验收通过；`main.py 65e69d66…` |
| P1-A1 统一输出清洗（v6） | **已部署（P3 failopen 修复 `bba95b71…`）；PENDING 2 已结案；PENDING 1/3 未关闭** | 是 | 2026-11-19 00:02 部署 v6；2026-11-22 14:21 部署 P3 修复；sha256 与候选 snapshot 一致 |
| P1-A2 其余直发点（9 处会把模型正文直发） | 未开始 | 否 | 见 `HANDOFF.md` 遗留项 |
| P1-A2a 裸 DSML 清理 | **封版（限定验收通过；真实链路最小冒烟通过，有证据边界；非完整 E2E 原文取证）** | 是 | 2026-11-21 22:30 部署历史 v14（`2f180cf0…`，现已被 P3 修复 `bba95b71…` 替代）；204 项 ALL PASS；冒烟 `req=ea208a4056ea`；报告见 `_deliver/P1-A2-v14-部署/`、`_deliver/P1-A2-v14-真实QQ冒烟/` |
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
4. **PENDING 1（完整 DSML 标记端到端清理）**：2026-11-19 真机中，模型输出裸标记
   （DB msg 35：`前缀A ｜｜DSML｜｜ calls 后缀B`，无尖括号），v6 删 `｜DSML｜` 后留下 `｜｜ calls` 残片；
   完整标记没有以原样到达 cleaner。v6 对完整标记的隔离清理为 `前缀A  后缀B`（v6 测试 + 内存实测）。
   **L2 隔离管道（2026-11-22）**：v6/v14 均出站 `前缀A  后缀B`；仍不是真实模型/QQ E2E。
   结论：**PENDING 1 未关闭**（完整标记真实 E2E 未验证）。
5. **PENDING 3（fail-closed 真机证据）**：隔离测试覆盖 finalize 异常/读取失败/空链；M1 核心合同核对通过。
   **M2（2026-11-22）发现 fail-open 缺陷**：`has_marker` 在 targets 推导中抛异常时，guard 未 stop，
   核心吞异常后继续发送未清洗原文；v6/v14 均复现（见 `测试结果-P1-A1-L2-M2.log`）。
   修复候选：`p1-a1-v14-failclosed` @ `3ac1c5f400b7e568816981ae1cfd1edfa7416856`（27 项 ALL PASS，复审通过）；
   P3 修复已部署（`bba95b71…`；27 项 + 204 项 PASS；备份 v14 `2f180cf0…`）。
   **PENDING 3 未关闭（真机故障注入未验证）**。
   - 设计与评估：部署脚本整改设计、权限安全专项评估、PENDING 1 测试方案、PENDING 3 验证方案已出（`_deliver/P1-A1-PENDING复审/`），待复审；未施工、未执行。
   - v36/v37/v38 设计整改：v36、v37、v38 均经 Agent Teams 四队友复审不通过；v39 设计阶段已获主人批准，四队友接口清单已收齐，Lead 完成 D1–D14 跨领域裁定并冻结 `v39跨领域接口冻结.md`；v39 完整设计已出，四队友复审**四人均不通过**（`v39复审报告.md`），建议 v40。v40 已获主人批准：四队友接口合同收齐，Lead 冻结 H1–H12，完整设计/矩阵/实验已出，v40 复审不通过（六项 P0）。v41 已出：G1–G10 冻结、四队友差异裁定、完整设计 `部署脚本整改设计-v41.md`、完整矩阵 `v41测试矩阵.md`（101 族/104 子例）、完整实验 `v41目标Linux实验方案.md`；v41 独立复审**不通过**（`v41复审报告.md`），建议 v42。v42 已启动：新四队友 A/B/C/D 差异裁定收齐，Lead 冻结 `v42核心裁定.md`（J1–J8）与 `v42接口冻结与差异裁定.md`（token→latch、W4R、WAL 重开/追加、D0–D9、error pipe/SC/N、101 族/105 子例）；勘误后完整设计 `部署脚本整改设计-v42.md`、完整矩阵 `v42测试矩阵.md`（101 族/105 子例，P1–P14/F-* 完整）、完整实验 `v42目标Linux实验方案.md`（E01–E16+E16e 映射+F-SEAL）已出。v43 修订完成：K1–K6（F-HALT/W4R epoch、收养/live_children、orphan token、FRAME EOF、T3-02/T2-02/T3-18/NOT-SENT、继承规范）+ 正常启动/安装器/L/M/FD/R0–R5；产出 `v43修订说明.md`、`部署脚本整改设计-v43.md`、`v43测试矩阵.md`、`v43目标Linux实验方案.md`。v43 独立复审**不通过**（`v43复审报告.md`），建议 v44。v44 独立复审**不通过**（`v44复审报告.md`），建议 v45：hold-live 未入唯一选择顺序、W4R 失败恢复未闭合、核心裁定 T_REAP 冲突；PID 来源/orphan token/T_SUP_EXIT_FRAMED/T2-02a 注入未闭合。v45 已写 `v45修订说明.md`（hold 状态机唯一表、W4R S1/S2/S3、T_REAP 统一、PID 发布协议、token schema、T2-02a 注入语义、跨文档一致性表）。v45 完整交付：四队友独立分析后，Lead 裁定 hold-live/latch 优先、W4R S1/S2a/S2b/S3a/S3b/S4、resolution.json、resolved/anchor 派生、cli_spawned 时序、spawn_closed/observed、pidfd 事件、T_SUP 起点穷尽、T3-22 故障向量、103 族/113 子例；产出 `v45核心裁定.md`、`v45接口冻结与差异裁定.md`（修订追踪表）、`部署脚本整改设计-v45.md`、`v45测试矩阵.md`、`v45目标Linux实验方案.md`。v46 修订：spawn_closed/cli_spawn_failure、T2-21a 计时、W4R live/dead、resolution 双写原子性、P3a/P4a/P1-H/token 失败映射；计数 108 族/145 子例；产出 `v46修订说明.md`、`部署脚本整改设计-v46.md`、`v46测试矩阵.md`、`v46目标Linux实验方案.md`。v46 独立复审**不通过**（`v46复审报告.md`），建议 v47：resolution 完成态、文件/WAL 失败矛盾、T2-05 断言、S4/12 出口、P1-H fsync EIO、P3a/P4a、token 形态。v47 已写 `v47修订说明.md`（resolution 保留、统一 0、T2-05 恢复、S4 单列、P1-H a/b、P3a/P4a 互斥、token 形态、108/147），并同步 v46 设计/矩阵/实验。v47 独立复审**不通过**（`v47复审报告.md`），建议 v48：resolution 缺失恢复唯一判据、S4-dead 唯一、P3a/P4a 入设计/矩阵、wal_audit_missing 持久位置、计数 108/147 统一。v48 已写 `v48修订说明.md`（六行决策表、S4 f1/f2/f3、P3a/P4a 注入、resolution.audit.json、108/148），并同步 v46 设计/矩阵/实验。v48 独立复审**不通过**（`v48复审报告.md`），建议 v49：S4 同步设计/实验、audit 失败语义、A 域前置、计数归属。v49 已写 `v49修订说明.md`（S4 三阶段、audit wal_audit/audit_record 分离、A 域前置+重建身份来源、108/148+归属表），并同步 v46 设计/矩阵/实验。v49 独立复审**不通过**（`v49复审报告.md`），建议 v50：六行表入设计/矩阵、audit_record 入 schema/矩阵、逐 ID 归属。v50 已写 `v50修订说明.md`（六行表入设计 §4、T3-25e 严格+n/o/p、schema audit_record、m1/m2/m3、逐 ID 清单、108/156），并同步 v46 设计/矩阵/实验。v50 独立复审**不通过**（`v50复审报告.md`），建议 v51：清宽泛“补文件”、n/o/p 入矩阵、audit 失败证据边界、计数 161。v51 已写 `v51修订说明.md`（六行表唯一、n/o/p 正式行、audit 失败仅 stdout/残留 unknown、108/161），并同步 v46 设计/矩阵/实验。v51 独立复审**不通过**（`v51复审报告.md`），建议 v52：audit 合同统一、身份来源表入设计、历史口径、归档防覆盖。v52 已写 `v52修订说明.md`（audit 只 written/失败 stdout、身份来源表、q/r/s/t、108/165、归档不覆盖），并同步 v46 设计/矩阵/实验。待复审。未施工、未执行实验。
   - 脚本整改：v34 独立复审**不通过**（归档 `_deliver/P1-A1-PENDING复审/v34复审结论.md`）；v35 设计已出，Agent Teams 四队友独立复审**四人均不通过**（`_deliver/P1-A1-PENDING复审/v35复审报告.md`），建议 v36；未施工。
6. **PENDING 2（代码块保真归因）→ 已结案（2026-11-22）**：DB msg 37 原始 completion 69 字符、格式完好；
   最终发送 58 字符；style_strip 重放逐字节相等；P1-A1/multi_bubble/AstrBot 排除。
   **归因闭合，不代表 B 修复完成**；B 仍独立待办。
7. **v6/v14 验收对象区分**：P1-A1 三条 PENDING 的验收对象是 v6（`c4497e04…`，2026-11-19 部署）；
   当前线上是 P3 修复（`bba95b71…`，2026-11-22 部署，基于 v14）。v14 的裸标记冒烟不能替代 P1-A1 完整标记 E2E。
8. **`metadata.yaml` 版本号与代码不一致**：日志显示插件版本 `1.0.0`（来自 `metadata.yaml`），
   代码 `@register` 是 `1.3.0`。低优先级维护事项，未改。

## 四、遗留与独立事项（含 P1-A1 待办、P1-A2a、B 代码保护、维护）

### A. 裸 DSML 标记清理（**v14 已部署；封版（限定验收通过；真实链路最小冒烟通过，有证据边界；非完整 E2E 原文取证）**）

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
- **部署准备**：核验、备份确认、部署与回滚方案、验证清单已完成。
  材料：`_deliver/P1-A2-v14-部署准备/部署准备报告.md`（commit `25bcac98e9255b95b58ab61f486ccc5ca08a5f31`）。
- **历史 v14 已部署**（2026-11-21 22:30，已重启）；历史线上 `main.py` = `2f180cf0…`（v14），当前已被 P3 修复 `bba95b71…` 替代；
  备份 `/opt/astrbot/shared/记忆/备份_20261121_p1a2_v14_pre/`（v6 `c4497e04…`）。
- 部署后验证：插件加载成功、适配器已连接、204 项隔离测试 ALL PASS、无 Traceback。
- 部署执行报告：`_deliver/P1-A2-v14-部署/部署执行报告.md`（commit `76e40648b215a04989601db45987f23f180e8364`）。
- 真实 QQ 冒烟：**已执行并限定验收通过**（`req=ea208a4056ea`，最终发送 `前缀A  后缀B`，无残片、正文保留）。
  观察到清洗器检测条件命中并调用 finalize_text()；原始 completion_text 不可得，无法独立确认清理前的完整文本，
  也无法独立确认最终文本变化由清洗器实际删除字符造成。
  结果：`_deliver/P1-A2-v14-真实QQ冒烟/真实QQ冒烟验收结果.md`。
- 完整原文 E2E 取证：**未完成**（completion_text 不可得）。
- 状态：**封版（限定验收通过）；P1-A1 PENDING 1/3 未关闭、PENDING 2 已结案、9 个直发点未处理；B v6 设计基线已确认、代码施工未批准未开始**。
- 证据边界：204 项是隔离测试，不等于真实发送管道。v14 冒烟原始 completion_text 不可得，完整原文 E2E 取证未完成（P1-A1 的钩子前文本已由 DB 回溯，见第三节第 4/6 条）。

### B. `style_strip` 代码内容保护（独立问题）

- **已归因闭合（2026-11-22）**：DB 钩子前原文 69 字符、最终发送 58 字符，style_strip 重放逐字节相等；P1-A1/multi_bubble/AstrBot 排除。
- 真实样本是**无围栏的纯文本代码**（缩进行），不是 ``` 围栏块；只保护围栏会漏掉这个形态。
- 目标：格式化插件应识别并保护代码块，保留代码标点、缩进、换行和围栏。
- 状态：**B v6 设计基线已确认；代码施工未批准、未开始**。

### C. 维护事项（低优先级）

- `tool_xml_guard/metadata.yaml` 的 version 与新代码不一致（见第三节第 7 条）。
- 插件文件权限为 `0666`（v14 部署前后一致，非本次引入）；后续单独评估权限加固，未验证前不改线上。

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
