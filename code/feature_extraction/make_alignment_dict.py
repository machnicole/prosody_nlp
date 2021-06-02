import os
from bs4 import BeautifulSoup
import cPickle as pickle
# import pickle
import pandas as pd
import sys

sys.setrecursionlimit(100000)

nxt_dir = '/group/corporapublic/switchboard/nxt/xml/'
# mstate_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/swb_ms98_transcriptions'
mstate_dir = '/afs/inf.ed.ac.uk/group/corpora/large/switchboard/switchboard1/transcriptions/swb_ms98_transcriptions'

pw_dir = os.path.join(nxt_dir,'phonwords')
phone_dir = os.path.join(nxt_dir,'phones')
syll_dir = os.path.join(nxt_dir,'syllables')

out_dir = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/swbd_word_times"
# out_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/swbd_word_times'
# out_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/swbd_word_times/tree_aligned/'

non_pw = ['[silence]','[noise]','[laughter]','[vocalized-noise]','<b_aside>','<e_aside>']

def find_ids_in_range(href_ids,conv):
    href_ids = href_ids.replace('id(','').replace(')','')
    if '..' in href_ids:
        out_ids = []
        start,end = href_ids.split('..')
        start_idx = int(start[-1])
        end_idx = int(end[-1])
        id_base = start[:-1]
        for i in range(start_idx,end_idx+1):
            out_ids.append(conv+'_'+id_base+str(i))
        return out_ids
    else:
        return([conv+'_'+href_ids]) # Only one id anyway

def flatten_list(lst):
    return [item for sublist in lst for item in sublist]

# for pw_file in ['sw3796.A.phonwords.xml']:#os.listdir(pw_dir):
for pw_file in os.listdir(pw_dir):

    pw_dict = {} # Make one dict per conversation/speaker pair.

    ph2info = {} # Dictionaries to make on the way:
    syll2phon = {} 
    pw2syll = {}
    pw2phon = {}
    
    conv,spk,_,_ = pw_file.split('.')
    # print(conv,spk)

    outfile = os.path.join(out_dir,'word_times_'+conv+spk+'.pickle')
    #if os.path.exists(outfile):
    #    continue
    
    # Open phones file
    phone_file = conv+'.'+spk+'.'+'phones.xml'
    phone_filepath = os.path.join(phone_dir,phone_file)
    phone_f = open(phone_filepath,'r')
    phone_contents = phone_f.read()
    phone_soup = BeautifulSoup(phone_contents,'lxml')
    phones = phone_soup.find_all('ph')

    print("works until here 1")

    # Make dict where key = phonword id, value = phones
    #     Each phone is a tuple: (start,end,contents)
    for ph in phones:
        ph_id = conv+'_'+ph['nite:id']
        start = float(ph['nite:start'])
        end = float(ph['nite:end'])
        contents = ph.contents[0]
        print("works until here 2")
        if ph_id in ph2info:
            print('duplicate phone!')
            import pdb;pdb.set_trace()
        else:
            ph2info[ph_id] = (start,end,contents)
    print("works until here 3")

    # Open syll file (to make syllable-to-phone dict)
    syll_file = conv+'.'+spk+'.syllables.xml'
    syll_filepath = os.path.join(syll_dir,syll_file)
    syll_f = open(syll_filepath,'r')
    syll_contents = syll_f.read()
    syll_soup = BeautifulSoup(syll_contents,'lxml')
    sylls = syll_soup.find_all('syllable')
    for syll in sylls:
        syll_id = conv+'_'+syll['nite:id']
        phon_child = syll.find_all('nite:child')[0]
        href_ids = phon_child['href'].split('#')[-1]
        phon_ids = find_ids_in_range(href_ids,conv)
        syll2phon[syll_id] = phon_ids
    print("works until here 4")
    # Load corrected phonword start/stop times
    mstate_path = os.path.join(mstate_dir,conv[2:4],conv[2:],conv+spk+'-ms98-a-word.text')
    corrected_times = []
    with open(mstate_path,'r') as f:
        rows = [l.strip() for l in f.readlines()]
    for row in rows:
        sent_id,start,end,orth = row.split()
        start = float(start)
        end = float(end)
        if not orth in non_pw: # discard silences and noises etc
            corrected_times.append((orth,start,end))

    print("works until here 5")
        

    print('loaded syll and msstate files')
    # Open up phonwords file
    pw_filepath = os.path.join(pw_dir,pw_file)
    pw_f = open(pw_filepath,'r')
    pw_contents = pw_f.read()
    pw_soup = BeautifulSoup(pw_contents,'lxml')
    pws = pw_soup.find_all('phonword')
   
    for i,pw in enumerate(pws):
        pw_id = conv+'_'+pw['nite:id']
        start = float(pw['nite:start'])
        end = float(pw['nite:end'])
        orth = pw['orth']
        all_sylls = pw.find_all('nite:child')
        try:
            syll_child = all_sylls[0]
            href_ids = syll_child['href'].split('#')[-1]
            syll_ids = find_ids_in_range(href_ids,conv)
            phon_ids = []
            for syll in syll_ids:
                if syll in syll2phon:
                    phon_ids.append(syll2phon[syll])
            phon_ids = flatten_list(phon_ids)

            #Go through phons and create the list off phones, start and end times
            phones = []
            phone_starts = []
            phone_ends = []
            for phon in phon_ids:
                start,end,phone = ph2info[phon]
                phones.append(phone)
                phone_starts.append(start)
                phone_ends.append(end)
        except:
            print(pw_id)
            print('no syll children')
            phones = []
            phone_starts = []
            phone_ends = []


        corrected_start = corrected_times[i][1]
        corrected_end = corrected_times[i][2]
        corrected_orth = corrected_times[i][0]

        print("works until here 6")
        if orth==corrected_orth:
            start = corrected_start
            end = corrected_end
        else:
            print('orths dont match')
            print(orth)
            print(corrected_orth)
            import pdb;pdb.set_trace()
        print("works until here 7")
        pw_info = {'text':orth,
                   'start_time':start,
                   'end_time':end,
                   'phone_start_times':phone_starts,
                   'phone_end_times':phone_ends,
                   'phones':phones}
        print(pw_info)
        pw_dict[pw_id] = pw_info
        
    print(outfile)
    with open(outfile,'wb') as f:
        pickle.dump(pw_dict,f,protocol=2)

    

