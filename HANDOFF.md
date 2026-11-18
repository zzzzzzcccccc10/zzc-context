# 最近交接（2026-11-19 00:00）

## 一、当前任务

**P1-A1 输出清洗，v5 已提交，待独立复审。线上未部署。**

| 项 | 值 |
|---|---|
| 审查对象 | 公开仓库 `zzc`，分支 `p1-a1-v5` |
| commit SHA | `9a84dc71246c1d8b34da59417b82158dc9709ce3` |
| 上一版 | v4 `25e1fed1ff00808220143a75fcc268c10f703e66`（分支 `p1-a1-v4`，保留不动） |
| 材料目录 | `reviews/P1-A1-v5/`（15 个文件） |
| 测试 | 20 组 **84 项 ALL PASS**（v4 是 74 项） |

改动范围：只改 `astrbot_plugin_tool_xml_guard/main.py` + `测试/test_out_guard.py`；`multi_bubble` 保持 v4 不动。

### v5 相对 v4 的四项

1. **R1 文本保真**：删掉 `_tidy_deleted()` 里会修剪所有行尾空格的全局 `re.sub`；改成逐行判断——只丢弃「删完只剩空白、原文有内容」的行，其余逐字保留（含行尾空格、缩进）；行数变化时不做行级处理。
2. **R2 测试**：新增 4 项「同一条消息部分清洗、其余逐字保留」。
3. **R3 测试**：新增 5 项围栏边界（3/4 反引号交叉、反引号 vs 波浪线、关闭行带非空白、未闭合围栏假提案不入箱）。
4. **R4 证据**：`scan_hooks.py`（可复核扫描，含每个 `main.py` 的 sha256）+ 完整 JSON + 线上/部署后两张顺序表 + AstrBot 4.29.4 排序实现 + **覆盖边界说明**（只证明静态 8 个注册点，不证明运行时无动态注册）。

### 待裁定（唯一悬着的一条）

标签位置的行尾空格要不要修剪？
- 现行规范：**不修剪**（`"正文 <invoke…>内部</invoke>  "` → `"正文   "`）。
- 审查方示例期望 `"正文 "`（修剪掉两个尾随空格）。
- 需要审查方给明确规则；定了我就改并锁测试。

## 二、下一步（按顺序）

1. 审查方复审 v5（固定 SHA `9a84dc71…`），裁定上面那条空白规则。
2. 通过后**单独审批部署**（主人批准，不可由审查意见代替）。
3. 部署：备份两文件 → 替换 → 重启 → 真实消息验收（含控制标记的测试消息、多气泡补发、日志里 `req=` 关联）。
4. 部署后确认：`tool_xml_guard` 在 decorating 链最后执行（priority −1000000）、`<｜｜ calls>` 不再外泄。
5. 之后才谈 P1-A2（9 个直发点）或 `<｜｜ calls>` 独立立项。

## 三、不要做的事

- 复审通过前不部署、不重启线上服务。
- 不扩大施工范围（只动 `tool_xml_guard` / `multi_bubble` / 测试）。
- 不碰 recall_boost / P0 / B0.5 / B1 / trust_gate / trust_context / 核心（除已登记的补丁）。
- 不为了省事关闭 TLS 校验或改目标分支；推送失败就重试并按原因记录。

## 四、Git 与仓库约定

- 推送前：核对目标分支与本地 commit；推送后：核对远端 SHA 与本地一致，不一致就停下报告，不 force push。
- 网络：服务器到 GitHub 的 TLS 不稳定，推送通常要重试 1–3 次；记录每次失败原因（`GnuTLS recv error -110` / `HTTP2 framing layer` / `TLS handshake timeout`）。
- 仓库：`zzc`（公开）= 代码与审查材料；`zzc-context`（私有）= 本项目档案，GitHub 连接器当前读不到私有库，以 `HANDOFF.md` 文本交接为准。

## 五、环境速查

- 服务器：腾讯云（地址见维护手册，不写进仓库）；SSH 密钥 `default-workspace/.ssh/id_desktop`
- 容器：`astrbot`（AstrBot v4.29.4）、`snowluma`（OneBot v11）、`ollama`（bge-m3）
- 插件目录：`/opt/astrbot/data/plugins`（容器内 `/AstrBot/data/plugins`），共 106 个
- 备份目录：`/opt/astrbot/shared/记忆/备份_2026xxxx_*`
- 工作区文档：`肥鱼维护手册.md`、`肥鱼优化日志.md`、`插件清单.md`、`小恋-人格与生命设计.md`、各阶段 `交付-*.md` / `审查-*.md`
- 测试副本位置：容器 `/tmp/rbtest_p1a/`（与 `reviews/P1-A1-v5/snapshot/` 一致）
