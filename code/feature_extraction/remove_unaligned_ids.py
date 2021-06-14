import pickle
import os

# # English data
# path_to_unaligned = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_eng_textgrids_complete/unaligned.txt"
#
# lang = "eng"

# German data
path_to_unaligned = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_ger_textgrids_complete/unaligned.txt"
path_to_textgrids = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_ger_textgrids_complete"

lang = "ger"

with open('sentence_id2recording_{}.pickle'.format(lang), 'rb') as handle:
    sentence_id2recording = pickle.load(handle)
with open('sentence_id2speaker_{}.pickle'.format(lang), 'rb') as handle:
    sentence_id2speaker = pickle.load(handle)

unaligned = set()
with open(path_to_unaligned, "r") as file:
    for line in file:
        unaligned.add(line[4:].split("\t")[0].strip())

# You can't trust the output of MFA. It can be that it did not align a file
# without logging it...
wav_files = list(sentence_id2recording.items())
for sentence_id, file in wav_files:
    if os.path.isfile(os.path.join(path_to_textgrids,
                                 sentence_id2speaker[sentence_id],
                                 sentence_id2speaker[sentence_id] + "-" +
                                 os.path.splitext(os.path.basename(file))[
                                     0].replace("_", "-")
                                 + ".TextGrid")):
        continue
    else:
        if os.path.splitext(os.path.basename(file))[
                                     0].replace("_", "-").split("\t")[0].strip() not in unaligned:
            unaligned.add(os.path.splitext(os.path.basename(file))[
                                     0].replace("_", "-").split("\t")[0].strip())

print(unaligned)
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

