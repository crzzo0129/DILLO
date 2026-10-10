# DILLO

DILLO 研究 RollingQuad 2 的三维行走、持续滚动、Stand→Roll 和 Roll→Stand。
独立滚动速度估计器保留完整的采集、训练、评估与 NumPy 在线推理链路。
项目沿用 `curl_robot_2d` 名称；二维几何和旧名称模块中仍被当前流程调用的共享实现保留。

从 [项目索引](PROJECT_INDEX.md) 选择工作流；
[当前入口与模型](docs/current_workflows_zh.md) 说明各条主线使用的代码及接口。

## 运行环境

在本目录运行命令。CPU MuJoCo 工具使用 `requirements.txt`；
MJX/PPO 训练在 Linux GPU 环境使用 `requirements-mjx.txt`；
独立估计器采集与训练使用 `requirements-estimator.txt`。
估计器的在线推理只需要 NumPy。

```bash
python -m pip install -r requirements.txt
python -m scripts.walk_cem --controller sine --view
```

正弦行走基线不需要训练权重。CEM、PPO 回放、续训和部署需要相应的本地产物。
运行前按 [本地产物管理](docs/local_artifacts_zh.md) 单独准备 reference、标定表、快照和权重。

## 保留的主线

| 用途 | 入口 | 说明 |
|---|---|---|
| 三维行走 | `scripts.train_ppo_walk3d`、`scripts.train_ppo_deploy`、`scripts.train_ppo_deploy_v2`、`scripts.train_ppo_deploy_v4` | Walking 与可部署历史观测接口；v4 复用 v2 实现 |
| 持续滚动 | `scripts.train_mjx_3d_roll_distillation`、`scripts.train_mjx_3d_roll_student_dr_ppo` | CEM 教师、BC/DAgger、PPO 与 DR |
| Stand→Roll | `scripts.train_mjx_3d_stand_to_roll`、`scripts.distill_stand_to_roll_symmetry` | 静止启动与对称教师蒸馏 |
| Roll→Stand | `scripts.train_mjx_3d_transition_ppo` | 真实滚动快照、动态展开与稳定站立 |
| 独立速度估计 | `scripts.collect_calibrated_rolling_velocity_data`、`scripts.train_rolling_velocity_estimator`、`scripts.evaluate_rolling_velocity_estimator` | 50 Hz 标定 CEM 版本，独立于控制策略 |
| 实机接口 | `hardware/rolling_command/` | 手柄、滚动接管与 RTNeural 校验；版本边界见部署说明 |

Roll→Stand 完成后，自动切入 Walking 的完整链路仍需独立验证。
文档中的既有实验结果和部署回执不等于本次整理重新进行了训练或实机验证。

## 文件管理

GitHub 保留代码、模型结构、测试、依赖声明和当前文档。
结果、权重、数据集、视频、发布包及生成的 reference/标定表仅保留本地，
不再通过 Git 传输到云端。新克隆的仓库不会自动包含这些运行文件。

历史代码和文档移至 `.local_archive/20261010/`，保持原相对目录结构并排除 Git。
[整理清单](docs/cleanup_manifest_zh.md) 记录保留依据和归档范围。
