import os
import trees

#split = 'train'
#split = 'dev'
split = 'test'

data_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed'
turn_trees = os.path.join(data_dir,f'turn_{split}.trees')
turn_ids = os.path.join(data_dir,f'turn_{split}_sent_ids.txt')

trees, ids = trees.load_trees_with_idx(turn_trees,turn_ids,strip_top=False)

out_trees = []
out_ids = []

## Step 1: print stats on dataset
leaf_lens = []
for tree,id_num in zip(trees,ids):
    leaves = tree.leaves()
    num_leaves = 0
    for leaf in leaves:
        num_leaves += 1
    leaf_lens.append(num_leaves)
    #print(f'{id_num}\t{num_leaves}')
print('-'*50)
print(f'Max len: {max(leaf_lens)}')
print(f'Mean len: {sum(leaf_lens)/len(leaf_lens)}')
for ln in leaf_lens:
    if ln > 270:
        print(ln)


## Step 2: Select subset under a certain len
long_turns = 0
for tree,id_num in zip(trees,ids):
    leaves = tree.leaves()
    num_leaves = 0
    for leaf in leaves:
        num_leaves += 1
    if num_leaves <= 270:
        out_trees.append(tree)
        out_ids.append(id_num)
    else:
        long_turns += 1

## Step 3: Output to new files
out_trees_f = os.path.join(data_dir,f'turn_{split}_medium.trees')
out_ids_f = os.path.join(data_dir,f'turn_{split}_sent_ids_medium.txt')

with open(out_trees_f,'w') as f:
    for tree in out_trees:
        f.write(tree.linearize())
        f.write('\n')
with open(out_ids_f,'w') as f:
    for id_num in out_ids:
        f.write(id_num)
        f.write('\n')
        
print(f'long turns: {long_turns}')

