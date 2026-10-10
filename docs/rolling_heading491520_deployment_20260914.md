# 新滚动策略部署：真机接管初速 0.75 m/s

> 2026-10-10 整理：本页保留该流程的实现说明和既有验证记录。当前入口见 [工作流](current_workflows_zh.md)；权重、数据、reference 和 ZIP 均需 [单独传输](local_artifacts_zh.md)，不再通过 Git 同步。

用户确认的方向：保留现有 15 帧混合和连续 15 帧健康直行稳定阶段；稳定后将新策略输入的 vx 设为用户报告的真机接管速度估计 0.75 m/s，再以 0.15 m/s² 渐变到摇杆目标。居中目标 0.60 m/s，范围 0.45–0.75 m/s。yaw 为 0 或 ±0.02–0.07 rad/s，变化速率 0.07 rad/s²。这个初速不是实时速度测量，1 秒到 0.60 指命令渐变时间。

策略来源：用户提供的 `student_rtneural (2).json`。网络所有层和权重原样保留，补充硬件关节顺序与控制器要求元数据；`handoff_command_transition.runtime_initial_speed_estimate_m_s` 改为 0.75，仿真原估计另存为 `training_initial_speed_estimate_m_s`。

目标文件：

- 策略：`/home/pi/pupperv3-monorepo/ros2_ws/src/neural_controller/models/rolling_command_heading_000000491520.json`
- 配置：`/home/pi/pupperv3-monorepo/ros2_ws/src/neural_controller/launch/config_rollingquad_gamepad.yaml` 中的 `neural_controller_roll.ros__parameters.rolling_model_path`。
- 控制器修改：`include/neural_controller/rolling_command_runtime.inc`、`rolling_handoff.hpp`、`neural_controller.hpp`。支持 v3 契约，保留旧策略契约，保留实际传感器和动作历史，仅在混合/稳定结束时为当前输入设置接管速度种子。
- 备份：`/home/pi/pupperv3-monorepo/ros2_ws/rolling_heading491520_backup_20260914`。包含修改前头文件、配置、DR696320 策略和编译后的控制器库。
- 部署暂存与回执：`/home/pi/rolling_heading491520_stage_20260914`。

原源码和二进制在用户要求先确认方向后已恢复；用户确认 0.75 m/s 方案后再重新部署。没有修改 stand-to-roll 策略、roll-to-stand 策略、蓝牙或按键映射。

在机器人上启动现有手柄流程：

```bash
source /opt/ros/jazzy/setup.bash
source /home/pi/pupperv3-monorepo/ros2_ws/install/setup.bash
ros2 launch neural_controller rollingquad_gamepad.launch.py
```

回退时先退出控制程序，再运行：

```bash
bash /home/pi/rolling_heading491520_stage_20260914/rollback.sh
```

该回退脚本会恢复旧策略配置、源码和旧二进制，不启动控制器。

验证范围：机器人端 RTNeural 720→12 模型加载；原 JSON 与补充元数据后的策略在 12 组输入上输出一致；锁定外展输出；新旧接管流程、0.75→0.60 的 50 个策略步渐变与不健康超时停止。没有本地训练/仿真测试，没有自动启动控制或发送电机命令。最终部署状态以 deployment_receipt.json 为准。

## 最终状态

已部署并核对安装目录配置、模型与控制器库哈希；ROS 包解析指向主工作区，动态库依赖完整，手柄 launch 参数解析通过。控制程序未启动。

部署策略 SHA256：`2174e6ddb4f84e229702ca39da2b19f489d1a2381c1df77a05b9bbb222d5fa42`。原始上传 JSON SHA256：`87dec179443edeead4b8bbd8b61ddab928355a296296e8c6d340b601156b2fa7`。
