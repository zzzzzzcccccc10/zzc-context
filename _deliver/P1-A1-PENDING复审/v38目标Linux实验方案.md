# v38 目标 Linux 实验方案（只设计，不执行）

- **文档类型**：实验设计（需主人单独授权后才可执行）
- **对应设计**：`_deliver/P1-A1-PENDING复审/部署脚本整改设计-v38.md`
- **状态**：**未执行**；不触碰线上小恋、不挂生产 docker.sock、不挂 `/opt/astrbot`
- **日期**：2026-11-23

## 一、公共环境与安全边界

- **环境**：一次性 VM（QEMU/KVM 或独立测试机），内核尽量与目标一致；`uname -r` 固定记录；无生产数据/凭据；网络可断（实验不需外网）。
- **版本前置**：Linux ≥5.4（`pidfd_open/P_PIDFD/waitid`；cgroup v2 统一层级）、Python ≥3.9（`os.pidfd_open`/`os.P_PIDFD`）；E01 记录实际值，不满足则对应实验标记“不可执行”，不得降级。
- **授权拆分**：**A1 只读** = E01 + E14（目标宿主只读盘点，不产生系统改动）；**A2 主动** = E02–E13 + E15（一次性 VM 内）。A1 与 A2 分别授权；A1 通过不构成 A2 授权。
- **退出判据**：每项实验必须“预期结果全部满足 + 清理确认完成”才记为通过；任一不满足即失败并记录原始输出/errno/内核版本；不得以“大致符合”通过；“不可判定”不得计通过。
- **隔离哨兵**：`/run/deploy-test-vm` 存在；`/opt/astrbot` 不存在；无名为 `astrbot` 的容器；无 `soulter/astrbot` 镜像；`/var/run/docker.sock` 不存在或 `DOCKER_HOST` 不指向生产；`/proc/self/mountinfo` 无生产路径 bind mount；`systemd-detect-virt`/QEMU 证明是 VM；VM 镜像 hash 记录；无共享目录/SSH agent；E02–E13 默认 `--net none`。缺任一条件拒绝运行。
- **权限**：VM 内 root 仅用于实验；普通非 root 用户运行探针；不 sudo 提权到生产路径；E08/E10 的 cgroup/mount 操作属 VM 内豁免，需在授权单列出。
- **实验根**：`/srv/deploy-test/` 或 `mktemp -d /tmp/proto-eN.XXXXXX`（0700）。
- **禁止**：向任何生产进程发信号；不做故障注入到线上；不改系统配置/sysctl/权限（VM 内授权单列明的除外）；不安装生产包。
- **清理顺序（v38 修正）**：先归档证据（strace/errno/输出）→ 杀探针/子进程 → 删临时目录 → umount 私有 tmpfs → rmdir cgroup → 恢复 mount/sysctl → 销毁/回滚 VM → 记录销毁/回滚证明；失败路径同样执行。

## 二、实验清单（E01–E15；E01/E14 只读，E02–E13/E15 VM 内）

| ID | 目的 | 环境/前置 | 测试程序要点 | 操作 | 预期结果 | 判定/用途 | 清理 |
|---|---|---|---|---|---|---|---|
| E01 | 环境盘点（只读，不执行协议实验） | 目标宿主只读或同版本 VM | `uname -a/-r/-m`、`/boot/config-$(uname -r)` 或 `/proc/config.gz`、`/sys/fs/cgroup` 挂载、`python3 -V`、syscall 探测 | 只读采集 | 记录内核/配置/Python/cgroup v2；`CONFIG_AF_UNIX_OOB` 明确 | 决定 Q01/Q12；不满足则 fail-closed；**不授权 E02–E14** | 无 |
| E02 | SCM_RIGHTS 在 STREAM 的交付位置 | VM | 发送 36B+1fd；接收三法：`recvmsg(4)+cmsg`、`recvmsg(36)+cmsg`、`recvmsg(4)` 无 cmsg 后 `recvmsg(32)+cmsg` | 三组配对 | fd 随首字节（4B 前缀那次）返回；无 cmsg 时 `MSG_CTRUNC` 且 fd 被内核关闭 | 证实“每次 recvmsg 带控制缓冲、fd 按帧累计”唯一正确 | 关 fd、删目录 |
| E03 | fd 绑定第二段 sendmsg/部分读 | 同上 | 先发 4B 无 fd、再发 32B+fd；逐字节喂入 | 运行 | fd 随第二段首字节返回；仍归属当前帧 | 确认粘包/分段接收合同 | 同上 |
| E04 | 0 长度语义 | 同上 | 0 字节 sendmsg（带/不带 fd）、0 长度 recvmsg/read、shutdown 后读 | 运行 | 0 长度 send 不产生字节；0 长度 read 在数据在队时也返回 0（证伪 EOF 判据）；shutdown 后返回 0 | 证实禁止 0 长度请求、STREAM 无零长度记录 | 同上 |
| E05 | shutdown vs close/ECONNRESET | 同上 | 对端 shutdown/close（有/无未读数据）；关后写；MSG_NOSIGNAL 对照 | 运行 | shutdown→干净 EOF；close+未读→可能 ECONNRESET；无 MSG_NOSIGNAL 收 SIGPIPE | 决定 ECONNRESET 必须 fail-closed；MSG_NOSIGNAL 必须 | 同上 |
| E06 | CTRUNC 时内核是否关 fd | 同上 | 控制缓冲故意不足，发送带 fd 帧；数 fd 与 strace | 运行 | 收到 CTRUNC；fd 计数不增长（或记录内核行为） | 文档化；合同不依赖该行为 | 同上 |
| E07 | pidfd 身份/fdinfo/waitid | VM | `pidfd_open`、读 fdinfo `Pid`、`waitid(P_PIDFD)`、`/proc/pid/stat` 第 22 字段、PID 复用窗口 | 运行 | fdinfo 字段可用；waitid 可回收；starttime 可交叉核对 | 确认身份链；缺字段则退化为 hold（不按 pid 杀） | 同上 |
| E08 | cgroup v2 叶节点/迁移/空判定 | VM root | 建 0700 目录、读 `cgroup.events`、写 `cgroup.procs`、进程退出后 `populated`、`rmdir` | 运行 | 可建/可迁/非空 rmdir EBUSY/空判定可靠 | 确认 cgroup 合同；不可用 fail-closed | rmdir、杀残留 |
| E09 | subreaper + 孤儿收养 + 回收 | VM | 主设 subreaper→fork supervisor→fork CLI→杀 supervisor | 运行 | CLI reparent 主进程；waitid 可回收；无僵尸 | 确认回收合同 | 杀进程 |
| E10 | ENOSPC/EROFS/fsync errno | VM + 私有 tmpfs | 256k tmpfs 预填；open 后 remount,ro；write/fsync 返回 | 运行 | ENOSPC/EROFS 语义记录；部分写记录 | 确定“未持久化”判定；fsync 失败只 T2 覆盖 | umount、删 |
| E11 | flock 跨 fork/exec/CLOEXEC | VM | 父 flock→inheritable→exec 子；子 fstat/fdinfo；另一进程 probe；kill -9 后 probe | 运行 | 锁随最后持有 fd 关闭释放；probe 语义；fdinfo `lock:` 行记录 | 确认锁持有/释放观测方式 | 删锁文件 |
| E12 | 超时/时钟校准 | VM 负载可调 | 各握手阶段 ≥200 次采样；CLOCK_MONOTONIC 抖动；覆盖 `T_PIDFD/T_DONE/T_ACK/T_FIN/T_SUP_EOF/T_MAIN_EOF/T_REAP/T_CLI_WAIT/T_TOTAL` | 运行 | 得到各阶段分位数；握手常量 ≥10× 余量；CLI 等待单列；负载/分位定义写入报告 | 冻结超时常量；不可判定=不通过 | 删结果 |
| E13 | Bash 能力边界复核 | VM | 逐项尝试 pipe2/SCM_RIGHTS/pidfd/prctl/fsync/CLOCK_MONOTONIC/flock | 运行 | 逐项记录“不可行/需外部程序” | 支撑“Bash 不够”结论 | 删脚本 |
| E14 | 目标 CLI 形态（只读） | 目标只读或镜像 | `file /usr/bin/docker`、脚本包装链、`/proc/<pid>/exe` 期望 | 只读 | 确定 ELF/脚本/解释器链 | 决定 T-EXEC-SUCCESS 的 proc_exe 可用性；归 A1 | 无 |
| E15 | OOB / SO_OOBINLINE 行为 | VM | 记录 `CONFIG_AF_UNIX_OOB`；`send(MSG_OOB)` 返回；`SO_OOBINLINE` 设置结果与内联字节位置；普通读行为 | 运行 | 三种分支（不支持/支持未内联/支持已内联）均记录并可判定 | 冻结 OOB 合同；不得把 OOB 当启动条件 | 关 fd、删目录 |

## 三、执行前置与授权

- 全部实验需主人单独授权；授权前结论保持“未验证”。**A1 只读（E01/E14）与 A2 主动（E02–E13/E15）分开授权**；A1 通过不构成 A2 授权。
- 每项最低版本：Linux ≥5.4、Python ≥3.9（E01 实测记录）；不满足的实验标“不可执行”，不得降级。
- 建议顺序：A1（E01/E14）→ A2 内 E02/E04/E05/E15 → E06 → E07/E08/E09 → E11/E12 → E13 → E03/E10。
- 任一实验结果与合同假设不符 → 记录、设计返修；不得放宽 fail-closed。
- 实验报告需附：命令、原始输出、errno、内核版本、清理确认、销毁/回滚证明；不携带生产数据。
