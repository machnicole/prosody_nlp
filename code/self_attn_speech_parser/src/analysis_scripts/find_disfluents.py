import os

datadir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed'
id_file = os.path.join(datadir,'turn_dev_sent_ids_medium.txt')
tree_file = os.path.join(datadir,'turn_dev_medium.trees')
disf_file = os.path.join(datadir, 'disfluent_dev_sent_ids.txt')
fluent_file = os.path.join(datadir, 'fluent_dev_sent_ids.txt')

ids = [l.strip() for l in open(id_file).readlines()]
trees = [l.strip() for l in open(tree_file).readlines()]

id2tree = dict(zip(ids,trees))

disf_ids = []
fluent_ids = []
for idnum,tree in zip(ids,trees):
    if 'EDITED' in tree:
        disf_ids.append(idnum)
    else:
        fluent_ids.append(idnum)

with open(disf_file,'w') as disf:
    for idnum in disf_ids:
        disf.write(idnum)
        disf.write('\n')
                    
with open(fluent_file,'w') as flu:
    for idnum in fluent_ids:
        flu.write(idnum)
        flu.write('\n')


