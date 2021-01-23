"""
Do preproc necessary to report F1 scores by sentence length
"""
import os
import trees
import numpy as np
import tempfile
from PYEVALB import scorer

data_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed/'
results_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/code/self_attn_speech_parser/output/turn_pause_dur_fixed'
output_dir = os.path.join(results_dir,'length_eval')
gold_file = os.path.join(data_dir,'turn_dev_medium.trees')
sp_file = os.path.join(results_dir,'turn_medium_sp_glove_72240_dev=91.38.pt_turn_dev_predicted.txt')
nonsp_file = os.path.join(results_dir,'turn_medium_nonsp_glove_72240_dev=86.82.pt_turn_dev_predicted.txt')
gold_id_file = os.path.join(data_dir,'turn_dev_sent_ids_medium.txt')

gold_trees,ids = trees.load_trees_with_idx(gold_file,gold_id_file)
nonsp_trees,ids = trees.load_trees_with_idx(nonsp_file,gold_id_file)
sp_trees,ids = trees.load_trees_with_idx(sp_file,gold_id_file)

id2goldtree = dict(zip(ids,gold_trees))
id2nonsptree = dict(zip(ids,nonsp_trees))
id2sptree = dict(zip(ids,sp_trees))

lens = []
for tree in gold_trees:
    lens.append(len(list(tree.leaves())))

median = np.quantile(np.array(lens),0.5)
lower_med = np.quantile(np.array(lens),0.25)
upper_med = np.quantile(np.array(lens),0.75)


lower_half = []
upper_half = []
q1 = []
q2 = []
q3 = []
q4 = []
for id_num,tree in zip(ids,gold_trees):
    tree_len = len(list(tree.leaves()))
    if tree_len < median:
        lower_half.append(id_num)
        if tree_len <= lower_med: # Have to change this so that you don't get zero things in q1
            q1.append(id_num)
        else:
            q2.append(id_num)
    else:
        upper_half.append(id_num)
        if tree_len < upper_med:
            q3.append(id_num)
        else:
            q4.append(id_num)


quant2lst = {'q1':q1,
           'q2':q2,
           'q3':q3,
           'q4':q4,
           'lower_half':lower_half,
           'upper_half':upper_half}

temp_dir = tempfile.TemporaryDirectory(prefix="evalb-")
gold_path = os.path.join(temp_dir.name, "gold.txt")
nonsp_path = os.path.join(temp_dir.name, "nonsp.txt")
sp_path = os.path.join(temp_dir.name, "sp.txt")

for quant in ('q1','q2','q3','q4','lower_half','upper_half'):
    with open(gold_path,'w') as goldf:
        with open(nonsp_path,'w') as nonspf:
            with open(sp_path,'w') as spf:
                for idnum in quant2lst[quant]:
                    goldf.write(id2goldtree[idnum].linearize())
                    goldf.write('\n')
                    nonspf.write(id2nonsptree[idnum].linearize())
                    nonspf.write('\n')
                    spf.write(id2sptree[idnum].linearize())
                    spf.write('\n')
           
        sp_output = os.path.join(output_dir, f'{quant}_sp_output.txt')
        nonsp_output = os.path.join(output_dir, f'{quant}_nonsp_output.txt')
        scr = scorer.Scorer()
        scr.evalb(gold_path,sp_path,sp_output)
        scr.evalb(gold_path,nonsp_path,nonsp_output)        
temp_dir.cleanup()

    
            
import pdb;pdb.set_trace()


