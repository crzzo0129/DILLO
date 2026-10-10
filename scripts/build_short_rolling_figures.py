"""Run 9.5 s rolling-command episodes and prepare fig1/fig3 source data.
Use --case 0.5, 0.6, 0.7 or turn for individual simulations, then --case prepare.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse
import csv
import json
import shutil
import numpy as np
from scripts.plot_latest_rolling_policy import collect, event_time

def smooth(a):
    kernel=np.ones(201)
    return np.convolve(a,kernel,'same')/np.convolve(np.ones_like(a),kernel,'same')

def simulate(out, case):
    turning=case=='turn'
    settings=SimpleNamespace(out=out/('turn' if turning else 'straight'),
        rolling=Path('C:/Users/12481/Downloads/student_rtneural (2).json'),
        startup=Path('../pupperv3-monorepo/ros2_ws/src/neural_controller/models/stand_to_roll_student_clipped_bc_norm_v1.json'),
        stop=Path('C:/Users/12481/Downloads/policy_rtneural.json'),
        xml=Path('assets/rollingquad_description_2/mjcf/rollingquad_abd10_no_self_collision.xml'),
        handoff_mode='prescribed',direct_takeover_time_s=1.,yaw=.07 if turning else 0.,turn_seconds=9.5)
    collect(settings,.6 if turning else float(case))

def load(folder):
    report=json.loads((folder/'report.json').read_text())
    with np.load(folder/'telemetry.npz') as f:
        a={k:f[k] for k in f.files}
    events={k:event_time(report,v) for k,v in [('startup','stand_to_roll_enabled'),
        ('rolling','ppo_rolling_takeover'),('stop_request','roll_to_stand_requested'),('stop','roll_to_stand_takeover')]}
    assert np.isclose(events['stop_request']-events['rolling'],9.5)
    assert report['sequence_completed'] and np.isfinite(a['qvel']).all()
    t=a['time_s']; valid=(t>=events['rolling']-1e-8)&(t<events['stop']-1e-8)
    phase=np.where(t<events['startup']-1e-8,'hold',np.where(t<events['rolling']-1e-8,'startup',np.where(valid,'rolling','stop')))
    events.update(stand_success=report['stand_success'],stable_stand_s=report['longest_stable_stand_s'],
                  actual_rolling_duration_s=events['stop']-events['rolling'])
    return a,events,valid,phase,report

def prepare(out):
    prior=Path('results/final_figures_20260915')
    for name in ('fig2_source.csv','fig2_cycle_metadata.json'):
        shutil.copy2(prior/name,out/name)
    # Copy the standalone plotting script for a self-contained result bundle.
    text=(prior/'redraw_figures.py').read_text()
    text=text.replace("'fig3': (1.65, 1.65)","'fig3': (3.3, 1.65)")
    text=text.replace("KNEE_STYLES = [(0,(4,2)), (0,(1,1.5))]  # FL long dash, FR short dash",
                      "KNEE_STYLES = [(0,(2.5,1.5)), (0,(.1,2.0))]  # FL short dash, FR round dots")
    text=text.replace("lw=LINE_PT,ls=style,label=label)","lw=LINE_PT,ls=style,dash_capstyle='round' if side=='right' else 'butt',label=label)")
    text=text.replace("fig1 3.3 x 1.65 in; fig2/fig3 1.65 x 1.65 in", "fig1/fig3 3.3 x 1.65 in; fig2 1.65 x 1.65 in")
    (out/'redraw_figures.py').write_text(text)
    meta={'speed_runs':{},'turn_run':{},'requested_rolling_duration_s':9.5,
          'plot_area_inches':{'fig1':[3.3,1.65],'fig2':[1.65,1.65],'fig3':[3.3,1.65]},
          'canvas_inches':{'fig1':[3.83,2.07],'fig2':[2.18,2.07],'fig3':[4.16,2.07]},'font_pt':8}
    with (out/'fig1_source.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['target_command_m_s','time_s','raw_heading_speed_m_s','displayed_speed_m_s','displayed_command_m_s','event_phase'])
        for speed in (.5,.6,.7):
            a,r,valid,phase,report=load(out/'straight'/f'v{speed:.1f}')
            meta['speed_runs'][str(speed)]=r
            w.writerows(zip(np.full(len(valid),speed),a['time_s'],a['velocity_heading_m_s'],smooth(a['velocity_heading_m_s']),np.where(valid,speed,0.),phase))
    a,r,valid,phase,report=load(out/'turn/v0.6')
    meta['turn_run']=r; meta['policies']=report['policy_files']; meta['physics']=report['physics']
    t=a['time_s']; yaw=np.gradient(np.unwrap(a['heading_rad']),t,edge_order=2)
    names=a['joint_names'].tolist()
    left=a['joint_position_rad'][:,names.index('front_left_knee')]
    right=a['joint_position_rad'][:,names.index('front_right_knee')]
    with (out/'fig3_source.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['time_s','yaw_rate_raw_rad_s','yaw_rate_displayed_rad_s',
            'front_left_knee_q_rad','front_right_knee_q_rad','front_left_knee_q_displayed_rad','front_right_knee_q_displayed_rad',
            'rolling_yaw_command_rad_s','event_phase'])
        w.writerows(zip(t,yaw,smooth(yaw),left,right,smooth(left),smooth(right),np.where(valid,.07,0.),phase))
    (out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta,indent=2),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',choices=['0.5','0.6','0.7','turn','prepare'],required=True)
    parser.add_argument('--out',type=Path,default=Path('results/final_figures_20260915_short'))
    args=parser.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    prepare(args.out) if args.case=='prepare' else simulate(args.out,args.case)
