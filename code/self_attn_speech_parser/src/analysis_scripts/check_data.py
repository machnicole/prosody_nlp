import pickle
import os
import trees

#data_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/input_features'
#tree_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/trees'
data_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features'
tree_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/trees'

split = 'turn_train'

dur_file = os.path.join(data_dir,f'{split}_duration.pickle')
part_file =  os.path.join(data_dir,f'{split}_partition.pickle')
pitch_file =  os.path.join(data_dir,f'{split}_pitch.pickle')
fbank_file =  os.path.join(data_dir,f'{split}_fbank.pickle')
pause_file =  os.path.join(data_dir,f'{split}_pause.pickle')

#tree_file =  os.path.join(tree_dir,f'{split}.trees')
tree_file =  os.path.join(data_dir,f'{split}.trees')
#time_file =  os.path.join(tree_dir,f'{split}.times')

dur_dict = pickle.load(open(dur_file,'rb'))
part_dict = pickle.load(open(part_file,'rb'))
pitch_dict = pickle.load(open(pitch_file,'rb'))
fbank_dict = pickle.load(open(fbank_file,'rb'))
pause_dict = pickle.load(open(pause_file,'rb'))

with open(tree_file) as f:
    tree_lines = [l.strip() for l in f.readlines()]
    

"""
sent_ids = []
with open(time_file) as f:
    lines = f.readlines()
    for i,line in enumerate(lines):
        conv,spk,sent,_,_,_ = line.split('\t')
        sent = sent.split('~')[-1]
        id_num = '_'.join([conv,spk,sent])
        sent_ids.append(id_num)
"""

id_file = os.path.join(data_dir,f'{split}_sent_ids.txt')
with open(id_file,'r') as f:
    sent_ids = [l.strip() for l in f.readlines()]
sent_ids = sorted(sent_ids)

tree_dict = {}
loaded_trees,tree_ids = trees.load_trees_with_idx(tree_file, id_file)
for tree_id,tree in zip(tree_ids,loaded_trees):
    tree_dict[tree_id] = [(leaf.tag, leaf.word) for leaf in tree.leaves()]


    
for sent in sent_ids:
    print(sent)
    if sent in dur_dict:
        dur = dur_dict[sent]
        part = part_dict[sent]
        pitch = pitch_dict[sent]
        fbank = fbank_dict[sent]
        pause = pause_dict[sent]
        tree = tree_dict[sent]
        tree_wds = len(tree)
        dur_wds = dur.shape[-1]
        if not tree_wds == dur_wds:
            print(sent)
            print(tree)
            import pdb;pdb.set_trace()
    else:
        print('sent not in dur_dict')
        import pdb;pdb.set_trace()
