# v40 目标 Linux 实验方案（完整交付）

- **对应设计**：`部署脚本整改设计-v40.md` §8
- **状态**：设计交付；**未执行、未授权**；执行需主人对 A0/A1/A2/A2-R 分别签发
- **边界**：只读/一次性 VM；不改源码、不跑项目测试、不部署线上

## 一、授权单元

| 单元 | 环境 | 覆盖 | 明确不含 |
|---|---|---|---|
| A1 | 目标宿主只读（或同版本 VM/overlay 只读证明） | T0a 生产工件、E01、E14a | 写文件、执行项目代码、sudo、起服务、T0b/T1–T4/E16 |
| A0 | 一次性 VM/独立根（不在目标宿主） | T0b-01..16（逐条）、E16a–f、installer 直调 | E02–E15、目标宿主、生产 |
| A2 | 一次性 VM | T1–T4、E02–E13/E15、E14b | T0b、E16、目标宿主、生产 docker |
| A2-R | 一次性 VM（真实 docker） | FC-01b/T3-02 | 生产 socket/宿主 |

- A0/A1/A2/A2-R 独立授权、互不蕴含；A1 通过不构成 A2；A2 不构成 A0；实验授权≠施工；设计通过≠部署。
- A0 使用 VM 内 canonical `/opt/astrbot-deploy` 与 `/var/lib/astrbot-deploy`（由 A0 harness 重建），不碰目标宿主同名路径；`.a0-test-root` marker 门控 `--test-*`。

## 二、公共前置（所有 A2 实验）

一次性 VM（QEMU/KVM 或独立测试机）；哨兵：`/run/deploy-test-vm` 存在、`/opt/astrbot` 不存在、无 `astrbot` 容器/生产镜像、无生产 `docker.sock`、无 9p/virtiofs/nfs/host share、`SSH_AUTH_SOCK` 未设、`--net none`（除 A2-R/E02 等显式声明）；测试根 `$H`（0700，SHA256SUMS 冻结）；最低版本 Linux≥5.4、Python 3.9–3.12 64 位、cgroup v2 统一；不满足即“不可执行”，不得降级。

## 三、E01–E16

| ID | 授权 | 前置/环境 | 程序与操作 | 唯一判据 | 清理 | 预算 |
|---|---|---|---|---|---|---|
| E01 | A1 | 目标宿主只读或同版本 VM | 只读采集 kernel/Python/cgroup v2/pidfd/waitid/prctl/flock/OOB/`/usr/bin/{python3,sha256sum,stat,docker}` 形态；`$H/e01/probe > out` | 必需项齐全；缺失→fail-closed，后续实验不可执行 | C3 | 10m |
| E02 | A2 | socketpair | recvmsg 三法+cmsg 计数 | fd 随帧首字节交付；无 cmsg→CTRUNC 且 fd 计数不增 | C1 | 10m |
| E03 | A2 | socketpair | 两段 sendmsg/逐字节 | fd 随第二段首字节返回，仍归当前帧 | C1 | 10m |
| E04 | A2 | socketpair | 0 长度矩阵 | 0 长度 send 不产生字节；数据在队时 0 长度 read 返 0；shutdown 后读 0 | C1 | 10m |
| E05 | A2 | socketpair | shutdown/close/MSG_NOSIGNAL | shutdown→干净 EOF；close+未读→可 ECONNRESET；SIGPIPE 处置记录 | C1 | 10m |
| E06 | A2 | socketpair | 控制缓冲不足 | 记录 CTRUNC 时内核是否关 fd；合同不依赖 | C1 | 10m |
| E07 | A2 | P2 | pidfd/fdinfo/waitid | fdinfo Pid=pid；waitid 回收；starttime 交叉一致 | C1 | 10m |
| E08 | A2 | P2（VM root） | cgroup v2 叶节点 | mkdir 0700；写 cgroup.procs 可迁；退出后 populated=0；rmdir 成功 | C1 | 15m |
| E09 | A2 | P2 | subreaper/收养/回收 | 孤儿归 main；waitid 回收；无僵尸 | C1 | 10m |
| E10 | A2 | P6 | ENOSPC/EROFS/fsync | 语义记录且可判定 | C1 | 15m |
| E11 | A2 | P2 | flock 跨 fork/exec | 锁随最后 fd 关闭释放；probe 可判；fdinfo lock 行记录 | C1 | 10m |
| E12 | A2 | 负载可调 | 超时校准（见 §4） | §4 全部阈值满足；否则 FAIL | C1 | 90m |
| E13 | A2 | P2 | Bash 能力边界 | 逐项记录可行/不可行/需外部程序 | C1 | 15m |
| E14a | A1 | P1 | CLI 静态形态 | ELF/脚本链/解释器链确定；`/proc/exe` 预期记录；无活体→U5 | C3 | 10m |
| E14b | A2 | P2+CLI 活体 | 动态 `/proc/exe` | 50 次采样 exe 稳定=exec 目标；无活体→U5 | C1 | 10m |
| E15 | A2 | P2 | OOB/SO_OOBINLINE | 三分支（不支持/支持未内联/支持已内联）记录完整；不成为启动条件 | C1 | 10m |
| E16 | A0 | P5（VM 内 canonical） | `$H/e16/run --sub=a..f` | E16a–f 逐项（见 §5）；40/41 精确 | C2 | 45m |

## 四、E12 阈值

- 采样：握手 6 阶段（`T_PIDFD/T_DONE/T_ACK/T_FIN/T_SUP_EOF/T_MAIN_EOF`）每负载 ≥200 次；`T_REAP`/`T_CLI_WAIT` 每负载 ≥100 次；负载 L0 空闲、L1=1×ncpu、L2=2×ncpu；记录 loadavg/CPU%/steal。
- 通过（全部满足）：每阶段每负载 `p99 ≤ 0.1×cap` 且 `max ≤ 0.5×cap`；握手累计 `p99 ≤ 0.5×10s` 且 `max ≤ 0.75×20s`；10k 次 MONOTONIC 抖动 |Δ|≤1ms。
- cap 冻结值：阶段 5s、`T_REAP=5s`、`T_CLI_WAIT=120s`、`T_HANDSHAKE_TOTAL=20s`。
- 任一不满足 → FAIL（不改 cap 迁就）；L2 相对 L1 的 p99 离散 >3× 视为噪声，重跑一次，仍噪声 → U6（不通过）。

## 五、E16 子项（仅 A0，VM 内 canonical）

- E16a 首次安装：exit 0；4 文件/模式/SHA/VERSION/install.json 齐全；selfcheck 0；无 `.old`。
- E16b 升级：exit 0；VERSION 新；保留 1 代 prev；selfcheck 0；包 SHA 交叉一致。
- E16c 回滚：诱导验证失败→回滚成功 exit 40；canonical 恢复旧 VERSION；selfcheck 0。
- E16d 回滚失败：移走 prev 后诱导失败→exit 41；状态记录完整、无静默成功。
- E16e 崩溃点 S2/S4/S5/S6/S7（D0–D9）：inotify 观察 `.new/.old/canonical` 后 SIGKILL；重跑安装器；终态只能“旧→新完成”或“回滚成功”；S4 窗口 wrapper 允许 10（窗口预期），安装结果不由 wrapper 10 判定；恢复后 selfcheck 0。
- E16f 预置 latch/未裁决 hold：安装/升级拒绝 exit 11，零改动。
- 边界：40/41 是安装器表（不进 helper 表）；VM 销毁后以销毁日志证明。

## 六、清理与隔离

### C-A2 清理顺序（失败路径同样执行；任一步失败→U4 并阻断后续）

1. 冻结证据（复制 WAL/sidecar/errno/strace/日志到 `$H/out`，SHA256 清单，只读）→ 2. 杀探针/子进程（TERM→KILL，waitpid，无僵尸）→ 3. cgroup：迁回根、确认 populated=0、rmdir → 4. umount 私有 tmpfs → 5. 恢复 mount/sysctl（记录 diff 后恢复并复核）→ 6. 删测试根/临时根 → 7. 销毁 VM 或回滚快照，记录销毁/回滚证明 → 8. 归档清理证据与判定。

### C-A0

归档→销毁 VM→销毁证明；`.a0-test-root` 随 VM 销毁；目标宿主两路径的 A1 前后快照必须不变（哨兵）。

### C-A1

无宿主写入；本地归档 transcript + 白名单复核；前后快照（findmnt/ps/stat+sha256）逐项不变；任一变化 ⇒ A1 FAIL（不是 U）。强证明变体：同版本 VM + overlayfs 只读 lower + tmpfs upper，运行后 upper 为空。

## 七、A1 零写入证明（W-A1）

- 命令白名单（stat/readlink/sha256sum/file/cat/proc 读取）；argv 落盘审计。
- 前后快照：`findmnt -R`、`ps -eo pid,lstart,cmd`、安装树/状态根 stat（ino/size/mtime/ctime）+ sha256 逐项不变；无新进程；状态根无新文件。
- E14a 的 `/proc/<pid>/exe` 动态部分不属于 A1（拆 E14b/A2）；无活体→U5；T-EXEC-SUCCESS 不得依赖 proc_exe。

## 八、判定与授权边界

- 实验通过 = 唯一判据全部满足 + 清理证明齐全 + 无不可判定；任一 U 计不通过；watchdog 触发=FAIL；实验 FAIL 依赖 case BLOCKED。
- 每项实验落盘：exp_id/auth/run_id/env（VM 镜像 SHA、kernel、Python、boot_id）/pre_sentinel/命令与原始输出/expected 逐项/result/cleanup/destroy_proof。
- 未执行、未授权；执行需主人对 A0/A1/A2/A2-R 分别书面签发，单次有效。
