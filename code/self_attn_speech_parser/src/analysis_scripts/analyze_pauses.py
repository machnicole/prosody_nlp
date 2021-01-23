import os
import pickle

pause_file = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/sentence/train_pause.pickle'

sent2pause = pickle.load(open(pause_file,'rb'))

for sent in sent2pause:
    bef = sent2pause[sent]['pause_bef']
    aft = sent2pause[sent]['pause_aft']
    assert len(bef)==len(aft)
    if len(bef)>1:
        try:
            assert bef[1:]==aft[:-1]
            print('passed assert')
        except:
            print('failed assert')
            print(f'bef: {bef}')
            print(f'aft: {aft}')
            import pdb;pdb.set_trace()
        

