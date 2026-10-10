"""Run and plot startup -> commanded turning roll -> stand, without state resets.

Figures: shaded sequence stages in separate 1:1 speed/time and heading yaw-rate/time
plots, with left/right front-knee positions on the latter's right axis.
Raw simulation telemetry and unsmoothed measurements remain available for audit.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np
from scripts.plot_latest_rolling_policy import collect, event_time


def moving_mean(values, window=201):
    kernel = np.ones(window)
    return np.convolve(values, kernel, 'same')/np.convolve(np.ones_like(values), kernel, 'same')


def analyze(args):
    run_dir = args.out/'v0.6'
    report = json.loads((run_dir/'report.json').read_text())
    with np.load(run_dir/'telemetry.npz') as archive:
        a = {key: archive[key] for key in archive.files}
    t = a['time_s']
    heading = np.unwrap(a['heading_rad'])
    yaw_rate = np.gradient(heading, t, edge_order=2)
    forward = a['velocity_heading_m_s']
    forward_plot, yaw_plot = moving_mean(forward), moving_mean(yaw_rate)
    names = a['joint_names'].tolist()
    knee_left = a['joint_position_rad'][:, names.index('front_left_knee')]
    knee_right = a['joint_position_rad'][:, names.index('front_right_knee')]
    knee_left_plot = moving_mean(knee_left)
    knee_right_plot = moving_mean(knee_right)
    assert np.isfinite(knee_left).all() and np.isfinite(knee_right).all()
    takeover = event_time(report, 'ppo_rolling_takeover')
    stop_request = event_time(report, 'roll_to_stand_requested')
    stop_takeover = event_time(report, 'roll_to_stand_takeover')
    startup_time = event_time(report, 'stand_to_roll_enabled')
    stages = [('Hold', 0., startup_time, (240,240,240)),
              ('Stand to roll', startup_time, takeover, (255,232,203)),
              ('Rolling', takeover, stop_takeover, (230,240,250)),
              ('Roll to stand', stop_takeover, float(t[-1]), (239,228,244))]
    trace = json.loads((run_dir/'trace.json').read_text())
    trace_t = np.asarray([row['time_s']-.001 for row in trace])
    index = np.clip(np.searchsorted(trace_t, t+1e-8, side='right')-1, 0, len(trace)-1)
    commanded_v = np.asarray([trace[i]['command'][0] for i in index])
    commanded_yaw = np.asarray([trace[i]['command'][2] for i in index])
    phases = np.asarray([trace[i]['phase'] for i in index])
    command_defined = (t >= takeover-1e-8) & (t < stop_takeover-1e-8)
    # Policy input placeholders outside rolling are not defined task commands.
    speed_reference = [float(v) if valid else '' for v, valid in zip(commanded_v, command_defined)]
    yaw_reference = [float(v) if valid else '' for v, valid in zip(commanded_yaw, command_defined)]
    # Physics timestamps accumulate floating-point error; events use rounded ticks.
    # Apply the same tolerance used for mapping the trace to telemetry above.
    rolling = (t >= takeover-1e-8) & (t < stop_request-1e-8)
    assert np.isfinite(yaw_rate).all() and np.isfinite(a['qvel']).all()
    assert np.allclose(commanded_v[rolling], .6)
    assert np.allclose(commanded_yaw[rolling], .07)
    assert np.all(phases[rolling] == 'rolling')
    assert np.isclose(takeover, 1.)
    stats = {}
    for name, start in [('rolling', takeover), ('last_5s_rolling', stop_request-5)]:
        window = (t >= start-1e-8) & (t < stop_request-1e-8)
        times = t[window]
        span = times[-1]-times[0]
        delta = float(heading[window][-1]-heading[window][0])
        stats[name] = dict(window_s=[float(times[0]), float(times[-1])],
            mean_heading_speed_m_s=float(np.trapezoid(forward[window], times)/span),
            mean_heading_yaw_rate_rad_s=delta/span, heading_change_deg=float(np.rad2deg(delta)),
            net_world_x_m=float(a['qpos'][window, 0][-1]-a['qpos'][window, 0][0]),
            net_world_y_m=float(a['qpos'][window, 1][-1]-a['qpos'][window, 1][0]))
    metrics = dict(command=dict(vx_m_s=.6, yaw_z_rad_s=.07),
        takeover_s=takeover, stop_request_s=stop_request, stop_takeover_s=stop_takeover,
        stand_success=report['stand_success'], longest_stable_stand_s=report['longest_stable_stand_s'],
        statistics=stats, smoothing='201 samples at 1 kHz, centered moving mean; edge-normalized',
        yaw_definition='Time derivative of unwrapped horizontal rolling-axis heading, not torso-local z gyro',
        knee_definition='Separate measured front_left_knee and front_right_knee positions in radians; each uses the same display smoothing as yaw rate',
        command_definition='Defined only during continuous rolling; absent during hold, stand-to-roll and roll-to-stand',
        stages=[dict(name=name,start_s=start,end_s=end,rgb=rgb) for name,start,end,rgb in stages],
        policy_files=report['policy_files'], physics=report['physics'])
    (args.out/'turn_metrics.json').write_text(json.dumps(metrics, indent=2)+'\n')
    with (args.out/'turn_source.csv').open('w', newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['time_s','forward_speed_raw_m_s','forward_speed_displayed_m_s',
            'yaw_rate_raw_rad_s','yaw_rate_displayed_rad_s','heading_rad',
            'world_x_m','world_y_m','policy_input_forward_m_s','policy_input_yaw_rad_s','phase',
            'front_left_knee_q_rad','front_right_knee_q_rad','front_left_knee_q_displayed_rad','front_right_knee_q_displayed_rad',
            'rolling_speed_command_m_s','rolling_yaw_command_rad_s'])
        writer.writerows(zip(t,forward,forward_plot,yaw_rate,yaw_plot,heading,
                            a['qpos'][:,0],a['qpos'][:,1],commanded_v,commanded_yaw,phases,
                            knee_left,knee_right,knee_left_plot,knee_right_plot,speed_reference,yaw_reference))
    plot(args.out, t, forward_plot, yaw_plot, knee_left_plot, knee_right_plot, stages)
    print(json.dumps(metrics, indent=2), flush=True)


def plot(out, time, forward, yaw, knee_left, knee_right, stages):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],
        'mathtext.fontset':'stix','font.size':14,'axes.labelsize':17,'axes.labelpad':1.5,
        'axes.spines.top':True,'axes.spines.right':True,'axes.linewidth':.7,
        'xtick.direction':'in','ytick.direction':'in','xtick.top':True,'ytick.right':True,
        'xtick.major.pad':2,'ytick.major.pad':2,'legend.frameon':False,
        'svg.fonttype':'none','pdf.fonttype':42})
    # Editable RGB colors (0–255), dimensions in inches and linewidth in points.
    yaw_rgb, knee_left_rgb, knee_right_rgb = (217,74,0), (0,70,199), (0,125,54)
    yaw_color, knee_left_color, knee_right_color = [np.asarray(rgb)/255
        for rgb in (yaw_rgb, knee_left_rgb, knee_right_rgb)]
    rolling_stage = next(stage for stage in stages if stage[0] == 'Rolling')
    command_start, command_end = rolling_stage[1:3]

    def shade(axis):
        for _, start, end, rgb in stages:
            axis.axvspan(start,end,color=np.asarray(rgb)/255,ec='none',zorder=-10)

    def export(figure, name):
        for ext in ['png','pdf','svg']:
            figure.savefig(out/f'{name}.{ext}',dpi=600,facecolor='white')

    speed_fig, speed_ax = plt.subplots(figsize=(5,5))
    shade(speed_ax)
    speed_ax.plot(time[::10],forward[::10],color=knee_left_color,lw=1.8,label=r'$v$')
    speed_ax.plot([command_start,command_end],[.6,.6],color='.25',lw=1.5,ls=':',label=r'$v^{\mathrm{cmd}}$')
    speed_ax.set(xlim=(0,time[-1]),xlabel='Time (s)',ylabel=r'$v$ (m/s)')
    speed_fig.subplots_adjust(left=.17,right=.97,bottom=.14,top=.97)
    # Keep the speed legend fixed at upper left; expand y limits if necessary.
    for margin in [.10,.20,.35,.50,.75]:
        speed_ax.margins(y=margin)
        speed_legend=speed_ax.legend(loc='upper left',fontsize=14,handlelength=1.5,handletextpad=.4,borderaxespad=.7)
        speed_fig.canvas.draw()
        box=speed_legend.get_window_extent(speed_fig.canvas.get_renderer()).expanded(1.04,1.04)
        points=np.concatenate([np.column_stack([time,forward]),
            np.column_stack([np.linspace(command_start,command_end,1000),np.full(1000,.6)])])
        pixels=speed_ax.transData.transform(points)
        if not ((pixels[:,0]>=box.x0)&(pixels[:,0]<=box.x1)&(pixels[:,1]>=box.y0)&(pixels[:,1]<=box.y1)).any():
            break
        speed_legend.remove()
    else:
        raise RuntimeError('Cannot place speed legend at upper left without overlap')
    export(speed_fig,'turn_forward_speed_stages')
    plt.close(speed_fig)

    fig, ax = plt.subplots(figsize=(5,5))
    shade(ax)
    right = ax.twinx()
    yaw_line, = ax.plot(time[::10],yaw[::10],color=yaw_color,lw=1.8,label=r'$\omega_z$')
    command_line, = ax.plot([command_start,command_end],[.07,.07],color='.25',lw=1.5,ls=':',label=r'$\omega_z^{\mathrm{cmd}}$')
    knee_left_line, = right.plot(time[::10],knee_left[::10],color=knee_left_color,lw=1.8,ls='--',label=r'$q_{\mathrm{FL,knee}}$')
    knee_right_line, = right.plot(time[::10],knee_right[::10],color=knee_right_color,lw=1.8,ls='--',label=r'$q_{\mathrm{FR,knee}}$')
    ax.set(xlim=(0,time[-1]),xlabel='Time (s)',ylabel=r'$\omega_z$ (rad/s)')
    right.set_ylabel(r'$q$ (rad)',color='black')
    ax.yaxis.label.set_color(yaw_color)
    ax.tick_params(axis='y',colors=yaw_color,right=False)
    right.tick_params(axis='y',colors='black',left=False,right=True)
    fig.subplots_adjust(left=.18,right=.83,bottom=.14,top=.97)
    handles = [yaw_line,command_line,knee_left_line,knee_right_line]
    # Check both y-axis transforms before accepting an internal legend position.
    found = False
    for margin in [.10,.20,.35,.50]:
        ax.margins(y=margin)
        right.margins(y=margin)
        for loc in ['upper right','upper left','lower right','lower left']:
            legend=right.legend(handles=handles,loc=loc,fontsize=14,handlelength=1.5,handletextpad=.4,borderaxespad=.7)
            fig.canvas.draw()
            renderer=fig.canvas.get_renderer()
            box=legend.get_window_extent(renderer).expanded(1.04,1.04)
            pixels=np.concatenate([ax.transData.transform(np.column_stack([time,yaw])),
                                   right.transData.transform(np.column_stack([time,knee_left])),
                                   right.transData.transform(np.column_stack([time,knee_right]))])
            overlap=((pixels[:,0]>=box.x0)&(pixels[:,0]<=box.x1)&(pixels[:,1]>=box.y0)&(pixels[:,1]<=box.y1)).any()
            command_y=ax.transData.transform([[0,.07]])[0,1]
            if not overlap and not box.y0<=command_y<=box.y1:
                found = True
                break
            legend.remove()
        if found:
            break
    if not found:
        raise RuntimeError('No clear internal legend position')
    export(fig,'turn_yaw_rate_front_knees_lr_stages')
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--rolling',type=Path,default=Path('C:/Users/12481/Downloads/student_rtneural (2).json'))
    parser.add_argument('--mode',choices=['all','plot'],default='all')
    args=parser.parse_args()
    if args.mode=='all':
        settings=SimpleNamespace(out=args.out,rolling=args.rolling,
            startup=Path('../pupperv3-monorepo/ros2_ws/src/neural_controller/models/stand_to_roll_student_clipped_bc_norm_v1.json'),
            stop=Path('C:/Users/12481/Downloads/policy_rtneural.json'),
            xml=Path('assets/rollingquad_description_2/mjcf/rollingquad_abd10_no_self_collision.xml'),
            handoff_mode='prescribed',direct_takeover_time_s=1.,yaw=.07)
        collect(settings,.6)
    analyze(args)


if __name__=='__main__':
    main()
