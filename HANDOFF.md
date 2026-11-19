# 最近交接（2026-11-19 00:2x）

## 一、当前任务

**P1-A1 v6 已部署（2026-11-19 00:02），验收部分完成，仍有 PENDING。下一轮不施工，等裁定。**

| 项 | 值 |
|---|---|
| 已部署版本 | `p1-a1-v6` @ `bc04462361e418219da8110f28d6b50377834105` |
| 线上 sha256 | `tool_xml_guard c4497e04…` / `multi_bubble 5e2519…`（与仓库 snapshot `diff -q` 为空） |
| 部署前备份 | `记忆/备份_20261119_p1a1/`（`665eabb4…` / `f368e8ef…`） |
| 测试 | 21 组 88 项 ALL PASS（隔离测试，不是线上端到端） |

### 真机验收结果（区分已完成 / PENDING）

已完成（真实 QQ）：
1. 普通文本保真：`今天 19 号，周四` 等，标点/中文正常。
2. 首条气泡走管道；后续气泡直发 2 条，内容干净（`multi_bubble` 日志有 `排队 2 条待补发`）。
3. 4 条入站消息全部有回复；无发送失败、无空消息、Traceback 0。

PENDING（未取得证据，**不得当作 PASS**）：
1. **完整 DSML 标记的端到端清理**：模型把 `<｜｜DSML｜｜ calls>` 改写成不带尖括号的 `｜｜DSML｜｜ calls`，
   清洗器确实执行（`req=91584d1eff55`），实发 `前缀A ｜｜ calls 后缀B`。
   候选实验（线上代码跑 6 个候选原串）显示带尖括号的输入会被清成 `前缀A  后缀B`，
   与实发一致的是无尖括号版本——**这是候选实验，不是真实 QQ 端到端验收**。
2. **代码块保真**：该轮无 `tool_xml_guard` 日志（清洗器未触发）；`style_strip.restyle()` 隔离实验确认会把
   `def add(a, b):\n    return a + b` 改成 `def add(a，b):\nreturn a + b`；原始 `completion_text` 未取得，
   **不能据此归因于 P1-A1**。
3. **fail-closed 真机证据**：不做线上故障注入；现有证据仅限隔离测试用例 + 部署后线上代码行为验证。

## 二、下一步

1. **A（裸 DSML 清理规范）**：v6 文档审查通过。下一步是主人逐项裁定
   `DECISIONS/P1-A2-R1边界裁定清单.md` 里的 R1-a～R1-h（每项已列选项、后果、默认行为）。
   裁定后写回规范 v7 → 出施工方案与测试矩阵 → 审查通过并批准后才动代码。**当前代码未施工、未授权**。
2. **B（`style_strip` / `rule_guard` 代码内容保护）**：独立待办，走只读调用链审查 + 测试设计，不并入 P1-A1。
3. P1-A1 的三条 PENDING（完整 DSML 端到端、代码块保真归因、fail-closed 真机）保持原样，
   只能靠新的真实 QQ 场景或 `completion_text` 观测手段补证据；在此之前验收记录保持"部分完成"。

## 三、不要做的事

- 复审通过前不部署、不重启线上服务。
- 不扩大施工范围（只动 `tool_xml_guard` / `multi_bubble` / 测试）。
- 不碰 recall_boost / P0 / B0.5 / B1 / trust_gate / trust_context / 核心（除已登记的补丁）。
- 推送失败重试，但不关闭 TLS 校验、不改目标分支、不 force push。

## 四、已知限制（验收记录必须保留）

- hook 顺序证据只覆盖**静态可见的 8 个注册点**（`astrbot_plugin_*/main.py` 里的装饰器）。
  不覆盖动态注册、别名导入、其它文件注册与 AstrBot 内置 handler；线上进程注册表没有只读接口可 dump。
- P1-A1 只覆盖主回复管道 + 多气泡补发；A 类直发点 9 处（`agency_core`、`life`、`heartbeat`、`note_ack`、
  `follow_through`、`catchup`、`diary_deliver`、`promise_remind`、`day_plan`）未修。
- 测试日志是 dsh 在自己容器里跑的；审查方核对的是源码与日志，不是独立复测。

## 五、Git 与仓库约定

- 推送前核对目标分支与本地 commit；推送后核对远端 SHA，不一致就停下报告。
- 服务器到 GitHub 的 TLS 不稳定，推送通常重试 1–3 次；记录失败原因。
- `zzc`（公开）= 代码与审查材料；`zzc-context`（**2026-11-19 已公开**）= 项目档案，可直接读取。
- 隐私提示：`zzc-context` 历史里含 QQ 号（`COOPERATION.md` 第 7 行、`PROJECT_STATUS.md` 白名单行），
  已固化在全部 9 个历史版本；要彻底脱敏需改写历史，未做。

## 六、环境速查

- 服务器：腾讯云（地址见维护手册，不写进仓库）；SSH 密钥 `default-workspace/.ssh/id_desktop`
- 容器：`astrbot`（AstrBot v4.29.4）、`snowluma`（OneBot v11）、`ollama`（bge-m3）
- 插件目录：`/opt/astrbot/data/plugins`（容器内 `/AstrBot/data/plugins`），共 106 个
- 备份目录：`/opt/astrbot/shared/记忆/备份_2026xxxx_*`
- 测试副本：容器 `/tmp/rbtest_p1a/`（与 `reviews/P1-A1-v6/snapshot/` 一致）
- 工作区文档：`肥鱼维护手册.md`、`肥鱼优化日志.md`、`插件清单.md`、`小恋-人格与生命设计.md`、各阶段 `交付-*.md` / `审查-*.md`
