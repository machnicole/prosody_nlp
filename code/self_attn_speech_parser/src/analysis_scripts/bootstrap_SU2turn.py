from PYEVALB import scorer
import itertools
import random
import os
import pickle
import time
from bootstrap_resample import get_p_value
import tempfile
import string

def tree2str(tree):
    return ' '.join(''.join(ch for ch in tree if not ch.isupper()).replace('(','').replace(')','').translate(str.maketrans('', '', string.punctuation)).strip().split())


def su2turn(su_f,id_f,turn2su_f,turn_ids,su2turn_out,turn2gold):
    sus = [l.strip() for l in open(su_f).readlines()]
    ids = [l.strip() for l in open(id_f).readlines()]
    id2su = dict(zip(ids,sus))
    turn_id2su_ids = pickle.load(open(turn2su_f,'rb'))

    with open(su2turn_out,'w') as f:
        for turn in turn_ids:
            su_ids = turn_id2su_ids[turn]
            sus = [id2su[su_id] for su_id in su_ids]
            joined_sus = ' '.join(sus)
            turn_tree = f'(TURN {joined_sus})'
            try:
                assert tree2str(turn_tree)==tree2str(turn2gold[turn])
            except:
                print(turn_tree)
                print(turn2gold[turn])
                import pdb;pdb.set_trace()
            f.write(turn_tree)
            f.write('\n')
        


# Paths:
output_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/code/self_attn_speech_parser/output/turn_pause_dur_fixed'
data_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed'

# Gold turn files:
gold_f = os.path.join(data_dir,'gold.txt')
gold_id_f = os.path.join(data_dir,'turn_dev_sent_ids_medium.txt')

gold_lines = [l.strip() for l in open(gold_f).readlines()]
turn_ids = [l.strip() for l in open(gold_id_f).readlines()]
turn2gold = dict(zip(turn_ids,gold_lines))

# Pred turn files:
turn_f = os.path.join(output_dir,'turn_sp_correct_eval_72240_dev=90.90.pt_dev_predicted.txt')

# Pred SU files:
su_f = os.path.join(output_dir,'..','sentence_pause_dur_fixed','sp_glove_72240_dev=91.10.pt_dev_predicted_evalb.txt')
su_id_f = os.path.join(data_dir,'..','sentence_pause_dur_fixed','dev_sent_ids.txt')
turn2sent_f = os.path.join(data_dir,'..','turn2sent.pickle')
temp_dir = tempfile.TemporaryDirectory(prefix="evalb-")
su2turn_out = os.path.join(temp_dir.name,'su2turn.txt')

su2turn(su_f,su_id_f,turn2sent_f,turn_ids,su2turn_out,turn2gold)

get_p_value(su2turn_out,gold_f,turn_f,turn_ids)
