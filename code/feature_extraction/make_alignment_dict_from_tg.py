import pickle
import trees
import os
import textgrids
# Goal is:
# pw_info = {'text': orth,
#            'start_time': start,
#            'end_time': end,
#            'phone_start_times': phone_starts,
#            'phone_end_times': phone_ends,
#            'phones': phones}
# print(pw_info)

# pw_dict[pw_id] = pw_info
# # Example entry:
# # ('sw2005_ms52A_pw804',
# # {'phones': ['m', 'ah', 'ch'],
# # 'start_time': 399.744625,
# # 'phone_start_times': [399.744625, 399.834625, 399.904625],
# # 'end_time': 400.044625,
# # 'phone_end_times': [399.834625, 399.904625, 400.044625],
# # 'text': 'much'})
#
# print(outfile)
# with open(outfile, 'wb') as f:
#     pickle.dump(pw_dict, f, protocol=2)

with open('sentence_id2recording_eng.pickle', 'rb') as handle:
    sentence_id2recording = pickle.load(handle)

with open('sentence_id2speaker_eng.pickle', 'rb') as handle:
    sentence_id2speaker = pickle.load(handle)

out_dir = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/vm_word_times"

path_to_trees = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/new_trees/all_clean.trees"
path_to_sent_ids = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/all_clean_sent_ids.txt"
path_to_textgrids = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/textgridoutput"

wav_files = list(sentence_id2recording.items())[:10]
trees, sent_ids = trees.load_trees_with_idx(path_to_trees, path_to_sent_ids, strip_top=False)



for sentence_id, file in wav_files:
    if file.endswith('.wav'):
        index_of_sent_id = sent_ids.index(sentence_id)
        tree = trees[index_of_sent_id]
        transcription = []

        for child in tree.leaves():
            try:
                word = child.word
                transcription.append(word)
            except AttributeError:
                print(tree)
                pass

        pw_dict = {}

        outfile = os.path.join(out_dir, 'word_times_' + sentence_id + '.pickle')

        textgrid_file = os.path.join(path_to_textgrids,
                                     sentence_id2speaker[sentence_id],
                                     sentence_id2speaker[sentence_id] + "-" +
                                     os.path.splitext(os.path.basename(file))[0].replace("_", "-")
                                     + ".TextGrid")

        grid = textgrids.TextGrid(textgrid_file)
        index = 0
        # get all alignments (based on recording)
        alignments = []
        for word in grid["words"]:
            label = word.text.transcode()
            if label != "":
                alignments.append(word)
        save_alignments = False
        # get alignments for transcription (based on the tree)
        for word in alignments:
            if transcription:
                word_label = word.text.transcode()
                if word_label == transcription[0].lower() or word_label == "<unk>":
                    transcription.pop(0)
                    index += 1
                    pw_id = sentence_id + "_" + str(index).zfill(4)
                    phones = []
                    phone_starts = []
                    phone_ends = []
                    for phone in grid["phones"]:
                        # word consists of only one phone:
                        if phone.xmin == word.xmin and phone.xmax == word.xmax:
                            label = phone.text.transcode()
                            phones.append(label)
                            phone_starts.append(phone.xmin)
                            phone_ends.append(phone.xmax)
                        # phone is at the beginning of a word
                        elif phone.xmin == word.xmin:
                            label = phone.text.transcode()
                            phones.append(label)
                            phone_starts.append(phone.xmin)
                            phone_ends.append(phone.xmax)
                        # phone is in the middle of a word
                        elif phone.xmin > word.xmin and phone.xmax < word.xmax:
                            label = phone.text.transcode()
                            phones.append(label)
                            phone_starts.append(phone.xmin)
                            phone_ends.append(phone.xmax)
                        # phone is at the end of a word
                        elif phone.xmax == word.xmax:
                            label = phone.text.transcode()
                            phones.append(label)
                            phone_starts.append(phone.xmin)
                            phone_ends.append(phone.xmax)
                        else:
                            continue

                    pw_info = {'text': word_label,
                               'start_time': word.xmin,
                               'end_time': word.xmax,
                               'phone_start_times': phone_starts,
                               'phone_end_times': phone_ends,
                               'phones': phones}
                    pw_dict[pw_id] = pw_info
                    save_alignments = True
                else:
                    if save_alignments == True:
                        print(transcription)
                        print(word_label)
                        raise ValueError("Timestamps in TextGrid don't match with words in tree.")
                    else:
                        continue
        else:
            assert transcription == []

        # print(pw_dict)

        with open(outfile, 'wb') as f:
            pickle.dump(pw_dict, f, protocol=2)







