import os
import zipfile
import pickle
import trees
from collections import defaultdict

# English
# path_to_zip = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/vm_eng_sample.zip'
# path_to_trees = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/new_trees/all_clean.trees"
# path_to_sent_ids = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/all_clean_sent_ids.txt"
# path_to_transcriptions = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/transcriptions"
# lang = "eng"

# German
path_to_zip = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/vm_ger_sample.zip'
path_to_trees = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/new_trees/all_clean.trees"
path_to_sent_ids = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/all_clean_sent_ids.txt"
path_to_transcriptions = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/transcriptions"
lang = "ger"

with open('sentence_id2recording_{}.pickle'.format(lang), 'rb') as handle:
    sentence_id2recording = pickle.load(handle)

with open('sentence_id2speaker_{}.pickle'.format(lang), 'rb') as handle:
    sentence_id2speaker = pickle.load(handle)

corpus_zip = zipfile.ZipFile(path_to_zip, 'w')

wav_files = list(sentence_id2recording.items())[:150]

trees, sent_ids = trees.load_trees_with_idx(path_to_trees, path_to_sent_ids, strip_top=False)

transcriptions = defaultdict(list)
recording2speaker = dict()

for sentence_id, file in wav_files:
    if file.endswith('.wav'):
        index_of_sent_id = sent_ids.index(sentence_id)
        tree = trees[index_of_sent_id]
        transcription = []

        for child in tree.leaves():
            try:
                word = child.word
                transcriptions[os.path.basename(file)].append(word)
            except AttributeError:
                print(tree)
                pass

        if os.path.join(sentence_id2speaker[sentence_id], os.path.basename(file)) in corpus_zip.namelist():
            pass # already in zip
        else:
            corpus_zip.write(file,
                             os.path.join(sentence_id2speaker[sentence_id], os.path.basename(file)),
                             compress_type=zipfile.ZIP_DEFLATED)
            recording2speaker[os.path.basename(file)] = sentence_id2speaker[sentence_id]

for filename, transcription_list in transcriptions.items():
    with open(os.path.join(path_to_transcriptions, os.path.splitext(filename)[0] + ".txt"),
              "w") as t:
        t.write(" ".join(transcription_list))
    corpus_zip.write(os.path.join(path_to_transcriptions, os.path.splitext(filename)[0] + ".txt"),
                     os.path.join(recording2speaker[filename],
                                   os.path.splitext(filename)[0] + ".txt"),
                     compress_type=zipfile.ZIP_DEFLATED)

corpus_zip.close()