import os

"""
id_dir = '../../data/swbd_word_times/tree_aligned'

ids_seen = set()
with open('file_ids.txt','w') as f:
    for filename in os.listdir(id_dir):
        print(filename)
        id_num = filename.split('_')[2].replace('sw','').replace('A','').replace('B','').replace('.pickle','')
        if id_num in ids_seen: continue
        f.write(id_num)
        f.write('\n')
        ids_seen.add(id_num)
"""

#split = 'train'
#split = 'dev'
split = 'test'
times_file = f'/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/trees/{split}.times'
out_file = f'/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/input_features/{split}_sent_ids.txt'

with open(times_file,'r') as f:
    lines = [l.strip() for l in f.readlines()]

ids = []
for line in lines:
    conv,spk,sent,_,_,_ = line.split('\t')
    sent = sent.split('~')[-1]
    sent_id = '_'.join([conv,spk,sent])
    ids.append(sent_id)

with open(out_file,'w') as f:
    for idx in ids:
        f.write(idx)
        f.write('\n')
    

