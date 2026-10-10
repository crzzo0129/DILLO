# 定时接管拒绝：修复与部署记录（v5.3）

> 2026-10-10 整理：本页保留该流程的实现说明和既有验证记录。当前入口见 [工作流](current_workflows_zh.md)；权重、数据、reference 和 ZIP 均需 [单独传输](local_artifacts_zh.md)，不再通过 Git 同步。

## 已确认的现象

用户提供日志中，stand-to-roll 策略于 `1789377649.682081` 开始，约 0.81843 s 后报 `Automatic rolling command/axis/rate invalid at deadline`。没有进入混合阶段。这不是定时器没有触发。

只读检查机器人上的 `recording_2026-09-14_17-20-47`：第一条录到的滚动命令在启动后约 0.04817 s，内容为 vx=0.6、yaw=−0.07。协调器在约 0.0485 s 进入 rolling 状态。因此不能说本次没有发送转向命令或没有触发启动策略。

bag 在拒绝后才记录到 observation、policy_output 和 IMU：第一条 observation 的接收时间约 +1.090 s，IMU 约 +1.114 s。观测消息可能包含 DDS 保留的较早样本，且没有独立的采样时间戳，不能用其接收时间推定拒绝瞬间的真实状态。原错误没有打印是哪一个条件失败，所以无法确认本次唯一原因。

## 已安装的修复

1. 定时模式不再要求最低滚速 0.5 rad/s。仍拒绝非有限状态、超过 12 rad/s 的滚速或超过 15° 的滚动轴侧倾。手动接管模式原健康门槛不变。
2. 自动模式在站姿准备和 starting 阶段持续发布滚动命令；不再依赖先收到 policy_output 才开始发布。启用启动策略前检查摇杆有效和命令发布器已有订阅者，并先发送一次命令。发布器订阅者计数不是电机或特定控制器的接收回执；控制器仍会在接管时核对实际收到的命令。
3. 自动模式可从 starting 直接根据控制器的 blending/continuous 状态更新 UI，避免状态依赖策略输出话题发现顺序。
4. 接管时记录 elapsed、command_valid、command_age、vx、yaw、axis_z、roll_rate，命令错误与状态错误分别报出。

0.8 s 启动 + 0.2 s 混合、接管后固定 −0.07 rad/s、P=5.5/D=0.1、关节目标连续性限制、停止/急停逻辑不变。没有修改按键映射或网络权重。

## 验证与当前状态

实际 Python 协调器的离线检查通过，包括输出发现较晚时 starting 阶段仍发命令、启用前命令顺序、订阅者检查、状态更新、固定右转、□ 取消和掉线急停。

机器人端 C++ 时序与门槛检查通过，包括零滚速/低滚速可进入定时模式、过大侧倾/速度/非有限值拒绝、0.8–1.0 s 混合、停止优先、调度偏差和旧模式兼容。

**状态：2026-09-14 17:44:22 已备份并安装到机器人（192.168.3.5）。** 重新上电后重新上传暂存文件，机器人独立目录编译成功（1 package finished）；已安装三个修复源码文件及控制器动态库。安装时没有运行 ros2_control_node，未启动控制器或执行真机运动。

新库 SHA256：`1de9293a2db3ffc9695e1970ce591b9a7be239a7427366ad40fceecd2eedd388`。

备份目录：`/home/pi/pupperv3-monorepo/ros2_ws/rolling_auto_right_fix_backup_20260914_174422`。退出控制程序后，可回退本轮修复：

```bash
bash /home/pi/pupperv3-monorepo/ros2_ws/rolling_auto_right_fix_backup_20260914_174422/rollback.sh
```

该回退只恢复 v5.2 自动右转版。若要恢复更早的手动接管版，须先执行上述回退，再执行原自动右转版本备份中的回退脚本，见 [原流程与备份](rolling_auto_right_1s_20260914.md)。

继续使用原来的 `ros2 launch neural_controller rollingquad_gamepad.launch.py` 入口。手柄节点版本应为 `gamepad-continuous-roll-v5.3-timed-right-ready`。接管时新增 `AUTO RIGHT deadline` 数值日志；如仍拒绝，可区分命令缺失/过期和轴倾角/过高转速异常。

本地修复：工作区 `.rolling_auto_right_fix_20260914/`，包括 `changes.diff`、原文件、修复后文件、检查脚本和安装脚本。

机器人暂存：`/home/pi/rolling_auto_right_fix_stage_20260914`；编译复用独立的 `/home/pi/rolling_auto_right_stage_20260914`，不涉及正在安装的源目录。
