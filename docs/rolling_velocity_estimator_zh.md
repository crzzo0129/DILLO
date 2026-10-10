# 独立滚动速度估计器：当前在线接口

当前保留版本为 [50 Hz 标定 CEM v3](rolling_velocity_estimator_calibrated_zh.md)。
旧 v1/v2 说明移入本地归档；通用采集器继续作为标定采集器的依赖保留。
估计器独立于滚动 policy，不把估计值接入 policy 输入。

## 输入与输出

- 每 20 ms 输入一帧 36 维原始 observation，按导出模型的观测契约构造。
- 历史为 20 帧；前 19 帧 `update` 返回 `None`。
- 网络输入排除 command，使用 gyro、重力方向、关节偏移及上次有效 action。
- 输出为 `[rolling_speed_m_s, trajectory_turn_rate_rad_s]`。
- 转向率是地面运动轨迹方向变化率，不是身体翻滚角速度或单纯滚动轴 heading rate。
- 不对原始 observation 预先使用 policy normalizer；模型自行使用匹配的训练归一化。

## NumPy 在线推理

```python
from curl_robot_2d_mjx.rolling_velocity_estimator import RollingVelocityEstimator

estimator = RollingVelocityEstimator(
    "results/velocity_estimator_cem_calibrated_v3/model/estimator.npz"
)
# 每 20 ms 从真实传感器与实际动作历史取得一帧：
prediction = estimator.update(raw_observation_36)
if prediction is not None:
    rolling_speed, trajectory_turn_rate = map(float, prediction)

# 新回合、传感器流重启或明显丢帧后，清空并重新积累历史：
estimator.reset()
```

在线推理只需要 NumPy。模型、数据和评估文件均保留本地，需要 [独立传输](local_artifacts_zh.md)。
模型的 `provenance["observation_contract"]` 用于核对动作中心、缩放与历史约定。
旧 52 Hz 模型不能按本页的 50 Hz 配置直接使用。

## 采集、训练与评估

`scripts.collect_calibrated_rolling_velocity_data` 使用认可 CEM reference 和匹配的速度/转向标定表；
`scripts.collect_rolling_velocity_data` 保留通用标签与采集工具。
训练、评估和转向分段诊断分别使用 `scripts.train_rolling_velocity_estimator`、
`scripts.evaluate_rolling_velocity_estimator` 和 `scripts.analyze_rolling_estimator_turns`。
完整命令、数据划分、模型来源与既有验证指标见 [v3 说明](rolling_velocity_estimator_calibrated_zh.md)。

标签使用根原点水平速度与因果 EMA；低速等无效转向标签在训练时 mask。
训练/验证/测试按完整轨迹划分，不把同一轨迹的窗口随机混入不同集合。

## 验证边界

v3 文档中的数值来自已有 CEM 仿真评估，尚未验证实机、强打滑和跨摩擦泛化。
当前网络没有运行时有效性/置信度输出头；历史填满只表示输入就绪。
不能把分段均值误差解释为逐帧转向误差，也不能把低速 mask 当成实机可直接获取的真值。

```bash
python -m unittest discover -s tests -p test_rolling_velocity_estimator.py -v
```
