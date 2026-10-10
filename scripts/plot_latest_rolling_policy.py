"""Two separate figures from continuous nominal MuJoCo policy rollouts.

Figure contract: quantify actual torque/angular-velocity operating points at
0.6 m/s command and speed tracking through startup, rolling and standing.
Single-axis bilateral-mean phase portrait and a separate time-series comparison.
Exports: editable SVG/PDF, 600 dpi PNG, raw NPZ/CSV, provenance and metrics.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np
import mujoco
from scripts import simulate_rolling_policy_sequence as sequence
from curl_robot_2d_mjx.deployment_rolling_3d import CONTROLLER_JOINT_NAMES_3D


def collect(args, speed):
    out = args.out / f'v{speed:.1f}'
    run_args = SimpleNamespace(startup=args.startup, rolling=args.rolling,
        stop=args.stop, xml=args.xml, out=out, vx=speed, yaw=getattr(args, 'yaw', 0.),
        turn_seconds=getattr(args, 'turn_seconds', 12.), stop_seconds=6., handoff_mode=args.handoff_mode, video=False,
        direct_takeover_time_s=args.direct_takeover_time_s,
        heading_hold_gain=getattr(args, 'heading_hold_gain', 0.))
    # Instrument the existing runner without changing its policy/control logic.
    original_step = mujoco.mj_step
    samples = []
    ids = {}

    def recorded_step(model, data):
        if not ids:
            joints = np.array([model.joint(n).id for n in CONTROLLER_JOINT_NAMES_3D])
            ids['qi'] = model.jnt_qposadr[joints]
            ids['vi'] = model.jnt_dofadr[joints]
            ids['ai'] = np.array([model.actuator(n+'_servo').id for n in CONTROLLER_JOINT_NAMES_3D])
            ids['torso'] = model.body('torso').id
            assert np.allclose(model.actuator_gear[ids['ai'], 0], 1.)
        # Forces returned by mj_step are evaluated at this pre-integration state.
        t = float(data.time)
        qpos, qvel, ctrl = data.qpos.copy(), data.qvel.copy(), data.ctrl[ids['ai']].copy()
        R = data.xmat[ids['torso']].reshape(3, 3)
        heading = np.arctan2(-R[0, 1], R[1, 1])
        velocity = np.cos(heading)*qvel[0] + np.sin(heading)*qvel[1]
        original_step(model, data)
        samples.append((t, velocity, heading, qpos, qvel, ctrl,
                        data.actuator_force[ids['ai']].copy()))

    mujoco.mj_step = recorded_step
    try:
        sequence.run(run_args)
    finally:
        mujoco.mj_step = original_step
    time, speed_h, heading, qpos, qvel, ctrl, torque = map(np.asarray, zip(*samples))
    np.savez_compressed(out/'telemetry.npz', time_s=time, velocity_heading_m_s=speed_h,
        heading_rad=heading, qpos=qpos, qvel=qvel, target_rad=ctrl,
        joint_position_rad=qpos[:, ids['qi']], joint_velocity_rad_s=qvel[:, ids['vi']],
        torque_nm=torque, joint_names=np.asarray(CONTROLLER_JOINT_NAMES_3D))
    if args.handoff_mode == 'prescribed':
        report = json.loads((out/'report.json').read_text())
        first_turn = event_time(report, 'rolling_requested_after_one_turn' if args.direct_takeover_time_s is None
                                else 'rolling_requested_at_direct_time')
        takeover = event_time(report, 'ppo_rolling_takeover')
        if first_turn != takeover:
            raise RuntimeError(f'Expected first-turn takeover at {first_turn}, got {takeover}')


def event_time(report, name):
    return next(e['time_s'] for e in report['events'] if e['event'] == name)


def last_complete_roll_cycle(telemetry, start, end):
    """Consecutive downward torso-pitch zero crossings define one full turn."""
    t = telemetry['time_s']
    w, x, y, z = telemetry['qpos'][:, 3:7].T
    pitch = np.arctan2(2*(x*z-w*y), 1-2*(x*x+y*y))
    indices = np.flatnonzero((pitch[:-1] >= 0) & (pitch[1:] < 0)
                             & (np.abs(np.diff(pitch)) < np.pi))
    crossings = (t[indices] - pitch[indices]*(t[indices+1]-t[indices])
                 / (pitch[indices+1]-pitch[indices]))
    crossings = crossings[(crossings >= start) & (crossings <= end)]
    if len(crossings) < 2:
        raise ValueError('Steady window does not contain a complete roll cycle')
    cycle = crossings[-2:]
    phase = np.interp(cycle, t, np.unwrap(pitch))
    if not np.isclose(abs(phase[1]-phase[0]), 2*np.pi, atol=1e-6):
        raise ValueError('Selected interval is not one full torso revolution')
    return float(cycle[0]), float(cycle[1])


def plot(args):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from matplotlib.colors import to_rgb
    from matplotlib.lines import Line2D
    plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman'],
        'mathtext.fontset': 'stix', 'font.size': 12, 'axes.labelsize': 14,
        'axes.spines.top': True, 'axes.spines.right': True, 'axes.labelpad': 1.5,
        'xtick.direction': 'in', 'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
        'xtick.major.pad': 2, 'ytick.major.pad': 2,
        'axes.linewidth': .7, 'svg.fonttype': 'none', 'pdf.fonttype': 42,
        'legend.frameon': False})
    reports, arrays = {}, {}
    for speed in (.5, .6, .7):
        folder = args.out/f'v{speed:.1f}'
        reports[speed] = json.loads((folder/'report.json').read_text())
        with np.load(folder/'telemetry.npz') as archive:
            arrays[speed] = {key: archive[key] for key in archive.files}
        if not reports[speed]['sequence_completed']:
            raise RuntimeError(f'{speed}: full sequence did not complete; inspect report')

    def save(fig, name):
        for ext in ('png', 'pdf', 'svg'):
            fig.savefig(args.out/f'{name}.{ext}', dpi=600, facecolor='white')
        plt.close(fig)

    metrics = {}
    for speed, a in arrays.items():
        r = reports[speed]
        stop = event_time(r, 'roll_to_stand_requested')
        mask = (a['time_s'] >= stop-5) & (a['time_s'] < stop)
        v = a['velocity_heading_m_s'][mask]
        metrics[str(speed)] = dict(steady_window_s=[stop-5, stop], mean_speed_m_s=float(v.mean()),
            instantaneous_speed_std_m_s=float(v.std()), instantaneous_mae_m_s=float(np.abs(v-speed).mean()),
            steady_heading_change_deg=float(np.rad2deg(np.unwrap(a['heading_rad'][mask])[-1]-np.unwrap(a['heading_rad'][mask])[0])),
            stand_success=r['stand_success'], stop_takeover_s=event_time(r, 'roll_to_stand_takeover'))

    torque_folder = (args.torque_source or args.out)/'v0.6'
    torque_report = json.loads((torque_folder/'report.json').read_text())
    with np.load(torque_folder/'telemetry.npz') as archive:
        a = {key: archive[key] for key in archive.files}
    end = event_time(torque_report, 'roll_to_stand_requested')
    start = end - 5
    steady_window = [start, end]
    if args.torque_window == 'single-cycle':
        start, end = last_complete_roll_cycle(a, start, end)
        interior = a['time_s'][(a['time_s'] > start) & (a['time_s'] < end)]
        time = np.concatenate([[start], interior, [end]])
    else:
        time = a['time_s'][(a['time_s'] >= start) & (a['time_s'] < end)]
    velocity = np.interp(time, a['time_s'], a['velocity_heading_m_s'])
    torque_mean_speed = float(np.trapezoid(velocity, time)/(time[-1]-time[0]))
    fig, ax = plt.subplots(figsize=(5.0, 5.0))
    groups = [('Front hip', 1, 4), ('Front knee', 2, 5), ('Rear hip', 7, 10), ('Rear knee', 8, 11)]
    means = {}
    filtered_means = {}
    legend_handles = []
    if args.filter_cutoff_hz:
        from scipy.signal import butter, sosfiltfilt
        fs = 1/float(np.median(np.diff(a['time_s'])))
        sos = butter(4, args.filter_cutoff_hz, fs=fs, output='sos')
        # Filter with 1 s of context on either side, then select the plot window.
        context = (a['time_s'] >= steady_window[0]-1) & (a['time_s'] <= steady_window[1]+1)
    joint_colors_rgb = [(0, 70, 199), (217, 74, 0), (138, 0, 170), (0, 125, 54)]
    joint_colors = [tuple(channel/255 for channel in rgb) for rgb in joint_colors_rgb]
    for (title, left, right), color in zip(groups, joint_colors):
        q, qdot, torque = [np.interp(time, a['time_s'], a[key][:, [left, right]].mean(axis=1))
                           for key in ['joint_position_rad', 'joint_velocity_rad_s', 'torque_nm']]
        means[title] = (q, qdot, torque)
        if args.filter_cutoff_hz:
            raw_v = a['joint_velocity_rad_s'][context][:, [left, right]].mean(axis=1)
            raw_tau = a['torque_nm'][context][:, [left, right]].mean(axis=1)
            plot_v = np.interp(time, a['time_s'][context], sosfiltfilt(sos, raw_v))
            plot_tau = np.interp(time, a['time_s'][context], sosfiltfilt(sos, raw_tau))
        else:
            plot_v, plot_tau = qdot, torque
        filtered_means[title] = (plot_v, plot_tau)
        points = np.column_stack([plot_v, plot_tau])
        segments = np.stack([points[:-1], points[1:]], axis=1)
        progress = ((time[:-1]+time[1:])/2-time[0])/(time[-1]-time[0])
        rgb = 1-(.30+.70*progress[:, None])*(1-np.asarray(to_rgb(color)))
        ax.add_collection(LineCollection(segments, colors=rgb, linewidths=1.8,
                                        capstyle='round', joinstyle='round'))
        legend_handles.append(Line2D([], [], color=color, lw=1.8, label=title))
    ax.axhline(0, color='.85', lw=.6, zorder=0)
    ax.axvline(0, color='.85', lw=.6, zorder=0)
    ax.autoscale(enable=True, axis='both', tight=False)
    ax.margins(x=.06, y=.09)
    ax.tick_params(axis='both', labelsize=14)
    ax.set_xlabel(r'$\dot{q}$ (rad/s)', fontsize=17)
    ax.set_ylabel(r'$\tau$ (N m)', fontsize=17)
    ax.legend(handles=legend_handles, loc='upper left', ncol=1, fontsize=14,
              handlelength=1.5, handletextpad=.4, borderaxespad=.7)
    fig.subplots_adjust(left=.145, right=.97, bottom=.14, top=.97)
    save(fig, 'figure1_torque_vs_joint_velocity')
    with (args.out/'figure1_source.csv').open('w', newline='') as f:
        w=csv.writer(f); w.writerow(['time_s','joint','mean_q_rad','mean_qdot_rad_s','mean_torque_nm',
                                     'filtered_mean_qdot_rad_s','filtered_mean_torque_nm'])
        for k, t in enumerate(time):
            for title, (q, qdot, torque) in means.items():
                fv, ft = filtered_means[title]
                w.writerow([t, title, q[k], qdot[k], torque[k], fv[k], ft[k]])
    (args.out/'figure1_metadata.json').write_text(json.dumps(dict(
        source_run=str(torque_folder), steady_window_s=steady_window,
        plotted_window_s=[start,end], plotted_duration_s=end-start,
        cycle_selection=args.torque_window, mean_speed_m_s=torque_mean_speed,
        cycle_definition='Last two downward torso-pitch zero crossings in the steady window; boundaries linearly interpolated',
        averaging='(left + right) / 2 independently for torque and joint angular velocity at each time sample',
        time_color_encoding=dict(time_range_s=[float(time[0]), float(time[-1])],
            early_white_fraction=.70, late_white_fraction=0., direction='light early, dark late'),
        filter=dict(type='Butterworth SOS forward-backward', design_order=4,
                    cutoff_hz=args.filter_cutoff_hz, context_each_side_s=1,
                    interpretation='Offline display smoothing; peaks and high-frequency motion are attenuated'),
        source_policies=torque_report['policy_files']), indent=2)+'\n')

    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    colors = ['#3276A5', '#C07B40', '#6B609B']
    source = []
    for speed, color in zip((.5, .6, .7), colors):
        a, r = arrays[speed], reports[speed]
        t, v = a['time_s'], a['velocity_heading_m_s']
        # Centered 0.20 s boxcar; edge normalization avoids zero-padding bias.
        kernel = np.ones(201)
        displayed = np.convolve(v, kernel, 'same') / np.convolve(np.ones_like(v), kernel, 'same')
        ax.plot(t[::10], displayed[::10], color=color, lw=1.25, label=f'{speed:.1f} m/s')
        ax.axhline(speed, color=color, lw=.9, ls=(0, (5, 3)), alpha=.75)
        trace = json.loads((args.out/f'v{speed:.1f}'/'trace.json').read_text())
        indices = np.clip(np.searchsorted([x['time_s']-.001 for x in trace], t+1e-8, side='right')-1, 0, len(trace)-1)
        for k in range(len(t)):
            row=trace[indices[k]]
            source.append([speed,t[k],v[k],displayed[k],row['command'][0],row['phase']])
    end=max(a['time_s'][-1] for a in arrays.values())
    ax.set(xlim=(0,end), xlabel='Time (s)', ylabel=r'$v$ (m/s)')
    ax.axhline(0, color='.8', lw=.65)
    ax.legend(loc='upper right', ncol=1, fontsize=11.5,
              handlelength=1.6, handletextpad=.5, borderaxespad=.7)
    fig.subplots_adjust(left=.10,right=.975,bottom=.145,top=.97)
    save(fig, 'figure2_speed_vs_time')
    with (args.out/'figure2_source.csv').open('w', newline='') as f:
        w=csv.writer(f); w.writerow(['target_command_m_s','time_s','raw_heading_speed_m_s',
            'displayed_speed_m_s','applied_policy_speed_command_m_s','phase']); w.writerows(source)
    (args.out/'metrics.json').write_text(json.dumps(metrics, indent=2)+'\n')
    print(json.dumps(metrics, indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rolling', type=Path, required=True)
    p.add_argument('--startup', type=Path, default=Path('../pupperv3-monorepo/ros2_ws/src/neural_controller/models/stand_to_roll_student_clipped_bc_norm_v1.json'))
    p.add_argument('--stop', type=Path, default=Path('C:/Users/12481/Downloads/policy_rtneural.json'))
    p.add_argument('--xml', type=Path, default=Path('assets/rollingquad_description_2/mjcf/rollingquad_abd10_no_self_collision.xml'))
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--mode', choices=['collect','plot','all'], default='all')
    p.add_argument('--handoff-mode', choices=['smooth','prescribed'], default='smooth',
                   help='prescribed: immediate rolling-policy takeover at the first full-turn policy tick')
    p.add_argument('--torque-source', type=Path, help='Use the original figure 1 run for the bilateral mean')
    p.add_argument('--filter-cutoff-hz', type=float, default=0., help='Optional 4th-order zero-phase low-pass for figure 1')
    p.add_argument('--direct-takeover-time-s', type=float, help='Absolute simulation time for direct takeover, prescribed mode only')
    p.add_argument('--torque-window', choices=['single-cycle', 'full-window'], default='single-cycle',
                   help='Figure 1: last complete torso revolution or all 5 steady seconds')
    args=p.parse_args()
    if not np.isfinite(args.filter_cutoff_hz) or not 0 <= args.filter_cutoff_hz < 500:
        p.error('filter-cutoff-hz must lie in [0, 500)')
    if args.mode in ('collect','all'):
        for speed in (.5,.6,.7): collect(args, speed)
    if args.mode in ('plot','all'): plot(args)


if __name__=='__main__': main()
