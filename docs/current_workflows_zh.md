# 当前入口、模型与接口

命令在项目根目录执行。运行所需权重、reference、标定表和快照需要独立文件传输，
见 [本地产物管理](local_artifacts_zh.md)。

## 三维行走

- `scripts.train_ppo_walk3d`：速度命令条件行走，共享物理、关节和模型参数。
- `scripts.train_ppo_deploy`：硬件一致的 36 维单帧、20 帧历史、12 维关节位置动作。
- `scripts.train_ppo_deploy_v2`：直行、低速与镜像一致性训练。
- `scripts.train_ppo_deploy_v4`：复用 v2，默认 0.10–0.60 m/s 与部署 DR。
- `scripts.walk_cem`：三维 CEM/正弦基线，参数位于本地 `assets/controllers/walk_cem.json`；
  新克隆可先用 `--controller sine`，或重新运行 `optimize`。

行走共享模型以 `assets/rollingquad_description_2/mjcf/rollingquad.xml` 为基础。
足端球体和地形通过现有选项选择；`scripts.export_rtneural` 是共享导出器。

## 持续滚动

主链为 CEM reference → 速度/转向标定 → BC → DAgger → 固定评估 → critic 预热 → actor PPO → DR → 接管评估。
入口为 `scripts.train_mjx_3d_roll_distillation` 和 `scripts.train_mjx_3d_roll_student_dr_ppo`。
当前命令训练使用 `rollingquad_2_abd10_no_self_collision`；recipe、PD 和指令域按对应配置核对。

续训工具保留 `scripts.run_rolling_low_speed_recovery`、`scripts.run_rolling_dr_continuation`、
`scripts.run_rolling_handoff_tracking` 和 `scripts.run_rolling_speed_fast`。
后者保留 v3 warmup、连续退化判断和严格选模规则，见 [速度探索](rolling_speed_explore_v3.md)。
默认 source/step 是既有实验路径，更换来源时显式指定参数。

`scripts.collect_rolling_handoff_bank`、`scripts.simulate_rolling_policy_sequence`、
`scripts.rolling_handoff` 和诊断工具保留接管状态及动作历史契约。

## Stand→Roll

入口为 `scripts.train_mjx_3d_stand_to_roll`；
`scripts.collect_cem_cycle_data`、`scripts.collect_cem_startup_data` 提供周期和零速度启动监督。
成功 PPO 策略通过 `scripts.distill_stand_to_roll_symmetry` 蒸馏左右平均教师，
再由 `scripts.export_stand_to_roll_student` 导出。
当前部署 Student 来自对称教师蒸馏；早期 mixed 快照/查表 DAgger 方案已归档。

## Roll→Stand

当前动态展开训练使用 `scripts.train_mjx_3d_transition_ppo`；
`scripts.train_mjx_3d_roll_to_stand` 是调用包装器。
`scripts.collect_reference_roll_to_stand` 收集真实滚动状态，训练与评估使用不同滚动圈次。
以 +90° 附近 pitch 窗口交接，保留完整状态、观测历史和上一动作。
模型为 `rollingquad_abd10_no_self_collision.xml`；动态任务中 `brake_full` 是阶段标签。

回放使用 `scripts.prepend_roll_to_stand_replay` 和 `scripts.render_mjx_3d_policy`；
导出使用 `scripts.export_transition_rtneural`。
稳定站立后自动切入 Walking 的链路仍需独立验证，不能从单段训练成功推断。

## 独立滚动速度估计器

保留 `scripts.collect_rolling_velocity_data` 通用采集及当前标定入口
`scripts.collect_calibrated_rolling_velocity_data`。
训练、评估和分段诊断使用 `scripts.train_rolling_velocity_estimator`、
`scripts.evaluate_rolling_velocity_estimator`、`scripts.analyze_rolling_estimator_turns`。
在线接口为 `curl_robot_2d_mjx.rolling_velocity_estimator.RollingVelocityEstimator`，仅依赖 NumPy。
当前 v3 每 20 ms 输入 36 维原始观测，使用 20 帧历史，输出线速度和轨迹转向率。
见 [在线接口](rolling_velocity_estimator_zh.md) 和 [v3 复现](rolling_velocity_estimator_calibrated_zh.md)。

## 模型与共享实现

当前滚动/切换主要使用 `rollingquad_abd10_no_self_collision.xml`，行走以 `rollingquad.xml` 为基础。
`environment_3d.py`、`cem_reference.py`、模型生成器和 reference 评价复用二维几何。
部分旧名称模块、训练工厂及旧 XML 仍被共享实现调用，作为依赖保留。
本次没有重写公共 API 或剔除 recipe 枚举，以免改变 checkpoint 加载行为。

## 实机版本边界

项目内 `hardware/rolling_command/` 保存此前接管实现和校验工具。
2026-09-14 的 heading491520、PD5.5、自动右转 v5.3 记录保留在 `docs/`。
修复的完整暂存源码位于上级工作区 `.rolling_auto_right_fix_20260914/` 等目录，
并不全部在项目内硬件源码中。使用前核对 [版本边界](../hardware/rolling_command/README.md)。
本次没有连接机器人或重新部署。
