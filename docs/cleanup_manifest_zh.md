# 整理清单（2026-10-10）

用户确认：保留当前三维行走、持续滚动、双向切换、独立滚动速度估计器；
旧文件移入本地归档，结果、权重、数据集、视频及发布包不再上传 GitHub。

归档位置：`.local_archive/20261010/`，原相对目录保持不变。
归档文件移动前后逐一校验 SHA256；详细哈希和还原路径见本地 `plan.json`。
整理前入口和保留文档另存于归档的 `before_cleanup/`。

## 归档数量

| 类型 | 文件数 |
|---|---:|
| `curl_robot_2d/` | 1 |
| `curl_robot_2d_mjx/` | 10 |
| `docs/` | 85 |
| `scripts/` | 80 |
| `tests/` | 34 |
| 合计 | 210 |

旧版 `rolling_velocity_estimator_zh.md` 已归档；原路径重新提供当前 v3 在线接口说明。

## 保留依据

保留当前主线入口及其递归导入、子进程调用、共享导出器和模型生成依赖。
旧名称的训练工厂、二维 reward/config 和几何代码仍被共享模块调用，因此保留；
不把文件日期或名称作为唯一清理依据。对应当前实现的测试与硬件校验保留。
本轮开始前已有修改与新增的代码均保留原字节内容。

## GitHub 范围

取消跟踪 170 个已跟踪产物，磁盘文件全部保留。
包括 results、部署权重、NPZ、图像/GIF、发布 ZIP、生成 reference/标定表及部署结果 JSON。
新规则也忽略未跟踪的结果和发布包。仓库模型结构及手工实验登记表保留。
归档整理不重写历史或操作机器人；后续经用户授权提交和推送时，保持上述产物排除范围。详见 [本地产物管理](local_artifacts_zh.md)。

## 本次验证

- 210 个归档文件在移动前后校验原 SHA256，内容保持一致。
- 170 个取消跟踪的产物逐一检查仍在磁盘且 SHA256 未变。
- 186 个保留 Python 文件通过语法解析；递归内部代码及测试依赖无缺漏。
- 32 份入口/主线文档的本地代码和文档链接检查通过；结果链接按本地产物处理。
- `git ls-files -ci --exclude-standard` 无输出，确认忽略范围内已无跟踪文件。
- 工作区和暂存变更均通过 `git diff --check`。
- 完整测试发现 275 项：211 通过、10 跳过、52 因未安装 MuJoCo/JAX 无法执行、2 项既有断言失败。

既有失败为滚动诊断参数默认开关与奖励字段顺序断言；对应测试和实现与整理前 HEAD
逐字节对照一致（仅归一化 Git 换行）。本次保留行为，没有改动这些实现。
详细结果仅保留本地 `.local_archive/20261010/test_report.json` 和 `test_output.txt`。
本机没有进行 GPU 训练、MuJoCo 仿真或实机验证。

## 逐文件归档

### curl_robot_2d

- `curl_robot_2d/roll_to_walk.py`

### curl_robot_2d_mjx

- `curl_robot_2d_mjx/deploy_trajectory.py`
- `curl_robot_2d_mjx/environment_autonomous_startup_3d.py`
- `curl_robot_2d_mjx/environment_stopping_2d.py`
- `curl_robot_2d_mjx/environment_walk_compact_3d.py`
- `curl_robot_2d_mjx/reward_stopping.py`
- `curl_robot_2d_mjx/single_foot_compact_probe.py`
- `curl_robot_2d_mjx/stand_compact_wbc_3d.py`
- `curl_robot_2d_mjx/stop_evaluation.py`
- `curl_robot_2d_mjx/stop_task.py`
- `curl_robot_2d_mjx/walk_compact_3d.py`

### docs

- `docs/3d_abd10_self_collision_retrain_zh.md`
- `docs/3d_actuator_gain_curriculum_zh.md`
- `docs/3d_autonomous_startup_training_zh.md`
- `docs/3d_compact_coldstart_probe_zh.md`
- `docs/3d_compact_coldstart_results_20260831_zh.md`
- `docs/3d_compact_physics_diagnostic_zh.md`
- `docs/3d_compact_startup_training_zh.md`
- `docs/3d_curl_robot_redesign_zh.md`
- `docs/3d_forward_velocity_command_tracking_zh.md`
- `docs/3d_mass_inertia_curriculum_zh.md`
- `docs/3d_real_geometry_nominal_training_zh.md`
- `docs/3d_real_geometry_walking_training_zh.md`
- `docs/3d_robustness_curriculum_zh.md`
- `docs/3d_roll_handoff_probe_results_20260831_zh.md`
- `docs/3d_roll_handoff_probe_zh.md`
- `docs/3d_stand_compact_transition_controller_zh.md`
- `docs/3d_stand_to_roll_startup_zh.md`
- `docs/3d_terrain_adaptive_zh.md`
- `docs/3d_transition_policy_zh.md`
- `docs/3d_unified_stand_to_roll_training_zh.md`
- `docs/3d_walking_stand_to_compact_stage1_zh.md`
- `docs/active_roll_controller_baseline_zh.md`
- `docs/anymal_style_mjx_walking_zh.md`
- `docs/calibrated_distillation_review_20260912.md`
- `docs/cem_steering_comparison_20260912.md`
- `docs/collision_constrained_cem_zh.md`
- `docs/collision_model_revision_zh.md`
- `docs/design_discussion_zh.md`
- `docs/distillation_performance.md`
- `docs/dynamic_roll_to_stand_primitive_zh.md`
- `docs/energy_cem_3d_20260905_zh.md`
- `docs/evaluation_protocol_zh.md`
- `docs/experiment_management_zh.md`
- `docs/fixed_parameters_zh.md`
- `docs/handcrafted_roll_to_stand_abd10_zh.md`
- `docs/handoff_2026-07-29_2d_rolling_to_3d_zh.md`
- `docs/handoff_2026-08-04_3d_rolling_zh.md`
- `docs/leg_crossing_analysis_zh.md`
- `docs/locomotion_energy_3d_20260905_zh.md`
- `docs/nominal_com_mjx_rl_zh.md`
- `docs/project_roadmap_zh.md`
- `docs/pupper_reference_mesh_abduction_energy_20260907_zh.md`
- `docs/pupper_reference_primitive_abd10_20260907_zh.md`
- `docs/pupper_reference_primitive_stand_direct_20260908_zh.md`
- `docs/pupper_reference_rollingquad2_abd10_stand_direct_20260908_zh.md`
- `docs/residual_rl_curriculum_zh.md`
- `docs/rigid_phase_analysis_zh.md`
- `docs/rigid_release_baseline_zh.md`
- `docs/roll_to_stand_rl_handoff_20260908_zh.md`
- `docs/roll_to_stand_rl_progress_20260908_zh.md`
- `docs/roll_to_stand_training_zh.md`
- `docs/roll_to_walk_baseline_zh.md`
- `docs/rolling_cem_foot_contact_zh.md`
- `docs/rolling_command_distillation_cloud.md`
- `docs/rolling_distill_bc_dagger_review_20260912.md`
- `docs/rolling_estimator_steering_handoff_20260912_zh.md`
- `docs/rolling_low_speed_paired_review_20260912.md`
- `docs/rolling_low_speed_recovery.md`
- `docs/rolling_low_speed_review_20260912.md`
- `docs/rolling_ppo_actor_next_stage.md`
- `docs/rolling_ppo_candidates_decision.md`
- `docs/rolling_ppo_critic_review_20260911.md`
- `docs/rolling_ppo_diagnosis_20260911.md`
- `docs/rolling_ppo_recovery.md`
- `docs/rolling_ppo_tracking_review_20260912.md`
- `docs/rolling_speed_fast_20260913.md`
- `docs/rolling_speed_fast_v2_20260913.md`
- `docs/rolling_stop_training_plan_zh.md`
- `docs/rolling_velocity_estimator_switching_zh.md`
- `docs/rolling_velocity_estimator_zh.md`
- `docs/servo_release_baseline_zh.md`
- `docs/stand_roll_stand_video_zh.md`
- `docs/stand_to_roll_capture_cloud.md`
- `docs/stand_to_roll_load_cloud.md`
- `docs/stand_to_roll_stability_update.md`
- `docs/stand_to_roll_startup_cloud.md`
- `docs/stand_to_roll_student_json_cloud.md`
- `docs/stand_to_roll_symmetry_cloud.md`
- `docs/stand_to_roll_symmetry_distillation_cloud.md`
- `docs/stand_to_roll_symmetry_reward_cloud.md`
- `docs/stand_to_roll_v2_cloud.md`
- `docs/walking_controller_exploration_zh.md`
- `docs/walking_shell_clearance_zh.md`
- `docs/walking_to_compact_stage1_zh.md`
- `docs/walking_training_handoff_zh.md`

### scripts

- `scripts/analyze_3d_reference_contacts.py`
- `scripts/analyze_cem_horizon_generalization.py`
- `scripts/analyze_leg_contacts.py`
- `scripts/analyze_leg_crossing.py`
- `scripts/analyze_shell_motor_contacts.py`
- `scripts/analyze_walking_shell_clearance.py`
- `scripts/collect_braking_terminal_states.py`
- `scripts/collect_rolling_snapshots.py`
- `scripts/collect_transition_roll_snapshots.py`
- `scripts/collect_walking_start_snapshots.py`
- `scripts/compare_2d_references.py`
- `scripts/compare_mjx_3d_reference.py`
- `scripts/compare_mjx_cem_reference.py`
- `scripts/compare_physics_profiles.py`
- `scripts/demo_handcrafted_3d_walk.py`
- `scripts/diagnose_compact_physics.py`
- `scripts/diagnose_rolling_distillation.py`
- `scripts/evaluate_fixed_policy_torso_com.py`
- `scripts/evaluate_fixed_reference_shell_radius.py`
- `scripts/evaluate_mjx_3d_policy.py`
- `scripts/evaluate_mjx_3d_walking_policy.py`
- `scripts/evaluate_stand_compact_wbc_3d.py`
- `scripts/explore_walking_controller.py`
- `scripts/export_startup_handoff_bank.py`
- `scripts/inspect_model.py`
- `scripts/json_to_tensorboard.py`
- `scripts/manual_stand_to_compact.py`
- `scripts/mjx_3d_walking_smoke.py`
- `scripts/mjx_smoke.py`
- `scripts/optimize_energy_cem_3d.py`
- `scripts/plot_roll_phase_portrait_3d.py`
- `scripts/plot_stand_direct_roll_comparison.py`
- `scripts/probe_3d_compact_coldstart.py`
- `scripts/probe_3d_roll_handoff.py`
- `scripts/probe_cem_steering_comparison.py`
- `scripts/probe_high_speed_cem_steering.py`
- `scripts/probe_primitive_roll_reference.py`
- `scripts/render_3d_real_geometry.py`
- `scripts/render_3d_startup_evaluation.py`
- `scripts/render_model.py`
- `scripts/render_pupper_shell_coverage.py`
- `scripts/render_shell_radius_comparison.py`
- `scripts/render_stand_roll_stand.py`
- `scripts/replay_active_controller.py`
- `scripts/replay_compact_physics.py`
- `scripts/run_contact_free_cem.py`
- `scripts/run_contact_free_curriculum.py`
- `scripts/run_mjx_3d_real_geometry_walking_overnight.sh`
- `scripts/run_roll_to_walk.py`
- `scripts/run_rolling_ppo_candidate_eval.sh`
- `scripts/run_rolling_ppo_recovery.sh`
- `scripts/run_rolling_ppo_tracking_stage.sh`
- `scripts/run_shell_radius_warm_start_cem.py`
- `scripts/run_staged_cem_at_com.py`
- `scripts/scan_target_scale_reference.py`
- `scripts/search_3d_park_pose.py`
- `scripts/search_braking_schedule.py`
- `scripts/search_deploy_trajectory.py`
- `scripts/simulate_stand_to_compact.py`
- `scripts/smoke_mjx_stopping_env.py`
- `scripts/summarize_selected_staged_com.py`
- `scripts/summarize_staged_com_grid.py`
- `scripts/summarize_torso_com_sweep.py`
- `scripts/sweep_mjx_3d_physics.py`
- `scripts/sweep_mjx_ppo.py`
- `scripts/sweep_torso_com_cem.py`
- `scripts/sweep_upper_half_torso_com_cem.py`
- `scripts/train_mjx_3d_real_geometry_nominal.py`
- `scripts/train_mjx_3d_real_geometry_walking.py`
- `scripts/train_mjx_3d_startup_ppo.py`
- `scripts/train_mjx_3d_walking_ppo.py`
- `scripts/train_mjx_residual_ppo.py`
- `scripts/train_mjx_stopping_ppo.py`
- `scripts/train_roll_to_stand_reference_residual.py`
- `scripts/train_stand_to_roll_dagger.py`
- `scripts/train_walk_compact_ppo.py`
- `scripts/validate_3d_park_pose.py`
- `scripts/verify_3d_differential_authority.py`
- `scripts/verify_mjx_zero_residual_equivalence.py`
- `scripts/view_model.py`

### tests

- `tests/test_autonomous_startup_3d.py`
- `tests/test_collect_braking_terminal_states.py`
- `tests/test_collect_rolling_snapshots.py`
- `tests/test_collect_transition_roll_snapshots.py`
- `tests/test_compact_coldstart_probe.py`
- `tests/test_compact_physics_diagnostic.py`
- `tests/test_compact_reach_3d.py`
- `tests/test_compact_startup_3d.py`
- `tests/test_compare_mjx_3d_reference.py`
- `tests/test_energy_cem_3d.py`
- `tests/test_fixed_policy_torso_com.py`
- `tests/test_handcrafted_3d_walk.py`
- `tests/test_handoff_probe_3d.py`
- `tests/test_mjx_3d_training.py`
- `tests/test_mjx_3d_walking_contract.py`
- `tests/test_mjx_3d_walking_symmetry.py`
- `tests/test_mjx_3d_walking_training.py`
- `tests/test_mjx_contract.py`
- `tests/test_mjx_residual.py`
- `tests/test_mjx_sweep.py`
- `tests/test_render_3d_startup_evaluation.py`
- `tests/test_reward_stopping.py`
- `tests/test_roll_to_walk.py`
- `tests/test_rolling_3d_startup.py`
- `tests/test_search_braking_schedule.py`
- `tests/test_search_deploy_trajectory.py`
- `tests/test_single_foot_compact_probe.py`
- `tests/test_staged_cem_geometry.py`
- `tests/test_stand_roll_stand.py`
- `tests/test_stop_task.py`
- `tests/test_torso_com_sweep.py`
- `tests/test_upper_half_torso_com_cem.py`
- `tests/test_walk_compact_3d.py`
- `tests/test_walking_controller.py`

## 旧名称共享模块

| 模块 | 保留原因 |
|---|---|
| `curl_robot_2d` | dependency of scripts.build_primitive_collision |
| `curl_robot_2d.model` | dependency of scripts.generate_model |
| `curl_robot_2d.model_3d` | dependency of scripts.calibrate_cem_steering |
| `curl_robot_2d.parameters` | dependency of scripts.calibrate_cem_steering |
| `curl_robot_2d.planar_geometry` | dependency of scripts.optimize_phase_controller |
| `curl_robot_2d.pupper_shell_geometry` | dependency of scripts.build_primitive_collision |
| `curl_robot_2d.pupper_shell_model` | dependency of scripts.generate_pupper_original_shell |
| `curl_robot_2d.walking_cem` | dependency of scripts.evaluate_walk_lift |
| `curl_robot_2d_mjx` | dependency of curl_robot_2d_mjx.rolling_ppo_diagnostics |
| `curl_robot_2d_mjx.autonomous_startup_3d` | dependency of curl_robot_2d_mjx.compact_startup_3d |
| `curl_robot_2d_mjx.cem_matcher` | dependency of curl_robot_2d_mjx.environment_stand_to_roll_3d |
| `curl_robot_2d_mjx.cem_reference` | dependency of scripts.calibrate_cem_steering |
| `curl_robot_2d_mjx.compact_startup_3d` | dependency of curl_robot_2d_mjx.environment_3d |
| `curl_robot_2d_mjx.config` | dependency of curl_robot_2d_mjx |
| `curl_robot_2d_mjx.config_3d` | dependency of scripts.calibrate_cem_steering |
| `curl_robot_2d_mjx.config_stand_to_roll` | dependency of scripts.collect_cem_startup_data |
| `curl_robot_2d_mjx.config_transition_3d` | dependency of scripts.collect_reference_roll_to_stand |
| `curl_robot_2d_mjx.config_walking_3d` | dependency of curl_robot_2d_mjx.environment_walking_3d |
| `curl_robot_2d_mjx.curriculum_3d` | dependency of scripts.train_mjx_3d_residual_ppo |
| `curl_robot_2d_mjx.deployment_rolling_3d` | dependency of scripts.collect_calibrated_rolling_velocity_data |
| `curl_robot_2d_mjx.deployment_transition_3d` | dependency of scripts.train_mjx_3d_transition_ppo |
| `curl_robot_2d_mjx.deployment_walking_v2` | dependency of scripts.train_ppo_deploy_v2 |
| `curl_robot_2d_mjx.distillation_curriculum` | dependency of scripts.run_rolling_low_speed_recovery |
| `curl_robot_2d_mjx.distillation_eval_snapshots` | dependency of scripts.train_mjx_3d_roll_distillation |
| `curl_robot_2d_mjx.distillation_evaluation` | dependency of scripts.train_mjx_3d_roll_distillation |
| `curl_robot_2d_mjx.distillation_execution` | dependency of curl_robot_2d_mjx.rolling_ppo_diagnostics |
| `curl_robot_2d_mjx.environment` | dependency of scripts.train_mjx_ppo |
| `curl_robot_2d_mjx.environment_3d` | dependency of scripts.calibrate_cem_steering |
| `curl_robot_2d_mjx.environment_rolling_student_dr_3d` | dependency of scripts.train_mjx_3d_roll_student_dr_ppo |
| `curl_robot_2d_mjx.environment_stand_to_roll_3d` | dependency of scripts.render_stand_to_roll_checkpoint |
| `curl_robot_2d_mjx.environment_transition_3d` | dependency of scripts.mjx_3d_transition_smoke |
| `curl_robot_2d_mjx.environment_walking_3d` | dependency of curl_robot_2d_mjx.environment_transition_3d |
| `curl_robot_2d_mjx.failure_transition_3d` | dependency of scripts.train_mjx_3d_transition_ppo |
| `curl_robot_2d_mjx.handoff_probe_3d` | dependency of scripts.analyze_3d_roll_handoff |
| `curl_robot_2d_mjx.randomization_3d` | dependency of scripts.train_mjx_3d_roll_distillation |
| `curl_robot_2d_mjx.reference_bank_contract_3d` | dependency of scripts.train_mjx_3d_transition_ppo |
| `curl_robot_2d_mjx.reset_grounding` | dependency of scripts.collect_cem_startup_data |
| `curl_robot_2d_mjx.reward` | dependency of scripts.train_mjx_ppo |
| `curl_robot_2d_mjx.reward_3d` | dependency of scripts.train_mjx_3d_roll_student_dr_ppo |
| `curl_robot_2d_mjx.reward_config` | dependency of scripts.train_mjx_ppo |
| `curl_robot_2d_mjx.reward_transition_3d` | dependency of scripts.train_mjx_3d_transition_ppo |
| `curl_robot_2d_mjx.reward_walking_3d` | dependency of curl_robot_2d_mjx.environment_walking_3d |
| `curl_robot_2d_mjx.roll_snapshot_curriculum_3d` | dependency of curl_robot_2d_mjx.transition_initialization_3d |
| `curl_robot_2d_mjx.rolling_diagnostics_3d` | dependency of scripts.train_mjx_3d_roll_distillation |
| `curl_robot_2d_mjx.rolling_ppo_diagnostics` | current workflow entry or existing local change |
| `curl_robot_2d_mjx.rolling_ppo_gradient_diagnostics` | dependency of scripts.train_mjx_3d_roll_student_dr_ppo |
| `curl_robot_2d_mjx.rolling_speed_tracking` | dependency of curl_robot_2d_mjx.rolling_ppo_diagnostics |
| `curl_robot_2d_mjx.rolling_student_dr_ppo_3d` | dependency of scripts.train_mjx_3d_roll_student_dr_ppo |
| `curl_robot_2d_mjx.rolling_student_snapshot_pool` | dependency of scripts.train_mjx_3d_roll_student_dr_ppo |
| `curl_robot_2d_mjx.rolling_velocity_estimator` | dependency of scripts.evaluate_rolling_velocity_estimator |
| `curl_robot_2d_mjx.runtime` | dependency of scripts.mjx_3d_smoke |
| `curl_robot_2d_mjx.stand_to_roll_training` | dependency of scripts.collect_cem_startup_data |
| `curl_robot_2d_mjx.startup_rolling_3d` | dependency of scripts.train_mjx_3d_roll_distillation |
| `curl_robot_2d_mjx.steering_calibration` | dependency of scripts.calibrate_cem_steering |
| `curl_robot_2d_mjx.supervisor_transition_3d` | current transition contract validation |
| `curl_robot_2d_mjx.terrain_3d` | dependency of scripts.bake_terrain |
| `curl_robot_2d_mjx.training_transition_3d` | dependency of scripts.train_mjx_3d_transition_ppo |
| `curl_robot_2d_mjx.transition_console` | dependency of scripts.train_mjx_3d_transition_ppo |
| `curl_robot_2d_mjx.transition_control_3d` | dependency of curl_robot_2d_mjx.environment_transition_3d |
| `curl_robot_2d_mjx.transition_domain_randomization_3d` | dependency of scripts.train_mjx_3d_transition_ppo |
| `curl_robot_2d_mjx.transition_initialization_3d` | dependency of scripts.collect_reference_roll_to_stand |
| `curl_robot_2d_mjx.transition_robustness_3d` | dependency of curl_robot_2d_mjx.environment_transition_3d |
| `curl_robot_2d_mjx.transition_snapshot_cli_3d` | dependency of scripts.inspect_transition_roll_snapshots |
| `curl_robot_2d_mjx.wrappers_rolling_student_dr_3d` | dependency of scripts.train_mjx_3d_roll_student_dr_ppo |
| `curl_robot_2d_mjx.wrappers_transition_3d` | dependency of scripts.mjx_3d_transition_smoke |
| `scripts` | dependency of scripts.analyze_rolling_turn_sequence |
| `scripts.analyze_3d_roll_handoff` | dependency of curl_robot_2d_mjx.autonomous_startup_3d |
| `scripts.analyze_roll_phase` | dependency of scripts.run_release_baseline |
| `scripts.analyze_rolling_student_5s` | dependency of scripts.render_rolling_student_json |
| `scripts.analyze_rolling_turn_sequence` | current workflow entry or existing local change |
| `scripts.build_short_rolling_figures` | current workflow entry or existing local change |
| `scripts.deploy_collision` | dependency of scripts.train_ppo_deploy |
| `scripts.deploy_cycle_gait` | dependency of scripts.train_ppo_deploy |
| `scripts.deploy_gait` | dependency of scripts.train_ppo_deploy |
| `scripts.deploy_symmetry` | dependency of scripts.train_ppo_deploy |
| `scripts.deploy_terrain` | dependency of scripts.train_ppo_deploy |
| `scripts.export_fig4_cot` | current workflow entry or existing local change |
| `scripts.export_rtneural` | dependency of scripts.compare_neural_energy_at_speed_3d |
| `scripts.fig4_cot_simulation` | current workflow entry or existing local change |
| `scripts.plot_latest_rolling_policy` | current workflow entry or existing local change |
| `scripts.render_mjx_policy` | dependency of scripts.train_mjx_ppo |
| `scripts.run_handcrafted_roll_to_stand` | dependency of scripts.collect_reference_roll_to_stand |
| `scripts.run_release_baseline` | dependency of scripts.optimize_phase_controller |
| `scripts.train_mjx_3d_residual_ppo` | dependency of scripts.train_mjx_3d_roll_distillation |
| `scripts.train_mjx_ppo` | dependency of scripts.train_mjx_3d_residual_ppo |
