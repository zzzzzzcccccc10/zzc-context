# 最近交接（2026-11-20 21:40）· 新会话接手包

> **新会话第一步**：读完本文件，再读 `DECISIONS/P1-A2-施工方案.md`（v4 + 第十一节 v9 修订）。
> 本文件是当前唯一权威交接；旧内容已被替换。

## 一、一句话现状

小恋项目：P1-A1 输出清洗**已部署**（v6），但有 3 条 PENDING；P1-A2 裸 DSML 清理**v8 复审不通过，v9 已修订并提交待复审**（`p1-a2-v9` @ `a280025`，新增第二种闭合形式，171 项 ALL PASS，未部署）；B（`style_strip` 代码保护）是独立待办。

## 二、新会话先读这些（按顺序）

1. `DECISIONS/P1-A2-施工方案.md`（v4 + 第十一节 v9 修订说明）
2. `DECISIONS/P1-A2-裸DSML清理规范.md`（v7 + 第九节 v8 修订：第二种闭合形式，含 31 条正反例）
3. `DECISIONS/P1-A2-R1边界裁定清单.md`（R1-a～R1-h 裁定结果）
4. `PROJECT_STATUS.md`（模块状态总表）
5. 本文件

## 三、当前状态

| 项 | 状态 |
|---|---|
| P1-A1 v6 | **已部署**（00:02，`bc04462…`），3 条 PENDING 未结 |
| P1-A2 规范 | **v7 + 第九节 v8 修订**（第二种闭合形式） |
| P1-A2 施工方案 | **v4 + 第十一节 v9 修订说明** |
| P1-A2 代码施工 | **v8 复审不通过** @ `67b2f15`；**v9 已提交待复审** @ `a280025`（`p1-a2-v9`）；未部署 |
| B 代码块保护 | 独立待办，未开工 |
| 仓库 | `zzc`（公开，代码/审查材料）、`zzc-context`（公开，档案） |

### P1-A1 三条 PENDING（不得当作 PASS）

1. 完整 DSML 标记的端到端清理（真机被模型改写，清洗器执行但未验证完整标记）。
2. 代码块保真归因（受 `style_strip` 干扰，`completion_text` 未取得）。
3. fail-closed 真机证据（不做线上故障注入）。

## 四、下一步

**当前**：v9 已提交（`p1-a2-v9` @ `a280025`），等独立复审。v8 复审不通过已保留原包，不覆盖。
复审通过后才部署，部署前再备份线上 v6。

**v9 已完成的内容**：
1. 只改 `astrbot_plugin_tool_xml_guard/main.py` + `测试/test_out_guard.py`。
2. 备份线上文件：`/opt/astrbot/shared/记忆/备份_20261119_p1a2/`。
3. 按裁定新增第二种闭合形式 `<｜｜DSML｜｜ /name>`，接入严格栈式配对；标准闭合同步收紧。
4. 测试：**27 组 171 项 ALL PASS**（原有 88 + v8 新增 54 + v9 新增 29；5KB 4.61ms）。
5. 提交 `zzc` 分支 `p1-a2-v9`：完整 diff、测试源码、日志、文件 SHA、性能实测，在 `reviews/P1-A2-v9/`。
6. **未部署、未重启**；线上 `main.py` 仍为 `c4497e04…`（v6）。

## 五、红线

- 未批准前：不改源码、不改测试、不改配置、不部署、不重启。
- 不碰：`multi_bubble`、P0、B0.5、B1、recall_boost、`trust_gate`、`trust_context`、AstrBot 核心。
- 不改 9 个直发点（P1-A2 其余部分）。
- 推送失败重试，但不关闭 TLS 校验、不改目标分支、不 force push。

## 六、环境速查

- 服务器：腾讯云 Ubuntu 22.04，SSH 密钥 `default-workspace/.ssh/id_desktop`
- 容器：`astrbot`（AstrBot v4.29.4）、`snowluma`（OneBot）、`ollama`（bge-m3）
- 线上插件：`/opt/astrbot/data/plugins`（容器 `/AstrBot/data/plugins`），106 个
- 当前线上 `tool_xml_guard/main.py`：`c4497e04…`（v6）；`multi_bubble`：`5e2519…`
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
