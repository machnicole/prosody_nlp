import os
import pickle
import numpy as np
import trees
import math

data = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed/seg'
out = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/code/self_attn_speech_parser/output/turn_pause_dur_fixed/seg'

def load_lines(filename):
    return [l.strip() for l in open(filename,'r').readlines()]

def load_pickle(filename):
    with open(filename,'rb') as f:
        return pickle.load(f)

SPEECH = True
    
golds = load_lines(os.path.join(data,'turn_dev.lbl'))
if SPEECH:
    preds = load_lines(os.path.join(out,'turn_sp_seg_72240_dev=99.71.pt_turn_dev_predicted.txt'))
else:
    preds = load_lines(os.path.join(out,'turn_nonsp_seg_72240_dev=73.31.pt_turn_dev_predicted.txt'))
    
ids = load_lines(os.path.join(data,'turn_dev.ids'))
turn2sent = load_pickle(os.path.join(data,'..','..','turn2sent.pickle'))

### STEP 1 #################################################
# correctly segmented turns -> add sent IDS to list
# incorrectly segmented turns 
#    -> combine sent ids and add to list
#    -> split sent ids and add to list
############################################################

tree_file = os.path.join(data,'..','..','sentence_pause_dur_fixed','dev.trees')
id_file =  os.path.join(data,'..','..','sentence_pause_dur_fixed','dev_sent_ids.txt')

treebank, all_sents = trees.load_trees_with_idx(tree_file,id_file) # EKN trees get loaded in as trees here
id2senttree = dict(zip(all_sents,treebank))


wrong_turn_ids = []
usable_sent_ids = []
for idnum,gold,pred in zip(ids,golds,preds):
    if gold==pred:
        usable_sent_ids.extend(turn2sent[idnum])
    else:
        g_list = np.array([int(i) for i in gold.split()])
        p_list = np.array([int(i) for i in pred.split()])
        if np.sum(g_list) > np.sum(p_list):
            print(f'{idnum}: UNDERSEG')
            sents = turn2sent[idnum]
            idx = 0
            curr_sent = ''
            for g,p in zip(g_list,p_list):
                if g==1 and p==0:
                    curr_sent = curr_sent+sents[idx]+':'
                    idx += 1
                elif g==1 and p==1:
                    usable_sent_ids.append(curr_sent+sents[idx])
                    curr_sent = ''
                    idx += 1
            if curr_sent:
                usable_sent_ids.append(curr_sent+sents[-1])
        elif np.sum(g_list) < np.sum(p_list):
            print(f'{idnum}: OVERSEG')
            idx = 0
            sents = turn2sent[idnum]
            subsent = 0
            unfinished_split = 0
            wd_idx = 0
            first_idx = 0
            for g,p in zip(g_list,p_list):

                if g==0 and p==1:
                    usable_sent_ids.append(f'{sents[idx]}+0+{wd_idx-first_idx+1}')
                    subsent += 1
                    unfinished_split = wd_idx-first_idx
                    #first_idx = wd_idx + 1
                elif g==1 and p==1:
                    if unfinished_split != 0:
                        usable_sent_ids.append(f'{sents[idx]}+{unfinished_split+1}+{wd_idx-first_idx+1}')
                        subsent += 1
                    usable_sent_ids.append(sents[idx])
                    idx += 1
                    unfinished_split = 0
                    first_idx = wd_idx+1
                elif g==0 and p==0:
                    pass
                else:
                    print('SOMETHING HAS GONE WRONG')
                    
                    import pdb;pdb.set_trace()
                wd_idx += 1
            if unfinished_split:
                usable_sent_ids.append(f'{sents[idx]}+{unfinished_split+1}+{wd_idx-first_idx}')
        else:
            print(f'{idnum}: wrongseg')

usable_sent_ids = set(usable_sent_ids)



##### STEP 2 ##############################
# Put sent ids and words into new files
###########################################


outid2tree = {}
for idnum in id2senttree:
    if idnum in usable_sent_ids:
        outid2tree[idnum] = id2senttree[idnum].linearize()
        usable_sent_ids.remove(idnum)

for idnum in usable_sent_ids:
    if ':' in idnum:
        curr_sents = idnum.split(':')
        trees = [id2senttree[sent].linearize() for sent in curr_sents]
        new_tree = '(TURN '+' '.join(trees)+')'
        outid2tree[idnum] = new_tree
    if '+' in idnum:
        original_id,start,end = idnum.split('+')
        start = int(start)
        end = int(end)
        wds = [leaf.word for leaf in id2senttree[original_id].leaves()]
        tags = [leaf.tag for leaf in id2senttree[original_id].leaves()]
        curr_wds = wds[start:end]
        curr_tags = tags[start:end]
        new_tree = '(TURN '+' '.join([f'({tag} {wd})' for tag,wd in zip(curr_tags,curr_wds)])+')'
        # Note: this is a dummy tree just to get the parser to parse the sentence;
        # we'll use the real turn for eval.
        outid2tree[idnum] = new_tree


##### STEP 3 ##############################
# Remake acoustic features
###########################################

if SPEECH:
    feats = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/sentence_pause_dur_fixed'
    outfeats = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed/seg'
    kaldi_feats = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/kaldi_feats/'
    sent2pause = pickle.load(open(os.path.join(feats,'dev_pause.pickle'),'rb'))
    sent2part = pickle.load(open(os.path.join(feats,'dev_partition.pickle'),'rb'))
    sent2dur = pickle.load(open(os.path.join(feats,'dev_duration.pickle'),'rb'))
    sent2fbank = pickle.load(open(os.path.join(feats,'dev_fbank.pickle'),'rb'))
    sent2pitch = pickle.load(open(os.path.join(feats,'dev_pitch.pickle'),'rb'))
    sent2term = pickle.load(open(os.path.join(feats,'..','sent2term.pickle'),'rb'))
    term2feats = pickle.load(open(os.path.join(feats,'..',f'term2feats.pickle'),'rb'))

    newsent2pause = {}
    newsent2dur = {}
    newsent2pitch = {}
    newsent2fbank = {}
    newsent2part = {}

    def times2frames(stime,etime,audio_len):
        sframe = max(0,math.floor(stime*100))
        eframe = min(math.ceil(etime*100),audio_len)
        return sframe,eframe


    for idnum in outid2tree:
        if idnum in id2senttree:
            newsent2pause[idnum] = sent2pause[idnum]
            newsent2part[idnum] = sent2part[idnum]
            newsent2pitch[idnum] = sent2pitch[idnum]
            newsent2dur[idnum] = sent2dur[idnum]
            newsent2fbank[idnum] = sent2fbank[idnum]
        elif ':' in idnum:
            sents = idnum.split(':')
        
            durs = [sent2dur[sent] for sent in sents]
            newsent2dur[idnum] = np.concatenate(durs,axis=1)

            parts = []
            pauses = {'pause_bef':[],
                      'pause_aft':[]}

            for sent in sents:
                parts.extend(sent2part[sent])
                pauses['pause_bef'].extend(sent2pause[sent]['pause_bef'])
                pauses['pause_aft'].extend(sent2pause[sent]['pause_aft'])
            
            newsent2pause[idnum] = pauses
            newsent2part[idnum] = parts

            ssent = sents[0]
            esent = sents[-1]
            # Pitch:

            conv,spk,_ = sent.split('_')

            pitch_dict = pickle.load(open(os.path.join(kaldi_feats,'swbd_pitch_pov',f'{conv}-{spk}.pickle'),'rb'))
            pitch_data = np.transpose(np.array(pitch_dict[list(pitch_dict.keys())[0]]))
        
            audio_len = pitch_data.shape[-1] - 1

            stime = term2feats[sent2term[ssent][0]]['start']
            etime = term2feats[sent2term[esent][-1]]['end']
            sframe,eframe = times2frames(stime,etime,audio_len)

            curr_pitch = pitch_data[:,sframe:eframe]
            newsent2pitch[idnum] = curr_pitch
        
            fbank_data = pickle.load(open(os.path.join(kaldi_feats,'swbd_fbank_energy','normed_fbanks',f'{conv}-{spk}.pickle'),'rb'))
            curr_fbank = fbank_data[:,sframe:eframe]
            newsent2fbank[idnum] = curr_fbank

            assert curr_fbank.shape[-1]==curr_pitch.shape[-1]
            assert len(parts) == len(pauses['pause_bef'])
            assert len(parts) == len(pauses['pause_aft'])
            assert len(parts) == newsent2dur[idnum].shape[-1]

            
        elif '+' in idnum:
            sent,start,end = idnum.split('+')
            conv,spk,_ = sent.split('_')
        
            start = int(start)
            end = int(end)-1
            terms = sent2term[sent]
            orths = [term2feats[term]['orth'] for term in terms][start:end]

            sterm = terms[start]
            eterm = terms[end]
            sorth = term2feats[sterm]['orth']
            eorth = term2feats[eterm]['orth']

            stime = term2feats[sterm]['start']
            etime = term2feats[eterm]['end']        
            
            pitch_dict = pickle.load(open(os.path.join(kaldi_feats,'swbd_pitch_pov',f'{conv}-{spk}.pickle'),'rb'))
            pitch_data = np.transpose(np.array(pitch_dict[list(pitch_dict.keys())[0]]))

            audio_len = pitch_data.shape[-1] - 1
            sframe,eframe = times2frames(stime,etime,audio_len)
            eframe = eframe
            
            curr_pitch = pitch_data[:,sframe:eframe]
            newsent2pitch[idnum] = curr_pitch
        
            fbank_data = pickle.load(open(os.path.join(kaldi_feats,'swbd_fbank_energy','normed_fbanks',f'{conv}-{spk}.pickle'),'rb'))
            curr_fbank = fbank_data[:,sframe:eframe]
            newsent2fbank[idnum] = curr_fbank

            
            pause_bef = sent2pause[sent]['pause_bef'][start:end+1]
            pause_aft = sent2pause[sent]['pause_aft'][start:end+1]
            newsent2pause[idnum] = {'pause_bef':pause_bef,
                                    'pause_aft':pause_aft}
            
            dur = sent2dur[sent][:,start:end+1]
            newsent2dur[idnum] = dur

            parts = sent2part[sent][start:end+1]
            newsent2part[idnum] = parts

            assert curr_fbank.shape[-1]==curr_pitch.shape[-1]
            assert len(parts) == len(pause_bef)
            assert len(parts) == len(pause_aft)
            assert len(parts) == dur.shape[-1]

            
    ## STEP 4: write all the files #######
    pickle.dump(newsent2fbank,open(os.path.join(outfeats,'dev_fbank.pickle'),'wb'))
    pickle.dump(newsent2pitch,open(os.path.join(outfeats,'dev_pitch.pickle'),'wb'))
    pickle.dump(newsent2pause,open(os.path.join(outfeats,'dev_pause.pickle'),'wb'))
    pickle.dump(newsent2part,open(os.path.join(outfeats,'dev_partition.pickle'),'wb'))
    pickle.dump(newsent2dur,open(os.path.join(outfeats,'dev_duration.pickle'),'wb'))


if SPEECH:
    trees_outfile = 'dev_for_parser.trees'
    ids_outfile = 'dev_sent_ids_for_parser.txt'
else:
    trees_outfile = 'dev_nonsp_for_parser.trees'
    ids_outfile = 'dev_nonsp_sent_ids_for_parser.txt'


with open(os.path.join(outfeats,trees_outfile),'w') as ftree:
    with open(os.path.join(outfeats,ids_outfile),'w') as fid:
        for idnum in outid2tree:
            tree = outid2tree[idnum]
            ftree.write(tree)
            ftree.write('\n')
            fid.write(idnum)
            fid.write('\n')
