import pickle
import subprocess
import os

# out_dir = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/sample_sph_files"
# lang = "ger"

out_dir = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_ger_sphfiles"
lang = "ger"

# out_dir = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_eng_sphfiles"
# lang = "eng"

with open('sentence_id2recording_{}.pickle'.format(lang), 'rb') as handle:
    sentence_id2recording = pickle.load(handle)
# take only the first 150 for creating sample data [:150]
for sentence_id, path_to_wav_file in list(sentence_id2recording.items()):
    subprocess.run('''
        # This will take a lot of memory (37.5 GB for 25000 sph files)
        sox -t wav {} -t sph {}.sph'''.format(path_to_wav_file, os.path.join(out_dir, sentence_id)),
                   shell=True, check=True,
                   executable='/bin/bash')