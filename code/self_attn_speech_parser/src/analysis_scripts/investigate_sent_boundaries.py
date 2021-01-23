import trees
import os

outdir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/code/self_attn_speech_parser/output/turn_pause_dur_fixed'
datadir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed'
pros_f = os.path.join(outdir,'turn_medium_sp_glove_72240_dev=91.38.pt_turn_dev_predicted.txt')
nonpros_f = os.path.join(outdir,'turn_medium_nonsp_glove_72240_dev=86.82.pt_turn_dev_predicted.txt')
gold_f = os.path.join(datadir,'turn_dev_medium.trees')

turn_ids_file = os.path.join(datadir,'turn_dev_sent_ids.txt')
turn_ids = [l.strip() for l in open(turn_ids_file).readlines()]
singlesent_turn_ids = set([l.strip() for l in open(os.path.join(datadir,'singlesent_turns_dev_sent_ids.txt')).readlines()])
multisent_turn_ids = set([l.strip() for l in open(os.path.join(datadir,'multisent_turns_dev_sent_ids.txt')).readlines()])

pros_trees, pros_ids = trees.load_trees_with_idx(pros_f,turn_ids_file,strip_top=True)
nonpros_trees, nonpros_ids = trees.load_trees_with_idx(nonpros_f,turn_ids_file,strip_top=True)
gold_trees, gold_ids = trees.load_trees_with_idx(gold_f,turn_ids_file,strip_top=True)

id2prostree = dict(zip(pros_ids,pros_trees))
id2nonprostree = dict(zip(nonpros_ids,nonpros_trees))
id2goldtree = dict(zip(gold_ids,gold_trees))

tree_dict = {'pros':id2prostree,
             'nonpros':id2nonprostree}

oversplit = {'pros':[],
             'nonpros':[]}
undersplit = {'pros':[],
              'nonpros':[]}

multiutt_disf = {'gold':[],
              'pros':[],
              'nonpros':[]}              

lens = {'gold':0,
        'pros':0,
        'nonpros':0}
num_sents_gold = 0
num_sents_pros = 0
num_sents_nonpros = 0

for tree_id in gold_ids:
    gold = id2goldtree[tree_id]
    pros = id2prostree[tree_id]
    nonpros = id2nonprostree[tree_id]    
    lens['gold'] = len(gold.children)
    lens['pros'] = len(pros.children)
    lens['nonpros'] = len(nonpros.children)
    treestr = id2goldtree[tree_id].linearize()
    ####### addition: look for multi-utt turns with disfluencies for paper ##############
    if 'EDITED' in treestr and len(gold.children)==len(pros.children) and not len(gold.children)==len(nonpros.children):
        if len(gold.children) > 1: multiutt_disf['gold'].append(tree_id)
        if len(pros.children) > 1: multiutt_disf['pros'].append(tree_id)
        if len(nonpros.children) > 1: multiutt_disf['nonpros'].append(tree_id)
    #####################################################################################
    num_sents_gold += len(gold.children)
    num_sents_pros += len(pros.children)
    num_sents_nonpros += len(nonpros.children)    
    for model in ('pros','nonpros'):
        if lens[model] > lens['gold']:
            oversplit[model].append(tree_id)
        elif lens[model] < lens['gold']:
            undersplit[model].append(tree_id)

#############################################################################
with open(os.path.join(outdir,'mulitutt_disf_gold.txt'),'w') as fgold:
    with open(os.path.join(outdir,'mulitutt_disf_pros.txt'),'w') as fpros:
        with open(os.path.join(outdir,'mulitutt_disf_nonpros.txt'),'w') as fnonpros:
            for treeid in multiutt_disf['gold']:
                fgold.write(id2goldtree[treeid].linearize()+'\n')
                fpros.write(id2prostree[treeid].linearize()+'\n')
                fnonpros.write(id2nonprostree[treeid].linearize()+'\n')                
                
            
#############################################################################

            
for model in ('pros','nonpros'):
    print(f'MODEL: {model}')
    correct_num_sents_correct_split_loc = 0
    correct_num_sents_incorrect_split_loc = 0    
    incorrect_num_sents_correct_split_loc = 0
    incorrect_num_sents_incorrect_split_loc = 0    

    print(f'under:\t\t{len(undersplit[model])}')
    print(f'over:\t\t{len(oversplit[model])}')
    print(f'correct num:\t{len(gold_ids) - len(undersplit[model]) - len(oversplit[model])}')
    id2predtree = tree_dict[model]
    # Now check the correct num ones to see if they split in the correct *place*
    for tree_id in gold_ids:
        pred = id2predtree[tree_id]
        gold = id2goldtree[tree_id]
        gold_num_sents = len(gold.children)
        pred_num_sents = len(pred.children)

        if not tree_id in oversplit[model] and not tree_id in undersplit[model]:
            pred_leaves = []
            gold_leaves = []
            for i in range(gold_num_sents):
                pred_leaves.extend([leaf for leaf in pred.children[i].leaves()])
                gold_leaves.extend([leaf for leaf in gold.children[i].leaves()])
            if gold_num_sents > 1:
                if len(pred_leaves)==len(gold_leaves):
                    correct_num_sents_correct_split_loc += 1
                else:
                    correct_num_sents_incorrect_split_loc += 1
        elif not gold_num_sents==1 and not pred_num_sents==1:
            pred_leaves = []
            gold_leaves = []
            pred_break_idxs = set()
            gold_break_idxs = set()         
            for i in range(pred_num_sents-1):
                pred_leaves.extend([leaf for leaf in pred.children[i].leaves()])
                pred_break_idxs.add(len(pred_leaves))
            for i in range(gold_num_sents-1):
                gold_leaves.extend([leaf for leaf in gold.children[i].leaves()]) 
                gold_break_idxs.add(len(gold_leaves))
            incorrect_num_sents_correct_split_loc += len(pred_break_idxs.intersection(gold_break_idxs))
            incorrect_num_sents_incorrect_split_loc += len(pred_break_idxs-gold_break_idxs)        

    print('For turns where the correct num of sents was predicted:')                        
    print(f'{model}: {correct_num_sents_correct_split_loc} correct splits')
    print(f'{model}: {correct_num_sents_incorrect_split_loc} incorrect splits')

    print('For turns where the INcorrect num of sents was predicted:')
    print(f'{model}: {incorrect_num_sents_correct_split_loc} correct splits')
    print(f'{model}: {incorrect_num_sents_incorrect_split_loc} incorrect splits')

import pdb;pdb.set_trace()

# Quick add-on: create subsets of turns with incorrect split nums from nonpros model
# This is so that I can see if the Berkeley analyzed errors correlate with incorrect sentence splits

nonpros_incorrect = []
with open(os.path.join(outdir,'tmp_badsplit_gold.txt'),'w') as fgold:
    with open(os.path.join(outdir,'tmp_badsplit_nonpros.txt'),'w') as fnonpros:
        for idnum in gold_ids:
            if idnum in oversplit['nonpros'] or idnum in undersplit['pros']:
                fgold.write(id2goldtree[idnum].linearize())
                fgold.write('\n')
                fnonpros.write(id2nonprostree[idnum].linearize())
                fnonpros.write('\n')






