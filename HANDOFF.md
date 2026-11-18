# 最近交接（2026-11-19 00:10）

## 一、当前任务

**P1-A1 输出清洗，v6 已提交，待独立复审。线上未部署。**

| 项 | 值 |
|---|---|
| 审查对象 | 公开仓库 `zzc`，分支 `p1-a1-v6` |
| commit SHA | `bc04462361e418219da8110f28d6b50377834105` |
| 上一版 | v5 `9a84dc71246c1d8b34da59417b82158dc9709ce3`（分支 `p1-a1-v5`，保留） |
| 材料目录 | `reviews/P1-A1-v6/`（15 个文件） |
| 测试 | 21 组 **88 项 ALL PASS**（v5 是 84 项） |

改动范围：只改 `astrbot_plugin_tool_xml_guard/main.py` + `测试/test_out_guard.py`；`multi_bubble` 与 v5 完全相同（未动）。

### v6 相对 v5

**R5（唯一代码修复）**：CRLF 下闭围栏识别失败。`_code_regions()` 的 `close` 正则加 `\r?`：

```python
close = re.compile(r"(?m)^ {0,3}" + re.escape(ch) + "{%d,}[ \t]*\r?$" % n)
```

否则 `\r\n` 行尾的 `$` 匹配不到闭合行，围栏外的控制标记会被当成代码保护、逃过清洗。

**测试**：新增 4 项 CRLF 回归（反引号围栏 / 波浪线围栏 / 代码块逐字保真 / 闭合行带空格）。

### 已裁定（v5 复审）

空白规范采用**逐字保留**：不修剪行尾空格、不动缩进、不压空行；只丢弃「删除后整行只剩空白且原文有内容」的行。
`"  前言保留空格  \n正文 <invoke…>内部</invoke>  \n"` → `"  前言保留空格  \n正文   \n"`（测试锁定）。本轮没有重新引入全局 trim。

## 二、下一步（按顺序）

1. 审查方复审 v6（固定 SHA `bc04462…`）。
2. 通过后**单独审批部署**（主人批准，不可由审查意见代替）。
3. 部署：备份两文件 → 替换 → 重启 → 真实消息验收（含控制标记的消息、多气泡补发、日志 `req=` 关联）。
4. 部署后确认：`tool_xml_guard` 在 decorating 链最后执行（priority −1000000）、`<｜｜ calls>` 不再外泄。
5. 之后才谈 P1-A2（9 个直发点）或 `<｜｜ calls>` 独立立项。

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
- `zzc`（公开）= 代码与审查材料；`zzc-context`（私有）= 项目档案。GitHub 连接器读不到私有库，以本文本交接。

## 六、环境速查

- 服务器：腾讯云（地址见维护手册，不写进仓库）；SSH 密钥 `default-workspace/.ssh/id_desktop`
- 容器：`astrbot`（AstrBot v4.29.4）、`snowluma`（OneBot v11）、`ollama`（bge-m3）
- 插件目录：`/opt/astrbot/data/plugins`（容器内 `/AstrBot/data/plugins`），共 106 个
- 备份目录：`/opt/astrbot/shared/记忆/备份_2026xxxx_*`
- 测试副本：容器 `/tmp/rbtest_p1a/`（与 `reviews/P1-A1-v6/snapshot/` 一致）
- 工作区文档：`肥鱼维护手册.md`、`肥鱼优化日志.md`、`插件清单.md`、`小恋-人格与生命设计.md`、各阶段 `交付-*.md` / `审查-*.md`
