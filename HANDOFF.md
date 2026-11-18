# 最近交接（2026-11-18 23:30）

## 一、当前任务

**P1-A1 v4（统一输出清洗）已提交，待 GPT 复审。线上未部署。**

- 审查对象：公开仓库 `zzc`，分支 `p1-a1-v4`
- commit SHA：`25e1fed1ff00808220143a75fcc268c10f703e66`（父提交 `7692e3ebc82c2b0aca95fe0dfc2f32fc68acc757`）
- 材料目录：`reviews/P1-A1-v4/`（10 个文件：报告、diff、测试日志、hook 证据、snapshot×2、baseline×2、测试源码、README）
- 测试：18 组 **74 项 ALL PASS**；改了两个插件：`tool_xml_guard`（+333/−118）、`multi_bubble`（+65/−6）

### v4 相对 v3 的四个修正

1. 围栏按行识别（结束必须独立行、同字符、长度≥开始、未闭合保护到末尾）；代码块里的字面量三反引号不提前结束保护。
2. 文本保真：去掉整条 strip；没删除的片段逐字返回；只清理删除留下的空白。
3. 异常处理：`after_sent` 日志只留类型+req；`_send_rest` 发送失败中止剩余补发。
4. 钩子顺序：发现 AstrBot 是 `sort(key=-priority)`（大的先执行），`tool_xml_guard` 改为 **−1000000** 才是最后执行。

## 二、下一步（按顺序）

1. GPT 复审 v4（固定 SHA），通过后**单独审批部署**。
2. 部署：备份两文件 → 替换 → 重启 → 真实消息验收（发一条含控制标记的测试、看气泡补发、看日志 req）。
3. 部署后确认：`tool_xml_guard` 在 decorating 链最后执行；`<｜｜ calls>` 不再外泄。
4. 之后才考虑 P1-A2（9 个直发点）或独立修 `<｜｜ calls>` 立项。
5. 只读追踪 `事件驱动状态.json`（停更于 11-08）。

## 三、不要做的事

- 不要在复审通过前部署或重启线上服务。
- 不要扩大施工范围（只动 `tool_xml_guard` / `multi_bubble` / 测试三个文件）。
- 不要碰 recall_boost / P0 / B0.5 / B1 / trust_gate / trust_context / 核心（除已登记的补丁）。

## 四、环境速查

- 服务器：腾讯云（地址见维护手册，不写进仓库）；SSH 密钥 `default-workspace/.ssh/id_desktop`
- 容器：`astrbot`（AstrBot）、`snowluma`（OneBot）、`ollama`
- 插件目录：`/opt/astrbot/data/plugins`（容器内 `/AstrBot/data/plugins`）
- 备份目录：`/opt/astrbot/shared/记忆/backup_2026xxxx_*`
- Git：服务器装了 `gh`（apt 2.4.0），已完成浏览器授权（账号 zzzzzzcccccc10），`gh auth setup-git` 已配置
- 工作区文档：`肥鱼维护手册.md`、`肥鱼优化日志.md`、`插件清单.md`、`小恋-人格与生命设计.md`、各阶段 `交付-*.md` / `审查-*.md`
