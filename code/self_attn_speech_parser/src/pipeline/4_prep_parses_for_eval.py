import os
import pickle
from PYEVALB import scorer
import tempfile
import string

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

id_file = os.path.join(data,'dev_sent_ids_for_parser.txt')

pred_tree_file = os.path.join(out,'sp_glove_72240_dev=99.71.pt_parsed.txt')
gold_id_file = os.path.join(data,'..','turn_dev_sent_ids_medium.txt')
gold_tree_file = os.path.join(data,'..','turn_dev_medium.trees')

pred_ids = load_lines(id_file)
pred_trees = load_lines(pred_tree_file)
gold_ids = load_lines(gold_id_file)
gold_trees = load_lines(gold_tree_file)

print(f'ids {len(pred_ids)}')
print(f'trees {len(pred_trees)}')
assert len(pred_ids)==len(pred_trees)


modsent2pred = dict(zip(pred_ids,pred_trees))
turn2gold = dict(zip(gold_ids,gold_trees))

## debug' ###
#pre_parsed_file = os.path.join(data,'dev_for_parser.trees')
#preparsed_trees = load_lines(pre_parsed_file)
#for idnum,pre,pred in zip(pred_ids,preparsed_trees,pred_trees):
#    if not tree2str(pre)==tree2str(pred):
#        print(tree2str(pre))
#        print(tree2str(pred))
#        import pdb;pdb.set_trace()
#######################

modsent2turn = {}
turn2modsent = {}
for modsent in pred_ids:
    if modsent in sent2turn:
        turn = sent2turn[modsent]
        modsent2turn[modsent] = turn
        if turn in turn2modsent:
            turn2modsent[turn].append(modsent)
        else:
            turn2modsent[turn] = [modsent]
    elif ':' in modsent:
        print(modsent)
        sent_id = modsent.split(':')[0]
        turn = sent2turn[sent_id]
        modsent2turn[modsent] = turn
        if turn in turn2modsent:
            turn2modsent[turn].append(modsent)
        else:
            turn2modsent[turn] = [modsent]

    elif '+' in modsent:
        sent_id = modsent.split('+')[0]
        turn = sent2turn[sent_id]
        modsent2turn[modsent] = turn
        if turn in turn2modsent:
            turn2modsent[turn].append(modsent)
        else:
            turn2modsent[turn] = [modsent] 

for turn in turn2modsent:
    turn2modsent[turn] = sorted(turn2modsent[turn])
        
pred2turntree = {}
for turn in gold_ids:
    modsents = turn2modsent[turn]
    if len(modsents)==1:
        pred = f'(TURN {modsent2pred[modsents[0]]})'
        pred2turntree[turn] = pred
    if len(modsents) > 1:
        pred = f'(TURN {" ".join([modsent2pred[sent] for sent in modsents])})'
        pred2turntree[turn] = pred



#trn = sent2turn['sw4877_B_0134']
#print(trn)
#print(turn2modsent[trn])
#import pdb;pdb.set_trace()
import string
for turn in pred2turntree:

    pred = tree2str(pred2turntree[turn])
    gold = tree2str(turn2gold[turn])
    if not pred==gold:
        print(pred)
        print('---')
        print(gold)
        import pdb;pdb.set_trace()
                
 

temp_dir = tempfile.TemporaryDirectory(prefix="evalb-")
predicted_path = os.path.join(temp_dir.name,'pred.txt')
output_path = os.path.join(temp_dir.name,'out.txt')

with open(predicted_path,'w') as f:
    for turn in gold_ids:
        f.write(pred2turntree[turn])
        f.write('\n')

scr = scorer.Scorer()
scr.evalb(gold_tree_file,predicted_path,output_path)
import pdb;pdb.set_trace()
temp_dir.cleanup()
