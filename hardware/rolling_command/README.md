# 滚动接管硬件源码与版本边界

本目录保留手柄控制、滚动接管、RTNeural 校验及安装工具。
这里的源码和安装脚本是此前接管版本，不能直接视为 2026-09-14 实机最终 v5.3 源码。
原说明已存入本地归档的 `before_cleanup/hardware/rolling_command/README.md`。

## 当前部署记录

- [heading491520 策略](../../docs/rolling_heading491520_deployment_20260914.md)：用户指定权重及 0.75 m/s 接管速度种子。
- [PD5.5](../../docs/rolling_pd55_20260914.md)：P=5.5、D=0.1 的部署记录。
- [自动右转](../../docs/rolling_auto_right_1s_20260914.md)：定时启动和混合。
- [自动右转 v5.3 修复](../../docs/rolling_auto_right_fix_20260914.md)：命令提前发布、定时模式门槛、日志和部署回执。

v5.3 完整暂存源码位于上级工作区 `.rolling_auto_right_fix_20260914/`；
其他部署暂存文件也位于上级工作区对应目录。它们属于项目外的现有工作，
本次整理未搬迁，也没有把旧安装脚本改成新版本安装器。
更换源码或权重前应按对应部署回执核对实际版本及哈希。

## 保留工具

| 内容 | 用途 |
|---|---|
| `neural_controller/include/`、`src/` | 已有接管逻辑、历史与控制器接口 |
| `neural_controller/scripts/` | 手柄映射与序列协调 |
| `install.py`、`install_pd55.py` | 原版本的独立构建、备份与安装 |
| `test_gamepad.py`、`test_rolling_handoff.py` | 手柄和接管离线检查 |
| `test_rolling_handoff.cpp`、`test_rolling_history.cpp` | 时序与历史契约校验 |
| `verify_rtneural/` | 无 ROS/电机接口的原生网络数值校验 |
| `record_steering_check.py` | [转向录包](../../docs/rolling_hardware_steering_check.md) 工具 |

## 导出与产物

`scripts.prepare_rolling_hardware_export` 从指定 run/step 导出 RTNeural JSON、
校验向量和结果包。当前权重必须显式指定，不能沿用旧 README 的 81920 模型绑定结论。
合成输入数值一致性只验证导出与推理，不等于闭环控制验证。

部署 JSON、校验结果、回执与 ZIP 保留本地，不加入 Git；
模型与数据需要 [单独传输](../../docs/local_artifacts_zh.md)。

## 操作与交接

原手柄入口保留 Walking、Stand→Roll、持续滚动接管、Roll→Stand 及急停流程。
自动右转与手动接管的门槛不同，按相应部署版本说明操作。
roll-to-stand 使用 pitch 门控，之后自动切到 Walking 的完整接口仍需独立验证。

本次只整理文件，没有连接机器人、安装控制器、启动 ROS 或使能电机。
