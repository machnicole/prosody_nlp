import os
import pickle
from PYEVALB import scorer
import tempfile
import string

def sort_subturns(subturns):
    i2subturn = {}
    for subturn in subturns:
        i = int(subturn.split(':')[-1])
        i2subturn[i] = subturn
    idxs = sorted(list(i2subturn.keys()))
    return [i2subturn[i] for i in idxs]
                

def tree2str(tree):
    return ' '.join(''.join(ch for ch in tree if not ch.isupper()).replace('(','').replace(')','').translate(str.maketrans('', '', string.punctuation)).strip().split())

def load_lines(filename):
    with open(filename,'r') as f:
        lines = f.readlines()
    return [l.strip() for l in lines]

data = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed/seg'
out = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/code/self_attn_speech_parser/output/turn_pause_dur_fixed/seg'

sent2turn = pickle.load(open(os.path.join(data,'..','..','sent2turn.pickle'),'rb'))
turn2sent = pickle.load(open(os.path.join(data,'..','..','turn2sent.pickle'),'rb'))

id_file = os.path.join(data,'dev_nonsp_sent_ids_for_parser.txt')
pred_tree_file = os.path.join(out,'nonsp_glove_72240_dev=73.31.pt_parsed.txt')
gold_id_file = os.path.join(data,'..','turn_dev_sent_ids_medium.txt')
gold_tree_file = os.path.join(data,'..','turn_dev_medium.trees')

subturn_ids = load_lines(id_file)
pred_trees = load_lines(pred_tree_file)
turn_ids = load_lines(gold_id_file)
gold_trees = load_lines(gold_tree_file)
turn2gold = dict(zip(turn_ids,gold_trees))

print(len(subturn_ids))
print(len(pred_trees))
assert len(subturn_ids)==len(pred_trees)

subturn2predtree = dict(zip(subturn_ids,pred_trees))

turn2subturn = {}
for subturn in subturn_ids:
    try:
        turn,_ = subturn.split(':')
    except:
        import pdb;pdb.set_trace()
    if turn in turn2subturn:
        turn2subturn[turn].append(subturn)
    else:
        turn2subturn[turn] = [subturn]

#for turn in turn2subturn:
#    turn2subturn[turn] = sorted(turn2subturn[turn])
    
temp_dir = tempfile.TemporaryDirectory(prefix="evalb-")
predicted_path = os.path.join(temp_dir.name,'pred.txt')
output_path = os.path.join(temp_dir.name,'out.txt')

with open(predicted_path,'w') as f:
    for turn in turn_ids:
        subturns = sort_subturns(turn2subturn[turn])
        trees = [subturn2predtree[subturn] for subturn in subturns]
        out_tree = '(TURN '+' '.join(trees)+')'
        outstr = tree2str(out_tree)
        goldstr = tree2str(turn2gold[turn])
        try:
            assert outstr==goldstr
        except:
            import pdb;pdb.set_trace()
        
        f.write(out_tree)
        f.write('\n')

scr = scorer.Scorer()
scr.evalb(gold_tree_file,predicted_path,output_path)
import pdb;pdb.set_trace()
