# 项目状态（截至 2026-11-18）

> 状态词：**封版**（验收通过、不再改动）/ **已部署**（线上在跑）/ **施工中** / **待复审** / **独立立项**（未排期）

## 一、总览

| 模块 | 状态 | 部署 | 证据 |
|---|---|---|---|
| P0 安全层（执行门禁 / 状态一致性 / Goal 租约） | 封版 | 是 | 2026-11-16 审查通过 |
| B0.5 工具门禁 | 封版 | 是 | gate harness 通过；白名单 10 工具 |
| B1 请求级信任上下文 + 外部来源标记 | 封版 | 是 | 2026-11-16 封版；harness 60 项 |
| P1-recall_boost（按问句检索 + 权限现查 + 缓存） | 封版 | 是 | 2026-11-17 节点二验收通过；`main.py 65e69d66…` |
| P1-A1 统一输出清洗（v6） | **已部署，待验收确认** | 是 | 2026-11-19 00:02 部署；`bc04462…`；`tool_xml_guard 973e54d4…` / `multi_bubble 7de0e5cb…` |
| P1-A2 其余直发点（9 处会把模型正文直发） | 未开始 | 否 | 见 `HANDOFF.md` 遗留项 |
| `<｜｜ calls>` 残片泄漏 | 独立立项 | 否 | 17:48 实测；`rule_guard` + `tool_xml_guard` 清理尾巴问题 |
| 好友管理权限收紧（严格 OWNER_QQ） | 待办 | — | 维护手册待办 |
| 情绪 / 生活线 / 愿望（人格与生命设计） | 设计阶段 | — | `小恋-人格与生命设计.md` v0.2 |

## 二、线上事实（2026-11-18）

- 环境：腾讯云 Ubuntu 22.04 + Docker；`astrbot`（AstrBot v4.29.4）+ `snowluma`（OneBot v11）+ `ollama`（bge-m3）。
- 插件总数 **106**（全部加载成功），另有 `plugins_off/group_chat_plus` 停用 1 个。
- recall_boost 缓存：`记忆/recall_boost_vectors.json`，跨重启 0 重算（0.2–0.3s 完成预热）。
- 会话白名单 6 条（主人私聊、三个群、3025260592、3669402050）。
- 核心补丁（已登记维护手册 9.1）：waking_check 群唤醒、respond 拦 `[不回]`、web_search 成本封顶、bilibili 记忆桥、whitelist 放行 request 事件。

## 三、最近一次部署（P1-A1 v6，2026-11-19 00:02）

- 部署前备份：`记忆/备份_20261119_p1a1/`（`af28ee24…` / `ec04a930…`）
- 部署后：`tool_xml_guard 973e54d4…`、`multi_bubble 7de0e5cb…`（= v6 snapshot）
- 重启 StartedAt 00:02:39，RestartCount 0，Traceback/ImportError 0，适配器 00:02:54 连接
- recall_boost 热启动：`docs=136 atoms=240 用时 0.2s`
- 真机 4 条：零异常、下发内容无 `<｜｜` 残片、多气泡补发 2 条正常
- 线上代码行为验证：输入 `测试 <｜｜DSML｜｜ calls> 结束` → 输出 `测试  结束`（标记删除、两侧空格保留）
- 未覆盖：真机未触发清洗器（她没输出标记）；代码块保真未在真机体现；版本号显示仍为 metadata.yaml 的 1.0.0

## 四、P1-recall_boost 节点二部署（2026-11-17）

- 部署后 `main.py 65e69d66…`、`vec_cache.py e8b6f3d0…`，独立备份在 `记忆/备份_20261117_recall_boost/`。
- 冷缓存：首轮 5 条失败未发布 READY，60 秒重试补全后发布（fail-closed 生效）。
- 请求级注入窗：0.18–9.4 秒（旧版分钟级）。
- 隐私：私聊 `r1=False`、群/非主人私聊只拿 public 原子 + 本会话文档；canary 8 项通过。

## 四、未完成的观测项（不阻断封版）

1. 线上满载并发（两个 query 槽位）未压满：单会话有 session lock + `msg_merge` 合并。
2. 请求级 LRU 命中缺线上计数（短问句 embed 仅 0.10s，耗时差异在噪声内）。
3. `_qlru_get_locked` 命中不刷新时间戳（实际是 TTL+容量缓存，非严格 LRU）。
4. `VectorCache._save()` 返回值未参与 READY 判定。
