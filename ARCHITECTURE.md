# 总体架构

## 一、部署形态

```
QQ 用户 ──▶ SnowLuma（OneBot v11，容器 snowluma）
                │  WS 反向连接（127.0.0.1:6199，token 存于 cmd_config）
                ▼
        AstrBot v4.29.4（容器 astrbot）
          ├─ 106 个插件（/AstrBot/data/plugins，bind mount）
          ├─ 人格/提示词（人设_当前_*.txt）
          ├─ livingmemory（记忆库 livingmemory.db + 原子.jsonl）
          └─ ollama（bge-m3 向量，127.0.0.1:11434）
```

## 二、消息处理管线（AstrBot 内置顺序）

```
WakingCheckStage        是否唤醒（@ / wake_prefix / 插件 filter）
WhitelistCheckStage     会话白名单（核心 PATCH: request 事件放行）
SessionStatusCheckStage 会话总开关
RateLimitStage          频率限制
ContentSafetyCheckStage 内容安全
PreProcessStage         预处理
ProcessStage            插件处理 → LLM 调用
ResultDecorateStage     回复装饰（on_decorating_result 钩子在这里）
RespondStage            真正发送（event.send）
```

之后触发 `OnAfterMessageSentEvent`（`multi_bubble.after_sent` 在这里补发气泡）。

## 三、关键数据流

### 记忆注入

```
用户消息 → recall_boost.split_questions（≥2 问句才动）
        → 阶段A：算 query 向量（await，15s 预算，2 线程池）
        → 阶段B：await 结束后现查权限（原子 vis / 文档 session+正文 hash）
        → 排序取 top → 追加到 system_prompt
```

### 输出清洗（P1-A1 目标）

```
LLM 文本 → multi_bubble 拆分（拆前清洗）
        → on_decorating_result 钩子链（rule_guard 80 / style_strip 90 / tool_xml_guard −1000000 最后）
        → RespondStage 发送
        → after_sent → multi_bubble 补发（补发前再清洗，直发不走 pipeline）
```

## 四、插件分层（106 个）

- 记忆：laboratory（livingmemory / recall_boost / fact_ledger / context_peek / event_digest）
- 人格情绪：growth / affinity / person_memory / fish_tone / signature_mood
- 表达输出：rule_guard / style_strip / multi_bubble / tool_xml_guard / face_map / meme_*（7）
- 生活日程：life / her_day / her_project / day_plan / diary_*（4）/ heartbeat
- 社交群：group_eye / light_gate / friend_gate / msg_merge / quiet_files
- 能力工具：desktop_view / web_lookup / B站 4 件 / voice_stt / workshop / pocket_money / agency_core
- 安全门禁：antipromptinjector / owner_guard / pause_switch

完整清单见公开仓库 `zzc` 的 `插件清单.md`（含每插件工具、钩子、配置、状态目录）。

## 五、重构原则

1. 能改配置 → 改配置；配置不行 → 自己写插件；插件不暴露接口 → 才改核心并登记。
2. 一致性优先：门禁/权限判断一律 fail-closed。
3. 数据与判断分离：向量快照只当索引，权限每次现查。
