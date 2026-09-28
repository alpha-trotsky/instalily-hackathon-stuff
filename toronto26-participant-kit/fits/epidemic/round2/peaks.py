from variants import *
for c0,h0 in [(109.7,32.5),(113.8,37.7),(106.6,58.4),(237,60.5)]:
    run={'initial':{'daily_cases':c0,'hospital_load':h0},'actions':[{'school_closure':0,'mask_mandate':0,'vaccination_rate':0}]*60}
    p=sim(run,MASKFAT=True,PE=1.0,ALLPOP=1.0); print(c0, 'v1 no-control peak %.0f @%d'%(p[:,0].max(),p[:,0].argmax()))
