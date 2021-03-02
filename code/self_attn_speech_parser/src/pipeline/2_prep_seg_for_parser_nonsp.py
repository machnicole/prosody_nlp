import os
import trees

data = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed/seg'
out = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/code/self_attn_speech_parser/output/turn_pause_dur_fixed/seg'

def load_lines(filename):
    return [l.strip() for l in open(filename,'r').readlines()]

preds = load_lines(os.path.join(out,'turn_nonsp_seg_72240_dev=73.31.pt_turn_dev_predicted.txt'))


tree_file = os.path.join(data,'..','turn_dev_medium.trees')
id_file =  os.path.join(data,'..','turn_dev_sent_ids_medium.txt')

turn_trees,turn_ids = trees.load_trees_with_idx(tree_file,id_file) # EKN trees get loaded in as trees here
id2turntree = dict(zip(turn_ids,turn_trees))

assert len(turn_ids)==len(preds)


subturn2tree = {}
ordered_subturns = []
for turn,pred in zip(turn_ids,preds):
    turn_tree = id2turntree[turn]
    wds = [leaf.word for leaf in turn_tree.leaves()]
    tags = [leaf.tag for leaf in turn_tree.leaves()]
    preds = pred.split()
    assert len(wds) == len(preds)
    
    subturn_wds = []
    subturn_tags = []
    subturn_idx = 0
    turn_len = len(wds)

    counter = 0
    for num,wd,tag in zip(preds,wds,tags):
        if num=='0' and counter != turn_len-1:
            subturn_wds.append(wd)
            subturn_tags.append(tag)
        else:
            subturn_wds.append(wd)
            subturn_tags.append(tag)            
            subturn_tree = '(S '+' '.join([f'({tag} {w})' for w,tag in zip(subturn_wds,subturn_tags)])+')'
            subturn_id = f'{turn}:{subturn_idx}'
            subturn2tree[subturn_id] = subturn_tree
            ordered_subturns.append(subturn_id)

            subturn_wds = []
            subturn_tags = []
            subturn_idx += 1
        counter += 1


out_ids = os.path.join(data,'dev_nonsp_sent_ids_for_parser.txt')
out_trees = os.path.join(data,'dev_nonsp_for_parser.trees')

with open(out_ids,'w') as fids:
    with open(out_trees,'w') as ftrees:
        for subturn in ordered_subturns:
            fids.write(subturn)
            fids.write('\n')
            ftrees.write(subturn2tree[subturn])
            ftrees.write('\n')
    

    
