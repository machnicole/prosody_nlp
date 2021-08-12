import os
import sys
sys.path.append("../")
import trees
import pickle
import string
import re
from collections import defaultdict
"""
Analyze where the parser puts sentence breaks, relative to certain prosodic feature
or alternatively, relative to certain constitents.

Current hypothesis:
The parser likely splits sentences 
- After lower f0 feats
- At pauses > cat1
- Possibly at the end of EDITED constituents (which also coincide with longer pauses)
"""





# English
# output_dir = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/code/self_attn_speech_parser/results"
# turndir = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_eng_turns"
# datadir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features'
# sentdir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/new_trees'
# lang = "eng"
# German
lang = "ger"
output_dir = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/code/self_attn_speech_parser/results"
turndir = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_ger_turns"
datadir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features'
sentdir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/new_trees'

#pred_tree_file = os.path.join(output_dir,"turn_nonsp_correct_eval_72240_dev=86.09.pt_dev_predicted.txt")
#pred_tree_file = os.path.join(output_dir,"turn_sp_correct_eval_72240_dev=90.90.pt_dev_predicted.txt")
#pred_tree_file = os.path.join(output_dir,"turn_dur_only_correct_eval_72240_dev=86.24.pt_dev_predicted.txt")
#pred_tree_file = os.path.join(output_dir,"turn_fbank_only_correct_eval_72240_dev=90.29.pt_dev_predicted.txt")
#pred_tree_file = os.path.join(output_dir,"turn_pause_only_correct_eval_72240_dev=86.21.pt_dev_predicted.txt")
#
# pred_tree_file = os.path.join(output_dir,"turn_vm_eng_with_speech_output_top.txt")
# pred_tree_file = os.path.join(output_dir,"turn_vm_eng_pitch_output_top.txt")
# pred_tree_file = os.path.join(output_dir,"turn_vm_eng_intensity_output_top.txt")
# pred_tree_file = os.path.join(output_dir,"turn_vm_eng_duration_output_top.txt")
# pred_tree_file = os.path.join(output_dir,"turn_vm_eng_pause_output_top.txt")
# pred_tree_file = os.path.join(output_dir,"turn_vm_eng_no_speech_output_top.txt")

# pred_tree_file = os.path.join(output_dir,"turn_vm_ger_with_speech_output_top.txt")
# pred_tree_file = os.path.join(output_dir,"turn_vm_ger_pitch_output_top.txt")
# pred_tree_file = os.path.join(output_dir,"turn_vm_ger_intensity_output_top.txt")
# pred_tree_file = os.path.join(output_dir,"turn_vm_ger_duration_output_top.txt")
# pred_tree_file = os.path.join(output_dir,"turn_vm_ger_pause_output_top.txt")
# pred_tree_file = os.path.join(output_dir,"turn_vm_ger_no_speech_output_top.txt")



# #
gold_tree_file = os.path.join(turndir,'turn_dev_top.trees')
id_file = os.path.join(turndir,'turn_dev_sent_ids_top.txt')
# gold_tree_file = os.path.join(turndir,'turn_train.trees')
# id_file = os.path.join(turndir,'turn_train_sent_ids.txt')

# gold_tree_file = os.path.join(turndir,'turn_dev_disfluent.trees')
# id_file = os.path.join(turndir,'turn_dev_disfluent_sent_ids.txt')

# disfluent_id_file = os.path.join(turndir,'turn_dev_disfluent_sent_ids.txt')
# disfluent_turn_ids = [l.strip() for l in open(os.path.join(turndir,'turn_dev_disfluent_sent_ids.txt'),'r').readlines()]
#
sentence_tree_file = os.path.join(sentdir, 'dev.trees')
sentence_id_file = os.path.join(datadir, 'dev_sent_ids.txt')
#
# sentence_tree_file = os.path.join(sentdir, 'train.trees')
# sentence_id_file = os.path.join(datadir, 'train_sent_ids.txt')
#
turn2part = pickle.load(open(os.path.join(turndir,'turn_dev_partition.pickle'),'rb'))
turn2pitch = pickle.load(open(os.path.join(turndir,'turn_dev_pitch.pickle'),'rb'))
turn2fbank = pickle.load(open(os.path.join(turndir,'turn_dev_fbank.pickle'),'rb'))
turn2pause = pickle.load(open(os.path.join(turndir,'turn_dev_pause.pickle'),'rb'))
turn2dur = pickle.load(open(os.path.join(turndir,'turn_dev_duration.pickle'),'rb'))
# turn_ids = [l.strip() for l in open(os.path.join(turndir,'turn_dev_sent_ids.txt'),'r').readlines()]
# turn_trees = [l.strip() for l in open(os.path.join(turndir,'turn_dev.trees'),'r').readlines()]
turn_ids = [l.strip() for l in open(os.path.join(turndir,'turn_dev_sent_ids_top.txt'),'r').readlines()]
turn_trees = [l.strip() for l in open(os.path.join(turndir,'turn_dev_top.trees'),'r').readlines()]
sent2turn = pickle.load(open(os.path.join(datadir,'sent2turn.pickle'),'rb'))
turn2sent = pickle.load(open(os.path.join(datadir,'turn2sent.pickle'),'rb'))
#
# turn2part = pickle.load(open(os.path.join(turndir,'turn_train_partition.pickle'),'rb'))
# turn2pitch = pickle.load(open(os.path.join(turndir,'turn_train_pitch.pickle'),'rb'))
# turn2fbank = pickle.load(open(os.path.join(turndir,'turn_train_fbank.pickle'),'rb'))
# turn2pause = pickle.load(open(os.path.join(turndir,'turn_train_pause.pickle'),'rb'))
# turn2dur = pickle.load(open(os.path.join(turndir,'turn_train_duration.pickle'),'rb'))
# turn_ids = [l.strip() for l in open(os.path.join(turndir,'turn_train_sent_ids.txt'),'r').readlines()]
# turn_trees = [l.strip() for l in open(os.path.join(turndir,'turn_train.trees'),'r').readlines()]
# sent2turn = pickle.load(open(os.path.join(datadir,'sent2turn.pickle'),'rb'))
# turn2sent = pickle.load(open(os.path.join(datadir,'turn2sent.pickle'),'rb'))
# #
#
# # treestrings = [l.strip() for l in open(pred_tree_file).readlines()]
# tree_list,ids = trees.load_trees_with_idx(pred_tree_file,id_file)
# turn2tree = dict(zip(ids,tree_list))
# turn2treestring = dict(zip(ids,treestrings))



def get_wd_len(constituent):
    leaves = 0
    for leaf in constituent.leaves():
        leaves += 1
    return leaves

def get_sent_break_idx_old(tree):
    if len(tree.children) == 1:
        return False
    else:
        idxs = []
        for i,child in enumerate(tree.children):
            left_leaf_len = sum([get_wd_len(tree.children[j]) for j in range(i+1)])
            idxs.append(left_leaf_len-1)
        return idxs

def get_sent_break_idx(tree, sentence_trees_in_turn):
    if len(tree.children) == 1:
        return False
    else:
        idxs = []

        # for i,child in enumerate(tree.children):
            # leaves = [leaf.word for leaf in child.leaves()]
            # sentence_tree = sentence_trees_in_turn.pop(0)
            # if leaves == [leaf.word for leaf in sentence_tree.leaves()]:
            #     pass
            # else:
            #     leaves.
        total_leaf_len = 0
        for sentence_tree in sentence_trees_in_turn:
            left_leaf_len = sum([get_wd_len(sentence_tree)])
            total_leaf_len += left_leaf_len
            idxs.append(total_leaf_len-1)
        return idxs

def get_interruption_idx2(tree, turn_id):

    path_to_vm_annotations_1 = "/group/corporapublic/verbmobil/1.3"
    path_to_vm_annotations_2 = "/group/corpora/large4/verbmobil/2.3"

    terminals_in_tree = [leaf.word for leaf in tree.leaves()]
    terminals = len(terminals_in_tree)

    idxs = []

    print(turn_id, turn2sent[turn_id])

    if len(turn_id.split("_")) > 3:
        turn_id = turn_id[:-4]
    if os.path.isfile(os.path.join(path_to_vm_annotations_1, turn_id[0:5],
                                   turn_id + ".par")):
        path_to_par = os.path.join(path_to_vm_annotations_1, turn_id[0:5],
                                   turn_id + ".par")
    elif os.path.isfile(os.path.join(path_to_vm_annotations_2, turn_id[0:5],
                                     turn_id + ".par")):
        path_to_par = os.path.join(path_to_vm_annotations_2, turn_id[0:5],
                                   turn_id + ".par")
    else:
        print(turn_id)
        raise FileNotFoundError
    # print(path_to_par)
    with open(path_to_par, "r", encoding="ISO-8859-1") as parfile:
        partext = parfile.read()
    tr2 = re.findall('TR2:\s\d+\s.*', partext)
    ort = re.findall('ORT:\s\d+\s.*', partext)

    tr2 = [(line2, line) for line, line2 in zip(tr2, ort)
           if "=/+" not in line.split("\t")[2]
           and not line.split("\t")[2].endswith("<%>")
           and not line.split("\t")[2].startswith("<%>")
           and "=/-" not in line.split("\t")[2]
           and "=" not in line.split("\t")[2]
           and not line.split("\t")[2].endswith("=:>/+")]

    # full_transcription = ""
    # for line in tr2:
    #     transcription = line.split("\t")[2]
    #     full_transcription += transcription + " "
    #
    # false_starts = re.findall("-/(.*?[^=])/-", full_transcription)
    # repetitions = re.findall("\+/(.*?[^=])/\+", full_transcription)

    transcriptions = [line.split("\t")[2] for (line2, line) in tr2
                      if '<"ah>' not in line.split("\t")[2]
                      and '<h"as>' not in line.split("\t")[2]
                      and '<"ah>' not in line.split("\t")[2]
                      and '<"ahm>' not in line.split("\t")[2]]
    orts = [line2.split("\t")[2] for (line2, line) in tr2
            if '<"ah>' not in line.split("\t")[2]
            and '<h"as>' not in line.split("\t")[2]
            and '<"ah>' not in line.split("\t")[2]
            and '<"ahm>' not in line.split("\t")[2]]
    assert len(transcriptions) == len(orts)
    edit_idxs_from_transcriptions = []
    pre_edit_idxs_from_transcriptions = []
    disfluency_found = False
    for i,j in enumerate(transcriptions):
        if ('+/' in j or "-/" in j) and not "=/-" in j and not "=/+" in j:
            if disfluency_found == False:
                # check if the disfluency annotation is complete:
                if ('/+' in "".join(transcriptions[i:]) or "/-" in "".join(transcriptions[i:])) \
                    and not "=/-" in "".join(transcriptions[i:]) and not "=/+" in "".join(transcriptions[i:]):
                    pre_edit_idxs_from_transcriptions.append(i)
                    disfluency_found = True
            else:
                pre_edit_idxs_from_transcriptions.pop(-1)
                pre_edit_idxs_from_transcriptions.append(i)
                disfluency_found = True
        if ('/+' in j or "/-" in j) and not "=/-" in j and not "=/+" in j:
            if disfluency_found:
                edit_idxs_from_transcriptions.append(i)
                disfluency_found = False


    if edit_idxs_from_transcriptions == [] or pre_edit_idxs_from_transcriptions == []:
        return []
    try:
        assert len(edit_idxs_from_transcriptions) == len(pre_edit_idxs_from_transcriptions)
    except:
        print(pre_edit_idxs_from_transcriptions, edit_idxs_from_transcriptions)
        print(transcriptions)
        print(terminals_in_tree)
        raise
    edit_span_ids = {edit_idx: pre_edit_idx for
                     pre_edit_idx, edit_idx in
                     zip(pre_edit_idxs_from_transcriptions, edit_idxs_from_transcriptions)}

    if edit_idxs_from_transcriptions:
        if len(transcriptions) == len(terminals_in_tree):
            idxs = edit_idxs_from_transcriptions
        else:
            for id in edit_idxs_from_transcriptions:
                count = terminals_in_tree.count(orts[id].lower().translate(str.maketrans('', '', string.punctuation + string.digits)))
                if count == 1:
                    print("one case")
                    idxs.append(terminals_in_tree.index(orts[id].lower().translate(str.maketrans('', '', string.punctuation + string.digits))))
                else:
                    idxs = []
                    break
            else:
                return idxs
            print("IDX",edit_idxs_from_transcriptions)
            print(terminals_in_tree)
            print(transcriptions)
            print(len(transcriptions), len(terminals_in_tree))
            for id in edit_idxs_from_transcriptions:
                count = terminals_in_tree.count(orts[id].lower().translate(str.maketrans('', '', string.punctuation + string.digits)))

                pre_edit_idx =  edit_span_ids[id]
                try:
                    post_edit_raw_string_tree = terminals_in_tree[
                        id + 1].lower().translate(
                        str.maketrans('', '',
                                      string.punctuation + string.digits))
                except IndexError:
                    post_edit_raw_string_tree = ""

                try:
                    post_edit_raw_string_transcript = orts[id+1].lower().translate(
                        str.maketrans('', '', string.punctuation + string.digits))
                    if post_edit_raw_string_transcript == "uh":
                        post_edit_raw_string_transcript = "ah"
                except IndexError:
                    post_edit_raw_string_transcript = ""


                try:
                    edit_raw_string_tree_id = terminals_in_tree[
                        id].lower().translate(str.maketrans('', '',
                                                            string.punctuation + string.digits))
                except IndexError:
                    edit_raw_string_tree_id = ""

                try:
                    edit_raw_string_tree = terminals_in_tree[id - (
                                len(transcriptions) - len(
                            terminals_in_tree))].lower().translate(
                        str.maketrans('', '',
                                      string.punctuation + string.digits))
                except IndexError:
                    edit_raw_string_tree = ""

                edit_raw_string_transcript = orts[id].lower().translate(str.maketrans('', '', string.punctuation + string.digits))
                try:
                    edit_raw_string_tree_next =terminals_in_tree[id+1].lower().translate(str.maketrans('', '', string.punctuation + string.digits))
                except IndexError:
                    edit_raw_string_tree_next = ""
                try:
                    edit_raw_string_tree_before =terminals_in_tree[id-1].lower().translate(str.maketrans('', '', string.punctuation + string.digits))
                except IndexError:
                    edit_raw_string_tree_before = ""
                pre_edit_raw_string_transcript = orts[pre_edit_idx].lower().translate(
                    str.maketrans('', '', string.punctuation + string.digits))
                try:
                    pre_edit_raw_string_tree_id = terminals_in_tree[pre_edit_idx].lower().translate(
                        str.maketrans('', '', string.punctuation + string.digits))
                except IndexError:
                    pre_edit_raw_string_tree_id = ""
                try:
                    pre_edit_raw_string_tree_next = terminals_in_tree[
                        pre_edit_idx + 1].lower().translate(
                        str.maketrans('', '', string.punctuation + string.digits))
                except IndexError:
                    pre_edit_raw_string_tree_next = ""
                try:
                    pre_edit_raw_string_tree_before = terminals_in_tree[
                        pre_edit_idx - 1].lower().translate(
                        str.maketrans('', '', string.punctuation + string.digits))
                except IndexError:
                    pre_edit_raw_string_tree_before = ""

                print(edit_raw_string_transcript, edit_raw_string_tree_id, edit_raw_string_tree_next)
                # if edit_raw_string_transcript in edit_raw_string_tree \
                #         and pre_edit_raw_string_transcript in pre_edit_raw_string_tree:
                #         #and post_edit_raw_string_transcript in post_edit_raw_string_tree:
                #     idxs.append(id)
                #     print("exact match", edit_raw_string_transcript)
                #
                # else:

                try:
                    pre_edit_raw_string_tree = terminals_in_tree[pre_edit_idx - (
                                len(transcriptions) - len(
                            terminals_in_tree))].lower().translate(
                        str.maketrans('', '',
                                      string.punctuation + string.digits))
                except IndexError:
                    pre_edit_raw_string_tree = ""
                print("NEW", edit_raw_string_tree, edit_raw_string_transcript)
                print(pre_edit_raw_string_transcript, pre_edit_raw_string_tree)
                print(post_edit_raw_string_transcript, post_edit_raw_string_tree)
                # print(raw_string_transcript, raw_string_tree)
                if edit_raw_string_transcript in edit_raw_string_tree\
                        and pre_edit_raw_string_transcript in pre_edit_raw_string_tree\
                        and edit_raw_string_tree != edit_raw_string_tree_id:
                   idxs.append(
                       id - (len(transcriptions) - len(terminals_in_tree)))
                   print("not exact match", transcriptions[id],
                         terminals_in_tree[id - (len(transcriptions) - len(
                             terminals_in_tree))])
                elif edit_raw_string_transcript in edit_raw_string_tree\
                        and pre_edit_idx - (len(transcriptions) - len(terminals_in_tree)) < 0\
                        and edit_raw_string_tree != edit_raw_string_tree_id:
                   idxs.append(
                       id - (len(transcriptions) - len(terminals_in_tree)))
                   print("not exact match", transcriptions[id],
                         terminals_in_tree[id - (len(transcriptions) - len(
                             terminals_in_tree))])
                   print("border case")
                elif edit_raw_string_transcript in edit_raw_string_tree_id \
                        and pre_edit_raw_string_transcript in pre_edit_raw_string_tree_id\
                        and post_edit_raw_string_transcript in post_edit_raw_string_tree:
                    idxs.append(id)
                    print("exact match", edit_raw_string_transcript)
                elif edit_raw_string_transcript.endswith("nt") and edit_raw_string_tree_next != "" and terminals_in_tree[id+1] == "not":
                    idxs.append(id+1)
                    print("negation match", edit_raw_string_transcript,terminals_in_tree[id+1] )
                elif edit_raw_string_transcript in edit_raw_string_tree_next\
                        and pre_edit_raw_string_transcript in pre_edit_raw_string_tree_next:
                    idxs.append(
                        id -1)  # sometimes we need to skip a word (ah) that is not in the tree
                    print("next match", edit_raw_string_transcript, edit_raw_string_tree_next)
                elif edit_raw_string_transcript in edit_raw_string_tree_before\
                        and pre_edit_raw_string_transcript in pre_edit_raw_string_tree_before:
                    idxs.append(
                        id - 1)  # sometimes we need to skip a word (ah) that is not in the tree
                    print("before match", edit_raw_string_transcript, edit_raw_string_tree_before)
                elif count == 1:
                    print("one case")
                    if terminals_in_tree.index(orts[id].
                                                       lower().
                                                       translate(str.maketrans('', '', string.punctuation + string.digits))) <= id - (len(transcriptions) - len(terminals_in_tree)):

                        idxs.append(terminals_in_tree.index(orts[id].lower().translate(str.maketrans('', '', string.punctuation + string.digits))))


                else:
                    continue





    #
    # tree_index = 0
    # for i, word in enumerate(orts):
    #     print(word, terminals_in_tree[tree_index])
    #     if word == terminals_in_tree[tree_index]:
    #         print(word)
    #         tree_index += 1
    #         if '/-' in transcriptions[i] or '/+' in transcriptions[i]:
    #             idxs.append(terminals_in_tree.index(word.lower()))
    #             print("disfluency found")
    #     else:
    #         if orts[i+1] == terminals_in_tree[tree_index+1]:
    #             continue


    # for word in terminals_in_tree:
    #
    #     if word in false_starts or word in repetitions:
    # for i, word in enumerate(orts):
    #     if word in terminals_in_tree
        # if word == terminals_in_tree[i]:
        #     if '/-' in transcriptions[i] or '/+' in transcriptions[i]:
        #

    # idxs = [i for i, word in enumerate(words_in_transcription) if '/-' in word or '/+' in word]
    print("IDX", idxs)
    print(turn_id)

    return idxs

def get_sent_idxs_from_turn_idxs(turn_id, idxs, sent_trees, sent_ids):

    sentence_lengths = []
    for sent_tree in sent_trees:
        terminals_in_sent_tree = len([leaf.word for leaf in sent_tree.leaves()])
        sentence_lengths.append(terminals_in_sent_tree)

    idxs = sorted(set(idxs))

    idxs_copy = idxs.copy()
    sent_idx = defaultdict(list)
    for i, sent_id in enumerate(sent_ids):
        for j, idx in enumerate(idxs):
            print(sent_id)
            print((idx - sum(sentence_lengths[:i])))
            print(idx, sentence_lengths[:i])
            print(sentence_lengths[i])
            if idx not in sent_idx[sent_id] \
                    and (idx - sum(sentence_lengths[:i])) >= 0 \
                    and (idx - sum(sentence_lengths[:i])) < sentence_lengths[
                i]:
                sent_idx[sent_id].append((idx - sum(sentence_lengths[:i])))
                print("popping", idx)
                idxs_copy.remove(idx)
                print(idxs_copy)

    # remove negative (invalid) idxs
    idxs_copy = [item for item in idxs_copy if item >= 0]

    try:
        assert idxs_copy == []
    except AssertionError:
        print(turn_id, turn2sent[turn_id], idxs_copy)
        raise
    return sent_idx

def get_interruption_idx(tree, turn_id, sent_trees, sent_ids):
    if turn_id in disfluent_turn_ids:
        pass
    else:
        return []

    path_to_vm_annotations_1 = "/group/corporapublic/verbmobil/1.3"
    path_to_vm_annotations_2 = "/group/corpora/large4/verbmobil/2.3"

    terminals_in_tree = [leaf.word for leaf in tree.leaves()]
    terminals = len(terminals_in_tree)

    sentence_lengths = []
    for sent_tree in sent_trees:
        terminals_in_sent_tree = len([leaf.word for leaf in sent_tree.leaves()])
        sentence_lengths.append(terminals_in_sent_tree)
    idxs = []

    if len(turn_id.split("_")) > 3:
        turn_id = turn_id[:-4]
    if os.path.isfile(os.path.join(path_to_vm_annotations_1, turn_id[0:5],
                                   turn_id + ".par")):
        path_to_par = os.path.join(path_to_vm_annotations_1, turn_id[0:5],
                                   turn_id + ".par")
    elif os.path.isfile(os.path.join(path_to_vm_annotations_2, turn_id[0:5],
                                     turn_id + ".par")):
        path_to_par = os.path.join(path_to_vm_annotations_2, turn_id[0:5],
                                   turn_id + ".par")
    else:
        print(turn_id)
        raise FileNotFoundError
    # print(path_to_par)
    with open(path_to_par, "r", encoding="ISO-8859-1") as parfile:
        partext = parfile.read()
    tr2 = re.findall('TR2:\s\d+\s.*', partext)
    ort = re.findall('ORT:\s\d+\s.*', partext)
    tr2 = [line for line in tr2
           if not line.split("\t")[2].endswith("=/+")
           and not line.split("\t")[2].endswith("<%>")
           and not line.split("\t")[2].startswith("<%>")
           and not line.split("\t")[2].endswith("=/-") ]

    def replace_umlaut(transcription):
        transcription = transcription.replace('"o', 'o')
        transcription = transcription.replace('"a', 'a')
        transcription = transcription.replace('"u', 'u')
        return transcription

    def replace_trans(transcription, i, tr2, lang):
        if lang == "eng":
            if "don't" in transcription:# and terminals_in_tree[i] == "do" and terminals_in_tree[i+1] == "not":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "do\tnot/-"
                return "do\tnot"
            if "couldn't" in transcription:# and terminals_in_tree[i] == "do" and terminals_in_tree[i+1] == "not":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "could\tnot/-"
                return "could\tnot"
            elif "won't" in transcription:# and terminals_in_tree[i] == "would" and terminals_in_tree[i+1] == "not":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "would\tnot/-"
                return "would\tnot"
            elif "wouldn't" in transcription:# and terminals_in_tree[i] == "would" and terminals_in_tree[i+1] == "not":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "would\tnot/-"
                return "would\tnot"
            elif "won't" in transcription:# and terminals_in_tree[i] == "will" and terminals_in_tree[i+1] == "not":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "will\tnot/-"
                return "will\tnot"
            elif "shouldn't" in transcription:# and terminals_in_tree[i] == "will" and terminals_in_tree[i+1] == "not":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "should\tnot/-"
                return "should\tnot"
            elif "isn't" in transcription and terminals_in_tree[i] == "is" and terminals_in_tree[i+1] == "not":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "is\tnot/-"
                return "is\tnot"
            elif "aren't" in transcription:# and terminals_in_tree[i] == "is" and terminals_in_tree[i+1] == "not":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "are\tnot/-"
                return "are\tnot"
            elif "doesn't" in transcription and terminals_in_tree[i] == "does" and terminals_in_tree[i+1] == "not":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "does\tnot/-"
                return "does\tnot"
            elif "didn't" in transcription and terminals_in_tree[i] == "did" and terminals_in_tree[i+1] == "not":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "did\tnot/-"
                return "did\tnot"
            elif "can't" in transcription and terminals_in_tree[i] == "can" and terminals_in_tree[i+1] == "not":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "can\tnot/-"
                return "can\tnot"
            elif "within" in transcription and terminals_in_tree[i] == "with" and terminals_in_tree[i + 1] == "in":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "with\tin/-"
                return "with\tin"
            elif "Mister" in transcription and terminals_in_tree[i] == "mr":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "mr/-"
                return "mr"
            elif "Misses" in transcription:# and terminals_in_tree[i] == "mrs":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "mrs/-"
                return "mrs"
            elif "I'll" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "will/-"
                return "will"
            elif "deja-vu" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "deja\tvu/-"
                return "deja\tvu"
            elif "that's" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "this\tis/-"
                return "this\tis"
            elif i < terminals and terminals_in_tree[
                i] == "alright" and "all" in transcription \
                    and "right" in tr2[i + 1].split("\t")[2]:
                if "/+" in transcription or "/-" in transcription or "+/" in transcription or "-/" in transcription:
                    print(transcription)
                    return "alright/-"
                return "alright"
            elif "right" in transcription and "all" in tr2[i - 1].split("\t")[2] and not terminals_in_tree[
                i] == "right":
                return "$$$"
            elif transcription.startswith("afternoon") and terminals_in_tree[i] == "after" and terminals_in_tree[i + 1] == "noon":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "after\tnoon/-"
                return "after\tnoon"
            else:
                return transcription
        if lang == "ger":
            if "ver_" in transcription \
                    and "_schiedene" in tr2[i + 1].split("\t")[2]:
                if "/+" in transcription or "/-" in transcription or "+/" in transcription or "-/" in transcription:
                    return "verschiedene/-"
                return "verschiedene"
            elif "_schiedene" in transcription and "ver_" in tr2[i - 1].split("\t")[2]:
                return "$$$"
            elif "ne" == transcription and "eine" in terminals_in_tree:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "eine/-"
                return "eine"
            elif "mach" in transcription and "mache" in terminals_in_tree:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "mache/-"
                return "mache"
            elif "denk" in transcription and "denke" in terminals_in_tree:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "denke/-"
                return "denke"
            elif "kauf" in transcription and "kaufe" in terminals_in_tree:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "kaufe/-"
                return "kaufe"
            elif "schlag" in transcription and "schlage" in terminals_in_tree:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "schlage/-"
                return "schlage"
            elif 'w"ar' in transcription and "ware" in terminals_in_tree:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "ware/-"
                return "ware"
            elif 'k"onnt\'' in transcription and not transcription.endswith(">"):
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "konnte/-"
                return "konnte"
            elif 'h"att\'' in transcription and not transcription.endswith(">"):
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "hatte/-"
                return "hatte"
            elif 'w"urd' in transcription and "wurde" in terminals_in_tree and not transcription.endswith("en"):
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "wurde/-"
                return "wurde"
            elif 'kl"ar' in transcription:#and terminals_in_tree[i] == "ware":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "klare/-"
                return "klare"
            elif 'ruf' in transcription and "rufe" in terminals_in_tree:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "rufe/-"
                return "rufe"
            elif 'guck' in transcription and "gucke" in terminals_in_tree:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "gucke/-"
                return "gucke"
            elif 'kuck' in transcription and "kucke" in terminals_in_tree:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "kucke/-"
                return "kucke"
            elif "seh'" in transcription and transcription.startswith("s") and not transcription.endswith("n"):
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "sehe/-"
                return "sehe"
            elif 'm"ocht\'' in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "mochte/-"
                return "mochte"
            elif "organisier\'" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "organisiere/-"
                return "organisiere"
            elif "hab'" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "habe/-"
                return "habe"
            elif "sag'" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "sage/-"
                return "sage"
            elif "kenn'" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "kenne/-"
                return "kenne"
            elif "buch'" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "buche/-"
                return "buche"
            elif "nehm'" in transcription and not "nehmen" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "nehme/-"
                return "nehme"
            elif "reservier'" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "reserviere/-"
                return "reserviere"
            elif "werd'" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "werde/-"
                return "werde"
            elif "wollt'" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "wollte/-"
                return "wollte"
            elif "geh'" in transcription and not "gehen" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "gehe/-"
                return "gehe"
            elif "frag" in transcription and not "fragen" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "frage/-"
                return "frage"
            elif "grad" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "grade/-"
                return "grade"
            elif 'm"u"st' in transcription and "muste" in terminals_in_tree:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "muste/-"
                return "muste"
            elif 'mein' in transcription and "meine" in terminals_in_tree:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "meine/-"
                return "meine"
            elif "'s" in transcription and not "a'so" in transcription and not "das" in transcription:
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "es/-"
                return "es"
            elif "glei" in transcription:# and terminals_in_tree[i] == "es":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "gleich/-"
                return "gleich"

            elif "'nen" in transcription:
                # and not transcription.startswith("e") \
                #     and not transcription.startswith("b")\
                #     and not transcription.startswith("v")\
                #     and not transcription.startswith("#"):
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "einen/-"
                return "einen"
            elif "'nem" in transcription:
                # and not transcription.startswith("e") \
                #     and not transcription.startswith("b")\
                #     and not transcription.startswith("v")\
                #     and not transcription.startswith("#"):
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "einem/-"
                return "einem"
            elif "'ne" in transcription:
                # and not transcription.startswith("e") \
                #     and not transcription.startswith("b")\
                #     and not transcription.startswith("v")\
                #     and not transcription.startswith("#"):
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "eine/-"
                return "eine"
            elif "'n" in transcription.split("<")[0]:
                # and not transcription.startswith("e") \
                #     and not transcription.startswith("b")\
                #     and not transcription.startswith("v")\
                #     and not transcription.startswith("#"):
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "ein/-"
                return "ein"
            elif 'f"umunachtzig' in transcription:# and terminals_in_tree[i] == "es":
                if "/+" in transcription or "/-" in transcription:
                    return "funfundachtzig/-"
                return "funfundachtzig"
            elif transcription == "un'":# and terminals_in_tree[i] == "es":
                if "/+" in transcription or "/-" in transcription:
                    print(transcription)
                    return "und/-"
                return "und"
            elif "<Z>" in transcription:
                return transcription.replace("<Z>", "")
            else:
                return transcription

    transcriptions = [replace_trans(line.split("\t")[2], i, tr2, lang) for i,line in enumerate(tr2)]
    if "$$$" in transcriptions:
        transcriptions.remove("$$$")
    transcriptions = "\t".join(transcriptions)

    full_transcription = ""
    skip = False
    mismatch = False
    count_mismatch = 0
    # print(terminals_in_tree)
    # for i,line in enumerate(tr2):
    #     print(transcriptions.split("\t"))
    for i, transcription in enumerate(transcriptions.split("\t")):
        # if len(transcriptions.split("\t")) <= len(terminals_in_tree):
            # transcription = line.split("\t")[2]
            # print(transcription)
            # print(terminals_in_tree)
        if mismatch == True:
            i = i-count_mismatch
        if i == len(terminals_in_tree):
            break
        s = transcription.lower().translate(str.maketrans('', '', string.punctuation))
        st = terminals_in_tree[i].translate(str.maketrans('', '', string.punctuation))
        s = s.translate(str.maketrans('', '', string.digits))
        st = st.translate(str.maketrans('', '', string.digits))
        # print(s, st)
        # print(terminals_in_tree[i], s, terminals_in_tree[i] in s)
        if st == s.strip():
            full_transcription += transcription + "\t"
            skip = False

        elif len(s.split()) > 1 and st in s:
            full_transcription += transcription + "\t"
            skip = False

        elif st == "ahm":
            full_transcription += "ahm" + "\t"
            skip = False
        elif st == "ah":
            full_transcription += "ah" + "\t"
            skip = False
        elif st == "has":
            full_transcription += "has" + "\t"
            skip = False
        elif st == "will" and transcription == "would":
            full_transcription += "will" + "\t"
            skip = False
        elif st == "uns" and transcription == "und":
            full_transcription += "uns" + "\t"
            skip = False
        elif st == "und" and transcription == "u":
            full_transcription += "und" + "\t"
            skip = False
        elif st == "recht" and transcription == "r":
            full_transcription += "recht" + "\t"
            skip = False
        elif st == "irgendwelche" and transcription == "i":
            full_transcription += "irgendwelche" + "\t"
            skip = False
        elif st == "wir" and transcription == "wi":
            full_transcription += "wir" + "\t"
            skip = False
        elif st == "eine" and "ein" in transcription:
            full_transcription += "eine" + "\t"
            skip = False
        elif st == "dampfbad" and transcription == "Dampfba":
            full_transcription += "dampfbad" + "\t"
            skip = False
        elif st == "unserem" and terminals_in_tree[i+1] == "nachsten" and transcription == "und":
            full_transcription += "unserem" + "\t"
            skip = False
        elif st == "nachsten" and terminals_in_tree[i-1] == "unserem" and transcription == "ein":
            full_transcription += "nachsten" + "\t"
            skip = False
        elif st == "unsrer" and transcription == "und":
            full_transcription += "unserer" + "\t"
            skip = False
        elif st == "losgehen" and "los" in transcription:
            full_transcription += "losgehen" + "\t"
            skip = False
        elif st == "also" and terminals_in_tree[i-1] == "also" and transcription == "es":
            full_transcription += "also" + "\t"
            skip = False
        else:
            mismatch = True
            count_mismatch += 1

    # false_starts = re.findall("-/(.*?)/-", full_transcription)
    # repetitions = re.findall("\+/(.*?)/\+", full_transcription)

    try:
        assert terminals == len(full_transcription.strip().split("\t"))
    except AssertionError:
        # print(ort)
        print(turn_id)
        print(terminals)
        print(len(full_transcription.strip().split("\t")))
        print(terminals_in_tree)
        print(transcriptions.split("\t"))
        print(full_transcription.strip().split("\t"))
        print(full_transcription)
        raise

    words_in_transcription = full_transcription.strip().split("\t")
    idxs = [i for i, word in enumerate(words_in_transcription) if '/-' in word or '/+' in word]
    # for id in idxs:
    #     print(full_transcription.strip().split("\t")[id])

    # if turn_id in disfluent_turn_ids and not idxs:
    #     print(f"Disfluent turn not recognized: {turn_id}")

    idxs_copy = idxs.copy()
    sent_idx = defaultdict(list)
    for i, sent_id in enumerate(sent_ids):
        for j, idx in enumerate(idxs):
            # if idx < sentence_lengths[i]:
            #     if idx not in sent_idx[sent_id]:
            #         try:
            #             assert words_in_transcription[idx].lower().translate(str.maketrans('', '', string.punctuation+string.digits)) == [leaf.word for leaf in sent_trees[i].leaves()][idx].lower().translate(str.maketrans('', '', string.punctuation+string.digits))
            #         except AssertionError:
            #             print(sentence_lengths[i], i)
            #             print(turn_id, turn2sent[turn_id], idxs)
            #             print(words_in_transcription[idx].lower().translate(str.maketrans('', '', string.punctuation+string.digits))
            #                   , [leaf.word for leaf in sent_trees[i].leaves()][idx])
            #             print(idx)
            #             raise
            #         sent_idx[sent_id].append(idx)
            #         idxs_copy.pop(j)
            # else:
            print(sent_id)
            print((idx - sum(sentence_lengths[:i])))
            print(idx, sentence_lengths[:i])
            print(sentence_lengths[i])
            if idx not in sent_idx[sent_id] \
                    and (idx - sum(sentence_lengths[:i])) >= 0 \
                    and (idx - sum(sentence_lengths[:i])) < sentence_lengths[i]:
                try:
                    assert [leaf.word for leaf in sent_trees[i].leaves()][idx - sum(sentence_lengths[:i])].lower().translate(str.maketrans('', '', string.punctuation+string.digits)) in words_in_transcription[idx].lower().translate(str.maketrans('', '', string.punctuation+string.digits))
                except AssertionError:
                    print(sentence_lengths[i], i, sentence_lengths[:i])
                    print(turn_id, turn2sent[turn_id], idxs)
                    print(words_in_transcription[idx].lower().translate(str.maketrans('', '', string.punctuation+string.digits)),
                          [leaf.word for leaf in sent_trees[i].leaves()][
                              idx - sum(sentence_lengths[:i])])
                    print(idx,idx - sum(sentence_lengths[:i]) )
                    raise
                sent_idx[sent_id].append((idx - sum(sentence_lengths[:i])))
                print("popping", idx)
                idxs_copy.remove(idx)
                print(idxs_copy)

    try:
        assert idxs_copy == []
    except AssertionError:
        print(turn_id, turn2sent[turn_id], idxs_copy)
        raise
    return idxs, sent_idx

def get_break_pauses(idx,pauses):
    aft = pauses['pause_aft']
    break_pauses = [aft[i] for i in idx]
    return break_pauses

def count_pauses(pauses):
    pause_counts = {}
    for pause in pauses:
        if pause in pause_counts:
            pause_counts[pause] += 1
        else:
            pause_counts[pause] = 1
    return pause_counts

def count_leaves(constituent):
    constituent = constituent.replace('(','').replace(')','').replace('£','').replace('$','')
    constituent = ''.join(ch for ch in constituent if not ch.isupper() and not ch == "-")
    return len(constituent.split())


def get_edit_idxs(tree):
    num_leaves = len(list(tree.leaves()))
    tree_string = tree.linearize()
    
    if 'EDITED' in tree_string:
        pre_edit_idx = []
        post_edit_idx = []

        tree_string = tree_string.replace('EDITED','£')
        for i,char in enumerate(tree_string):
            if char == '£':
                prefix = tree_string[:i]
                pre_edit_idx.append(count_leaves(prefix)-1)
                edited_span = []
                open_paren_stack = ['(']
                j = 1
                while open_paren_stack:
                    next_char = tree_string[i+j]
                    edited_span.append(next_char)
                    if next_char == '(':
                        open_paren_stack.append('(')
                    elif next_char == ')':
                        open_paren_stack.pop()
                    j += 1
                
                edited_span = ''.join(edited_span)
                post_edit_idx.append(count_leaves(prefix)+count_leaves(edited_span)-1)
        return pre_edit_idx,post_edit_idx
    return None


def get_VF_idxs(tree):
    num_leaves = len(list(tree.leaves()))
    tree_string = tree.linearize()

    if 'VF' in tree_string:
        pre_edit_idx = []
        post_edit_idx = []

        tree_string = tree_string.replace('VF ', '£ ')
        for i, char in enumerate(tree_string):
            if char == '£':
                prefix = tree_string[:i]
                pre_edit_idx.append(count_leaves(prefix) - 1)
                edited_span = []
                open_paren_stack = ['(']
                j = 1
                while open_paren_stack:
                    next_char = tree_string[i + j]
                    edited_span.append(next_char)
                    if next_char == '(':
                        open_paren_stack.append('(')
                    elif next_char == ')':
                        open_paren_stack.pop()
                    j += 1

                edited_span = ''.join(edited_span)
                post_edit_idx.append(
                    count_leaves(prefix) + count_leaves(edited_span) - 1)
        return post_edit_idx
    return None

def get_ITJ_idxs_eng(tree):
    num_leaves = len(list(tree.leaves()))
    tree_string = tree.linearize()

    if 'CNJ' in tree_string:
        pre_edit_idx = []
        post_edit_idx = []

        tree_string = tree_string.replace('CNJ', '£')
        for i, char in enumerate(tree_string):
            if char == '£':
                prefix = tree_string[:i]
                pre_edit_idx.append(count_leaves(prefix) - 1)
                edited_span = []
                open_paren_stack = ['(']
                j = 1
                while open_paren_stack:
                    next_char = tree_string[i + j]
                    edited_span.append(next_char)
                    if next_char == '(':
                        open_paren_stack.append('(')
                    elif next_char == ')':
                        open_paren_stack.pop()
                    j += 1

                edited_span = ''.join(edited_span)
                post_edit_idx.append(
                    count_leaves(prefix) + count_leaves(edited_span) - 1)
        return post_edit_idx
    return None

def get_ITJ_idxs_ger(tree):
    num_leaves = len(list(tree.leaves()))
    tree_string = tree.linearize()

    if 'KOORD' in tree_string:
        pre_edit_idx = []
        post_edit_idx = []

        tree_string = tree_string.replace('KOORD', '£')
        for i, char in enumerate(tree_string):
            if char == '£':
                prefix = tree_string[:i]
                pre_edit_idx.append(count_leaves(prefix) - 1)
                edited_span = []
                open_paren_stack = ['(']
                j = 1
                while open_paren_stack:
                    next_char = tree_string[i + j]
                    edited_span.append(next_char)
                    if next_char == '(':
                        open_paren_stack.append('(')
                    elif next_char == ')':
                        open_paren_stack.pop()
                    j += 1

                edited_span = ''.join(edited_span)
                post_edit_idx.append(
                    count_leaves(prefix) + count_leaves(edited_span) - 1)
        return post_edit_idx
    return None

def get_NF_idxs(tree):
    num_leaves = len(list(tree.leaves()))
    tree_string = tree.linearize()

    if 'NF' in tree_string:
        pre_edit_idx = []
        post_edit_idx = []

        # if "(NF " in tree_string:
        #     print(tree_string)
        #     tree_string = tree_string.replace('NF', '£')
        #     print(tree_string)


        tree_string = tree_string.replace('(NF', '(£')

        # tree_string = re.sub('NF', r'\1£', tree_string)

        for i, char in enumerate(tree_string):
            if char == '£':
                prefix = tree_string[:i]
                pre_edit_idx.append(count_leaves(prefix) - 1)
                edited_span = []
                open_paren_stack = ['(']
                j = 1
                while open_paren_stack:
                    next_char = tree_string[i + j]
                    edited_span.append(next_char)
                    if next_char == '(':
                        open_paren_stack.append('(')
                    elif next_char == ')':
                        open_paren_stack.pop()
                    j += 1

                edited_span = ''.join(edited_span)
                post_edit_idx.append(
                    count_leaves(prefix) + count_leaves(edited_span) - 1)
        return pre_edit_idx
    return None

def intersection_size(lst1, lst2):
    return len(list(set(lst1) & set(lst2)))

def main():
    # pred_trees,ids = trees.load_trees_with_idx(pred_tree_file,id_file)
    gold_trees,ids = trees.load_trees_with_idx(gold_tree_file,id_file)

    sentence_trees, sentence_ids = trees.load_trees_with_idx(sentence_tree_file, sentence_id_file, strip_top = False)

    sent_edit_final_idxs = defaultdict(list)
    turn_med_breaks = 0
    sent_break_pauses = []
    VF_pauses = []
    VF_counter = 0

    NF_pauses = []
    NF_counter = 0

    ITJ_pauses = []
    ITJ_counter = 0

    koord_turns = []

    interruption_point_pauses = []
    interruption_points = 0

    pre_edit_breaks = 0
    post_edit_breaks = 0
    VF_breaks = 0
    NF_breaks = 0

    total_turn_medial_positions = 0 # number of positions between words that sentence breaks could go. sum(len(turn)-1) over all turns
    
    total_pred_breaks = 0
    total_gold_edits = 0
    
    for i, tree in enumerate(gold_trees):
        sentence_trees_in_turn = []
        for su in turn2sent[ids[i]]:
            sentence_trees_in_turn.append(sentence_trees[sentence_ids.index(su)])

        total_turn_medial_positions += (get_wd_len(tree)-1)

        break_idxs = get_sent_break_idx(tree, sentence_trees_in_turn)
        old_break_idxs = get_sent_break_idx_old(tree)
        print(old_break_idxs, break_idxs)
        assert break_idxs == old_break_idxs
        # print(break_idxs, turn2sent[ids[i]])


        VF_idx = get_VF_idxs(tree)
        NF_idx = get_NF_idxs(tree)
        if VF_idx:
            print("VF IDS:", VF_idx, ids[i], tree.linearize())
            try:
                VF_pauses.extend(
                    get_break_pauses(VF_idx, turn2pause[ids[i]]))
            except:
                print(VF_idx, ids[i])
                raise
            VF_counter += len(VF_idx)

        if NF_idx:
            try:
                get_break_pauses(NF_idx, turn2pause[ids[i]])
            except:
                print(NF_idx, ids[i], tree.linearize())
                raise
            NF_pauses.extend(
                get_break_pauses(NF_idx, turn2pause[ids[i]]))
            NF_counter += len(NF_idx)

        if break_idxs:
            # pauses = get_break_pauses(break_idxs[:-1], turn2pause[ids[i]])
            # if 5 in pauses:
            #     print("5 in ", ids[i], turn2sent[ids[i]])
            sent_break_pauses.extend(get_break_pauses(break_idxs[:-1], turn2pause[ids[i]]))
            turn_med_breaks += len(break_idxs[:-1])



        interruption_point_idx = get_interruption_idx2(tree, ids[i])



        if break_idxs and interruption_point_idx:
            post_edit_breaks += intersection_size(interruption_point_idx, break_idxs[:-1])

        if break_idxs and VF_idx:
            VF_breaks += intersection_size(VF_idx, break_idxs[:-1])

        if break_idxs and NF_idx:
            NF_breaks += intersection_size(NF_idx, break_idxs[:-1])

        sent_idxs = get_sent_idxs_from_turn_idxs(ids[i], interruption_point_idx, sentence_trees_in_turn, turn2sent[ids[i]])

        sent_edit_final_idxs = {**sent_edit_final_idxs, **sent_idxs}


        # interruption_point_idx, sent_idxs = get_interruption_idx(tree, ids[i], sentence_trees_in_turn, turn2sent[ids[i]])
        # print("OLD IDX", interruption_point_idx)
        # if not interruption_point_idx == interruption_point_idx2:
        #     print("OLD IDX", interruption_point_idx)
        #     print("NEW IDX", interruption_point_idx2)
        #     raise ValueError
        # if not sent_idxs == sent_idxs2:
        #     print("OLD IDX", sent_idxs.items())
        #     print("NEW IDX", sent_idxs2.items())
        #     raise ValueError
        # if interruption_point_idx:
        #     print(ids[i], turn2sent[ids[i]], interruption_point_idx)
        #     print(sent_idxs.items())

        # print(interruption_point_idx)
        # print(get_break_pauses(interruption_point_idx, turn2pause[ids[i]]))
        # print(turn2pause[ids[i]])
        interruption_point_pauses.extend(get_break_pauses(interruption_point_idx, turn2pause[ids[i]]))
        interruption_points += len(interruption_point_idx)

        if lang == "eng":
            itj_idxs = get_ITJ_idxs_eng(tree)
            if break_idxs and itj_idxs:
                for b in break_idxs:
                    try:
                        itj_idxs.remove(b)
                    except:
                        pass
        if lang == "ger":
            itj_idxs = get_ITJ_idxs_ger(tree)
            if break_idxs and itj_idxs:
                for b in break_idxs:
                    try:
                        itj_idxs.remove(b)
                    except:
                        pass

        if itj_idxs:
            try:
                ITJ_pauses.extend(
                    get_break_pauses(itj_idxs, turn2pause[ids[i]]))
            except:
                print(itj_idxs, ids[i],tree.linearize())
                print(len(turn2pause[ids[i]]['pause_aft']))
                print(turn2pause[ids[i]]['pause_aft'])
                raise
            ITJ_counter += len(itj_idxs)
            if 5 in get_break_pauses(itj_idxs, turn2pause[ids[i]]):
                koord_turns.append(ids[i])

    pause_counts = count_pauses(sent_break_pauses)
    interruption_point_pause_counts = count_pauses(interruption_point_pauses)
    VF_pause_counts = count_pauses(VF_pauses)
    NF_pause_counts = count_pauses(NF_pauses)
    ITJ_pause_counts = count_pauses(ITJ_pauses)

    #     gold_edit_idxs = get_edit_idxs(gold_trees[i])
    #     if gold_edit_idxs: total_gold_edits += len(gold_edit_idxs[0])
    #     if break_idxs:
    #         total_pred_breaks += len(break_idxs)-1
    #         turn_id = ids[i]
    #         sent_break_pauses.extend(get_break_pauses(break_idxs[:-1],turn2pause[turn_id])) #Q: what pauses happen at sent breaks?
    #         turn_med_breaks += len(break_idxs[:-1])
    #     if gold_edit_idxs and break_idxs:
    #         pre_edit_idxs = gold_edit_idxs[0]
    #         post_edit_idxs = gold_edit_idxs[1]
    #
    #         pre_edit_breaks += intersection_size(pre_edit_idxs,break_idxs)
    #         post_edit_breaks += intersection_size(post_edit_idxs,break_idxs)
    #
    #
    # pause_counts = count_pauses(sent_break_pauses)
    # print(pred_tree_file.split('/')[-1])

    sent_edit_final_idxs = defaultdict(list, sent_edit_final_idxs)
    # with open('sent_edit_final_idxs_ger_dev.pickle', 'wb') as handle:
    #     pickle.dump(sent_edit_final_idxs, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print('Pauses at turn-internal sentence breaks:')
    print(pause_counts)
    print('Distribution of Pauses at turn-internal sentence breaks:')
    print([(pause, count / turn_med_breaks) for pause, count in
           pause_counts.items()])
    print(f'Turn-medial breaks: {turn_med_breaks}')
    # > 0.05s = cat 3,4,5
    print(f'Percentage of SU boundaries with long pauses: '
          f'{100 * (sum([pause_counts[x] for x in [3,4,5]])/turn_med_breaks)} %')
    print(f"Total interruption points: {interruption_points}")
    print(f"Pauses at interruption points:")
    print(interruption_point_pause_counts)
    print(f"Distribution of Pauses at interruption points:")
    print([(pause, count/interruption_points) for pause, count in interruption_point_pause_counts.items()])
    print(f'Percentage of IPs with long pauses: '
          f'{100 * (sum([interruption_point_pause_counts[x] for x in [3, 4, 5]]) / interruption_points)} %')
    print('Pauses at the end of VF:')
    print(VF_pause_counts)
    print('Distribution of Pauses after VFs:')
    print([(pause, count / VF_counter) for pause, count in
           VF_pause_counts.items()])
    print(sum([count / VF_counter for pause, count in
           VF_pause_counts.items()]))
    print('Pauses before NF:')
    print(NF_pause_counts)
    print('Distribution of Pauses before NFs:')
    print([(pause, count / NF_counter) for pause, count in
           NF_pause_counts.items()])
    print(sum([count / NF_counter for pause, count in
           NF_pause_counts.items()]))
    print('Pauses after ITJ:')
    print(ITJ_pause_counts)
    print('Distribution of Pauses after ITJs:')
    print([(pause, count / ITJ_counter) for pause, count in
           ITJ_pause_counts.items()])
    print(sum([count / ITJ_counter for pause, count in
           ITJ_pause_counts.items()]))
    print(koord_turns)
    # print(f'Total edits: {total_gold_edits}')
    # print(f'Predicted breaks pre-edits: {pre_edit_breaks}')
    # print(f'Predicted breaks post-edit: {post_edit_breaks}')
    # print(f'Total turn medial positions: {total_turn_medial_positions}')
    print("================================================")
    print("Total predicted boundaries: ", turn_med_breaks)
    print("Predicted boundaries at disfluency: ", post_edit_breaks)
    print("Predicted boundaries after VF: ", VF_breaks)
    print("Predicted boundaries before NF: ", NF_breaks)

def output():
    pred_trees, pred_ids = trees.load_trees_with_idx(pred_tree_file,id_file)
    gold_trees, ids = trees.load_trees_with_idx(gold_tree_file, id_file)

    sentence_trees, sentence_ids = trees.load_trees_with_idx(
        sentence_tree_file, sentence_id_file, strip_top=False)

    sent_edit_final_idxs = defaultdict(list)
    turn_med_breaks = 0
    sent_break_pauses = []
    VF_pauses = []
    VF_counter = 0

    NF_pauses = []
    NF_counter = 0

    interruption_point_pauses = []
    interruption_points = 0

    pre_edit_breaks = 0
    post_edit_breaks = 0
    VF_breaks = 0
    NF_breaks = 0

    total_turn_medial_positions = 0  # number of positions between words that sentence breaks could go. sum(len(turn)-1) over all turns

    total_pred_breaks = 0
    total_gold_edits = 0

    for i, (tree, pred_tree) in enumerate(zip(gold_trees, pred_trees)):
        sentence_trees_in_turn = []
        for su in turn2sent[ids[i]]:
            sentence_trees_in_turn.append(
                sentence_trees[sentence_ids.index(su)])

        total_turn_medial_positions += (get_wd_len(tree) - 1)

        break_idxs = get_sent_break_idx_old(pred_tree)

        VF_idx = get_VF_idxs(tree)
        NF_idx = get_NF_idxs(tree)
        if VF_idx:
            print("VF IDS:", VF_idx, ids[i], tree.linearize())
            try:
                VF_pauses.extend(
                    get_break_pauses(VF_idx, turn2pause[ids[i]]))
            except:
                print(VF_idx, ids[i])
                raise
            VF_counter += len(VF_idx)

        if NF_idx:
            try:
                get_break_pauses(NF_idx, turn2pause[ids[i]])
            except:
                print(NF_idx, ids[i], tree.linearize())
                raise
            NF_pauses.extend(
                get_break_pauses(NF_idx, turn2pause[ids[i]]))
            NF_counter += len(NF_idx)

        if break_idxs:
            # pauses = get_break_pauses(break_idxs[:-1], turn2pause[ids[i]])
            # if 5 in pauses:
            #     print("5 in ", ids[i], turn2sent[ids[i]])
            sent_break_pauses.extend(
                get_break_pauses(break_idxs[:-1], turn2pause[ids[i]]))
            turn_med_breaks += len(break_idxs[:-1])

        interruption_point_idx = get_interruption_idx2(tree, ids[i])

        if break_idxs and interruption_point_idx:
            post_edit_breaks += intersection_size(interruption_point_idx,
                                                  break_idxs[:-1])

        if break_idxs and VF_idx:
            VF_breaks += intersection_size(VF_idx, break_idxs[:-1])

        if break_idxs and NF_idx:
            NF_breaks += intersection_size(NF_idx, break_idxs[:-1])

        sent_idxs = get_sent_idxs_from_turn_idxs(ids[i],
                                                 interruption_point_idx,
                                                 sentence_trees_in_turn,
                                                 turn2sent[ids[i]])

        sent_edit_final_idxs = {**sent_edit_final_idxs, **sent_idxs}

        interruption_point_pauses.extend(
            get_break_pauses(interruption_point_idx, turn2pause[ids[i]]))
        interruption_points += len(interruption_point_idx)

    pause_counts = count_pauses(sent_break_pauses)
    interruption_point_pause_counts = count_pauses(interruption_point_pauses)
    VF_pause_counts = count_pauses(VF_pauses)
    NF_pause_counts = count_pauses(NF_pauses)

    print("================================================")
    print("Total predicted boundaries: ", turn_med_breaks)
    print("Predicted boundaries at disfluency: ", post_edit_breaks)
    print("Predicted boundaries after VF: ", VF_breaks)
    print("Predicted boundaries before NF: ", NF_breaks)


if __name__=='__main__':
    main() # for gold standard
    # output() # for output