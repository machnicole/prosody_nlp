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

# # English data
# lang = "eng"
#
# out_dir = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/vm_word_times"
#
# path_to_trees = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/new_trees/all_clean.trees"
# path_to_sent_ids = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/all_clean_sent_ids.txt"
# path_to_textgrids = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_eng_textgrids_complete"


# German data
lang = "ger"

out_dir = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/vm_word_times"

path_to_trees = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/new_trees/all_clean.trees"
path_to_sent_ids = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/all_clean_sent_ids.txt"
path_to_textgrids = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_ger_textgrids_complete"

with open('sentence_id2recording_{}_new.pickle'.format(lang), 'rb') as handle:
    sentence_id2recording = pickle.load(handle)

with open('sentence_id2speaker_{}.pickle'.format(lang), 'rb') as handle:
    sentence_id2speaker = pickle.load(handle)

# take [:150] for sample data
wav_files = list(sentence_id2recording.items())
trees, sent_ids = trees.load_trees_with_idx(path_to_trees, path_to_sent_ids, strip_top=False)



for sentence_id, file in wav_files:
    if file.endswith('.wav') and sentence_id in sent_ids:
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

        #alignment_words = [word.text.transcode() for word in alignments]
        def remove(alignments):
            print([(word_from_tg.text.transcode(), word_from_transcription) for word_from_tg,word_from_transcription in zip(alignments, transcription)])
            if all(word_from_tg.text.transcode() == word_from_transcription for
                   word_from_tg,word_from_transcription in zip(alignments, transcription)):
                print("all", alignments)
                return alignments
            else:
                alignments.pop(0)
                return remove(alignments)

        alignments = remove(alignments)
        print("alignments", alignments)



        save_alignments = False


        transcription_index = 0
        alignment_index_match = 0


        # for i, word in enumerate(alignments):
        #     word_label = word.text.transcode()
        #
        #     if i + 1 < len(alignments):
        #         next_word_label = alignments[i + 1].text.transcode()
        #
        #         try:
        #             if (word_label == "<unk>") and next_word_label == transcription[transcription_index+1].lower():
        #                 next_word_label_condition = True
        #             elif (word_label == "<unk>") and next_word_label == "<unk>":
        #                 next_next_word_label = alignments[i + 2].text.transcode()
        #                 if sentence_id == "cd13_00_1732":
        #                     print("got here")
        #                     print(transcription_index+2, len(transcription))
        #                 if next_next_word_label == transcription[transcription_index+2].lower():
        #                     next_word_label_condition = True
        #                 else:
        #                     next_word_label_condition = False
        #
        #             else:
        #                 next_word_label_condition = False
        #         except IndexError:
        #             # last word in tree is unk
        #             if (word_label == "<unk>") and (transcription_index+1 == len(transcription)):
        #                 next_word_label_condition = True
        #             elif (word_label == "<unk>") and next_word_label == "<unk>" and (transcription_index+2 == len(transcription)):
        #                 next_word_label_condition = True
        #             else:
        #                 next_word_label_condition = False
        #     elif len(alignments) == i+1:
        #         # last word in tree is unk
        #         if (word_label == "<unk>") and (
        #                 transcription_index + 1 == len(transcription)):
        #             next_word_label_condition = True
        #         else:
        #             next_word_label_condition = False
        #
        #     else:
        #         next_word_label = ""
        #         next_word_label_condition = False
        #
        #     if transcription_index < len(transcription):
        #         if word_label == transcription[transcription_index].lower() or next_word_label_condition:
        #             if sentence_id == "cd28_00_971":
        #                 print("transcription_index +1")
        #                 print("match", word_label, transcription[transcription_index].lower())
        #             transcription_index += 1
        #             print("transcription index", transcription_index)
        #             if transcription_index == len(transcription) and alignment_index_match != 0:
        #                 print("got here")
        #                 old_alignment_index_match = alignment_index_match
        #                 alignment_index_match = old_alignment_index_match + 1
        #                 eos_index = alignment_index_match + len(transcription)
        #                 indices = [i for i, x in enumerate([word.text.transcode() for word in
        #                     alignments[alignment_index_match:eos_index]]) if
        #                            x == "<unk>"]
        #                 if sentence_id == "cd28_00_971":
        #                     print("alignment index", alignment_index_match)
        #                     print([word.text.transcode() for word in
        #                     alignments[alignment_index_match:eos_index]
        #                     if word.text.transcode() != "<unk>"])
        #                     print([word for i, word in enumerate(transcription) if i not in indices])
        #                 if [word.text.transcode() for word in
        #                     alignments[alignment_index_match:eos_index]
        #                     if word.text.transcode() != "<unk>"] == [word for i, word in enumerate(transcription) if i not in indices]:
        #                     break
        #                 else:
        #                     alignment_index_match = old_alignment_index_match
        #
        #         else:
        #             if sentence_id == "cd28_00_971":
        #                 print("no match", transcription_index)
        #                 print("alignment index", i)
        #                 print(transcription)
        #                 eos_index = i + len(
        #                     transcription)
        #                 print(eos_index, len(transcription), i)
        #                 print("i", i)
        #                 print([word.text.transcode() for word in alignments[i:eos_index]])
        #             transcription_index = 0
        #             alignment_index_match = i
        #             eos_index = alignment_index_match + len(transcription)
        #             if [word.text.transcode() for word in alignments[alignment_index_match:eos_index]] == transcription:
        #                 break
        #
        #
        # if sentence_id == "cd28_00_971":
        #     print("alignment index", alignment_index_match)
        #     eos_index = alignment_index_match + len(transcription)
        #     print([word.text.transcode() for word in alignments[alignment_index_match:eos_index]])
        #     print([word.text.transcode() for word in alignments])

        # get alignments for transcription (based on the tree)
        for i, word in enumerate(alignments):
            if transcription:
                word_label = word.text.transcode()
            # # if i >= alignment_index_match:
            #     if transcription:
            #         word_label = word.text.transcode()
            #         # TODO this is a hacky way to handle UNKs - can fix this by having a proper pronunciation dict
            #         if i+1 < len(alignments):
            #             next_word_label = alignments[i + 1].text.transcode()
            #         else:
            #             next_word_label = ""
            #         if word_label == transcription[0].lower() or \
            #                 ((word_label == "<unk>") and len(transcription) == 1)\
            #                 or ((word_label == "<unk>") and next_word_label == transcription[1].lower())\
            #                 or (word_label == "<unk>") and next_word_label == "<unk>":
                if word_label == transcription[0].lower():
                        word_from_transcription = transcription.pop(0)
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

                        pw_info = {'text': word_from_transcription,
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
                        print(textgrid_file)
                        print(sentence_id)
                        raise ValueError("Timestamps in TextGrid don't match with words in tree.")
                    else:
                        continue
        else:
            try:
                assert transcription == []
            except AssertionError:
                print(transcription)
                print(textgrid_file)
                print(sentence_id)
                print(pw_dict)
                # print(alignment_index_match)
                # print([word.text.transcode() for word in
                #  alignments[alignment_index_match:]])
                # print([word.text.transcode() for word in
                #  alignments])
                # print(alignments[36])
                raise

        print(pw_dict)
        print(textgrid_file)

        with open(outfile, 'wb') as f:
            pickle.dump(pw_dict, f, protocol=2)







