# 最近交接（2026-11-24）· 新会话接手包

> **新会话启动（固定口令）**：主人说「继续小恋项目，先按 zzc-context 最新 COOPERATION.md 执行上下文启动校验」
> 时，按 `COOPERATION.md` 第四节执行：先读 HANDOFF → PROJECT_STATUS → COOPERATION → _deliver/README，
> 记录分支/commit/路径，检查新旧冲突，再读决策/报告/代码，向主人汇报基线。
> 本文件是当前交接入口；旧内容已被替换。

## 一、一句话现状

小恋项目：P1-A1 输出清洗**已部署**（v6），**PENDING 2 已结案（归因闭合）**，PENDING 1 的 L2 通过（仍非真实模型/QQ E2E），PENDING 3 修复已部署（线上 `bba95b71…`），真机验证仍未关闭；P1-A2 裸 DSML 清理 **v14 已部署、封版（限定验收通过：真实链路最小冒烟通过，有证据边界；非完整 E2E 原文取证）**；P1-A2 另外九个直发点、B（`style_strip` 代码保护）仍未完成；P1-A1 第二条代码块保真与 B 关联。

## 二、新会话先读这些（按顺序）

1. 本文件（HANDOFF.md）
2. `PROJECT_STATUS.md`（模块状态、部署状态、PENDING）
3. `COOPERATION.md`（三方职责、启动协议、交付规范）
4. `_deliver/README.md`（当前/历史正式报告索引）
5. 当前任务的决策文件（本阶段：`DECISIONS/P1-A2-施工方案.md`、`DECISIONS/P1-A2-裸DSML清理规范.md`、`DECISIONS/P1-A2-R1边界裁定清单.md`）
6. 当前任务的正式交付报告（部署执行：`_deliver/P1-A2-v14-部署/部署执行报告.md`，创建 commit `76e40648b215a04989601db45987f23f180e8364`；部署准备报告为历史材料）
7. 报告引用的代码、测试源码与日志（`zzc` 分支 `p1-a2-v14` 的 `reviews/P1-A2-v14/`）

## 三、当前状态

| 项 | 状态 |
|---|---|
| P1-A1 v6 | **已部署**（00:02，`bc04462361e418219da8110f28d6b50377834105`）；**P3 failopen 修复已部署（`bba95b71…`）**；PENDING 2 已结案；PENDING 1/3 未关闭 |
| P1-A2 规范 | **v7 + 第九节 v8 修订 + 第十节 v11 修订**（非法候选隔离） |
| P1-A2 施工方案 | **v4 + 第十一节 v9 + 第十二节 v10 + 第十三节 v11 修订** |
| P1-A2 代码施工 | **v14 已部署**（历史版本 `2f180cf0…`；当前线上为 P3 修复 `bba95b71…`）@ `91514773b2f04bcb83c20e8a1daaa6cfc359a475`（`p1-a2-v14`）；**封版（限定验收通过；真实链路最小冒烟通过，有证据边界；非完整 E2E 原文取证）** |
| B 代码块保护 | 独立待办，未开工 |
| 仓库 | `zzc`（公开，代码/审查材料）、`zzc-context`（公开，档案） |

### P1-A1 三条 PENDING（不得当作 PASS）

1. 完整 DSML 标记的端到端清理（真机被模型改写，清洗器执行但未验证完整标记）。
2. 代码块保真归因 → **已结案（2026-11-22，归因闭合）**；B 代码保护仍未修复，B v6 设计基线已确认，代码施工未批准、未开始。
3. fail-closed 真机证据（不做线上故障注入）；P3 修复已部署（线上 `bba95b71…`），但 PENDING 3 尚缺真机验证证据。

## 四、下一步

**P1-A1 复审后续（2026-11-22）**：PENDING 2 已结案；PENDING 1 的 L2 通过（v6/v14 出站 `前缀A  后缀B`）；
PENDING 3 的 M2 复现 fail-open（`has_marker` 异常时未 stop，发送未清洗原文；v6/v14 均复现）。
修复候选 `p1-a1-v14-failclosed` @ `3ac1c5f400b7e568816981ae1cfd1edfa7416856` **复审通过**；
**P3 修复已部署**（线上 `bba95b71…`；27 项 + 204 项 PASS；备份 v14 `2f180cf0…`）；
PENDING 3 未关闭（真机故障注入未验证）；B v6 设计基线已确认、代码施工未批准未开始；线上原 v14 已被 P3 修复替换。**不施工。**
**设计与评估（2026-11-22）**：部署脚本整改设计、权限安全专项评估、PENDING 1 真实链路方案、PENDING 3 fail-closed 方案已出，待复审；未施工、未执行。PENDING 1/3 未关闭。
**v34 复审（2026-11-23）**：v34 独立复审**不通过**，建议 v35；v35 待整改。v35 正式复审须用 **Agent Teams** 四队友（内核/Socket 语义、协议/进程生命周期、Evidence/审计状态机、对抗场景/测试覆盖）只读独立审查，Lead 汇总并标注未验证项；不以多数意见代替技术证明。设计通过≠施工授权。
**v35 复审（2026-11-23）**：Agent Teams 四队友（a-kernel/b-protocol/c-evidence/d-adversarial）独立审查，**四人均不通过**；汇总结论 v35 不通过、建议 v36；报告 `_deliver/P1-A1-PENDING复审/v35复审报告.md`。核心阻断：SCM_RIGHTS/分帧合同、execve 结果不可观测、放行不可审计、端点继承顺序、evidence 重放/单写者、测试判据缺失。未验证项（需目标 Linux 实验）已列，等主人单独授权。未施工。
**v36 设计（2026-11-23）**：Agent Teams 四队友按新分工（通信协议/执行确认与进程安全/Evidence 与恢复/实现与测试架构）收集合同，Lead 合并为 `_deliver/P1-A1-PENDING复审/部署脚本整改设计-v36.md`（六项合同）；目标 Linux 实验方案 `v36目标Linux实验方案.md` 已出，**未执行、待主人单独授权**。待独立复审；未施工。
**v37 复审（2026-11-23）**：v36 复审不通过（启动链/S 继承/WAL-sidecar 等），形成 v37 设计与 `v37目标Linux实验方案.md`；Agent Teams 四队友（a-env/b-proc/c-evidence/d-test）独立复审 v37，**四人均不通过**；报告 `v37复审报告.md`，建议 v38。核心阻断：启动链不可信、launcher 端点持有不可证、gate/exec 判定未闭合、WAL/sidecar 矛盾、正向对照不可执行。未施工、未执行实验。
**v38 复审（2026-11-23）**：v38 三契约设计 + 测试矩阵 + 实验方案已出；Agent Teams 四队友（a-chain/b-fd/c-state/d-matrix）独立复审，**四人均不通过**；报告 `v38复审报告.md`，建议 v39。核心阻断：安装根/状态根未闭合、退出码表缺失、四状态 fd 清单未落地、R08 execve 时点矛盾、migrate/release gate 矛盾、重放前置/顺序、矩阵不可交付（正向对照/变异/授权）。未施工、未执行实验。
**v39 接口冻结（2026-11-23）**：主人批准 v39 设计阶段；Agent Teams 新四队友（a-chain/b-fd/c-state/d-test）交付接口清单；Lead 裁定 D1–D14（单文件 deploy.py、安装根 /opt/astrbot-deploy、状态根 /var/lib/astrbot-deploy、迁移前置、FD 双集合、hold latch+22/23、时间预算共享 deadline、A0/A1/A2 授权），冻结稿 `v39跨领域接口冻结.md`。下一步：按冻结稿写完整 v39 设计并复审；**实验/施工未授权**。
**v39 完整设计复审（2026-11-23）**：v39 完整设计 + 冻结稿 + 测试矩阵/实验方案骨架已出；Agent Teams 四队友（a-chain/b-fd/c-state/d-test）独立复审，**四人均不通过**；报告 `v39复审报告.md`，建议 v40。核心阻断：hold/operator 生命周期与 L 副本死结、安装器/持 L 死锁/换名恢复、launcher 步骤/端点/error pipe 缺失、exec_begin 持久化/spawned 顺序导致错误 not_sent、release 二义、evidence 表矛盾、矩阵/实验未完整落盘。未施工、未执行实验。
**v40 设计（2026-11-23）**：主人批准 v40；Agent Teams 新四队友（a-chain/b-fd/c-state/d-test）交付接口合同；Lead 冻结 H1–H12（hold/锁、两次 fork、WAL 写权、CLOEXEC、时间预算、授权）并写完整设计 `部署脚本整改设计-v40.md`、完整矩阵 `v40测试矩阵.md`（101 例）、完整实验方案 `v40目标Linux实验方案.md`（E01–E16）。待 v40 独立复审；**实验/施工未授权**。
**v41 设计（2026-11-23）**：v40 复审六项 P0（hold/WAL 写权冲突、非子进程死亡证明、W2 重开、error pipe、D0–D9、矩阵错误）；新四队友（a-hold/b-fd/c-state/d-test）交付 v41 差异裁定；Lead 冻结 G1–G10，写 `v41核心裁定.md`、`v41接口差异与冲突裁定.md`、完整设计 `部署脚本整改设计-v41.md`、完整矩阵 `v41测试矩阵.md`（101 族/104 子例）、实验方案 `v41目标Linux实验方案.md`。待 v41 独立复审；**实验/施工未授权**。
**v41 复审（2026-11-23）**：独立复审**不通过**，建议 v42；报告 `v41复审报告.md`。核心阻断：W3 重开 WAL 追加位置未闭合、audit dirfd 关闭/重开不一致、hold/HOLD_REQ/收尸/W4/token 多套时序、D0–D9 子状态（D5x/D6b/D7b）未落表、P1–P14/F-* 不可独立复现、error pipe/SC0–SC6 枚举未逐项定义。保留 G1–G10 主体。未施工、未执行实验。
**v42 接口冻结（2026-11-23）**：新四队友 A/B/C/D 交付差异裁定；Lead 二次裁定并冻结 `v42核心裁定.md`（J1–J8）+ `v42接口冻结与差异裁定.md`：token→latch、W4R/epoch5、四种 HALT、W1–W4R 写权唯一、WAL 重开（逐级 openat+O_APPEND+尾修复 256KiB）与追加证明、D0–D9 15 子状态、error pipe 七态两层、SC0–SC6、N1–N7、101 族/105 子例。下一步：写 v42 完整设计/矩阵/实验；**实验/施工未授权**。
**v42 完整设计（2026-11-23）**：勘误冻结文件（token→latch、W3/W4/W4R、openat 全链、尾修复 256KiB、126s/125s、101/105）后，写 `部署脚本整改设计-v42.md`、`v42测试矩阵.md`（101 族/105 子例，P1–P14/F-* 完整）、`v42目标Linux实验方案.md`（E01–E16+E16e 映射+F-SEAL 10 步）。待独立复审；**实验/施工未授权**。
**v43 修订（2026-11-23）**：按主人要求修订 K1–K6：F-HALT/W4R epoch 持久化矛盾（epoch 只由 WAL 推进；W4R 仅 T-HALT；F/M-HALT latch-only 22）、main 收养/live_children 证据、orphan token 授权、FRAME 必须 EOF、T3-02/T2-02/T3-18/NOT-SENT 判据；补齐正常启动/安装器/L/M/FD/R0–R5。产出 `v43修订说明.md`、`部署脚本整改设计-v43.md`、`v43测试矩阵.md`、`v43目标Linux实验方案.md`。待复审；**实验/施工未授权**。
**v43 复审（2026-11-23）**：独立复审**不通过**，建议 v44；报告 `v43复审报告.md`。核心阻断：K2 waitpid/收养判定错误（返回 0/ECHILD 语义）、`/proc/children` 不精确；K1 三种 hold 路径未唯一化（W3/T-HALT/F/M-HALT/observed=false）；P1：HALT epoch、fstatat 无 AT_SYMLINK_NOFOLLOW、A0 门禁 U-01/U-02、T2-02a 注入点、T3-18 夹具、orphan token 合同、时间起点。保留 K4/K5/完整启动/安装器/L/M/FD/R0–R5。未施工、未执行实验。
**v44 修订（2026-11-24）**：新四队友（a-proc/b-wal/c-auth/d-test）裁定收齐；Lead 冻结 `v44核心裁定.md`+`v44接口冻结与差异裁定.md`（P0-1 waitpid 五分支/observed 三态/T-HALT；P0-2 hold 决策表 P1–P5+W4/W4R；P1：HALT 四字段、fstatat AT_SYMLINK_NOFOLLOW、A0 门禁、T2-02a 注入、T3-18 A/B/C、orphan token、时间起点 126/125）。产出完整设计 `部署脚本整改设计-v44.md`、矩阵 `v44测试矩阵.md`（101 族/105 子例）、实验 `v44目标Linux实验方案.md`。待独立复审；**实验/施工未授权**。
**v44 复审（2026-11-24）**：独立复审**不通过**，建议 v45；报告 `v44复审报告.md`。P0：hold-live 未入唯一选择顺序；W4R 失败恢复未闭合（takeover 未落盘/已落盘无 attempt_hold）；核心裁定 T_REAP 仍写 M-HALT/23 与冻结冲突。P1：PID 权威来源未定义；orphan token 三文档 schema 不一致；T_SUP_EXIT_FRAMED 起点文字冲突；T2-02a 注入语义未写明。保留 waitpid/observed/fstatat/A0 门禁/T3-18/FRAME/101-105。未施工、未执行实验。
**v45 修订（2026-11-24）**：写 `v45修订说明.md`：hold 状态机唯一表（先活体后写权；有活体只 P2 或 hold-live；P3/P4a 限无活体 observed=true）；W4R 失败 S1/S2/S3 + recover basis=latch；T_REAP 统一 T-HALT/22；PID 发布协议（WAL spawned/cli_spawned + main 独立验证）；orphan token 唯一 schema；T_SUP_EXIT_FRAMED 合法帧含 EOF；T2-02a 注入语义（stub 首次 EIO/第二次真实 fsync）；跨文档一致性表。待完整 v45 设计/矩阵/实验；**实验/施工未授权**。
**v45 完整交付（2026-11-24）**：新四队友（a-proc/b-wal/c-hold/d-test）独立分析，发现并裁定跨域冲突：hold-live/latch 失败优先、W4R S1/S2a/S2b/S3a/S3b/S4、resolution.json 载体、resolved/anchor 派生、cli_spawned 发布时序、spawn_closed/observed、pidfd POLLHUP≥6.9、T_SUP 起点穷尽、T3-22 故障向量、103 族/113 子例。产出 `v45核心裁定.md`、`v45接口冻结与差异裁定.md`（含修订追踪表）、`部署脚本整改设计-v45.md`、`v45测试矩阵.md`、`v45目标Linux实验方案.md`。待独立复审；**实验/施工未授权**。
**v46 修订（2026-11-24）**：按 v45 待审意见修五项：spawn_closed/cli_spawn_failure（failure 合法终止）、T2-21a 计时（t_eof 起 126s；早退分支 a2）、W4R 六子态 live/dead 与 hold-live 优先级（T3-22c/d/e 拆 live/dead）、resolution 双写原子性（文件先/WAL 后/文件权威/文件最后删）、P3a/P4a/P1-H/token 失败测试映射（T2-22/T3-24/T3-25）。计数 108 族/145 子例（不删旧）。产出 `v46修订说明.md`、`部署脚本整改设计-v46.md`、`v46测试矩阵.md`、`v46目标Linux实验方案.md`。待复审；**实验/施工未授权**。
**v46 复审（2026-11-24）**：独立复审**不通过**，建议 v47；报告 `v46复审报告.md`。P0：resolution.json 删除后完成态丢失；文件成功/WAL 失败“保留现场 vs exit 0”矛盾；T2-05 丢失 cli_spawn_failure+resolution 断言。P1：S4 分类/12 出口、P1-H fsync EIO 完整重放、P3a/P4a 重叠、token 持久化失败形态。P2：计数 108/145、T2-21a2 唯一、日期。
**v47 修订（2026-11-24）**：写 `v47修订说明.md`：resolution.json **永久保留**为完成态（清理不删）；文件成功/WAL 失败统一 0；T2-05/T2-04 恢复断言；S4 单列、五子态各 live/dead + T3-23 a1/f2；P1-H a/b；P3a/P4a 互斥（HALT 打开成功+写失败 vs 打开/预检失败）；token 形态 create/短写/fsync EIO/目录 fsync；计数 **108 族/147 子例**；日期改 11-24。同步 v46 设计/矩阵/实验。待复审；**实验/施工未授权**。
**v47 复审（2026-11-24）**：独立复审**不通过**，建议 v48；报告 `v47复审报告.md`。P0：resolution 文件缺失恢复无唯一判据（epoch5 无 WAL 事件不能重建）。P1：S4-dead “22/0”不唯一；P3a/P4a 未入设计/矩阵；wal_audit_missing 无持久位置。P2：计数 145/147 混用、T2 33/30、S4 重复计数。
**v48 修订（2026-11-24）**：写 `v48修订说明.md`：resolution 缺失六行决策表（文件有效→0；损坏→30；epoch4 WAL 一致→重建；epoch5/无事件→30；身份不符→30）；S4 拆 live/first/recover（f1/f2/f3）；P3a/P4a 注入条件入设计/矩阵（halt_fsync=EIO vs halt_dir=EACCES）；新增 `resolution.audit.json`（present/missing）；计数统一 **108 族/148 子例**、T2 23/30、T3 25/57。待复审；**实验/施工未授权**。
材料：`_deliver/P1-A1-PENDING复审/`（复审报告、L2-M2 执行报告、harness、脱敏摘录）；
B 方案：`_deliver/B-style_strip-代码保护/B-style_strip-代码保护设计方案.md`。

**历史**：**v14 已部署并通过限定验收**（2026-11-21 22:30，历史线上 `2f180cf0…`，现已被 P3 修复 `bba95b71…` 替代），服务已重启，
插件加载成功、适配器已连接、204 项隔离测试 ALL PASS。
**真实链路最小冒烟通过（有证据边界）**：观察到清洗器检测条件命中并调用 finalize_text()，最终发送符合预期；
原始 completion_text 不可得，非完整 E2E 原文取证。结果见 `_deliver/P1-A2-v14-真实QQ冒烟/真实QQ冒烟验收结果.md`；回滚点已备。
**交接已按限定验收范围修干净；等待主人决定下一阶段排期，不再自行追加规范或施工。**

部署执行报告（正式归档）：
- 仓库 `zzzzzzcccccc10/zzc-context`，分支 `main`
- 报告创建 commit：`76e40648b215a04989601db45987f23f180e8364`
- 文档索引修正 commit：`aeabb283183b9e0acafa0065d8140e6a3a601dd3`（只回填 SHA，报告内容未变）
- `_deliver/P1-A2-v14-部署/部署执行报告.md`
- 备份：`/opt/astrbot/shared/记忆/备份_20261121_p1a2_v14_pre/`（v6 `c4497e04…` + multi_bubble `5e2519…`）

**v14 已完成的内容**：
1. 只改 `astrbot_plugin_tool_xml_guard/main.py` + `测试/test_out_guard.py`。
2. 部署前备份：`/opt/astrbot/shared/记忆/备份_20261121_p1a2_v14_pre/`（SHA 已核验）。
3. 修复 v13 阻断项：`_syntax_regions()` 第二轮尊重第一轮 DSML SYNTAX；
   `_xml_deletions()` 只保护 DSML 区间；新增 3 项复审回归。
4. 测试：**32 组 204 项 ALL PASS**（v13 的 201 项保留 + v14 新增 3 项；5KB 5.62ms）。
5. 提交 `zzc` 分支 `p1-a2-v14`：完整 diff、测试源码、日志、文件 SHA、性能实测，在 `reviews/P1-A2-v14/`。
6. **历史 v14 已部署、已重启**；当前线上 `main.py` 为 P3 修复 `bba95b71…`（基于 v14；v14 为 `2f180cf0…`）；**封版（限定验收通过；真实链路最小冒烟通过，有证据边界；非完整 E2E 原文取证）**。

## 五、红线

- 未批准前：不改源码、不改测试、不改配置、不部署、不重启。
- 不碰：`multi_bubble`、P0、B0.5、B1、recall_boost、`trust_gate`、`trust_context`、AstrBot 核心。
- 不改 9 个直发点（P1-A2 其余部分）。
- 推送失败重试，但不关闭 TLS 校验、不改目标分支、不 force push。

## 六、环境速查

- 服务器：腾讯云 Ubuntu 22.04，SSH 密钥 `default-workspace/.ssh/id_desktop`
- 容器：`astrbot`（AstrBot v4.29.4）、`snowluma`（OneBot）、`ollama`（bge-m3）
- 线上插件：`/opt/astrbot/data/plugins`（容器 `/AstrBot/data/plugins`），106 个
- 当前线上 `tool_xml_guard/main.py`：`bba95b71…`（P3 修复，基于 v14）；历史 v14 `2f180cf0…`（2026-11-21 22:30 部署）；`multi_bubble`：`5e2519…`
- Git：服务器有 `gh`（已浏览器授权，账号 zzzzzzcccccc10），`gh auth setup-git` 已配
- 测试副本：容器 `/tmp/rbtest_p1a/`
- 工作区参考：`肥鱼维护手册.md`、`肥鱼优化日志.md`、`插件清单.md`、`小恋-人格与生命设计.md`

## 七、踩过的坑（省时间）

1. **Markdown 一律 LF**：Windows 上 `Path.write_text` 默认写 CRLF，会让 diff 变噪声。用 `write_text(..., newline="\n")`。
2. **PowerShell 传中文易乱码**：改含中文的文件用 `write` 工具或 Python 脚本，别用 `Set-Content`。
3. **`_stop(event, why)` 需要两个参数**；`finalize_text` 不吞异常。
4. **服务器到 GitHub TLS 不稳**：push/拉取要重试 3–5 次，记录失败原因。
5. **AstrBot 排序是 `sort(key=-priority)`**：priority 大的先执行，清理钩子要用最小 priority。
6. **闭合标签要校验到 `>`**：v8 的 `_match_r1()` 只匹配标签名前缀，`</… name="x">` 会被误当合法闭合。
   标准闭合和新闭合都要确认标签名后只有空格/Tab + `>`。
