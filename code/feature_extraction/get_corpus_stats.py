import trees as T
import pickle
import numpy as np
import os
import re
from collections import  Counter

def get_turn_stats(lang):
    path_to_vm_annotations_1 = "/group/corporapublic/verbmobil/1.3"
    path_to_vm_annotations_2 = "/group/corpora/large4/verbmobil/2.3"
    out_dir = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_{}_turns/".format(
        lang)
    if lang == "eng":
        path_to_input_features = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features"
    elif lang == "ger":
        path_to_input_features = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features"
    else:
        raise ValueError
    # load turn2sent : get #SUs per turn
    with open(os.path.join(path_to_input_features, "turn2sent.pickle"),
              "rb") as f:
        turn2sent = pickle.load(f)

    with open(os.path.join(out_dir, "stats.txt"), "w") as f:

        for split in ["train", "dev", "test"]:
            path_to_trees = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_{}_turns/turn_{}.trees".format(lang, split)
            path_to_sent_ids = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_{}_turns/turn_{}_sent_ids.txt".format(lang, split)

            # get trees and ids of turns
            trees, sent_ids = T.load_trees_with_idx(path_to_trees,
                                                    path_to_sent_ids,
                                                    strip_top=False)
            tokens = []
            sus = []
            disfluencies = []
            disfluent_turns = 0
            for turn_id in turn2sent:
                if turn_id in sent_ids:
                    index_of_turn_id = sent_ids.index(turn_id)
                    sus.append(len(turn2sent[turn_id]))
                    if len(turn2sent[turn_id]) == 18:
                        print(turn_id)

                else:
                    continue
                tree = trees[index_of_turn_id]
                # print(tree)
                transcription = []

                for child in tree.leaves():
                    try:
                        word = child.word
                        # print(word)
                        transcription.append(word)
                    except AttributeError:
                        # print(tree)
                        pass
                tokens.append(len(transcription))
                # print(split, np.mean(np.array(tokens)), np.mean(np.array(sus)))
                # do something with par files to get info about disfluencies
                if len(turn_id.split("_")) > 3:
                    turn_id = turn_id[:-4]
                if os.path.isfile(os.path.join(path_to_vm_annotations_1,turn_id[0:5], turn_id + ".par")):
                    path_to_par = os.path.join(path_to_vm_annotations_1, turn_id[0:5],turn_id + ".par")
                elif os.path.isfile(os.path.join(path_to_vm_annotations_2,turn_id[0:5], turn_id + ".par")):
                    path_to_par = os.path.join(path_to_vm_annotations_2, turn_id[0:5], turn_id + ".par")
                else:
                    print(turn_id)
                    raise FileNotFoundError
                # print(path_to_par)
                with open(path_to_par, "r", encoding="ISO-8859-1") as parfile:
                    partext = parfile.read()
                tr2 = re.findall('TR2:\s\d+\s.*', partext)
                full_transcription = ""
                for line in tr2:
                    transcription = line.split("\t")[2]
                    full_transcription += transcription + " "
                false_starts = re.findall("-/(.*?)/-", full_transcription)
                repetitions = re.findall("\+/(.*?)/\+", full_transcription)
                # filled_pauses = re.findall('<((?:uhm|uh|hm|hes|"ah|"ahm))>',
                #                            full_transcription)
                # print(full_transcription)
                if false_starts or repetitions:
                    disfluent_turns += 1
                    disfluencies.append(len(false_starts) + len(repetitions))
                else:
                    disfluencies.append(0)

            f.write("Stats for: "+ split + "\n")
            f.write("Mean number of tokens per turn: " + str(np.mean(np.array(tokens))) + "\n")
            f.write("Mean number of SUs per turn: " + str(
                np.mean(np.array(sus))) + "\n")
            f.write("SUs per turn: " + str(
                Counter(sus)) + "\n")
            f.write("Mean number of disfluencies per turn: " + str(
                np.mean(np.array(disfluencies))) + "\n")
            f.write("#Turns with disfluencies: " + str(
                disfluent_turns) + "\n")
            f.write("Percentage of disfluent turns: " + str(
                disfluent_turns/len(sent_ids)) + "\n")
            f.write("================================="+ "\n")



get_turn_stats("eng")
get_turn_stats("ger")


def get_sentence_stats():
    # lang = "eng"
    lang = "ger"

    with open('sentence_id2recording_{}_new.pickle'.format(lang), 'rb') as handle:
        sentence_id2recording = pickle.load(handle)

    with open('sentence_id2speaker_{}.pickle'.format(lang), 'rb') as handle:
        sentence_id2speaker = pickle.load(handle)

    # take [:150] for sample data
    wav_files = list(sentence_id2recording.items())

    def get_stats(path_to_trees, path_to_sent_ids):
        tokens = []
        speakers = set()
        scenarios = set()

        trees, sent_ids = T.load_trees_with_idx(path_to_trees,
                                                    path_to_sent_ids,
                                                    strip_top=False)

        for sentence_id, file in wav_files:
            if file.endswith('.wav') and sentence_id in sent_ids:
                index_of_sent_id = sent_ids.index(sentence_id)
                speakers.add(sentence_id2speaker[sentence_id])

                if "1.3" in file:
                    scenarios.add("d")
                elif "2.3" in file:
                    # 5th character = scenario
                    scenarios.add(os.path.splitext(os.path.basename(file))[0][4])
                else:
                    raise ValueError

                tree = trees[index_of_sent_id]
                # print(tree)
                transcription = []

                for child in tree.leaves():
                    try:
                        word = child.word
                        # print(word)
                        transcription.append(word)
                    except AttributeError:
                        # print(tree)
                        pass
                tokens.append(len(transcription))
            # print(tokens)
        return tokens, speakers, scenarios

    train_scenarios = set()
    train_speakers = set()

    # out_dir = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/"
    out_dir = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/"

    with open(os.path.join(out_dir, "stats.txt"), "w") as f:
        for split in ["train", "dev", "test"]:
            # English data
            # lang = "eng"
            #
            # path_to_trees = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/new_trees/{}.trees".format(split)
            # path_to_sent_ids = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/{}_sent_ids.txt".format(split)

            lang = "ger"
            path_to_trees = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/new_trees/{}.trees".format(split)
            path_to_sent_ids = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/{}_sent_ids.txt".format(split)

            tokens, speakers, scenarios = get_stats(path_to_trees, path_to_sent_ids)

            if split == "train":
                train_speakers = speakers
                train_scenarios = scenarios


            f.write("Statistics for: "+ split + "\n")
            f.write("Mean, std sentence length in tokens: "+ str(np.mean(np.array(tokens)))+ ", "+str(np.std(np.array(tokens)))+ "\n")
            f.write("Count of one token sentences: "+ str(tokens.count(1))+ "\n")
            f.write("Max sentence length: "+ str(max(tokens))+ "\n")
            f.write("Number of speakers: "+ str(len(speakers))+ "\n")
            f.write("Scenarios: "+str(scenarios)+ "\n")
            f.write("Speaker overlap with train set: "+str(len(train_speakers.intersection(speakers)))+ "\n")
            f.write("Scenario overlap with train set: "+str(train_scenarios.intersection(scenarios))+ "\n")
            f.write("================================="+ "\n")