import pickle
import os

path_to_unaligned = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_eng_textgrids/unaligned.txt"

lang = "eng"

with open('sentence_id2recording_{}.pickle'.format(lang), 'rb') as handle:
    sentence_id2recording = pickle.load(handle)

unaligned = []
with open(path_to_unaligned, "r") as file:
    for line in file:
        unaligned.append(line[4:].split("\t")[0].strip())


sentence_id2recording_new = dict()
removed = 0
for sentence_id in sentence_id2recording:
    if os.path.splitext(
            os.path.basename(
            sentence_id2recording[sentence_id]))[0].replace("_", "-") not in unaligned:
        sentence_id2recording_new[sentence_id] = sentence_id2recording[sentence_id]
    else:
        removed += 1

print("Removed {} mappings to {} unaligned recordings...".format(removed, len(unaligned)))

with open('sentence_id2recording_{}_new.pickle'.format(lang), 'wb') as handle:
    pickle.dump(sentence_id2recording_new, handle)

