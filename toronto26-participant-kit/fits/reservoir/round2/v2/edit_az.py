p='greybox/reservoir_model_v2.py'; s=open(p).read()
s=s.replace("'a_z': (0.2, 'unit')","'a_z': (0.04, 'az')")
s=s.replace("""    if kind == 'gam':
        return 1.0 + 4.0 * _sigmoid(raw)""","""    if kind == 'gam':
        return 1.0 + 4.0 * _sigmoid(raw)
    if kind == 'az':
        return 0.02 + 0.18 * _sigmoid(raw)""")
s=s.replace("""    if kind == 'gam':
        return _logit((value - 1.0) / 4.0)""","""    if kind == 'gam':
        return _logit((value - 1.0) / 4.0)
    if kind == 'az':
        return _logit((value - 0.02) / 0.18)""")
s=s.replace("""  Q1 reset transient: z decays fast (a_z ~ 0.04)""","""  Q1 reset transient: z decays fast (a_z in [0.02, 0.2], no clock-like slow drift)""")
s=s.replace("""        z *= (1.0 - a_z)""","""        z *= (1.0 - min(max(a_z, 0.02), 0.2))""")
open(p,'w').write(s)
