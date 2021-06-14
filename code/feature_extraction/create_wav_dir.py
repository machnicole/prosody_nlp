import pickle
import subprocess
import os

# out_dir = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_eng_wavs"
# lang = "eng"

out_dir = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_ger_wavs"
lang = "ger"

with open('sentence_id2recording_{}_new.pickle'.format(lang), 'rb') as handle:
    sentence_id2recording = pickle.load(handle)

for sentence_id, path_to_wav_file in list(sentence_id2recording.items()):
    subprocess.run('''
        # This will take a lot of memory (6GB for 25000 sph files)
        cp {} {}'''.format(path_to_wav_file, os.path.join(out_dir, sentence_id + ".wav")),
                   shell=True, check=True,
                   executable='/bin/bash')
