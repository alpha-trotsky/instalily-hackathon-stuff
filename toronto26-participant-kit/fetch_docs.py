"""Download the free brief, documents and budget for every system. Spends no simulator steps."""
import json
import os
from pathlib import Path
from client import Client

SYSTEMS = ['epidemic', 'market', 'traffic', 'power_grid', 'supply_chain', 'wildlife',
           'reservoir', 'ad_auction', 'social_contagion', 'hospital_queue']

if __name__ == '__main__':
    out = Path('docs')
    out.mkdir(exist_ok=True)
    with Client(os.environ['GROUNDTRUTH_GATEWAY_URL'], os.environ['GROUNDTRUTH_KEY']) as client:
        for system in SYSTEMS:
            data = {'brief': client.brief(system), 'documents': client.documents(system),
                    'budget': client.budget(system)}
            (out / f'{system}.json').write_text(json.dumps(data, indent=2) + '\n')
            print(f"{system}: saved, {data['budget']['simulator_steps_remaining']} steps remaining")
