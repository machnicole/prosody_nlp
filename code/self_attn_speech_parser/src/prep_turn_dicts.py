import pickle
import os
#from prep_input_dicts import load_orth2meandur


#data_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/input_features/'
#kaldi_feat_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/kaldi_feats/'
data_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/'
kaldi_feat_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/kaldi_feats/'
mfcc_dir = os.path.join(kaldi_feat_dir,'swbd_mfcc')
fbank_dir = os.path.join(kaldi_feat_dir,'swbd_fbank_energy')
pitchpov_dir = os.path.join(kaldi_feat_dir,'swbd_pitch_pov')

split = 'train'

# Intermediate dict files that are helpful
sent2pw = pickle.load(open(os.path.join(data_dir,f'sent2pw.pickle'),'rb'))
sent2term = pickle.load(open(os.path.join(data_dir,f'sent2term.pickle'),'rb'))
#term2pw = pickle.load(open(os.path.join(data_dir,f'term2pw.pickle'),'rb'))
turn2sent = pickle.load(open(os.path.join(data_dir,f'turn2sent.pickle'),'rb'))
sent2turn = pickle.load(open(os.path.join(data_dir,f'sent2turn.pickle'),'rb'))
#term2feats = pickle.load(open(os.path.join(data_dir,f'term2feats.pickle'),'rb'))
#pw2feats = pickle.load(open(os.path.join(data_dir,f'pw2feats.pickle'),'rb'))

# Files for the parser that are split into train/dev/test
sent2part = pickle.load(open(os.path.join(data_dir,f'{split}_partition.pickle'),'rb'))
sent2dur = pickle.load(open(os.path.join(data_dir,f'{split}_duration.pickle'),'rb'))
#sent2fbankenergy = pickle.load(open(os.path.join(data_dir,f'{split}_mfcc.pickle'),'rb'))
#sent2pitchpov= pickle.load(open(os.path.join(data_dir,f'{split}_fbank.pickle'),'rb'))
sent2pause = pickle.load(open(os.path.join(data_dir,f'{split}_pause.pickle'),'rb'))
with open(os.path.join(data_dir,f'{split}.trees'),'r') as f:
    trees = [l.strip() for l in f.readlines()]

# Files to make for parser that are turn based:
turn2part = {}
turn2dur = {}
turn2fbankenergy = {}
turn2pitchpov = {}
turn2pause = {}
turn_ids = []
turn_trees = []

sent_ids = sorted(list(sent2part.keys()))

def find_multisent_turns(turn2sent):
    multisent_turns = []
    singlesent_turns = []
    single_sents = []
    for turn in turn2sent:
        if len(turn2sent[turn]) > 1:
            multisent_turns.append(turn)
        elif len(turn2sent[turn]) == 1:
            singlesent_turns.append(turn)
            single_sents.extend(turn2sent[turn])
    return multisent_turns,singlesent_turns,single_sents

multisent_turns,singlesent_turns,single_sents = find_multisent_turns(turn2sent)

for sent in single_sents:
    
import pdb;pdb.set_trace()
