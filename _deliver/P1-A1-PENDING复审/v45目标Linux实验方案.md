# v45 目标 Linux 实验方案（完整交付）

- **对应设计**：`部署脚本整改设计-v45.md` §八
- **状态**：设计交付；**未执行、未授权**；执行需主人对 A0/A1/A2/A2-R 分别签发
- **计数**：E01–E16；新增 T2-21/T3-22 相关判据；不删旧实验项。

## 一、授权单元

| 单元 | 环境 | 覆盖 | 明确不含 |
|---|---|---|---|
| A1 | 目标宿主只读（或同版本 VM/overlay 只读证明） | T0a、E01、E14a、N5 静态依据 | 写文件、执行项目代码、sudo、起服务、T0b/T1–T4/E16 |
| A0 | 一次性 VM/独立根（不碰目标宿主） | T0b-01..16、E16a–f、D0–D9、installer 直调 | E02–E15、目标宿主、生产 |
| A2 | 一次性 VM | T1–T4、E02–E13/E15/E14b | T0b、E16、目标宿主、生产 docker |
| A2-R | 一次性 VM（真实 docker） | FC-01b/T3-02 | 生产 socket/宿主 |

- 四单元独立、互不蕴含；实验授权≠施工；设计通过≠部署。
- A0 使用 VM 内 canonical `/opt/astrbot-deploy` 与 `/var/lib/astrbot-deploy`（A0 harness 重建）；`.a0-test-root` 门控 `--test-*`。
- 每项落盘：exp_id/auth/run_id/env（镜像 SHA/kernel/Python/boot_id）/pre_sentinel/命令与原始输出/expected 逐项/result/cleanup/destroy_proof。

## 二、公共前置

一次性 VM；哨兵：`/run/deploy-test-vm`、`/opt/astrbot` 不存在、无 astrbot 容器/生产镜像/生产 socket、无 9p/virtiofs/nfs/host share、`SSH_AUTH_SOCK` 未设、`--net none`（A2-R 除外）；测试根 `$H` 0700+SHA 冻结；最低 Linux≥5.4、Python 3.9–3.12 64 位、cgroup v2 统一；不满足即不可执行。

**[GATE-A0]** U-01（VERSION/install.json/journal schema 与包摘要公式）与 U-02（生产/测试同源规范）已冻结；冻结登记 `$H/pre/u01-u02.freeze.json` 经 precheck 校验。未登记/哈希不符 → A0、F-SEAL、T0B-01..16、E16a–f、D0–D9、installer 直调 **BLOCKED(A0_GATE_U01_U02)**，不计分、不填 0/N/A；单独 A0 授权不能解除。

**[SEAL-DEP]** T0B-03/05/16 另需 F-SEAL 阳性对照 selfcheck 0 留证；未过 → **BLOCKED(F_SEAL_DEP)**。

## 三、E01–E16

| ID | 授权 | 前置 | 程序/操作 | 唯一判据 | 清理 | 预算 |
|---|---|---|---|---|---|---|
| E01 | A1 | P1 | 只读采集 kernel/Python/cgroup v2/pidfd/waitid/prctl/flock/OOB/工具形态 | 必需项齐全；缺失 fail-closed | C3 | 10m |
| E02 | A2 | P2+P11 | recvmsg 三法+cmsg 计数 | fd 随帧首字节；无 cmsg→CTRUNC 且 fd 计数不增 | C1 | 10m |
| E03 | A2 | P2+P11 | 两段 sendmsg/逐字节 | fd 随第二段首字节返回，仍归当前帧 | C1 | 10m |
| E04 | A2 | P2+P11 | 0 长度矩阵 | 0 长度 send 不产生字节；数据在队时 0 长度 read 返 0；shutdown 后读 0 | C1 | 10m |
| E05 | A2 | P2+P11 | shutdown/close/MSG_NOSIGNAL/FRAME 三态 | shutdown→干净 EOF；close+未读→可 ECONNRESET；8B+EOF/8B+extra/8B+TIMEOUT 记录 | C1 | 10m |
| E06 | A2 | P2+P11 | 控制缓冲不足 | 记录 CTRUNC 时内核是否关 fd；合同不依赖 | C1 | 10m |
| E07 | A2 | P2 | pidfd/fdinfo/waitid/poll | fdinfo Pid=pid；poll(POLLIN) 判死；POLLHUP 版本记录；starttime 一致 | C1 | 10m |
| E08 | A2 | P2（VM root） | cgroup v2 叶节点 | mkdir/迁移/read-back/populated=0/rmdir | C1 | 15m |
| E09 | A2 | P2 | subreaper/收养/回收 | 孤儿归 main；waitpid 五分支可复现；无僵尸；children 仅辅助；fork2 后未发布子步骤 | C1 | 15m |
| E10 | A2 | P6 | ENOSPC/EROFS/fsync EIO/短写 | 语义记录且可判定；fsync EIO 不当作未落盘；短写可补/不可补 | C1 | 15m |
| E11 | A2 | P2 | flock 跨 fork/exec/close | 锁随最后 fd 关闭释放；probe 可判；fdinfo lock 行 | C1 | 10m |
| E12 | A2 | 负载可调 | 超时校准（§四） | §四阈值全满足；否则 FAIL | C1 | 90m |
| E13 | A2 | P2 | Bash 能力边界 | 逐项记录可行/不可行/需外部程序 | C1 | 15m |
| E14a | A1 | P1 | CLI 静态形态 | ELF/脚本链/解释器链确定；无活体→U5 | C3 | 10m |
| E14b | A2 | P2+CLI 活体 | 动态 `/proc/exe` | 50 次稳定=exec 目标；无活体→U5 | C1 | 10m |
| E15 | A2 | P2 | OOB/SO_OOBINLINE | 三分支记录完整；不成为启动条件 | C1 | 10m |
| E16 | A0 | P5（U-01/U-02 冻结） | `$H/e16/run --sub=a..f` | E16a–f 逐项（§五）；40/41 精确 | C2 | 45m |

## 四、E12 阈值（起点统一）

- `CLOCK_MONOTONIC`；`handshake_deadline=spawn_begin+20s`；阶段 5s 仅上限。
- `T_CLI_WAIT=125s`（release_byte 起）；`T_SUP_EXIT_FRAMED=126s`（完整合法帧+EOF 起，含 125s+1s）；`T_SUP_EXIT=5s`（EOF 无帧）；完整帧无 EOF→1s 协议违规；P 开无帧无 EOF→5s 协议违规；`T_REAP=5s`；`T_EXEC_FRAME=5s`；`T_ABORT_WAIT=5s`；watchdog 180s（halt-live 例外）。
- 采样：握手 6 阶段+EXEC_FRAME 每负载 ≥200；REAP/CLI_WAIT ≥100；L0/L1/L2。
- 通过：每阶段每负载 p99≤0.1×cap、max≤0.5×cap；握手累计 p99≤10s、max≤15s；mono 抖动≤1ms；T2-21 起点/不叠加校验。
- 任一不满足→FAIL（不改 cap）；L2 相对 L1 p99 离散>3× 重跑一次，仍噪声→U6。

## 五、E16 子项与 E16e

- E16a 首装：0；4 文件/模式/SHA/VERSION/install.json；selfcheck 0；无 prev；需 U-01。
- E16b 升级：0；VERSION 新；prev 恰一代；selfcheck 0；需 U-01。
- E16c 回滚：验证失败→installer-rollback 40；canonical 旧 VERSION；selfcheck 0；需 U-01/U-02。
- E16d 回滚失败：移走 prev 后诱导失败→41；状态完整；需 U-01/U-02。
- E16e 崩溃点 S1–S9：inotify 观察后 SIGKILL；重跑；终态只能 0/40；S1/S2/S3→D6；S4→D6b/D8；S5→D7/D7b；S6→D7/D7b；S7→D4；S8→D4/D1；S9→D5/D8；不得残留 journal/pending；prev 恰一代；S4 窗口 helper/selfcheck 10 属预期；出现 41/30/D9 即 FAIL；需 U-01+renameat2。
- E16f 预置 latch/未裁决：安装/升级拒绝 11，零改动；仅受 A0 整体门禁。
- 边界：40/41 属安装器表；VM 销毁留证。

## 六、F-SEAL 10 步（A0）

1 备份→2 阳性对照→3 构造变体→4 同源封印器重封装→5 封印自检→6 原子植入→7 执行 case（T0B-03/05/16）→8 原子恢复→9 归档→10 失败语义（封印链不一致→BLOCKED；恢复失败→U4）。

## 七、v45 新增判据

- **T2-21a/b/c**：126s 从完整合法帧+EOF 起；5s 从 EOF 无帧起；TERM/KILL 精确点（126/127、5/6）；假时钟压缩；不叠加。
- **T3-22a**：fork2 后/cli_spawned 前杀 supervisor→observed=partial、spawn_state=open、cli_state=unknown；P2 22；无 not_sent/observed=true；不向未知 pid 发信号。
- **T3-22b**：同现场 halt(4) 写失败→hold-live（无 exit、心跳、SIGKILL→signal9、next 23）。
- **T3-22c/d/e**：W4R S1/S2/S3→22 latch-only；WAL 末 halt(4)/takeover5/半行；recover basis=latch；不补 takeover5/attempt_hold；首次不截断。
- **T3-18 A/B/C**：A=23（latch 后杀 main）、B=23（SIGSTOP supervisor+杀 main；pidfd/starttime）、C=30（boot_id 不符）；三向量零 WAL 写。

## 八、清理与隔离

### C-A2（失败路径同样执行；任一步失败→U4 并阻断后续）

1 冻结证据→2 杀探针/子进程（TERM→KILL，waitpid，无僵尸）→3 cgroup 迁回根、populated=0、rmdir→4 umount 私有 tmpfs→5 恢复 mount/sysctl→6 删测试根→7 销毁 VM/回滚快照，记录证明→8 归档判定。

### C-A0

归档→销毁 VM→销毁证明；`.a0-test-root` 随 VM 销毁；目标宿主两路径 A1 前后快照不变。

### C-A1

无宿主写入；本地归档 transcript+白名单复核；前后快照（findmnt/ps/stat+sha256）逐项不变；任一变化→A1 FAIL。强证明：overlayfs 只读 lower+tmpfs upper，运行后 upper 为空。

## 九、A1 零写入证明（W-A1）

- 命令白名单（stat/readlink/sha256sum/file/cat/proc）；argv 落盘审计。
- 前后快照：`findmnt -R`、`ps -eo pid,lstart,cmd`、安装树/状态根 stat+sha256 逐项不变；无新进程；状态根无新文件。
- E14a 动态 `/proc/<pid>/exe` 不属 A1（E14b/A2）；无活体→U5；T-EXEC-SUCCESS 不得依赖 proc_exe。

## 十、判定与授权边界

- 通过=唯一判据全满足+清理证明+无不可判定；任一 U 计不通过；watchdog=FAIL（halt-live 例外）；FAIL 依赖 case BLOCKED。
- A0 门禁未解除→A0 全单元 BLOCKED，不计分；单独 A0 授权不能跳过。
- 未执行、未授权；执行需主人对 A0/A1/A2/A2-R 分别书面签发，单次有效；实验≠部署，设计≠施工。
