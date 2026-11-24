# v46 目标 Linux 实验方案（完整交付）

- **对应设计**：`部署脚本整改设计-v46.md` §七
- **状态**：设计交付；**未执行、未授权**；执行需主人对 A0/A1/A2/A2-R 分别签发
- **基线**：v45 实验方案 E01–E16 与清理/授权不变；本文补 v46 新判据。

## 一、授权单元（继承）

| 单元 | 环境 | 覆盖 | 不含 |
|---|---|---|---|
| A1 | 宿主只读/同版本 VM overlay | T0a、E01、E14a | 写/执行/服务/T0b/T1–T4/E16 |
| A0 | 一次性 VM/独立根 | T0b-01..16、E16a–f、D0–D9、installer | E02–E15、宿主、生产 |
| A2 | 一次性 VM | T1–T4、E02–E13/E15/E14b | T0b、E16、宿主、生产 docker |
| A2-R | 一次性 VM+真实 docker | T3-02/FC-01b | 生产 socket/宿主 |

- 四单元独立、互不蕴含；实验≠施工；设计≠部署。
- A0 使用 VM 内 canonical/状态根（harness 重建）；`.a0-test-root` 门控；不碰宿主。

## 二、公共前置

哨兵（`/run/deploy-test-vm`、`/opt/astrbot` 不存在、无生产容器/socket/共享、`--net none`）；`$H` 0700+SHA 冻结；Linux≥5.4、Py3.9–3.12 64 位、cgroup v2；不满足不可执行。

**[GATE-A0]** U-01/U-02 未冻结→A0/F-SEAL/T0B-01..16/E16a–f/D0–D9/installer 直调 BLOCKED（不计分、不填 0/N/A）；单独 A0 授权不能解除。**[SEAL-DEP]** T0B-03/05/16 需 F-SEAL 阳性对照。

## 三、E01–E16（继承，补 v46 判据）

| ID | 授权 | 唯一判据（摘要） |
|---|---|---|
| E01 | A1 | 版本/内核/cgroup/pidfd/waitid/flock/OOB 齐全；缺失 fail-closed |
| E02 | A2 | fd 随帧首字节；无 cmsg→CTRUNC 且 fd 计数不增 |
| E03 | A2 | 两段/逐字节 fd 归当前帧 |
| E04 | A2 | 0 长度不产生字节；数据在队时 read=0；shutdown 后读 0 |
| E05 | A2 | shutdown→干净 EOF；close+未读→ECONNRESET；FRAME 三态记录 |
| E06 | A2 | CTRUNC 时内核是否关 fd；合同不依赖 |
| E07 | A2 | fdinfo Pid；poll(POLLIN) 判死；POLLHUP 版本记录；starttime 一致 |
| E08 | A2 | cgroup mkdir/迁移/read-back/populated=0/rmdir |
| E09 | A2 | subreaper 收养；waitpid 五分支；无僵尸；children 仅辅助；fork2 后未发布子步骤 |
| E10 | A2 | ENOSPC/EROFS/fsync EIO/短写语义；fsync EIO≠未落盘 |
| E11 | A2 | flock 跨 fork/exec/close；probe 可判 |
| E12 | A2 | 时间阈值（§四）；否则 FAIL |
| E13 | A2 | Bash 能力边界记录 |
| E14a | A1 | CLI 静态形态；无活体 U5 |
| E14b | A2 | `/proc/exe` 50 次稳定；无活体 U5 |
| E15 | A2 | OOB 三分支记录；不成为启动条件 |
| E16 | A0 | E16a–f；40/41 精确；D0–D9 映射 |

## 四、E12 时间阈值（v46）

- `T_HANDSHAKE_TOTAL=20s`；阶段 5s 仅上限；`T_CLI_WAIT=125s`（release_byte）；`T_SUP_EXIT_FRAMED=126s`（t_eof 起）；`T_SUP_EXIT=5s`（t_eof 无帧）；`T_EOF_WAIT=1s`（完整帧无 EOF）；`T_REAP=5s`；`T_EXEC_FRAME=5s`；`T_ABORT_WAIT=5s`；watchdog 180s（halt-live 例外）。
- 采样/负载/阈值同 v45（每阶段 p99≤0.1cap、max≤0.5cap；握手 p99≤10s、max≤15s；mono 抖动≤1ms）。
- 新增：T2-21 起点/早退/不退出三态校准；T2-21a2 早退无 TERM。

## 五、v46 新判据

### 5.1 cli_spawn_failure（T2-23）

- 构造：fork2 失败（`cli_spawn_failure{stage:"fork2",errno}`）。
- 断言：spawn_closed=true；observed=true；not_sent(`cli_launcher_spawn_failed`) 20；WAL 有 spawned/cli_spawn_begin/cli_spawn_failure；无 cli_spawned/terminal；单终态。
- 半行 failure 被截断→视为无 failure→spawn_closed=false（保守）→P2/hold-live；若 failure 与完整 cli_spawned 并存→HOLD 22。

### 5.2 T2-21 计时

- a：帧+EOF，supervisor 不退出→t_eof+126 TERM、+127 KILL、+131 REAP；P2 22。
- a2：帧+EOF，supervisor 在 126s 内退出→无 TERM、正常 finalize 22。
- c：EOF 无帧/截断→t_eof+5 TERM、+6 KILL。

### 5.3 W4R 五子态（S1/S2a/S2b/S3a/S3b）与 S4 三阶段

- 五子态各 live/dead：live→hold-live（无 exit、心跳、SIGKILL→9；next 23）；dead→22 latch-only（basis=latch）。
- S4 三阶段：S4-live（f1）→hold-live；S4-first（f2，无活体 observed=true、首次错误返回、未写 resolution）→22，basis=attempt_hold；S4-recover（f3，同现场后续 recover，A 域死亡证明通过）→写 resolution（epoch5 文件）+audit+清理→0。
- T3-23：a1/a2…e1/e2、f1/f2/f3 逐项断言 WAL 末行/HALT 字段/半行/不补写/退出/basis。
- 不补 takeover5/attempt_hold；S3a 首次不截断。

### 5.4 resolution 双写（T3-25）

- 前置：A 域死亡证明（launcher/CLI/live_children 全死）通过；有活体/不可观测→hold-live，不进入本表。

- a 文件成功/WAL 失败→文件权威、允许完成清理、0、audit_missing。
- c 文件+WAL 均成功→一致、0、清理后文件仍在。
- d 文件存在/WAL 缺→0、不重写 WAL。
- e 文件缺 + epoch4 operator_resolution 完整且身份一致→重建、0、不重写 WAL；否则 30、零 WAL 写、零清理、保留现场。
- f 不一致→30 保现场。
- g1 create 失败、g2 短写、g3 完整写+fsync EIO、g4 目录 fsync 失败→23、latch 保留、token_untrusted、不写 resolution。
- h token 失败+latch 失败→hold-live、SIGKILL→9、next 23。
- i 正常清理后 resolution.json 仍在→resolved=true；再次 recover 幂等 0。
- j epoch5 文件缺、WAL 无事件→30 保现场；不重建。
- k 文件损坏/字段不符→30；不覆盖。
- l WAL 事件存在但身份不符→30；不重建。
- m1 WAL present + audit 写失败→0、stdout `audit_record_write_failed`（不得报 wal_audit_missing）。
- m2 WAL missing + audit 写失败→0、stdout `wal_audit_missing`+`audit_record_write_failed`。
- m3 总述：audit 短写/fsync EIO/目录 fsync 失败→stdout `audit_record_write_failed`、残留 unknown、仍 0、不覆盖 resolution、不阻塞完成。
- m3a 完整写+fsync(file) EIO→重启 unknown（有 WAL epoch4→present）；m3b fsync(dir) EIO→unknown；m3c .failed 与原文件并存→unknown；m3d link 成功 unlink 失败→unknown。
- u 缺 resolved_at→30；v 缺 attempt_hold→30；w halt 缺 halt_seq→30；q1–q4 四组 dev-ino 各缺/不符→30；均零 WAL 写、零清理、保留现场。
- dev-ino 操作级：openat(O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC)→fstat(fd) 取 dev/ino→与 attempt_created 锚点比对→fstatat(AT_SYMLINK_NOFOLLOW) 与 fstat 一致；WAL 用 fstat(fd)+fstatat(audit_fd,name)；失败→30。
- n 非 epoch4→30、零 WAL 写、零清理、token/latch/HALT 保留。
- o 事件不完整（缺 basis/anchor/token_sha256/latch_ino）→30、零 WAL 写、零清理、保留。
- p 身份字段不符（token_sha256/latch_ino/attempt_id）→30、零 WAL 写、零清理、保留。
- q 缺 attempt_id/boot_id/dev-ino→30、零写、零清理、保留。
- r 缺 authority_seq/anchor→30、零写、零清理、保留。
- s 缺 observed/spawn_state→30、零写、零清理、保留。
- t 文件交叉不符→30、零写、零清理、保留。
- audit 文件：resolution.json 成功后写 `resolution.audit.json`（present/missing）；不参与 resolved；清理不删。

### 5.5 P3a/P4a/P1-H

- P3a（T2-22a）：HALT 失败、token+latch 成功→22 latch-only、无 HALT、basis=latch。
- P4a（T2-22b）：WAL/HALT 均不可用、latch 成功→22 latch-only、basis=latch。
- P1-H（T3-24a/b）：a 半行→22 latch-only、WAL 末 takeover(3)、basis=latch；b 完整写+fsync EIO→重启按 S4、basis=attempt_hold。
- P3a（`halt_fsync=EIO`，open 成功+写失败）与 P4a（`halt_dir=EACCES`，open/预检失败、未尝试写）注入不同，互斥。

## 六、清理/隔离（继承 v45）

- C-A2：冻结证据→杀进程→cgroup 清→umount→恢复 mount/sysctl→删根→销毁 VM→证明；失败路径同样执行；清理失败 U4。
- C-A0：归档→销毁 VM→销毁证明；宿主两路径 A1 前后不变。
- C-A1：无宿主写入；transcript+白名单；前后快照不变；overlay 强证明。

## 七、判定与授权

- 通过=唯一判据全满足+清理证明+无 U；watchdog=FAIL（halt-live 例外）；FAIL 依赖 case BLOCKED。
- A0 门禁未解除→A0 全单元 BLOCKED，不计分；单独 A0 授权不能跳过。
- 未执行、未授权；执行需主人对 A0/A1/A2/A2-R 分别书面签发；实验≠部署。

## 八、未验证

- 真实 fsync EIO（E10）、renameat2（E16e）、POLLHUP≥6.9、pidfd fdinfo、页缓存半行、目标发行版/内核/Python 未验证；不得写成已通过。
