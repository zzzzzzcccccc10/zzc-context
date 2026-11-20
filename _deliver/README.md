# 正式交付报告归档

本目录存放正式交付报告（2026-11-21 起按长期交付规范执行）。

- **zzc**：代码、测试源码、测试日志、版本快照、审查材料。
- **zzc-context**（本仓库）：项目状态、交接记录、协作规范、架构决策、正式交付报告。

## 报告索引

| 任务 | 报告 | 仓库 | 分支 | commit | 路径 | GitHub 链接 |
|---|---|---|---|---|---|---|
| P1-A2 v14 | 交付报告 | zzzzzzcccccc10/zzc-context | main | `25bcac9` | `_deliver/P1-A2-v14/交付报告.md` | https://github.com/zzzzzzcccccc10/zzc-context/blob/25bcac9/_deliver/P1-A2-v14/交付报告.md |
| P1-A2 v14 部署准备 | 部署准备报告 | zzzzzzcccccc10/zzc-context | main | `25bcac9` | `_deliver/P1-A2-v14-部署准备/部署准备报告.md` | https://github.com/zzzzzzcccccc10/zzc-context/blob/25bcac9/_deliver/P1-A2-v14-部署准备/部署准备报告.md |

## 代码与审查材料（zzc）

仓库：`zzzzzzcccccc10/zzc`

| 版本 | 分支 | commit | 审查材料路径 |
|---|---|---|---|
| v14（复审通过） | `p1-a2-v14` | `9151477` | `reviews/P1-A2-v14/` |
| v13 | `p1-a2-v13` | `6ae856c` | `reviews/P1-A2-v13/` |
| v12 | `p1-a2-v12` | `54ae3a9` | `reviews/P1-A2-v12/` |
| v11 | `p1-a2-v11` | `f066cf9` | `reviews/P1-A2-v11/` |
| v10 | `p1-a2-v10` | `ce2b90f` | `reviews/P1-A2-v10/` |
| v9 | `p1-a2-v9` | `a280025` | `reviews/P1-A2-v9/` |
| v8 | `p1-a2-v8` | `67b2f15` | `reviews/P1-A2-v8/` |

## 说明

- 报告引用的代码、测试源码、日志、SHA 均在 `zzc` 对应分支的 `reviews/<版本>/` 下。
- 隔离测试与真实线上验证分开表述；未部署时不得把隔离测试写成真实 E2E。
- 本索引随新报告追加更新。
