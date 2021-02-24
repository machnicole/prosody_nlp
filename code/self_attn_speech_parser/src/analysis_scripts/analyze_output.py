import os
import trees
import pickle
"""
Analyze where the parser puts sentence breaks, relative to certain prosodic feature
or alternatively, relative to certain constitents.

Current hypothesis:
The parser likely splits sentences 
- After lower f0 feats
- At pauses > cat1
- Possibly at the end of EDITED constituents (which also coincide with longer pauses)
"""





output_dir = "/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/code/self_attn_speech_parser/output/turn_pause_dur_fixed"
turndir = "/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed"
datadir = "/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features"
#pred_tree_file = os.path.join(output_dir,"turn_nonsp_correct_eval_72240_dev=86.09.pt_dev_predicted.txt")
#pred_tree_file = os.path.join(output_dir,"turn_sp_correct_eval_72240_dev=90.90.pt_dev_predicted.txt")
#pred_tree_file = os.path.join(output_dir,"turn_dur_only_correct_eval_72240_dev=86.24.pt_dev_predicted.txt")
#pred_tree_file = os.path.join(output_dir,"turn_fbank_only_correct_eval_72240_dev=90.29.pt_dev_predicted.txt")
#pred_tree_file = os.path.join(output_dir,"turn_pause_only_correct_eval_72240_dev=86.21.pt_dev_predicted.txt")
pred_tree_file = os.path.join(output_dir,"turn_pitch_only_correct_eval_72240_dev=90.71.pt_dev_predicted.txt")

gold_tree_file = os.path.join(turndir,'turn_dev_medium.trees')
id_file = os.path.join(turndir,'turn_dev_sent_ids_medium.txt')


turn2part = pickle.load(open(os.path.join(turndir,'turn_dev_partition.pickle'),'rb'))
turn2pitch = pickle.load(open(os.path.join(turndir,'turn_dev_pitch.pickle'),'rb'))
turn2fbank = pickle.load(open(os.path.join(turndir,'turn_dev_fbank.pickle'),'rb'))
turn2pause = pickle.load(open(os.path.join(turndir,'turn_dev_pause.pickle'),'rb'))
turn2dur = pickle.load(open(os.path.join(turndir,'turn_dev_duration.pickle'),'rb'))
turn_ids = [l.strip() for l in open(os.path.join(turndir,'turn_dev_sent_ids_medium.txt'),'r').readlines()]
turn_trees = [l.strip() for l in open(os.path.join(turndir,'turn_dev_medium.trees'),'r').readlines()]
sent2turn = pickle.load(open(os.path.join(datadir,'sent2turn.pickle'),'rb'))
turn2sent = pickle.load(open(os.path.join(datadir,'turn2sent.pickle'),'rb'))


treestrings = [l.strip() for l in open(pred_tree_file).readlines()]
tree_list,ids = trees.load_trees_with_idx(pred_tree_file,id_file)
turn2tree = dict(zip(ids,tree_list))
turn2treestring = dict(zip(ids,treestrings))



def get_wd_len(constituent):
    leaves = 0
    for leaf in constituent.leaves():
        leaves += 1
    return leaves

def get_sent_break_idx(tree):
    if len(tree.children) == 1:
        return False
    else:
        idxs = []
        for i,child in enumerate(tree.children):
            left_leaf_len = sum([get_wd_len(tree.children[j]) for j in range(i+1)])
            idxs.append(left_leaf_len-1)
        return idxs

def get_break_pauses(idx,pauses):
    aft = pauses['pause_aft']
    break_pauses = [aft[i] for i in idx]
    return break_pauses

def count_pauses(pauses):
    pause_counts = {}
    for pause in pauses:
        if pause in pause_counts:
            pause_counts[pause] += 1
        else:
            pause_counts[pause] = 1
    return pause_counts

def count_leaves(constituent):
    constituent = constituent.replace('(','').replace(')','').replace('£','').replace('$','')
    constituent = ''.join(ch for ch in constituent if not ch.isupper())
    return len(constituent.split())


def get_edit_idxs(tree):
    num_leaves = len(list(tree.leaves()))
    tree_string = tree.linearize()
    
    if 'EDITED' in tree_string:
        pre_edit_idx = []
        post_edit_idx = []

        tree_string = tree_string.replace('EDITED','£')
        for i,char in enumerate(tree_string):
            if char == '£':
                prefix = tree_string[:i]
                pre_edit_idx.append(count_leaves(prefix)-1)
                edited_span = []
                open_paren_stack = ['(']
                j = 1
                while open_paren_stack:
                    next_char = tree_string[i+j]
                    edited_span.append(next_char)
                    if next_char == '(':
                        open_paren_stack.append('(')
                    elif next_char == ')':
                        open_paren_stack.pop()
                    j += 1
                
                edited_span = ''.join(edited_span)
                post_edit_idx.append(count_leaves(prefix)+count_leaves(edited_span)-1)
        return pre_edit_idx,post_edit_idx
    return None

def intersection_size(lst1, lst2):
    return len(list(set(lst1) & set(lst2)))

def main():
    pred_trees,ids = trees.load_trees_with_idx(pred_tree_file,id_file)
    gold_trees,ids = trees.load_trees_with_idx(gold_tree_file,id_file)

    turn_med_breaks = 0
    sent_break_pauses = []

    pre_edit_breaks = 0
    post_edit_breaks = 0

    total_turn_medial_positions = 0 # number of positions between words that sentence breaks could go. sum(len(turn)-1) over all turns
    
    total_pred_breaks = 0
    total_gold_edits = 0
    
    for i,tree in enumerate(pred_trees):
        total_turn_medial_positions += (get_wd_len(tree)-1)
        break_idxs = get_sent_break_idx(tree)
        gold_edit_idxs = get_edit_idxs(gold_trees[i])
        if gold_edit_idxs: total_gold_edits += len(gold_edit_idxs[0])
        if break_idxs:
            total_pred_breaks += len(break_idxs)-1
            turn_id = ids[i]
            sent_break_pauses.extend(get_break_pauses(break_idxs[:-1],turn2pause[turn_id])) #Q: what pauses happen at sent breaks?
            turn_med_breaks += len(break_idxs[:-1])
        if gold_edit_idxs and break_idxs:
            pre_edit_idxs = gold_edit_idxs[0]
            post_edit_idxs = gold_edit_idxs[1]

            pre_edit_breaks += intersection_size(pre_edit_idxs,break_idxs)
            post_edit_breaks += intersection_size(post_edit_idxs,break_idxs)


    pause_counts = count_pauses(sent_break_pauses)
    print(pred_tree_file.split('/')[-1])
    print('Pauses at turn-internal sentence breaks:')
    print(pause_counts)
    print(f'Turn-medial breaks: {turn_med_breaks}')
    print(f'Total edits: {total_gold_edits}')
    print(f'Predicted breaks pre-edits: {pre_edit_breaks}')
    print(f'Predicted breaks post-edit: {post_edit_breaks}')
    print(f'Total turn medial positions: {total_turn_medial_positions}')


if __name__=='__main__':
    main()
