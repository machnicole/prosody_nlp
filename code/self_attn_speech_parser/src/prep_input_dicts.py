import os
from bs4 import BeautifulSoup
import pickle
import numpy as np
import re
import math
import kaldi_io
import json

def zero_pad_left(instr):

    strlen = len(instr)
    padlen = 4 - strlen
    return ('0'*padlen)+instr

def clean_text(raw_word):
    # from Trang Tran
    word = raw_word.lower()
    word = word.replace("_1", "")
    if '[laughter-' in word:
        word = word.lstrip('[laughter').rstrip(']').lstrip('-')
    if "/" in word and "[" in word and "]" in word:
        word = word.split("/")[-1].replace("]", "")
    if "[" in word:
        word = re.sub(r'\[[^)]*\]','', word)
    if "{" in word and "}" in word:
        word = word.replace("{", "").replace("}", "")
    if word.startswith("'"):
        word = word.lstrip("'")
    return word

tails = ["'ll", "'m", "'re", "'ve", "'s", "'d","n't"]

def make_turn2sent(nxt_dir='/group/corporapublic/switchboard/nxt/xml/'):
    turn_dir = os.path.join(nxt_dir,'turns')
    turn2sent = {}
    sent2turn = {}
    for turnfile in os.listdir(turn_dir):
        conv,spk,_,_ = turnfile.split('.')
        turnf = open(os.path.join(turn_dir,turnfile),'r')
        turnsoup = BeautifulSoup(turnf.read(),'lxml')
        turns = turnsoup.find_all('turn')
        for turn in turns:
            turn_id = '_'.join([conv,spk,turn['nite:id']])
            sent_href = turn.find_all('nite:child')[0]['href']
            sentrange = [int(sid.replace('id(','').replace(')','').replace('s','')) for sid in sent_href.split('#')[-1].split('..')]
            sents = [str(i) for i in range(sentrange[0],sentrange[-1]+1)]
            sent_ids = ['_'.join([conv,spk,zero_pad_left(sent)]) for sent in sents]
            if turn_id in turn2sent:
                turn2sent[turn_id].extend(sent_ids)
            else:
                turn2sent[turn_id] = sent_ids
            for sent in sent_ids:
                sent2turn[sent] = turn_id
    return turn2sent,sent2turn



def make_term2pw_feats(nxt_dir='/group/corporapublic/switchboard/nxt/xml/'):
    term_dir = os.path.join(nxt_dir,'terminals')
    term2pw = {}
    term2feats = {}
    for termfile in os.listdir(term_dir):

        conv,spk,_,_ = termfile.split('.')
        termf = open(os.path.join(term_dir,termfile),'r')
        termsoup = BeautifulSoup(termf.read(),'lxml')
        terms = termsoup.find_all('word')
        
        for term in terms:
            term_id = '_'.join([conv,term['nite:id']])
            orth = clean_text(term['orth'])
            """
            if orth == 'seven' or orth == 'moo' or orth == 'a': # These ones are where the first term is
                # aligned to the whole temporal extent of the phonword, but they nonetheless split it into
                # multiple terms. But all those terms do show up in the parse, so it's probably useful to keep them separate.
                try:
                    swword = term['swword'] 
                    if swword == '747':
                        orth = swword
                    elif swword == '{moogoo}':
                        orth = 'moogoo'
                    elif swword == 'ak-47s':
                        orth = swword
                except:
                    pass

            if orth == 'mumblex':
                orth = clean_text(term['swword'])
                print('MUMBLE:')
                print(orth)
                if orth == 'non-aligned': # Handle special cases:
                    orth = ''
                else:
                    tmp_orth = ''
                    for tail in tails:
                        if orth.endswith(tail):
                            tmp_orth = [orth.replace(tail,''),tail.lstrip("'")]
                    if tmp_orth:
                        orth = tmp_orth
                    print(orth)

            if orth in ['forty-seven', 'goo', 'gues-','noth-','mutt','sca-','cro-','a-a-an','w-w-','take-','-','diff-']: # do non-aligneds that *are* in the orth2meandur dict behave weirdly in this? Prob need to drop this conditional and just look for anything where both times are non-aligned and the swword is nonaligned
                print(orths) 
                try:
                    swword = clean_text(term['swword'])
                    if swword == 'non-aligned' or swword == 'n/a':
                        orth = ''
                except:
                    pass
            """    
            term2feats[term_id] = {'orth':orth}
            if term['nite:start'] == 'n/a' or term['nite:start'] == 'non-aligned': 
                term2feats[term_id]['start'] = -1
            else:
                term2feats[term_id]['start'] = float(term['nite:start'])
            if term['nite:end'] == 'n/a' or term['nite:end'] == 'non-aligned':
                term2feats[term_id]['end'] = -1
            else:
                term2feats[term_id]['end'] = float(term['nite:end'])
            try:
                pw = term.find_all('nite:pointer')[0]['href']
                pw_num = pw.split('(')[-1].split(')')[0]
                pw_id = '_'.join([conv,pw_num])
                term2pw[term_id] = pw_id
            except:
                pass

    return term2pw,term2feats


            
def make_sent2pw_term(term2pw,term2feats,nxt_dir='/group/corporapublic/switchboard/nxt/xml/'):

    syn_dir = os.path.join(nxt_dir,'syntax')
    sent2pw = {}
    sent2term = {}

    for filename in os.listdir(syn_dir):

        conv,spk,_,_ = filename.split('.')
        
        synf = open(os.path.join(syn_dir,filename),'r')
        synsoup = BeautifulSoup(synf.read(),'lxml')
        sents = synsoup.find_all('parse')

        for sent in sents:

            sent_num = zero_pad_left(sent['nite:id'].lstrip('s'))
            sent_id = '_'.join([conv,spk,sent_num])

            terms = sent.find_all('nite:child')
            for term in terms:

                term_num = term['href'].split('(')[-1].split(')')[0]
                term_id = '_'.join([conv,term_num])
                print(term_id)
                if term_id == 'sw3049_s167_23':
                    import pdb;pdb.set_trace()
                else:
                    if term_id in term2feats: # Checks to see if term is in the term dicts, which only contain words (no traces, punc, sil, etc)
                        if sent_id in sent2term:
                            sent2term[sent_id].append(term_id)
                        else:
                            sent2term[sent_id] = [term_id]
                    if term_id in term2pw:
                        pw_id = term2pw[term_id]
                        if sent_id in sent2pw:
                            sent2pw[sent_id].append(pw_id) 
                        else:
                            sent2pw[sent_id] = [pw_id]
    return sent2pw,sent2term

def load_pw2feats(conv,ta_feats_dir,alignment_dir,orth2meandur):
    # Load a dict from phonword to features for a given conversation (both speakers)
    spks = ['A','B']
    pw2feats = {}
    for spk in spks:
        # Load pause and norm feats that are generated by the defunct 'tree alignment' code
        ta_file = f'{conv}{spk}.features'
        ta_path = os.path.join(ta_feats_dir,ta_file)
        with open(ta_path,'rb') as f:
            data = pickle.load(f,encoding='latin1')
            for pw_id in data:
                pw2feats[pw_id] = {'text': data[pw_id]['text'],
                                   'raw_text': data[pw_id]['raw_text'],
                                   'pause_before': data[pw_id]['pause_before'],
                                   'pause_after': data[pw_id]['pause_after'],
                                   'word_norm': data[pw_id]['word_norm'],
                                   'rhyme_norm': data[pw_id]['rhyme_norm']}

        align_file = f'word_times_{conv}{spk}.pickle'
        with open(os.path.join(alignment_dir,align_file),'rb') as f:
            align_dict = pickle.load(f)
        for wd in align_dict:
            pw2feats[wd]['phones'] = align_dict[wd]['phones']
            pw2feats[wd]['start_time'] = align_dict[wd]['start_time']
            pw2feats[wd]['end_time'] = align_dict[wd]['end_time']
            pw2feats[wd]['phone_end_times'] = align_dict[wd]['phone_end_times']
            pw2feats[wd]['phone_start_times'] = align_dict[wd]['phone_start_times']
            #pw2feats[wd]['mean_dur'] = orth2meandur[pw2feats[pw_id]['text']]

    return pw2feats

def get_sents_for_conv(conv,sent_ids):
    return [sent_id for sent_id in sent_ids if conv in sent_id]

def check_valid(timestamp):
    # from Trang Tran
    if timestamp < 0 or np.isnan(timestamp): return False
    return True

def find_bad_alignment(num_list):
    # from Trang Tran
    bad_align = []
    for i in range(len(num_list)):
        if num_list[i] < 0 or np.isnan(num_list[i]): 
            bad_align.append(i)
    return bad_align

def phonebased_dur(pw,pw2feats,phone2meandur):
    phones = pw2feats[pw]['phones']
    dur = 0
    for phone in phones:
        dur += phone2meandur[phone]
    return dur

def clean_up(stimes, etimes, orth2meandur, orths, terms, term2pw,pw2feats,phone2meandur):
    # from Trang Tran, edited
    pws = [term2pw[term] if term in term2pw else None for term in terms ]
    total_raw_time = etimes[-1] - stimes[0]
    """
    for i,orth in enumerate(orths):
        if not orth in orth2meandur: # If this orth isn't in the duration dict ...
            pw = pws[i]
            pw_count = pws.count(pw)
            print(pws)
            phon_len = phonebased_dur(pw,pw2feats,phone2meandur) # ... then retreive its phone-based length ...
            phon_len = phon_len/pw_count # ... divide by num of words mapped to that phonword (hacky but going with it for now)
            orth2meandur[orth] = phon_len
    """

    total_mean_time = sum([orth2meandur[orth] for orth in orths if orth in orth2meandur])#pw_style_orths])
    scale = min(total_raw_time / total_mean_time, 1)

    no_start_idx = find_bad_alignment(stimes)
    no_end_idx = find_bad_alignment(etimes)

    # fix start times first
    for idx in no_start_idx:
        if idx not in no_end_idx:
            # this means the word does have an end time; let's use it
            stimes[idx] = etimes[idx] - scale*orth2meandur[orths[idx]]  #dur_stats[tokens[idx]]['mean']
        else:
            # this means the idx does not s/e times -- just use prev's start 
            stimes[idx] = stimes[idx-1]
            

    # now all start times should be there
    # EKN if there is no good meandur for the token, skip it for now ...
    for idx in no_end_idx:
        if orths[idx] in orth2meandur:
            etimes[idx] = stimes[idx] + scale*orth2meandur[orths[idx]] #dur_stats[tokens[idx]]['mean']
    
    # EKN ... and then go through again and map the unaligneds to the gaps between aligned words
    no_end_idx = find_bad_alignment(etimes)
    for idx in no_end_idx:
        etimes[idx] = stimes[idx+1]
    
    return stimes, etimes


def make_sent2part_and_times(sents,sent2part,sent2times,sent2term,term2pw,pw2feats,orth2meandur,term2feats,phone2meandur):
    
    for sent in sents:
        terms = sent2term[sent]
        stimes = []
        etimes = []
        orths = []
        for term in terms:
            orth = term2feats[term]['orth']
            if type(orth)==str:
                orths.append(orth)
            elif type(orth)==list:
                orths.extend(orth)
                         
        for term in terms:
            if term in term2pw:
                pw_id = term2pw[term]
                st = pw2feats[pw_id]['start_time']
                end = pw2feats[pw_id]['end_time']
                stimes.append(st)
                etimes.append(end)
            else:
                stimes.append(-1)
                etimes.append(-1)

        # This part is from Trang Tran, edited: ############
        if len(stimes)==1:
            if type(orths[0])==str:
                try:
                    first_word_mean_dur = orth2meandur[orths[0]]
                    last_word_mean_dur = orth2meandur[orths[-1]]
                except:
                    if orths[0]=='-':
                        first_word_mean_dur = 0
                    last_word_mean_dur = orth2meandur[orths[-1]]

            else:
                first_word_mean_dur = orth2meandur[orths[0][1]]
                last_word_mean_dur = orth2meandur[orths[-1][0]]
                    
                
            if (not check_valid(stimes[0])) and (not check_valid(etimes[0])):
                print("no time available for sentence", sent)
                continue
            elif not check_valid(stimes[0]):
                stimes[0] = max(etimes[0] - first_word_mean_dur, 0)
            else:
                etimes[0] = stimes[0] + first_word_mean_dur
                 
        if check_valid(stimes[0]): 
            begin = stimes[0]
        else:
            # cases where the first word is unaligned
            if check_valid(etimes[0]): 
                begin = max(etimes[0] - first_word_mean_dur, 0) 
                stimes[0] = begin
            elif check_valid(stimes[1]):
                begin = max(stimes[1] - last_word_mean_dur, 0)
                stimes[0] = begin
            else:
                continue

        if check_valid(etimes[-1]): 
            end = etimes[-1]
        else:
            # cases where the last word is unaligned
            if check_valid(stimes[-1]): 
                end = stimes[-1] + last_word_mean_dur
                etimes[-1] = end
            elif check_valid(etimes[-2]):
                end = etimes[-2] + last_word_mean_dur
                etimes[-1] = end
            else:
                continue
                
        # final clean up
        #print(sent)
        #print(sent2term[sent])
        stimes, etimes = clean_up(stimes, etimes, orth2meandur, orths, sent2term[sent], term2pw,pw2feats,phone2meandur)
        assert len(stimes) == len(etimes) == len(sent2term[sent])
        assert not -1 in stimes
        assert not -1 in etimes

        sent2times[sent] = (stimes,etimes)
        part = []
        for i in range(len(stimes)):
            spart = math.floor((stimes[i]-stimes[0])*100)
            epart = math.ceil((etimes[i]-stimes[0])*100)
            part.append((spart,epart))
        sent2part[sent] = part
        ############
    return sent2part,sent2times


def make_sent2dur(sents,sent2dur,sent2part,sent2times,sent2term,term2pw,pw2feats,orth2freq,term2feats,phone2meandur,orth2meandur):
    for sent in sents:
        raw_durs = []
        mean_durs = []
        stimes,etimes = sent2times[sent]
        terms = sent2term[sent]
        for i,term in enumerate(terms):
            raw_dur = etimes[i]-stimes[i]
            raw_durs.append(raw_dur)
            orth = term2feats[term]['orth']
            if orth in orth2freq:
                if orth2freq[orth] >= 15:
                    mean_durs.append(orth2meandur[orth]) # frequent, in orth2meandur
                else:
                    if term in term2pw:
                        pw = term2pw[term]
                        mean_durs.append(phonebased_dur(pw,pw2feats,phone2meandur)) # infrequent, in orth2meandur
                    else:
                        mean_durs.append(raw_dur)
            else:
                if term in term2pw: # not in orth2meandur but I can find the phones so I'll use those
                    print('term in term2pw but not orth2freq')
                    pw = term2pw[term]
                    mean_durs.append(phonebased_dur(pw,pw2feats,phone2meandur))
                else:
                    print('TODO figure out how to deal with unaligned terms') # not in orth2meandur and don't have the phones
                    mean_durs.append(raw_dur)
        normed_durs = np.expand_dims(np.array([raw_dur/mean_dur for raw_dur,mean_dur in zip(raw_durs,mean_durs)]),axis=0)
        normed_by_max_durs = np.expand_dims(np.array([raw_dur/max(raw_durs) for raw_dur in raw_durs]),axis=0)
        durs = np.concatenate((normed_durs,normed_by_max_durs),axis=0)
        
        sent2dur[sent] = durs
    return sent2dur

def times2frames(stime,etime,audio_len):
    sframe = max(0,math.floor(stime*100))
    eframe = min(math.ceil(etime*100),audio_len)
    return sframe,eframe

def make_sent2mfcc(conv,sents,sent2mfcc,sent2times,mfcc_dir):
    spks = ['A','B']
    for spk in spks:
        spk_sents = [sent for sent in sents if spk in sent]
        mfcc_file = f'{conv}-{spk}.pickle'
        with open(os.path.join(mfcc_dir,mfcc_file),'rb') as f:
            mfcc_dict = pickle.load(f)
        mfccs = np.transpose(np.array(mfcc_dict[list(mfcc_dict.keys())[0]]))
        audio_len = mfccs.shape[-1] - 1
        for sent in spk_sents:
            stime = sent2times[sent][0][0]
            etime = sent2times[sent][-1][-1]
            sframe,eframe = times2frames(stime,etime,audio_len)
            sent_mfccs = mfccs[:,sframe:eframe]
            sent2mfcc[sent] = sent_mfccs
    return sent2mfcc

def make_sent2pitchpov(conv,sents,sent2pitchpov,sent2times,pitchpov_dir):
    spks = ['A','B']
    for spk in spks:
        spk_sents = [sent for sent in sents if spk in sent]
        pitchpov_file = f'{conv}-{spk}.pickle'
        with open(os.path.join(pitchpov_dir,pitchpov_file),'rb') as f:
            pitchpov_dict = pickle.load(f)
        pitchpov = np.transpose(np.array(pitchpov_dict[list(pitchpov_dict.keys())[0]]))
        audio_len = pitchpov.shape[-1]-1
        for sent in spk_sents:
            stime = sent2times[sent][0][0]
            etime = sent2times[sent][-1][-1]
            sframe,eframe = times2frames(stime,etime,audio_len)
            sent_pitchpov = pitchpov[:,sframe:eframe]
            sent2pitchpov[sent] = sent_pitchpov
    return sent2pitchpov

def norm_energy_by_side(side_fbanks,spk_sents,sent2times):
    feat_dim = 41
    all_turns = np.empty((feat_dim,0))
    audio_len = side_fbanks.shape[-1]
    for sent in spk_sents:
        stime = sent2times[sent][0][0]
        etime = sent2times[sent][-1][-1]
        sframe,eframe =  times2frames(stime,etime,audio_len)
        curr_frames = side_fbanks[:,sframe:eframe]
        all_turns = np.hstack([all_turns, curr_frames])
    hi = np.max(all_turns, 1)
    e0 = side_fbanks[0, :]/hi[0]
    exp_fbank = np.exp(side_fbanks)
    e_total = exp_fbank[0, :]
    elow = np.log(np.sum(exp_fbank[1:21,:],0)/e_total)
    ehigh = np.log(np.sum(exp_fbank[21:,:],0)/e_total)
    return np.array([e0,elow,ehigh])

"""
def norm_energy_by_turn(sent_fbank,turn_fbank):
    hi = np.max(turn_fbank, 1)
    exp_fbank = np.exp(sent_fbank)
    e_total = exp_fbank[0, :]
    e0 = sent_fbank[0, :] / hi[0]
    elow = np.log(np.sum(exp_fbank[1:21,:],0)/e_total)
    ehigh = np.log(np.sum(exp_fbank[21:,:],0)/e_total)
    return np.array([e0,elow,ehigh])
"""

def make_sent2fbankenergy(conv,sents,sent2fbankenergy,sent2times,fbank_dir): #,sent2turn,turn2sent):
    spks = ['A','B']
    for spk in spks:
        spk_sents = [sent for sent in sents if spk in sent]
        fbank_file = f'{conv}-{spk}.pickle'
        with open(os.path.join(fbank_dir,fbank_file),'rb') as f:
            fbank_dict = pickle.load(f)
        side_fbanks = np.transpose(np.array(fbank_dict[list(fbank_dict.keys())[0]]))
        normed_fbanks = norm_energy_by_side(side_fbanks,spk_sents,sent2times)
        with open(os.path.join(fbank_dir,'normed_fbanks',f'{conv}-{spk}.pickle'),'wb') as f:
            pickle.dump(normed_fbanks,f)
        audio_len = side_fbanks.shape[-1] - 1
        for sent in spk_sents:
            stime = sent2times[sent][0][0]
            etime = sent2times[sent][-1][-1]
            sframe,eframe = times2frames(stime,etime,audio_len)
            
            """ # (undebugged) code for doing normalization by turn
            sent_fbanks = conv_fbanks[:,sframe:eframe]
            turn = sent2turn[sent] # If there is more than one sent in the turn, norm by the whole turn
            turn_sents = turn2sent[turn]
            if len(turn_sents) > 1:
                sturn = sent2times[turn_sents[0]][0][0]
                eturn = sent2times[turn_sents[-1]][-1][-1]
                sturn,eturn = times2frames(sturn,eturn,audio_len)
                turn_fbanks = conv_fbanks[:,sturn:eturn]
            else:
                turn_fbanks = sent_fbanks
            norm_energy = norm_energy_by_turn(sent_fbanks,turn_fbanks)
            """

            sent2fbankenergy[sent] = normed_fbanks[:,sframe:eframe]
    return sent2fbankenergy

def pause2cat(p):
    if np.isnan(p):
        cat = 6
    elif p == 0.0:
        cat = 1
    elif p <= 0.05:
        cat = 2
    elif p <= 0.2:
        cat = 3
    elif p <= 1.0:
        cat = 4
    else:
        cat = 5
    return cat


def make_sent2pause(sents,sent2pause,sent2term,term2pw,pw2feats):
    for sent in sents:
        terms = sent2term[sent]
        pws = [term2pw[term] if term in term2pw else None for term in terms]
        befs = []
        afts = []
        float_befs = []
        float_afts = []

        for pw in pws:
            if not pw:
                bef = float('NaN')
                aft = float('NaN')
            else:
                bef = pw2feats[pw]['pause_before'][0]
                aft = pw2feats[pw]['pause_after'][0]
            float_befs.append(bef)
            float_afts.append(aft)
            befs.append(pause2cat(bef))
            afts.append(pause2cat(aft))
        sent2pause[sent] = {'pause_bef':befs,
                            'pause_aft':afts}
    return sent2pause

def load_orth2meandur_json(data_dir,wordstats_file):
    wordstats_file = os.path.join(data_dir,wordstats_file)
    with open(wordstats_file,'r') as f:
        word_dict = json.load(f)
    orth2meandur = {}
    orth2freq = {}
    for word in word_dict:
        word_no_apos = word.lstrip("'")
        orth2meandur[word_no_apos] = word_dict[word]['mean']
        orth2freq[word_no_apos] = word_dict[word]['count']
    return orth2meandur,orth2freq

def load_orth2meandur(ta_stats_dir,data_dir,wordstats_file,tailstats_file,headstats_file):
    wordstats_file = os.path.join(data_dir,wordstats_file)
    tailstats_file = os.path.join(ta_stats_dir,tailstats_file)
    headstats_file = os.path.join(ta_stats_dir,headstats_file)
    orth2meandur = {}
    orth2freq = {}
    with open (wordstats_file,'rb') as f:
        wordstats = pickle.load(f,encoding='latin1')
    with open(tailstats_file,'rb') as f:
        tailstats = pickle.load(f,encoding='latin1')
    with open(headstats_file,'rb') as f:
        headstats = pickle.load(f,encoding='latin1')
    for word in wordstats:
        orth2meandur[word] = wordstats[word][1]
        orth2freq[word] = wordstats[word][0]
    for head in headstats: # If the 'head' is not already in the word dict, add it. Ignore ones already there and just use their earlier durs. (TODO fix this)
        if not head in wordstats:
            orth2meandur[head] = headstats[head][1]
            orth2freq[head] = headstats[head][0]
    for tail in tailstats: # If the 'tail' is already in the word dict, then combine the avg durs and add the freqs:
        if tail in wordstats:
            wd_freq = wordstats[tail][0]
            wd_mean = wordstats[tail][1]
            tail_freq = tailstats[tail][0]
            tail_mean = tailstats[tail][1]
            new_mean = (wd_freq*wd_mean + tail_freq*tail_mean)/(wd_freq + tail_freq)
            orth2meandur[tail] = new_mean
            orth2freq[tail] = wd_freq + tail_freq
        else:
            orth2meandur[tail] = tailstats[tail][1]
            orth2freq[tail] = tailstats[tail][0]
    return orth2meandur, orth2freq

   
def discard_no_phone_sents(sents,sent2pw,pw2feats):
    out_sents = set(sents)
    for sent in sents:
        pws = sent2pw[sent]
        for pw in pws:
            if not pw2feats[pw]['word_norm']:
                if sent in out_sents:
                    out_sents.remove(sent)
                    print(f'Removing {sent}')
    return list(out_sents)

    
def main():
    nxt_dir = '/group/corporapublic/switchboard/nxt/xml/'
    #data_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/input_features'
    #ta_feats_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/ta_features/tree_aligned'
    #ta_stats_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/ta_features/stats/tree_aligned'
    #alignment_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/swbd_word_times'
    data_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features'
    ta_feats_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/ta_features/tree_aligned'
    ta_stats_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/ta_features/stats/tree_aligned'
    alignment_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/swbd_word_times'


    # First: make or load the big dictionaries that map from sentence to terminal to phonword
    
    print('making term2pw...')
    term2pw_path = os.path.join(data_dir,'term2pw.pickle')
    term2feats_path = os.path.join(data_dir,'term2feats.pickle')
    if not (os.path.exists(term2pw_path) and os.path.exists(term2feats_path)):
        term2pw,term2feats = make_term2pw_feats(nxt_dir)
        with open(term2pw_path,'wb') as f:
            pickle.dump(term2pw,f)
        with open(term2feats_path,'wb') as f:
            pickle.dump(term2feats,f)
    else:
        with open(term2pw_path,'rb') as f:
            term2pw = pickle.load(f)
        with open(term2feats_path,'rb') as f:
            term2feats = pickle.load(f)

            
    print('making sent2pw and sent2term...')
    sent2pw_path = os.path.join(data_dir,'sent2pw.pickle')
    sent2term_path = os.path.join(data_dir,'sent2term.pickle')
    if not (os.path.exists(sent2pw_path) and os.path.exists(sent2term_path)):
        sent2pw,sent2term = make_sent2pw_term(term2pw,term2feats,nxt_dir)
        with open(sent2pw_path,'wb') as f:
            pickle.dump(sent2pw,f)
        with open(sent2term_path,'wb') as f:
            pickle.dump(sent2term,f)

    else:
        with open(sent2pw_path,'rb') as f:
            sent2pw = pickle.load(f)
        with open(sent2term_path,'rb') as f:
            sent2term = pickle.load(f)

    print('making turn2sent and sent2turn ...')
    turn2sent_path = os.path.join(data_dir,'turn2sent.pickle')
    sent2turn_path = os.path.join(data_dir,'sent2turn.pickle')    
    if (not os.path.exists(turn2sent_path)) or (not os.path.exists(sent2turn_path)):
        turn2sent,sent2turn = make_turn2sent(nxt_dir)
        with open(turn2sent_path,'wb') as f:
            pickle.dump(turn2sent,f)
        with open(sent2turn_path,'wb') as f:
            pickle.dump(sent2turn,f)

    else:
        with open(turn2sent_path,'rb') as f:
            turn2sent = pickle.load(f)
        with open(sent2turn_path,'rb') as f:
            sent2turn = pickle.load(f)
        
    
    # Second: load the sentence ids that we're generating output features for
    # and mine the conversation IDs

    #split = 'train'
    #split = 'dev'
    split = 'test'
    split_file = f'{split}_sent_ids.txt'#_from_times_file.txt'
    
    with open(os.path.join(data_dir,split_file),'r') as f:
        sent_ids = [l.strip() for l in f.readlines()]
    convs = list(set([sent_id.split('_')[0] for sent_id in sent_ids]))
    convs = sorted(convs)
    # Third: load dict of orth form to avg len of word; also heads and tails
    """
    with open(os.path.join(data_dir,'avg_word_stats.pickle'),'rb') as f:
        #with open(os.path.join(data_dir,'pw2meandur.pickle'),'rb') as f:
        orth2meandur = pickle.load(f) 
    """
    wordstats_file = 'term2meandur.pickle'
    tailstats_file = 'word_tail_stats.pickle'
    headstats_file = 'word_head_stats.pickle'
    #orth2meandur,orth2freq = load_orth2meandur(ta_stats_dir,data_dir,wordstats_file,tailstats_file,headstats_file)
    #avg_dur_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data'
    avg_dur_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data'
    wordstats_json = 'avg_word_stats.json'
    orth2meandur,orth2freq = load_orth2meandur_json(avg_dur_dir,wordstats_json)

    phone2meandur_path = os.path.join(data_dir,'phone2meandur.pickle')
    with open(phone2meandur_path,'rb') as f:
        phone2meandur = pickle.load(f)

    # TODO 1: Make a dummy work around for the '-ers' key that doesn't work, but print those ones out
    # TODO 2: (a big one) only actually keep words that have 15+ occurrences; otherwise retrieve the phones

    # Fourth: load phonword features for each conversation and use them to
    # generate all the output dictionaries for that conversation
    # Build the output dictionaries cumulatively

    sent2part = {}
    sent2times = {}
    sent2endstart = {}
    sent2dur = {}
    sent2mfcc = {}
    sent2fbankenergy = {}
    sent2pitchpov = {}
    sent2pause = {}

    #kaldi_feat_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/kaldi_feats/'
    kaldi_feat_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/kaldi_feats/'
    mfcc_dir = os.path.join(kaldi_feat_dir,'swbd_mfcc')
    fbank_dir = os.path.join(kaldi_feat_dir,'swbd_fbank_energy')
    pitchpov_dir = os.path.join(kaldi_feat_dir,'swbd_pitch_pov')

    
    for conv in convs:
        print(conv)
        pw2feats = load_pw2feats(conv,ta_feats_dir,alignment_dir,orth2meandur) # pw2feats for just this conversation
        sents = get_sents_for_conv(conv,sent_ids)
        sents = discard_no_phone_sents(sents,sent2pw,pw2feats)
        sents = sorted(sents)
        sent2part,sent2times = make_sent2part_and_times(sents,sent2part,sent2times,sent2term,term2pw,pw2feats,orth2meandur,term2feats,phone2meandur)
        sent2dur = make_sent2dur(sents,sent2dur,sent2part,sent2times,sent2term,term2pw,pw2feats,orth2freq,term2feats,phone2meandur,orth2meandur)
        sent2mfcc = make_sent2mfcc(conv,sents,sent2mfcc,sent2times,mfcc_dir)
        sent2fbankenergy = make_sent2fbankenergy(conv,sents,sent2fbankenergy,sent2times,fbank_dir)#,sent2turn,turn2sent)
        sent2pitchpov = make_sent2pitchpov(conv,sents,sent2pitchpov,sent2times,pitchpov_dir)
        sent2pause = make_sent2pause(sents,sent2pause,sent2term,term2pw,pw2feats)

    print('Pickling ...')
    with open(os.path.join(data_dir,f'{split}_partition.pickle'),'wb') as f:
        pickle.dump(sent2part,f)
    with open(os.path.join(data_dir,f'{split}_duration.pickle'),'wb') as f:
        pickle.dump(sent2dur,f)
    with open(os.path.join(data_dir,f'{split}_mfcc.pickle'),'wb') as f:
        pickle.dump(sent2mfcc,f)
    with open(os.path.join(data_dir,f'{split}_fbank.pickle'),'wb') as f:
        pickle.dump(sent2fbankenergy,f)
    with open(os.path.join(data_dir,f'{split}_pitch.pickle'),'wb') as f:
        pickle.dump(sent2pitchpov,f)
    with open(os.path.join(data_dir,f'{split}_pause.pickle'),'wb') as f:
        pickle.dump(sent2pause,f)
    print('done.')

        
if __name__=="__main__":
    main()
