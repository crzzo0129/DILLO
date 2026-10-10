# 本地产物与 GitHub 范围

用户确认：结果、权重、数据集、视频、发布包不再上传 GitHub，现有文件保留本地。
`.gitignore` 已移除 reference、快照、数据和云端 ZIP 的例外。
此前已跟踪的产物从 Git 索引移除；磁盘文件保留。

GitHub 继续保留源码、测试、当前文档、依赖声明、XML/URDF/CAD 模型结构，
以及手工维护的 `experiments/registry.csv`。它是实验登记信息，不是训练数据集。
生成的 CEM 参数、转向表、teacher 参数、部署回执、模型预览和碰撞报告均保留本地。

## 新克隆或云端运行

仓库不包含现成训练数据、策略或所有 CEM reference。
保持代码相对路径，将运行文件独立传输到对应目录，或用保留入口重建。
不要通过强制添加忽略文件、Git 提交 ZIP 或“发回结果到 GitHub”同步产物。

| 主线 | 单独准备的本地产物 | 重建/处理入口 |
|---|---|---|
| CEM 行走 | `assets/controllers/walk_cem.json` | `scripts.walk_cem optimize`；正弦基线可直接运行 |
| 持续滚动/标定估计器 | `results/rollingquad_abd10_high_speed_zero_contact_refine_smoke/01_zero_contact_speed_refine/best_phase_controller.json` | 传输认可 reference；保留三维 CEM 搜索工具，但重搜不保证相同结果 |
| 转向与 v3 估计器 | `assets/controllers/rollingquad_abd10_high_speed_steering_v1.json` | `scripts.calibrate_cem_steering`；reference 必须匹配 |
| Stand→Roll | 周期/启动 NPZ、匹配 BC 归一化和策略参数 | `scripts.collect_cem_cycle_data`、`scripts.collect_cem_startup_data` |
| Roll→Stand | 训练/验证 handoff NPZ 及来源说明 | `scripts.collect_reference_roll_to_stand` |
| 接管/PPO 续训 | actor/critic/student checkpoint、配置、handoff bank | 独立传输完整来源，用入口参数指定 source/step |
| 独立估计器推理 | `results/velocity_estimator_cem_calibrated_v3/model/estimator.npz` | 独立传输，或按 v3 文档采集训练 |
| 实机部署 | RTNeural JSON、部署元数据与校验结果 | 主线导出器及 `scripts.prepare_rolling_hardware_export` |

二维匹配、旧 reference 和当前高速 reference 不可互换。
转向表须匹配 CEM、模型和频率；权重须匹配历史、动作中心、关节顺序、归一化与 PD。
文档 `results/` 链接仅在本地有对应文件时可用。

## 归档与恢复

旧文件按原相对路径移入 `.local_archive/20261010/`。
归档包含 `plan.json`、原文件 SHA256、旧文档和整理前入口文档副本。
逐文件清单见 [整理清单](cleanup_manifest_zh.md)。

恢复时把所需源文件复制回原路径，同时恢复依赖及匹配模型。
整个归档目录排除 GitHub。

## 历史 Git 记录

取消跟踪后的删除只影响新的仓库版本，历史提交中已有产物仍存在。
本次整理不重写历史；后续提交和推送只发布代码、模型结构及文档，不包含已忽略的本地产物。
