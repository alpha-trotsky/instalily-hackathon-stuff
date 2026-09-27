"""Run an explicit segment schedule on the simulator, saving after every paid step.

Every step spends budget, so the step count must be confirmed on the command line:

    python run_schedule.py --system market --output data/market/A.json \
        --segments '[{"steps": 50, "action": {"interest_rate": 0, "transaction_tax": 0}}]' --confirm 50

Continue the same simulator run later (no reset) by pointing --continue at an earlier file:

    python run_schedule.py --continue data/market/A.json --segments '[...]' --confirm 125

A segment holds `action` for `steps` ticks, or ramps linearly from `action` to `ramp_to`.
New runs refuse to overwrite an existing file; continued runs only append.
"""
import argparse
import json
import os
import time
import uuid
from pathlib import Path
from client import Client

CREDENTIALS = Path(__file__).resolve().parent.parent / 'app-141-1d2abb-credentials.json'


def expand(segments, bounds):
    actions = []
    for segment in segments:
        start, end, steps = segment['action'], segment.get('ramp_to', segment['action']), segment['steps']
        if set(start) != set(bounds) or set(end) != set(bounds):
            raise ValueError(f'Every action must name exactly {sorted(bounds)}')
        for tick in range(steps):
            frac = (tick + 1) / steps if 'ramp_to' in segment else 0.0
            action = {name: start[name] + frac * (end[name] - start[name]) for name in bounds}
            for name, (low, high) in bounds.items():
                if not low <= action[name] <= high:
                    raise ValueError(f'{name}={action[name]} is outside [{low}, {high}]')
            actions.append(action)
    return actions


def save(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data) + '\n')
    # OneDrive briefly locks files it is syncing; the .tmp copy already holds every paid step.
    for attempt in range(50):
        try:
            os.replace(temp, path)
            return
        except PermissionError:
            time.sleep(0.2)
    print(f'warning: could not replace {path}; latest data is in {temp}')


def run(client, output, segments, confirm, system=None, continue_run=False):
    output = Path(output)
    if continue_run:
        data = json.loads(output.read_text())
        system = data['family']
    elif output.exists():
        raise ValueError('Choose a new output path to preserve earlier research')
    brief = data['brief'] if continue_run else client.brief(system)
    actions = expand(segments, brief['interventions'])
    if confirm != len(actions):
        raise ValueError(f'This schedule spends {len(actions)} steps; pass --confirm {len(actions)}')
    available = client.budget(system)['simulator_steps_remaining']
    if len(actions) > available:
        raise ValueError(f'This schedule needs {len(actions)} steps; {available} remain')
    print(f'{system}: spending {len(actions)} steps, {available} remaining before this run')

    if continue_run:
        run = data['runs'][-1]
    else:
        reset = client.reset(system)
        run = {'run_id': reset['run_id'], 'initial': reset['observation'], 'reset_response': reset,
               'segments': [], 'actions': [], 'observations': [], 'responses': []}
        data = {'family': system, 'brief': brief, 'runs': [run]}
        output.parent.mkdir(parents=True, exist_ok=True)
    run['segments'].append({'start_tick': len(run['actions']), 'segments': segments,
                            'started_at': time.strftime('%Y-%m-%dT%H:%M:%S')})
    save(output, data)

    for action in actions:
        tick = len(run['actions'])
        # Deterministic key: re-running after a crash cannot pay twice for the same tick.
        request_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{run['run_id']}/{tick}"))
        response = client.step(run['run_id'], action, request_id=request_id)
        run['actions'].append(action)
        run['observations'].append(response['observation'])
        run['responses'].append({k: v for k, v in response.items() if k != 'observation'})
        save(output, data)
    remaining = client.budget(system)['simulator_steps_remaining']
    print(f'Saved {len(actions)} observations to {output} (run length {len(run["actions"])}); {remaining} steps remain')
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--system')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--continue', dest='continue_path', type=Path)
    parser.add_argument('--segments', required=True, help='JSON list, or a path to a JSON file')
    parser.add_argument('--confirm', type=int, required=True, help='must equal the number of steps spent')
    args = parser.parse_args()
    text = Path(args.segments).read_text() if args.segments.endswith('.json') else args.segments
    segments = json.loads(text)
    credentials = json.loads(CREDENTIALS.read_text())
    with Client(credentials['gateway_url'], credentials['gateway_key']) as client:
        if args.continue_path:
            run(client, args.continue_path, segments, args.confirm, continue_run=True)
        else:
            if not (args.system and args.output):
                parser.error('--system and --output are required for a new run')
            run(client, args.output, segments, args.confirm, system=args.system)
