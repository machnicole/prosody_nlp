import os
from bs4 import BeautifulSoup
import pickle
import re

nxt_dir = '/group/corporapublic/switchboard/nxt/xml'
term_dir = os.path.join(nxt_dir,'terminals')
phone_dir = os.path.join(nxt_dir,'phones')
pw_dir = os.path.join(nxt_dir,'phonwords')
#out_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/input_features/'
out_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/'
term2meandur_file = os.path.join(out_dir,'term2meandur.pickle')
phone2meandur_file = os.path.join(out_dir,'phone2meandur.pickle')
pw2meandur_file =  os.path.join(out_dir,'pw2meandur.pickle')

def clean_text(raw_word):
    word = raw_word.lower()
    word = word.replace("_1", "")
    if '[laughter-' in word:
        word = word.lstrip('[laughther').rstrip(']').lstrip('-')
    if "/" in word and "[" in word and "]" in word:
        word = word.split("/")[-1].replace("]", "")
    if "[" in word:
        word = re.sub(r'\[[^)]*\]','', word)
    if "{" in word and "}" in word:
        word = word.replace("{", "").replace("}", "")
    return word
                                                                            

#"""
term2durs = {}
for termfile in os.listdir(term_dir):
    if termfile.startswith('sw2') or termfile.startswith('sw3'):
        termf = open(os.path.join(term_dir,termfile),'r')
        termsoup = BeautifulSoup(termf.read(),'lxml')
        terms = termsoup.find_all('word')

        for i,term in enumerate(terms):
            orth = clean_text(term['orth'])
            """
            if orth =='mumblex':
                orth = clean_text(term['swword'])
            if orth == 'seven' or orth == 'moo':
                try:
                    swword = term['swword']
                    orth = clean_text(swword)
                except:
                    pass
            """
            if not term['nite:start'] == 'n/a' and not term['nite:end'] == 'n/a' \
               and not term['nite:start'] == 'non-aligned' and not term['nite:end'] == 'non-aligned':
                dur = float(term['nite:end']) - float(term['nite:start'])
                if orth in term2durs:
                    term2durs[orth].append(dur)
                else:
                    term2durs[orth] = [dur]
            """
            elif term['nite:start']=='n/a' and term['orth']=="'":
                orth = terms[i-1]['orth']
                orth = clean_text(orth)
                dur = float(term['nite:end']) - float(terms[i-1]['nite:start'])
                if orth in term2durs:
                    term2durs[orth].append(dur)
                else:
                    term2durs[orth] = [dur]
            """ 

term2meandur = {}                
for orth in term2durs:
    meandur = sum(term2durs[orth])/len(term2durs[orth])
    freq = len(term2durs[orth])
    term2meandur[orth] = (freq,meandur)
import pdb;pdb.set_trace()    

with open(term2meandur_file,'wb') as f:
    pickle.dump(term2meandur,f)
#"""
"""
pw2durs = {}
for pwfile in os.listdir(pw_dir):
    pwf = open(os.path.join(pw_dir,pwfile),'r')
    pwsoup = BeautifulSoup(pwf.read(),'lxml')
    pws = pwsoup.find_all('phonword')

    for pw in pws:
        orth = clean_text(pw['orth'])
        try:
            dur = float(pw['nite:end']) - float(pw['nite:start'])
            if orth in pw2durs:
                pw2durs[orth].append(dur)
            else:
                pw2durs[orth] = [dur]
        except:
            pass

pw2meandur = {}
for pw in pw2durs:
    meandur = sum(pw2durs[pw])/len(pw2durs[pw])
    pw2meandur[pw] = meandur

import pdb;pdb.set_trace()
with open(pw2meandur_file,'wb') as f:
    pickle.dump(pw2meandur,f)
"""

"""
phone2durs = {}
for phonefile in os.listdir(phone_dir):
    phonef = open(os.path.join(phone_dir,phonefile),'r')
    phonesoup = BeautifulSoup(phonef.read(),'lxml')
    phones = phonesoup.find_all('ph')

    for phone in phones:
        ph = str(phone.contents[0])
        dur = float(phone['nite:end']) - float(phone['nite:start'])
        if ph in phone2durs:
            phone2durs[ph].append(dur)
        else:
            phone2durs[ph] = [dur]

phone2meandur = {}                
for ph in phone2durs:
    meandur = sum(phone2durs[ph])/len(phone2durs[ph])
    phone2meandur[str(ph)] = meandur

import pdb;pdb.set_trace()
with open(phone2meandur_file,'wb') as f:
    pickle.dump(phone2meandur,f)

"""
