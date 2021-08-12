import pickle
import os
from prep_input_dicts import times2frames,norm_energy_by_side
import numpy as np

# 0. Set paths
# data_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/'
# data_dir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features'
data_dir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features'
# sent_dir = os.path.join(data_dir,'sentence_pause_dur_fixed')
sent_dir = data_dir
# turn_dir = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_eng_turns"
turn_dir = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_ger_turns"

# kaldi_feat_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/kaldi_feats/'
# kaldi_feat_dir = '/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_eng_kaldi_output'
kaldi_feat_dir = '/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_ger_kaldi_output'

fbank_dir = os.path.join(kaldi_feat_dir,'vm_fbank_energy')
pitchpov_dir = os.path.join(kaldi_feat_dir,'vm_pitch_pov')

split = 'train'
# split = 'dev'
# split = 'test'
#
# 1. Load intermediate dict files that are potentially helpful
print('Loading helper dicts ...')
sent2pw = pickle.load(open(os.path.join(data_dir,f'sent2pw.pickle'),'rb'))
sent2term = pickle.load(open(os.path.join(data_dir,f'sent2term.pickle'),'rb'))
#term2pw = pickle.load(open(os.path.join(data_dir,f'term2pw.pickle'),'rb'))
turn2sent = pickle.load(open(os.path.join(data_dir,f'turn2sent.pickle'),'rb'))
sent2turn = pickle.load(open(os.path.join(data_dir,f'sent2turn.pickle'),'rb'))
term2feats = pickle.load(open(os.path.join(data_dir,f'term2feats.pickle'),'rb'))
#pw2feats = pickle.load(open(os.path.join(data_dir,f'pw2feats.pickle'),'rb'))


# 2. Files for the parser that are split into train/dev/test
print('Loading sentence-based dicts ...')
sent2part = pickle.load(open(os.path.join(sent_dir,f'{split}_partition.pickle'),'rb'))
# sent2dur = pickle.load(open(os.path.join(sent_dir,f'{split}_duration.pickle'),'rb'))
# sent2rawdur = pickle.load(open(os.path.join(sent_dir,f'{split}_raw_duration.pickle'),'rb'))
# sent2fbankenergy = pickle.load(open(os.path.join(sent_dir,f'{split}_fbank.pickle'),'rb'))
# sent2pitchpov= pickle.load(open(os.path.join(sent_dir,f'{split}_pitch.pickle'),'rb'))
sent2pause = pickle.load(open(os.path.join(sent_dir,f'{split}_pause.pickle'),'rb'))
with open(os.path.join(sent_dir,f'{split}_sent_ids.txt'),'r') as f:
    sent_ids = [l.strip() for l in f.readlines()]
with open(os.path.join(sent_dir, "new_trees", f'{split}.trees'),'r') as f:
    trees = [l.strip() for l in f.readlines()]

sent2tree = dict(zip(sent_ids,trees))

# 3. Create dicts that are turn based:
turn2part = {}
turn2dur = {}
turn2fbank = {}
turn2pitch = {}
turn2pause = {}
turn2tree = {}

sent_ids = sorted(list(sent2part.keys()))
# print(sent_ids)
# print("cd42_00_2306" in sent2part)
print('Sorting turns ...')
# 4. Separate turns where turn=sent from others
def sort_turns(turn2sent,sent2part):
    multisent_turns = []
    singlesent_turns = []
    single_sents = []
    for turn in turn2sent:
        sents = turn2sent[turn]
        sents_exist = True
        for sent in sents:
            if not sent in sent2part:
                sents_exist = False
            # if sent == "cd42_00_2306":
                # print(sents_exist)
        if sents_exist:
            if len(turn2sent[turn]) > 1:
                multisent_turns.append(turn)
            elif len(turn2sent[turn]) == 1:
                singlesent_turns.append(turn)
                single_sents.extend(turn2sent[turn])
    multisent_turns = sorted(multisent_turns)
    singlesent_turns = sorted(singlesent_turns)
    single_sents = sorted(single_sents)
    return multisent_turns,singlesent_turns,single_sents

multisent_turns,singlesent_turns,single_sents = sort_turns(turn2sent,sent2part)


# 5. For turns where turn=sent, just copy the sent data to a turn-based dict.
print('Copying over single-sentence turns ...')
for sent in single_sents:
    turn = sent2turn[sent]
    turn2part[turn] = sent2part[sent]
    # turn2dur[turn] = sent2dur[sent]

    # turn2dur[turn] = sent2dur[sent].reshape(1, -1)
    #
    # print(turn2dur[turn].shape)

    turn2pause[turn] = sent2pause[sent]
    # turn2pitch[turn] = sent2pitchpov[sent]
    # turn2fbank[turn] = sent2fbankenergy[sent]
    # #turn2tree[turn] = f'(TURN {sent2tree[sent] })'
    # tr = sent2tree[sent].replace('(TOP','')[:-1]
    tr = sent2tree[sent].replace('(TOP', '(SU')
    # tr = sent2tree[sent]
    turn2tree[turn] = '(TOP (TURN '+tr+'))'


# 6. Where there are 2+ sents per turn, create new feats for turn
print('Handling multi-sentence turns ...')
for turn in multisent_turns:
    # print(turn)
    sents = turn2sent[turn]

    # conv,spk,_ = sents[0].split('_')
    
    # 6a. Create features you can concatenate from sent features
    pauses = {'pause_bef':[],
              'pause_aft':[]}
    parts = []
    durs = []
    rawdurs = []
    curr_trees = ['(TOP (TURN']
    for sent in sents:
        pauses['pause_bef'].extend(sent2pause[sent]['pause_bef'])
        pauses['pause_aft'].extend(sent2pause[sent]['pause_aft'])
        # parts.extend(sent2part[sent])
        # tree_no_top = sent2tree[sent].replace('(TOP','')[:-1]
        # tree_no_top = sent2tree[sent]
        tree_no_top =sent2tree[sent].replace('(TOP', '(SU')
        curr_trees.append(tree_no_top)
        # durs.append(sent2dur[sent])
    curr_trees.append(') )')
    turn2pause[turn] = pauses
    turn2part[turn] = parts
    turn2tree[turn] = ' '.join(curr_trees)

    # turn2dur[turn] = np.concatenate(np.array(durs)).reshape(1,-1)
    # print(turn2dur[turn].shape)

    # Duration:
    # recompute norm by max in turn so that it's normed by max in turn, not utterance
    # normed_by_mean = np.concatenate([dur[0:1] for dur in durs],axis=1) # these are the same -- copy them over.
    # raw_durs = np.concatenate([np.array(sent2rawdur[sent]) for sent in sents])
    # print(raw_durs)
    # normed_by_max = np.expand_dims(raw_durs/np.max(raw_durs),axis=0)
    # print(normed_by_max)
    # print(np.max(raw_durs))


    # turn2dur[turn] = np.concatenate([normed_by_mean,normed_by_max],axis=0)

    # print(turn2dur[turn].shape)

    # 6b. Create features you have to recalculate
    # ssent = sents[0]
    # esent = sents[-1]
    # # it shouldn't matter which sent_id.pickle file we load here
    # # because all sent_ids have the same recording, i.e. the same features
    # # Pitch:
    # pitch_dict = pickle.load(open(os.path.join(kaldi_feat_dir,'vm_pitch_pov',f'{sents[0]}.pickle'),'rb'))
    # pitch_data = np.transpose(np.array(pitch_dict[list(pitch_dict.keys())[0]]))
    #
    # audio_len = pitch_data.shape[-1] - 1
    # stime = term2feats[sent2term[ssent][0]]['start']
    # etime = term2feats[sent2term[esent][-1]]['end']
    # sframe,eframe = times2frames(stime,etime,audio_len)
    # turn_pitch = pitch_data[:,sframe:eframe]
    # turn2pitch[turn] = turn_pitch
    # fbank_data = pickle.load(open(os.path.join(kaldi_feat_dir,'vm_fbank_energy','normed_fbanks',f'{sents[0]}.pickle'),'rb'))
    # turn_fbank = fbank_data[:,sframe:eframe]
    # turn2fbank[turn] = turn_fbank



# 7. Save all these to pickle files
print('Pickling ...')
# pickle.dump(turn2dur,open(os.path.join(turn_dir,f'turn_{split}_duration.pickle'),'wb'))
# pickle.dump(turn2pitch,open(os.path.join(turn_dir,f'turn_{split}_pitch.pickle'),'wb'))
# pickle.dump(turn2pause,open(os.path.join(turn_dir,f'turn_{split}_pause.pickle'),'wb'))
# pickle.dump(turn2part,open(os.path.join(turn_dir,f'turn_{split}_partition.pickle'),'wb'))
# pickle.dump(turn2fbank,open(os.path.join(turn_dir,f'turn_{split}_fbank.pickle'),'wb'))
#
with open(os.path.join(turn_dir,f'turn_{split}_sent_ids_top.txt'),'w') as f_id:
    with open(os.path.join(turn_dir,f'turn_{split}_top.trees'),'w') as f_tree:
        for turn in turn2tree:
            f_id.write(f'{turn}\n')
            f_tree.write(f'{turn2tree[turn]}\n')
#
# # 8. Write subsets of turn ids and trees as well:
# print(f'Making turn subsets of {split} ...')
# with open(os.path.join(turn_dir,f'multisent_turns_{split}_sent_ids.txt'),'w') as f_id:
#     with open(os.path.join(turn_dir,f'multisent_turns_{split}.trees'),'w') as f_tree:
#         for turn in multisent_turns:
#             f_id.write(f'{turn}\n')
#             f_tree.write(f'{turn2tree[turn]}\n')
#
# with open(os.path.join(turn_dir,f'singlesent_turns_{split}_sent_ids.txt'),'w') as f_id:
#     with open(os.path.join(turn_dir,f'singlesent_turns_{split}.trees'),'w') as f_tree:
#         for turn in singlesent_turns:
#             f_id.write(f'{turn}\n')
#             f_tree.write(f'{turn2tree[turn]}\n')
#
# # 9. Write sent subsets of sent ids and trees:
# print(f'Making sent subsets of {split} ...')
# with open(os.path.join(sent_dir,f'multisent_{split}_sent_ids.txt'),'w') as f_id_multi:
#     with open(os.path.join(sent_dir,f'multisent_{split}.trees'),'w') as f_tree_multi:
#         with open(os.path.join(sent_dir,f'singlesent_{split}_sent_ids.txt'),'w') as f_id_sing:
#             with open(os.path.join(sent_dir,f'singlesent_{split}.trees'),'w') as f_tree_sing:
#                 for sent in sent_ids:
#                     if sent in single_sents:
#                         f_id_sing.write(sent+'\n')
#                         f_tree_sing.write(sent2tree[sent]+'\n')
#                     else:
#                         f_id_multi.write(sent+'\n')
#                         f_tree_multi.write(sent2tree[sent]+'\n')
#
#
#
# print('Done.')
#
