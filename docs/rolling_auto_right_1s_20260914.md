# 1 秒自动接管并固定右转：真机试验版

> 2026-10-10 整理：本页保留该流程的实现说明和既有验证记录。当前入口见 [工作流](current_workflows_zh.md)；权重、数据、reference 和 ZIP 均需 [单独传输](local_artifacts_zh.md)，不再通过 Git 同步。

2026-09-14 17:44 已安装 v5.3 修复：定时接管取消最低滚速门槛，启动前准备命令，增加拒绝原因数值日志。详见 [v5.3 修复、部署及回退记录](rolling_auto_right_fix_20260914.md)。以下流程保持不变；文末原备份回退前须先回退 v5.3。

按用户要求，已安装到 pupper 的现有手柄启动入口。计时从 stand-to-roll 第一帧策略更新开始，前面的控制器切换、站姿准备和等待不计入这一秒。

| 相对启动策略的时间 | 行为 |
|---|---|
| 0–0.8 s | stand-to-roll 启动策略 |
| 0.8–1.0 s | 两个策略同时推理，以 smoothstep 在 0.2 s 内混合关节目标和 PD |
| ≥1.0 s | 完全使用持续滚动策略，固定 yaw command = −0.07 rad/s（最大右转） |

无需再按 ○，不再等待滚满一圈、特定 pitch 相位或候选目标差进入接管窗口；没有额外的直行稳定等待，也没有额外一秒的 yaw 渐变。时间按实际单调时钟计算，切换执行在最近的 50 Hz 策略周期，正常有约一个 20 ms 周期的量化/调度误差。

前进摇杆保留原映射：居中 0.60 m/s，范围 0.45–0.75 m/s。混合期间持续滚动策略的 vx 输入设为 0.75 m/s，接管后按原有 0.15 m/s² 速率趋近摇杆目标。旋转摇杆在此试验模式不改变持续滚动的右转指令。PPO 的 PD 为 P=5.5、D=0.1；网络权重未改。

手柄节点持续发布右转请求，控制器在 1.0 s 前保持实际策略 yaw 输入为 0，接管完成时直接设为 −0.07。bag 的 `rolling_cmd_vel` 是请求值，可以早于实际策略的转向输入；应使用 observation 第 8 项（从零计数）确认实际进入网络的命令。

□ 仍请求原来的 roll-to-stand；请求到达后取消固定右转，等待原来的停止策略相位入口。急停、手柄失联停止、命令时效和每步 0.12 rad 关节目标限制保留。历史坐标转换沿用已有实现，保留实际观测与已下发动作历史；没有冷清空 PPO 历史。

定时接管时仍要求基本的有限传感器/动作、近期命令、有效历史以及滚动轴与转速健康条件；IMU 报告年龄上限为 0.10 s。条件异常时停止，不以继续等待启动策略的方式突破定时目标。接管的策略混合比例在约 1 秒时到达 100%；若关节目标限速触发，最终发送位置仍遵循其连续性限制。

## 启动与确认

继续使用原来的命令，无需额外请求接管：

```bash
source /opt/ros/jazzy/setup.bash
source /home/pi/pupperv3-monorepo/ros2_ws/install/setup.bash
ros2 launch neural_controller rollingquad_gamepad.launch.py
```

进入 stand-to-roll 后，日志应依次出现：

```text
AUTO RIGHT t=0: first stand-to-roll policy update ...
AUTO RIGHT blend started: startup elapsed=0.8...s ...
AUTO RIGHT takeover complete: startup elapsed=1.0...s, blend alpha=1, yaw=-0.070 rad/s
```

本次没有自动启动控制器或电机，也没有进行新策略的真机运动试验。

## 已完成验证

- 机器人独立目录中编译完整 neural_controller 成功，随后安装验证后的动态库和源码。
- C++ 检查：0.8 s 混合起点、0.9 s 的 50% 混合、1.0 s 的完整接管和固定右转、调度偏差、停止请求优先和非法时间；原手动接管时序兼容检查通过。
- 对实际手柄协调器代码检查：自动接管状态更新、左摇杆 yaw 输入也被固定右转覆盖、□ 取消、掉线急停及原手动模式均通过。
- 原生 RTNeural 对 12 组观测的新旧模型输出一致，锁定外展输出保持一致。
- 检查上次 bag 启动后 0.816 s 的记录：滚动角速度约 3.963 rad/s，轴倾角约 −1.035°，历史转换后的最大有效 action 约 0.612，满足该时刻的历史转换范围。这仅验证已有启动记录的可接管条件，不是新流程的物理成功率测试。
- 安装配置、模型、源码、库哈希已验证；启动/停止策略保持原哈希。

## 备份与回退

完整备份（原代码、策略元数据、手柄配置/脚本、控制器动态库）：

`/home/pi/pupperv3-monorepo/ros2_ws/rolling_auto_right_backup_20260914_171241`

先退出控制程序，再执行：

```bash
bash /home/pi/pupperv3-monorepo/ros2_ws/rolling_auto_right_backup_20260914_171241/rollback.sh
```

这会恢复“○ 请求接管、摇杆控制转向”的上一版，持续滚动仍为 P=5.5、D=0.1。回退脚本不启动控制器，会检查后续文件变化以免覆盖新的修改。

当前策略文件 SHA256：`cb86908d78989462e3f1c4c3ade25e77bb6b77e2e03a2d7b5b7df05f5b2d0163`。

当前 v5.3 控制器库 SHA256：`1de9293a2db3ffc9695e1970ce591b9a7be239a7427366ad40fceecd2eedd388`。原 v5.2 库 SHA256：`8d44bbb9763aeb30a84d90107eaf8d99d09e16592c36312eb67b7b5a6dbdae48`。

机器人编译暂存与回执：`/home/pi/rolling_auto_right_stage_20260914`。本地精确源码、修改差异、检查和部署回执：工作区 `.rolling_auto_right_20260914/`。
