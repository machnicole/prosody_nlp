import os
import pickle
import numpy as np


#TODO merge with prep_input_dicts.py

def sort_pws(word_times,mapped_pws):
    sorted_pws = sorted(word_times, key=lambda x: word_times[x]['start_time'])
    sorted_pws = [pw for pw in sorted_pws if pw in mapped_pws]
    return sorted_pws


def get_pauses(info, sorted_keys):
    pause_before = {}
    pause_after = {}
    for i, pw in enumerate(sorted_keys):
        if i == 0:
            pause_before[pw] = np.nan
        else:
            prev = sorted_keys[i-1]
            if prev==pw: # EDIT: if the previous word is the same phonword, then there is no gap. 
                pause_before[pw] = 0
            else:
                pause_before[pw] = info[pw]['start_time'] - info[prev]['end_time']
        if i == len(sorted_keys) - 1:
            pause_after[pw] = np.nan
        else:
            follow = sorted_keys[i+1]
            if follow==pw:  # EDIT: if the next word is the same phonword, then there is no gap. 
                pause_after[pw]=0
            else:
                pause_after[pw] = info[follow]['start_time'] - info[pw]['end_time']
    return pause_before, pause_after

if __name__=="__main__":

    splits = ['train','dev','test']

    for split in splits:
        # sent_f = f'/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/sentence/{split}_sent_ids.txt'
        # sent_f = f'/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/{split}_sent_ids.txt'
        sent_f = f'/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/{split}_sent_ids.txt'

        sent_ids = [l.strip() for l in open(sent_f,'r').readlines()]
        # term2pw_path = f'/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/term2pw.pickle'
        # term2pw_path = f'/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/term2pw.pickle'
        term2pw_path = f'/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/term2pw.pickle'

        term2pw = pickle.load(open(term2pw_path,'rb'))
        mapped_pws = term2pw.values()
        mapped_pws = set(mapped_pws)
    
        # convs = sorted(list(set([sent.split('_')[0].replace('sw','') for sent in sent_ids])))

        all_before = {}
        all_after = {}

        # word_times_dir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/vm_word_times'
        word_times_dir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/vm_word_times'


        for picklefile in os.listdir(word_times_dir):
            word_times = pickle.load(
                open(os.path.join(word_times_dir, picklefile), "rb"))

            # This might very well not be necessary - pause features are already in .features pickle file
            # that was created in vm_extract_ta_features.py
            sorted_pws = sort_pws(word_times, mapped_pws)
            pause_before, pause_after = get_pauses(word_times, sorted_pws)

            all_before = {**all_before, **pause_before}
            all_after = {**all_after, **pause_after}
        #
        # for conv in convs:
        #     print(conv)
        #     word_times = {}
        #
        #     # wt_file_A = f'/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/swbd_word_times/word_times_sw{conv}A.pickle'
        #     # wt_file_B = f'/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/swbd_word_times/word_times_sw{conv}B.pickle'
        #     # wt_file_A = f'/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/swbd_word_times/word_times_sw{conv}A.pickle'
        #     wt_files = f'/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/vm_word_times/word_times_sw{conv}A.pickle'
        #     wt_file_B = f'/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/swbd_word_times/word_times_sw{conv}B.pickle'
        #     A_word_times = pickle.load(open(wt_file_A,'rb'))
        #     B_word_times = pickle.load(open(wt_file_B,'rb'))
        #
        #     word_times = {**A_word_times,**B_word_times}
        #
        #     # NEXT sort all pws and drop any that aren't mapped to terms
        #     sorted_pws = sort_pws(word_times,mapped_pws)
        #     pause_before,pause_after = get_pauses(word_times,sorted_pws)
        #
        #     all_before = {**all_before,**pause_before}
        #     all_after = {**all_after,**pause_after}

        pw2pause = {}
        for pw in all_before:
            pw2pause[pw] = {}
            pw2pause[pw]['pause_before'] = all_before[pw]
            pw2pause[pw]['pause_after'] = all_after[pw]

        # outfile = f'/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/sentence2/{split}_pw2pause.pickle'
        # outfile = f'/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/{split}_pw2pause.pickle'
        outfile = f'/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/{split}_pw2pause.pickle'

        with open(outfile,'wb') as f:
            pickle.dump(pw2pause,f)


