import os
from bs4 import BeautifulSoup
import pickle
import re

nxt_dir = '/group/corporapublic/switchboard/nxt/xml'
term_dir = os.path.join(nxt_dir,'terminals')
phone_dir = os.path.join(nxt_dir,'phones')
pw_dir = os.path.join(nxt_dir,'phonwords')
#out_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/input_features/'
out_dir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/input_features'
phone2meandur_file = os.path.join(out_dir,'phone2meandur.pickle')


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


