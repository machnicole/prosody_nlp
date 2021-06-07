import pickle
import subprocess
import os

out_dir = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/sample_sph_files"

with open('sentence_id2recording_eng.pickle', 'rb') as handle:
    sentence_id2recording = pickle.load(handle)

for sentence_id, path_to_wav_file in list(sentence_id2recording.items())[:150]:
    subprocess.run('''
        # This will take a lot of memory (37.5 GB for 25000 sph files)
        sox -t wav {} -t sph {}.sph'''.format(path_to_wav_file, os.path.join(out_dir, sentence_id)),
                   shell=True, check=True,
                   executable='/bin/bash')