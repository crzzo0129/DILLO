"""Validate matched-speed results and export fig4 data to the final figure bundle."""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np
import mujoco
from scripts.fig4_cot_simulation import ROOT,XML,ROLL,WALK,BEGIN,END

SELECTION=[(.60,.477,.64),(.65,.52,.705),(.70,.56,.788),(.75,.588,.86)]

def main():
    source=ROOT/'results/fig4_cot_20260915'
    data=ROOT.parent/'最终图表/重绘代码与数据'
    details=data/'fig4_计算明细'; details.mkdir(exist_ok=True)
    selected=[]; windows={}; reductions=[]
    for target,roll_command,walk_command in SELECTION:
        pair=[]
        for mode,command in [('roll',roll_command),('walk',walk_command)]:
            folder=source/f'{mode}_{command:.4f}_hold'
            result=json.loads((folder/'summary.json').read_text())
            assert all(result[k] for k in ('steady','straight','gait_ok'))
            assert abs(result['actual_speed_m_s']-target)<=.01, (target,mode,result['actual_speed_m_s'])
            result['target_speed_m_s']=target
            with np.load(result['telemetry']) as archive:
                a={k:archive[k] for k in archive.files}
            t=a['time_s']; mask=(t>=BEGIN-1e-8)&(t<END-1e-8)
            key=f'{mode}_{target:.2f}'
            windows[key+'_time_s']=t[mask]
            windows[key+'_torque_nm']=a['torque_nm'][mask]
            windows[key+'_qdot_rad_s']=a['joint_velocity_rad_s'][mask]
            windows[key+'_qpos']=a['qpos'][mask]
            windows[key+'_heading_rad']=a['heading_rad'][mask]
            work=float(np.abs(a['torque_nm'][mask]*a['joint_velocity_rad_s'][mask]).sum()*.001)
            assert np.isclose(work,result['absolute_work_j'],rtol=1e-9)
            selected.append(result); pair.append(result)
        mismatch=abs(pair[0]['actual_speed_m_s']-pair[1]['actual_speed_m_s'])
        assert mismatch<=.01, (target,mismatch)
        reductions.append({'target_speed_m_s':target,'speed_mismatch_m_s':mismatch,
            'rolling_cot_reduction_percent':100*(1-pair[0]['cot_absolute']/pair[1]['cot_absolute'])})
    fields=['target_speed_m_s','mode','command_m_s','actual_speed_m_s','cot_absolute','cot_positive',
            'absolute_work_j','positive_work_j','negative_work_j','distance_m','mass_kg','gravity_m_s2',
            'steady','straight','gait_ok','speed_trend_m_s2','heading_change_deg','lateral_displacement_m']
    with (data/'fig4_source.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); writer.writeheader(); writer.writerows(selected)
    np.savez_compressed(details/'measurement_windows.npz',**windows)
    meta={'definition':'COT_abs = integral(sum(abs(tau_i*qdot_i)),dt)/(m*g*d), all 12 actuators',
        'distance_definition':'Horizontal net displacement magnitude over the fixed measurement window',
        'energy_scope':'Absolute mechanical work only; no battery, electronics, transmission loss or regeneration model',
        'measurement_window_s':[BEGIN,END],'physics_timestep_s':.001,'policy_period_s':.02,
        'physics':'CPU MuJoCo CG20, implicitfast, elliptic contacts, zero root damping, ground collision enabled, self collision disabled',
        'mujoco_version':mujoco.__version__,'gains':{'kp':5.,'kd':.1,'torque_limit_nm':3.},
        'heading_hold':'Same gain 0.8 on heading error, clipped to +/-0.07 rad/s for both modes; correction work included',
        'matching_gate':{'max_target_error_m_s':.01,'max_pair_speed_difference_m_s':.01},
        'steady_gate':{'block_length_s':2.,'max_block_deviation_from_mean_m_s':.08,'max_speed_slope_m_s2':.008},
        'straight_gate':{'max_abs_lateral_displacement_over_distance':.05,'max_heading_change_deg':5},
        'gait_gate':'Walking upright tilt <15 degrees; rolling >4 complete revolutions per 10s, rolling-axis tilt <10 degrees',
        'replication':'One deterministic nominal run per gait and target speed. No error bars or inferential statistics.',
        'calibration':'Constant speed commands adjusted using measured speed and gait/straightness gates, not COT; fixed measurement window was retained.',
        'plot_area_inches':[1.65,1.65],'font_pt':8,
        'files':{name:{'path':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for name,path in [('rolling_policy',ROLL),('walking_policy',WALK),('model',XML)]},
        'selected_runs':selected,'comparison':reductions}
    (data/'fig4_metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    trials=[json.loads(p.read_text()) for p in sorted(source.glob('*/summary.json'))]
    (details/'calibration_trials.json').write_text(json.dumps(trials,indent=2)+'\n')
    print(json.dumps({'selected':[{k:r[k] for k in fields[:6]} for r in selected],'comparison':reductions},indent=2))

if __name__=='__main__':main()
