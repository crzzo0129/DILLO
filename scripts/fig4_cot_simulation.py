"""Matched-speed mechanical COT simulations using the latest rolling policy.

Predeclared evaluation: fixed t=20..30 s, all 12 actuator torques times their
matching pre-step joint velocities, same model/physics/gains for both modes.
Calibrate constant commands by achieved mean speed; never select by COT.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse
import json
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np
import mujoco
from scripts.plot_latest_rolling_policy import collect
from scripts.simulate_rolling_policy_sequence import Policy, cold_history, torso_gyro
from curl_robot_2d_mjx.deployment_rolling_3d import CONTROLLER_JOINT_NAMES_3D
from curl_robot_2d_mjx.reset_grounding import make_floor_clearance

ROOT=Path(__file__).resolve().parents[1]
XML=ROOT/'assets/rollingquad_description_2/mjcf/rollingquad_abd10_no_self_collision.xml'
ROLL=Path('C:/Users/12481/Downloads/student_rtneural (2).json')
WALK=ROOT.parent/'rollingquad_2_deploy_robust_dr_policy_stable.json'
START=ROOT.parent/'pupperv3-monorepo/ros2_ws/src/neural_controller/models/stand_to_roll_student_clipped_bc_norm_v1.json'
STOP=Path('C:/Users/12481/Downloads/policy_rtneural.json')
BEGIN,END=20.,30.

def make_model():
    m=mujoco.MjModel.from_xml_path(str(XML))
    m.opt.solver=mujoco.mjtSolver.mjSOL_CG
    m.opt.integrator=mujoco.mjtIntegrator.mjINT_IMPLICITFAST
    m.opt.cone=mujoco.mjtCone.mjCONE_ELLIPTIC
    m.opt.jacobian=mujoco.mjtJacobian.mjJAC_DENSE
    m.opt.iterations,m.opt.ls_iterations,m.opt.timestep=20,10,.001
    m.dof_damping[:6]=0
    return m

def walking(folder,command,heading_hold):
    m=make_model(); d=mujoco.MjData(m); policy=Policy(WALK)
    joints=np.array([m.joint(n).id for n in CONTROLLER_JOINT_NAMES_3D])
    qi,vi=m.jnt_qposadr[joints],m.jnt_dofadr[joints]
    ai=np.array([m.actuator(n+'_servo').id for n in CONTROLLER_JOINT_NAMES_3D])
    assert np.allclose(m.actuator_gear[ai,0],1.)
    torso=m.body('torso').id
    mujoco.mj_resetDataKeyframe(m,d,m.key('stand').id)
    d.qpos[qi]=policy.center; d.qvel[:]=0; d.ctrl[ai]=policy.center
    m.actuator_gainprm[ai,0]=policy.kps
    m.actuator_biasprm[ai,1]=-policy.kps; m.actuator_biasprm[ai,2]=-policy.kds
    mujoco.mj_forward(m,d)
    clearance=make_floor_clearance(m,m.geom('floor').id,np)
    d.qpos[2]+=max(0.,.0005-float(clearance(d))); mujoco.mj_forward(m,d)
    history=cold_history(); rows=[]
    for tick in range(31001):
        R=d.xmat[torso].reshape(3,3)
        if tick>=500 and tick%20==0:
            history[0,:3]=torso_gyro(m,d,torso)
            history[0,3:6]=R.T@np.array([0,0,-1.])
            yaw_command=float(np.clip(-.8*np.arctan2(-R[0,1],R[1,1]),-.07,.07)) if heading_hold else 0.
            history[0,6:9]=[command,0,yaw_command]; history[0,9:12]=[0,0,1]
            history[0,12:24]=d.qpos[qi]-policy.center
            raw=policy(history.reshape(-1)); d.ctrl[ai]=policy.target(raw)
            history=np.roll(history,1,axis=0); history[0,24:36]=raw
        heading=np.arctan2(-R[0,1],R[1,1])
        t=float(d.time); q=d.qpos.copy(); v=d.qvel[vi].copy()
        speed=np.cos(heading)*d.qvel[0]+np.sin(heading)*d.qvel[1]
        mujoco.mj_step(m,d)
        rows.append((t,q,v,d.actuator_force[ai].copy(),heading,speed))
        if not np.isfinite(d.qpos).all():
            raise RuntimeError('Nonfinite walking state')
    t,q,v,tau,heading,speed=map(np.asarray,zip(*rows))
    np.savez_compressed(folder/'telemetry.npz',time_s=t,qpos=q,
        joint_velocity_rad_s=v,torque_nm=tau,heading_rad=heading,velocity_heading_m_s=speed)

def simulate(mode,command,folder,heading_hold):
    if mode=='roll':
        settings=SimpleNamespace(out=folder,rolling=ROLL,startup=START,stop=STOP,xml=XML,
            handoff_mode='prescribed',direct_takeover_time_s=1.,yaw=0.,turn_seconds=30.,
            heading_hold_gain=.8 if heading_hold else 0.)
        collect(settings,command)
        source=folder/f'v{command:.1f}'/'telemetry.npz'
    else:
        walking(folder,command,heading_hold); source=folder/'telemetry.npz'
    return source

def summarize(source,mode,command):
    with np.load(source) as f:
        a={k:f[k] for k in f.files}
    t=a['time_s']; mask=(t>=BEGIN-1e-8)&(t<END-1e-8)
    assert mask.sum()==10000 and np.isfinite(a['torque_nm']).all()
    dt=float(np.median(np.diff(t))); power=a['torque_nm'][mask]*a['joint_velocity_rad_s'][mask]
    positive=float(np.maximum(power,0).sum()*dt)
    negative=float(np.maximum(-power,0).sum()*dt)
    x,y=a['qpos'][:,0],a['qpos'][:,1]
    dx=float(np.interp(END,t,x)-np.interp(BEGIN,t,x))
    dy=float(np.interp(END,t,y)-np.interp(BEGIN,t,y))
    d=float(np.hypot(dx,dy)); mean=d/(END-BEGIN)
    blocks=[]
    for start in np.arange(BEGIN,END,2.):
        delta=[np.interp(start+2,t,a['qpos'][:,j])-np.interp(start,t,a['qpos'][:,j]) for j in (0,1)]
        blocks.append(float(np.linalg.norm(delta)/2))
    heading=np.unwrap(a['heading_rad'])
    h0=float(np.interp(BEGIN,t,heading)); h1=float(np.interp(END,t,heading))
    m=make_model(); mass=float(m.body_mass.sum()); g=float(np.linalg.norm(m.opt.gravity))
    q=a['qpos'][mask,3:7]; w,xx,yy,z=q.T
    upright=np.rad2deg(np.arccos(np.clip(1-2*(xx*xx+yy*yy),-1,1)))
    axis=np.rad2deg(np.arcsin(np.clip(2*(yy*z+w*xx),-1,1)))
    pitch=np.unwrap(np.arctan2(2*(xx*z-w*yy),1-2*(xx*xx+yy*yy)))
    slope=float(np.polyfit(np.arange(5)*2,blocks,1)[0])
    steady=max(abs(v-mean) for v in blocks)<=.08 and abs(slope)<=.008
    straight=abs(dy)/max(d,1e-9)<.05 and abs(np.rad2deg(h1-h0))<5
    gait_ok=bool(np.max(upright)<15) if mode=='walk' else bool(abs(pitch[-1]-pitch[0])>8*np.pi and np.max(abs(axis))<10)
    return dict(mode=mode,command_m_s=command,actual_speed_m_s=mean,window_s=[BEGIN,END],
        block_speeds_m_s=blocks,speed_trend_m_s2=slope,steady=bool(steady),straight=bool(straight),gait_ok=gait_ok,
        forward_distance_m=dx,lateral_displacement_m=dy,distance_m=d,heading_change_deg=float(np.rad2deg(h1-h0)),
        positive_work_j=positive,negative_work_j=negative,absolute_work_j=positive+negative,
        cot_absolute=(positive+negative)/(mass*g*d),cot_positive=positive/(mass*g*d),
        mass_kg=mass,gravity_m_s2=g,max_upright_tilt_deg=float(np.max(upright)),max_axis_tilt_deg=float(np.max(abs(axis))),
        rolling_turns=float(abs(pitch[-1]-pitch[0])/(2*np.pi)),telemetry=str(source.resolve()))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['roll','walk'],required=True)
    parser.add_argument('--command',type=float,required=True)
    parser.add_argument('--heading-hold',action='store_true')
    parser.add_argument('--out',type=Path,default=ROOT/'results/fig4_cot_20260915')
    args=parser.parse_args(); folder=args.out/f'{args.mode}_{args.command:.4f}{"_hold" if args.heading_hold else ""}'; folder.mkdir(parents=True,exist_ok=True)
    source=folder/(f'v{args.command:.1f}/telemetry.npz' if args.mode=='roll' else 'telemetry.npz')
    if not source.exists(): source=simulate(args.mode,args.command,folder,args.heading_hold)
    result=summarize(source,args.mode,args.command)
    result['heading_hold']=args.heading_hold
    result['heading_hold_gain']=.8 if args.heading_hold else 0.
    result['heading_hold_yaw_limit_rad_s']=.07 if args.heading_hold else 0.
    (folder/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
