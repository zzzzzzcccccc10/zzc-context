# v39 目标 Linux 实验方案（骨架；待 v40 完整化）

- **状态**：**骨架，不完整**；v39 复审已判不通过；本文件仅消除设计 §8 引用悬空
- **对应设计**：`部署脚本整改设计-v39.md` §8
- **说明**：完整环境/程序/操作/唯一判据/清理/时间预算待 v40 补齐；**未执行、未授权**

## 一、授权单元

| 单元 | 名称 | 环境 | 允许 | 明确不含 |
|---|---|---|---|---|
| A0 | 启动实测 | 一次性 VM/独立测试根 | T0b、E16 安装/升级、selfcheck、篡改 | E02–E15、目标宿主、生产 |
| A1 | 只读盘点 | 目标宿主/同版本 VM | E01、E14（只读） | 写文件、执行项目代码、sudo、启动服务 |
| A2 | VM 主动实验 | 一次性 VM | E02–E13、E15 | A0/T0b、E16、生产 |

- A0/A1/A2 独立授权、互不蕴含；A0 不在目标宿主 `/opt/astrbot-deploy` 或 `/var/lib/astrbot-deploy` 执行。
- T0b 必须单独授权（A0 内逐条列出）。

## 二、实验清单（E01–E16，骨架）

| ID | 授权 | 目的 | 通过判据（骨架） |
|---|---|---|---|
| E01 | A1 | 环境盘点 | 内核/Python/cgroup v2/OOB 记录；不满足 fail-closed |
| E02 | A2 | SCM_RIGHTS 交付位置 | fd 随帧首字节、按帧累计 |
| E03 | A2 | 分段/部分读 | fd 仍归当前帧 |
| E04 | A2 | 0 长度语义 | 禁止 0 长度请求成立 |
| E05 | A2 | shutdown/close/ECONNRESET | 语义记录；ECONNRESET 非 EOF |
| E06 | A2 | CTRUNC fd 关闭 | 记录；合同不依赖 |
| E07 | A2 | pidfd/fdinfo/waitid | 身份链可用 |
| E08 | A2 | cgroup v2 | 建/迁/read-back/空判定 |
| E09 | A2 | subreaper | 收养/回收/无僵尸 |
| E10 | A2 | ENOSPC/EROFS/fsync | 语义记录 |
| E11 | A2 | flock 跨 fork/exec | 锁语义/探针 |
| E12 | A2 | 超时校准 | p99 阈值满足（v40 定义） |
| E13 | A2 | Bash 边界 | 记录不可行项 |
| E14 | A1 | CLI 形态 | ELF/脚本链/`/proc/exe` 可行性；无活体则 UNDECIDABLE |
| E15 | A2 | OOB | 三分支记录；不成为启动条件 |
| E16 | A0 | 安装/升级/回滚 | 原子性/崩溃恢复/40/41；独立根 |

## 三、清理（骨架）

冻结证据 → 杀探针 → 清 cgroup（确认空）→ umount → 恢复 mount/sysctl → rm → 销毁 VM → 销毁/回滚证明；失败路径同样执行；清理失败 = UNDECIDABLE(CLEANUP_FAIL)。

## 四、时间预算（骨架）

共享绝对 deadline `T_HANDSHAKE_TOTAL=20s`（spawn_begin 起）；阶段 5s 仅上限；`T_REAP`/`T_CLI_WAIT` 独立；E12 校准（≥200 次采样，p99≤0.1×cap、握手累计 p99≤0.5×total）；不可判定不计通过；watchdog 触发=FAIL。

## 五、待 v40 完整化

- 每项实验的环境/程序/命令/原始输出/唯一判据/清理步骤/时间预算；E16 安装链崩溃点；A1 零写入证明；FC-R scope；Docker `_ping`/Python 3.9/3.12 双版本要求。
