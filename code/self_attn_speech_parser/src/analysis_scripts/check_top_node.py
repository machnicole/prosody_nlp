import trees
import os


treefile = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/sentence_pause_dur_fixed/dev.trees'
idfile = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/sentence_pause_dur_fixed/dev_sent_ids.txt'

trees,ids = trees.load_trees_with_idx(treefile,idfile)

lbl2count = {}

for idnum,tree in zip(ids,trees):
    lbl = tree.label
    if lbl in lbl2count:
        lbl2count[lbl] += 1
    else:
        lbl2count[lbl] = 1

print("lbl2count")        
print(lbl2count)

output = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/code/self_attn_speech_parser/output/turn_pause_dur_fixed'
nonsp = os.path.join(output,"turn_medium_nonsp_glove_72240_dev=86.82.pt_turn_dev_predicted.txt")
sp = os.path.join(output,"turn_medium_sp_glove_ab_duration_72240_dev=91.32.pt_turn_dev_predicted.txt")

nonsp = open(nonsp,'r').read()
sp = open(sp,'r').read()

nonsp_parens = nonsp.count('(') + nonsp.count(')')
sp_parens = sp.count('(') + sp.count(')')


print("nonsp_parens",nonsp_parens)
print("sp_parens",sp_parens)

nonsp_S = nonsp.count('(S')
sp_S = sp.count('(S')


print("nonsp_S",nonsp_S)
print("sp_S",sp_S)

import pdb;pdb.set_trace()
