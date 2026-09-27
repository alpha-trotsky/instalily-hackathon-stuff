import json,sys
d=json.load(open('data/traffic/'+sys.argv[1]));r=d['runs'][0]
a=int(sys.argv[2]); b=int(sys.argv[3]) if len(sys.argv)>3 else len(r['observations'])
for t in range(a,b):
    o=r['observations'][t]; u=r['actions'][t]
    print(t, ' '.join(f'{o[k]:7.3f}' for k in ['flow_a','flow_b','speed_a','speed_b']), '|', ' '.join(f'{u[k]:.2f}' for k in ['signal_timing','lane_closure','toll','ramp_metering','freight_priority','clearance_effort']))
