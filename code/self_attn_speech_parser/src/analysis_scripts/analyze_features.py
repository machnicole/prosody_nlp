import pickle
import os
import numpy as np
import trees
import re
from statsmodels.stats import weightstats as stests
from scipy.stats import ttest_ind

datadir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/'
sentdir = os.path.join(datadir,'sentence_pause_dur_fixed')
turndir = os.path.join(datadir,'turn_pause_dur_fixed')


sent2part = pickle.load(open(os.path.join(sentdir,'train_partition.pickle'),'rb'))
sent2pitch = pickle.load(open(os.path.join(sentdir,'train_pitch.pickle'),'rb'))
sent2fbank = pickle.load(open(os.path.join(sentdir,'train_fbank.pickle'),'rb'))
sent2pause = pickle.load(open(os.path.join(sentdir,'train_pause.pickle'),'rb'))
sent2dur = pickle.load(open(os.path.join(sentdir,'train_duration.pickle'),'rb'))
sent_treestrings = [l.strip() for l in open(os.path.join(sentdir,'train.trees'),'r').readlines()]
sent_trees,sent_ids = trees.load_trees_with_idx(os.path.join(sentdir,'train.trees'),os.path.join(sentdir,'train_sent_ids.txt'))
sent2tree = dict(zip(sent_ids,sent_trees))
sent2treestring = dict(zip(sent_ids,sent_treestrings))

turn2part = pickle.load(open(os.path.join(turndir,'turn_train_partition.pickle'),'rb'))
turn2pitch = pickle.load(open(os.path.join(turndir,'turn_train_pitch.pickle'),'rb'))
turn2fbank = pickle.load(open(os.path.join(turndir,'turn_train_fbank.pickle'),'rb'))
turn2pause = pickle.load(open(os.path.join(turndir,'turn_train_pause.pickle'),'rb'))
turn2dur = pickle.load(open(os.path.join(turndir,'turn_train_duration.pickle'),'rb'))
turn_ids = [l.strip() for l in open(os.path.join(turndir,'turn_train_sent_ids.txt'),'r').readlines()]
turn_trees = [l.strip() for l in open(os.path.join(turndir,'turn_train.trees'),'r').readlines()]
sent2turn = pickle.load(open(os.path.join(datadir,'sent2turn.pickle'),'rb'))
turn2sent = pickle.load(open(os.path.join(datadir,'turn2sent.pickle'),'rb'))

turn_medial_sents = []
for turn in turn2sent:
    turn_medial_sents.extend(turn2sent[turn][:-1])

def cnn_feat_ttest(pitch1,pitch2):
    ttest_p1 ,pval_p1 = ttest_ind(pitch1[0], pitch2[0],equal_var=False)
    ttest_p2 ,pval_p2 = ttest_ind(pitch1[1], pitch2[1],equal_var=False)
    ttest_p3 ,pval_p3 = ttest_ind(pitch1[2], pitch2[2],equal_var=False)
    print(f'p_1 ttest,pval: {ttest_p1},{pval_p1}')
    print(f'p_2 ttest,pval: {ttest_p2},{pval_p2}')
    print(f'p_3 ttest,pval: {ttest_p3},{pval_p3}')

def dur_ttest(dur1,dur2):
    ttest_d1 ,pval_d1 = ttest_ind(dur1[0], dur2[0],equal_var=False)
    ttest_d2 ,pval_d2 = ttest_ind(dur1[1], dur2[1],equal_var=False)
    print(f'd_1 ttest,pval: {ttest_d1},{pval_d1}')
    print(f'd_2 ttest,pval: {ttest_d2},{pval_d2}')

    
def count_leaves(constituent):
    constituent = constituent.replace('(','').replace(')','').replace('£','').replace('$','')
    constituent = ''.join(ch for ch in constituent if not ch.isupper())
    #print(f'LEN OF: {constituent}')
    return len(constituent.split())

def treestring2strings(treestring):
    s = treestring.replace('(','').replace(')','')
    s = ''.join(ch for ch in s if not ch.isupper())
    s = s.split()
    return s

do_ttest = False

# 1: FEATURES at sentence/turn boundaries




# 1.1: Define everything you want to fill in

# pitch
sentfinal_tok_pitch = []
nonsentfinal_tok_pitch = []
all_tok_pitch = []
turnfinal_tok_pitch = []
nonturnfinal_tok_pitch = []

# intensity (fbank)
sentfinal_tok_fbank = []
nonsentfinal_tok_fbank = []
all_tok_fbank = []
turnfinal_tok_fbank = []
nonturnfinal_tok_fbank = []

# duration
sentfinal_dur = []
nonsentfinal_dur = []
all_dur = []
turnfinal_dur = []
nonturnfinal_dur = []

# pause
cat = 1 # Pause category to investigate
total_pauses = 0
total_cats = 0 # Use the turn version to find these, so you don't double count the end/beginning of a sentence
turn_final_cats = 0
turnfinal_pause = len(turn2pause)
sentfinal_pause = 0
midsent_pause = 0
sentfinal_cats = 0
total_per_cat = {0:0,1:0,2:0,3:0,4:0,5:0,6:0}

# words
sent_final_wds = []

# 1.2: go through each speech unit of interest

# sentences
for sent in sent2pitch:
    part = sent2part[sent]
    pitch = sent2pitch[sent]
    fbank = sent2fbank[sent]
    dur = sent2dur[sent]

    all_tok_pitch.append(pitch)
    sentfinal_tok_pitch.append(pitch[:,part[-1][0]:part[-1][-1]])
    nonsentfinal_tok_pitch.append(pitch[:,0:part[-1][0]])

    all_tok_fbank.append(fbank)
    sentfinal_tok_fbank.append(fbank[:,part[-1][0]:part[-1][-1]])
    nonsentfinal_tok_fbank.append(fbank[:,0:part[-1][0]])

    all_dur.append(dur)
    sentfinal_dur.append(np.expand_dims(dur[:,-1],axis=1))
    nonsentfinal_dur.append(dur[:,:-1])

    tree_string = sent2treestring[sent]
    tree = sent2tree[sent]
    num_leaves = len(list(tree.leaves()))
    midsent_pause += num_leaves
    sentfinal_pause += 1
    all_pauses = [sent2pause[sent]['pause_bef'][0]]+sent2pause[sent]['pause_aft']
    if all_pauses[-1] == cat:
        sentfinal_cats += 1

    wds = treestring2strings(tree_string)
    sent_final_wds.append(wds[-1])

                         
# turns
for turn in turn2pitch:
    part = turn2part[turn]
    pitch = turn2pitch[turn]
    fbank = turn2fbank[turn]
    dur = turn2dur[turn]
    
    turnfinal_tok_pitch.append(pitch[:,part[-1][0]:part[-1][-1]])
    nonturnfinal_tok_pitch.append(pitch[:,0:part[-1][0]])

    turnfinal_tok_fbank.append(fbank[:,part[-1][0]:part[-1][-1]])
    nonturnfinal_tok_fbank.append(fbank[:,0:part[-1][0]])

    turnfinal_dur.append(np.expand_dims(dur[:,-1],axis=1))
    nonturnfinal_dur.append(dur[:,:-1])

    all_pauses = [turn2pause[turn]['pause_bef'][0]]+turn2pause[turn]['pause_aft']
    if all_pauses[-1] == cat:
        turn_final_cats += 1
    for category in total_per_cat:
        total_per_cat[category] += np.sum(np.array(all_pauses)==category)
    total_cats += np.sum(np.array(all_pauses)==cat)
    total_pauses += len(all_pauses)


    
# turn-medial sents
turn_medial_final_tok_pitch = []
turn_medial_dur = []
for sent in turn_medial_sents:
    if sent in sent2pitch:
        pitch = sent2pitch[sent]
        part = sent2part[sent]
        dur = sent2dur[sent]
        
        turn_medial_final_tok_pitch.append(pitch[:,part[-1][0]:part[-1][-1]])
        turn_medial_dur.append(np.expand_dims(dur[:,-1],axis=1))

# 1.3 Concatenate and mean all the features

all_tok_pitch = np.concatenate(all_tok_pitch,axis=1)
sentfinal_tok_pitch = np.concatenate(sentfinal_tok_pitch,axis=1)
nonsentfinal_tok_pitch = np.concatenate(nonsentfinal_tok_pitch,axis=1)                              

avg_pitch = np.mean(all_tok_pitch,axis=1)
avg_sentfinal_pitch = np.mean(sentfinal_tok_pitch,axis=1)
avg_nonsentfinal_pitch = np.mean(nonsentfinal_tok_pitch,axis=1)

all_dur = np.concatenate(all_dur,axis=1)
sentfinal_dur = np.concatenate(sentfinal_dur,axis=1)

nonsentfinal_dur = np.concatenate(nonsentfinal_dur,axis=1)
avg_dur = np.mean(all_dur,axis=1)
avg_sentfinal_dur = np.mean(sentfinal_dur,axis=1)
avg_nonsentfinal_dur = np.mean(nonsentfinal_dur,axis=1)

turnfinal_tok_pitch = np.concatenate(turnfinal_tok_pitch,axis=1)
nonturnfinal_tok_pitch = np.concatenate(nonturnfinal_tok_pitch,axis=1)                              

avg_turnfinal_pitch = np.mean(turnfinal_tok_pitch,axis=1)
avg_nonturnfinal_pitch = np.mean(nonturnfinal_tok_pitch,axis=1)

turnfinal_dur = np.concatenate(turnfinal_dur,axis=1)
nonturnfinal_dur = np.concatenate(nonturnfinal_dur,axis=1)
avg_turnfinal_dur = np.mean(turnfinal_dur,axis=1)
avg_nonturnfinal_dur = np.mean(nonturnfinal_dur,axis=1)

       
turn_medial_final_tok_pitch = np.concatenate(turn_medial_final_tok_pitch,axis=1)
avg_turn_medial_final_pitch = np.mean(turn_medial_final_tok_pitch,axis=1)

turn_medial_dur = np.concatenate(turn_medial_dur,axis=1)
avg_turn_medial_dur = np.mean(turn_medial_dur,axis=1)

all_tok_fbank = np.concatenate(all_tok_fbank,axis=1)
sentfinal_tok_fbank = np.concatenate(sentfinal_tok_fbank,axis=1)
nonsentfinal_tok_fbank = np.concatenate(nonsentfinal_tok_fbank,axis=1)                              
avg_fbank = np.mean(all_tok_fbank,axis=1)
avg_sentfinal_fbank = np.mean(sentfinal_tok_fbank,axis=1)
avg_nonsentfinal_fbank = np.mean(nonsentfinal_tok_fbank,axis=1)


print('FBANK')
print(f'avg_fbank: {avg_fbank}')
print(f'avg_sentfinal_fbank: {avg_sentfinal_fbank}')
print(f'avg_nonsentfinal_fbank: {avg_nonsentfinal_fbank}')


    

print()
print('DUR')
print(f'avg_dur: {avg_dur}')
print(f'avg_nonsentfinal_dur: {avg_nonsentfinal_dur}')
print(f'avg_sentfinal_dur: {avg_sentfinal_dur}')
print(f'avg_turnfinal_dur: {avg_turnfinal_dur}')
print(f'avg_turn_medial_dur: {avg_turn_medial_dur}')

if do_ttest:
    print('ttest sentfinal dur vs nonsentfinal dur')
    dur_ttest(sentfinal_dur,nonsentfinal_dur)
    print('ttest turn medial/sentfinal dur vs nonsentfinal dur')
    dur_ttest(turn_medial_dur,nonsentfinal_dur)

print()
print('PITCH')
print(f'avg_pitch: {avg_pitch}')
print(f'avg_sentfinal_pitch: {avg_sentfinal_pitch}')
print(f'avg_nonsentfinal_pitch: {avg_nonsentfinal_pitch}')
print(f'avg_turnfinal_pitch: {avg_turnfinal_pitch}')
print(f'avg_nonturnfinal_pitch: {avg_nonturnfinal_pitch}')
print(f'avg_turn_medial_sent_final_pitch: {avg_turn_medial_final_pitch}')
print()
print('PAUSE')
print(f'cat: {cat}')
print(f'all cats: {total_cats}')
print(f'sent final cats: {sentfinal_cats}')
print(f'turn final cats: {turn_final_cats}')
print(f'all pauses: {total_pauses}')
print(f'midsent pauses: {midsent_pause}')        
print(f'sentfinal pause: {sentfinal_pause}')
print(f'total turn final: {turnfinal_pause}')



if do_ttest:
    print('ttests for turn medial vs turn final pitch')
    cnn_feat_ttest(turn_medial_final_tok_pitch,turnfinal_tok_pitch)
    print('ttests for turn medial/sent final vs all sentence medial pitch')
    cnn_feat_ttest(turn_medial_final_tok_pitch,nonsentfinal_tok_pitch)
    ttestfbank_p1 ,pvalfbank_p1 = ttest_ind(all_tok_fbank[0], sentfinal_tok_fbank[0],equal_var=False)
    ttestfbank_p2 ,pvalfbank_p2 = ttest_ind(all_tok_fbank[1], sentfinal_tok_fbank[1],equal_var=False)
    ttestfbank_p3 ,pvalfbank_p3 = ttest_ind(all_tok_fbank[2], sentfinal_tok_fbank[2],equal_var=False)

    print(f'final fbank ttests:')
    print(f'p_1 ttest,pval: {ttestfbank_p1},{pvalfbank_p1}')
    print(f'p_2 ttest,pval: {ttestfbank_p2},{pvalfbank_p2}')
    print(f'p_3 ttest,pval: {ttestfbank_p3},{pvalfbank_p3}')
    print('ttests for all toks vs sentfinal toks')
    cnn_feat_ttest(all_tok_pitch,sentfinal_tok_pitch)
    print('ttests for all nonturnfinal vs turnfinal toks')
    cnn_feat_ttest(turnfinal_tok_pitch,nonturnfinal_tok_pitch)
    print('ttests for all turnfinal vs sentfinal toks')
    cnn_feat_ttest(turnfinal_tok_pitch,sentfinal_tok_pitch)



# 2: Features around edits

total_edits = 0

pre_EDIT_cats = 0
post_EDIT_cats = 0

edit_final_pitches = []
non_edit_final_pitches = []
edit_final_intensities = []
non_edit_final_intensities = []
edit_final_durs = []
non_edit_final_durs = []

pre_edit_wds = []
all_wds = []

for sent in sent2pause:
    tree_string = sent2treestring[sent]
    tree = sent2tree[sent]
    num_leaves = len(list(tree.leaves()))
    all_pauses = [sent2pause[sent]['pause_bef'][0]]+sent2pause[sent]['pause_aft']
    if all_pauses[-1] == cat:
        sentfinal_cats += 1
    wds = treestring2strings(tree_string)
    all_wds.extend(wds)
        
    if 'EDITED' in tree_string:
        if 'UH' in tree_string:
            print(tree_string)
            import pdb;pdb.set_trace()
        pre_edit_idx = []
        post_edit_idx = []
        edit_final_idx = []
        tree_string = tree_string.replace('EDITED','£')
        for i,char in enumerate(tree_string):
            if char == '£':
                total_edits += 1
                prefix = tree_string[:i]
                pre_edit_idx.append(count_leaves(prefix))
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
                post_edit_idx.append(count_leaves(prefix)+count_leaves(edited_span))
                edit_final_idx.append(count_leaves(prefix)+count_leaves(edited_span)-1)

        for ed in pre_edit_idx:
            if all_pauses[ed] == cat:
                pre_EDIT_cats += 1
        for ed in post_edit_idx:
            pre_edit_wds.append(wds[ed-1])
            if all_pauses[ed] == cat:
                post_EDIT_cats += 1
        for ed in edit_final_idx:
            part = sent2part[sent][ed]
            pitch = sent2pitch[sent][:,part[0]:part[1]]
            durs = sent2dur[sent][:,ed]
            intens = sent2fbank[sent][:,part[0]:part[1]]
            if part[0] > 0 and part[1]+1 < sent2pitch[sent].shape[-1]:
                inverse_pitch = np.concatenate([sent2pitch[sent][:,:part[0]],sent2pitch[sent][:,part[1]+1:]],axis=1)
                inverse_dur = np.concatenate([sent2dur[sent][:,:ed],sent2dur[sent][:,ed+1:]],axis=1)
                inverse_intens = np.concatenate([sent2fbank[sent][:,:part[0]],sent2fbank[sent][:,part[1]+1:]],axis=1)
                
                non_edit_final_pitches.append(inverse_pitch)
                non_edit_final_intensities.append(inverse_intens)
                non_edit_final_durs.append(inverse_dur)

            elif part[0] > 0:
                inverse_pitch = sent2pitch[sent][:,:part[0]]
                inverse_dur = sent2dur[sent][:,:ed]
                inverse_intens = sent2fbank[sent][:,:part[0]]

                
                non_edit_final_pitches.append(inverse_pitch)
                non_edit_final_intensities.append(inverse_intens)
                non_edit_final_durs.append(inverse_dur)

            elif  part[1]+1 < sent2pitch[sent].shape[-1]:
                inverse_pitch = sent2pitch[sent][:,part[1]+1:]
                inverse_dur = sent2dur[sent][:,ed+1:]
                inverse_intens = sent2fbank[sent][:,part[1]+1:]

                
                non_edit_final_pitches.append(inverse_pitch)
                non_edit_final_intensities.append(inverse_intens)
                non_edit_final_durs.append(inverse_dur)


            edit_final_pitches.append(pitch)
            edit_final_intensities.append(intens)
            edit_final_durs.append(np.expand_dims(durs,axis=1))


edit_final_pitches = np.concatenate(edit_final_pitches,axis=1)
edit_final_intensities = np.concatenate(edit_final_intensities,axis=1)
edit_final_durs = np.concatenate(edit_final_durs,axis=1)


non_edit_final_pitches = np.concatenate(non_edit_final_pitches,axis=1)
non_edit_final_intensities = np.concatenate(non_edit_final_intensities,axis=1)
non_edit_final_durs = np.concatenate(non_edit_final_durs,axis=1)




print(f'total edits: {total_edits}')                

print(f'Mean pitch edit-final pitch feats: {np.mean(edit_final_pitches,axis=1)}')
print(f'Mean pitch edit-final intensity feats: {np.mean(edit_final_intensities,axis=1)}')
print(f'Mean pitch edit-final dur feats: {np.mean(edit_final_durs,axis=1)}')

print(f'Mean pitch non_edit-final pitch feats: {np.mean(non_edit_final_pitches,axis=1)}')
print(f'Mean pitch non_edit-final intensity feats: {np.mean(non_edit_final_intensities,axis=1)}')
print(f'Mean pitch non_edit-final dur feats: {np.mean(non_edit_final_durs,axis=1)}')

if do_ttest:
    print('ttest, non_edit_final pitches vs edit_final_pitches')
    cnn_feat_ttest(non_edit_final_pitches,edit_final_pitches)
    print('ttest, non_edit_final_intensities vs edit_final_intensities')
    cnn_feat_ttest(non_edit_final_intensities,edit_final_intensities)
    print('ttest, non_edit_final_dur vs edit_final_dur')
    dur_ttest(non_edit_final_durs,edit_final_durs)

print('ttest, sent_final_dur vs edit_final_dur')
dur_ttest(sentfinal_dur,edit_final_durs)
print('ttest, sent_final_pitch vs edit_final_pitch')
cnn_feat_ttest(sentfinal_tok_pitch,edit_final_pitches)
print('ttest, turn_medial,sent_final_pitch vs edit_final_pitch')
cnn_feat_ttest(turn_medial_final_tok_pitch,edit_final_pitches)

print('ttest, sent_final_fbank vs edit_final_fbank')
cnn_feat_ttest(sentfinal_tok_fbank,edit_final_intensities)

if do_ttest:
    print('edit-final durs vs sent-final durs significance')
    dur_ttest(edit_final_durs,sentfinal_dur)
    print('edit-final durs vs turn-med,sent-final durs significance')
    dur_ttest(edit_final_durs,turn_medial_dur)


print(f'pre edit cats: {pre_EDIT_cats}')
print(f'post edit cats: {post_EDIT_cats}')
print('-'*50)
for cat in total_per_cat:
    print(f'total {cat}: {total_per_cat[cat]}')



import nltk
from nltk.corpus import stopwords

stp = stopwords.words('english')

pre_edit_stopwords = [wd for wd in pre_edit_wds if wd in stp]
sent_final_stopwords = [wd for wd in sent_final_wds if wd in stp]
all_stopwords = [wd for wd in all_wds if wd in stp]

print(f'{len(pre_edit_stopwords)/len(pre_edit_wds)} percent of edit-final wds are stopwords')
print(f'{len(sent_final_stopwords)/len(sent_final_wds)} percent of sent-final wds are stopwords')
print(f'{len(all_stopwords)/len(all_wds)} percent of all wds are stopwords')
