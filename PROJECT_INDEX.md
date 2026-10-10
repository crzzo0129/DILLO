# DILLO 当前项目索引

整理日期：2026-10-10。范围限于本项目；上级目录中的其他机器人项目独立管理。

## 主线文档

| 主线 | 阅读入口 |
|---|---|
| 当前代码入口、模型与接口 | [工作流](docs/current_workflows_zh.md) |
| 行走 | [CEM/正弦基线](docs/walk_cem_zh.md)、[奖励对比](docs/deploy_reward_sweep_zh.md)、[对称步态](docs/deploy_trot_symmetry_zh.md)、[足端球体](docs/deploy_foot_spheres_zh.md)、[地形](docs/deploy_rough_terrain_zh.md)、[髋关节范围](docs/deploy_hip_rom_reward_zh.md) |
| 持续滚动 | [训练流程](docs/rolling_training_pipeline_20260912.md)、[真实观测蒸馏与 DR](docs/3d_roll_real_observation_distillation_zh.md)、[命令 PPO](docs/rolling_student_command_ppo.md)、[DR 续训](docs/rolling_dr_continuation_20260913.md)、[接管跟踪](docs/rolling_handoff_tracking_20260913.md)、[速度探索 v3](docs/rolling_speed_explore_v3.md) |
| Stand→Roll | [成功训练链路与 Student](docs/stand_to_roll_training_pipeline_summary_zh.md) |
| Roll→Stand→Walk | [训练与部署](docs/roll_to_walk_training_pipeline_20260912.md)、[pitch 热切换](docs/roll_to_stand_pitch_hot_switch.md) |
| 独立速度估计器 | [当前 50 Hz 标定 v3](docs/rolling_velocity_estimator_calibrated_zh.md)、[在线接口](docs/rolling_velocity_estimator_zh.md)、[转向标定](docs/cem_steering_calibration_20260912.md) |
| 回放与诊断 | [策略可视化](docs/rolling_policy_visualization.md)、[策略序列仿真](docs/rolling_sequence_simulation_20260912.md)、[平滑接管](docs/rolling_smooth_handoff_20260912.md) |
| 实机部署 | [硬件代码入口](hardware/rolling_command/README.md)、[491520 策略记录](docs/rolling_heading491520_deployment_20260914.md)、[PD 5.5](docs/rolling_pd55_20260914.md)、[自动右转](docs/rolling_auto_right_1s_20260914.md)、[v5.3 修复](docs/rolling_auto_right_fix_20260914.md)、[转向录包](docs/rolling_hardware_steering_check.md) |
| 数据与归档 | [本地产物管理](docs/local_artifacts_zh.md)、[整理清单](docs/cleanup_manifest_zh.md) |

## 目录职责

| 目录 | 用途 | GitHub |
|---|---|---|
| `curl_robot_2d/` | 当前流程依赖的几何、参数、模型与行走 CEM | 保留 |
| `curl_robot_2d_mjx/` | 环境、奖励、随机化、蒸馏、切换与估计器 | 保留 |
| `scripts/` | 当前主线入口及递归依赖的共享工具 | 保留 |
| `assets/rollingquad_description_2/` | CAD mesh、URDF、MJCF 模型结构 | 保留结构；生成图像和报告忽略 |
| `assets/controllers/` | 本地 CEM 参数与转向标定 | 忽略 |
| `tests/` | 当前代码的接口、奖励、导出和数据处理检查 | 保留 |
| `hardware/rolling_command/` | 接管源码、安装和校验工具 | 保留源码；部署结果 JSON 忽略 |
| `docs/` | 当前流程与部署版本说明 | 保留 |
| `experiments/registry.csv` | 手工维护的实验登记信息 | 保留 |
| `results/`、`renders/`、`deploy_exports/` | 结果、数据、权重与媒体 | 忽略，保留本地 |
| `.local_archive/20261010/` | 历史代码、文档及整理前版本 | 忽略，保留本地 |

共享模块中的旧几何或旧 recipe 选项不代表推荐训练入口；保留原因见整理清单。
所有示例中的结果路径均是本地产物路径。
