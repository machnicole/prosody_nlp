import trees
import numpy as np

tree_file = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/sentence_pause_dur_fixed/dev.trees'
id_file = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/sentence_pause_dur_fixed/dev_sent_ids.txt'

trees,ids = trees.load_trees_with_idx(tree_file,id_file)

lens = []

for tree in trees:
    leaves = 0
    for leaf in tree.leaves():
        leaves += 1
    lens.append(leaves)

print(f'mean: {sum(lens)/len(lens)}')
print(f'median: {np.median(np.array(lens))}')

