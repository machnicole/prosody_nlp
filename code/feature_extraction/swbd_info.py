from xml.etree import cElementTree as etree
import os
import pickle
from collections import Counter
import trees as T
import numpy as np

def get_turn_stats():
    in_dir = "/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed"
    out_dir = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/input_features"
    # load turn2sent : get #SUs per turn
    with open(os.path.join("/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features",
                           "turn2sent.pickle"),
              "rb") as f:
        turn2sent = pickle.load(f)

    with open(os.path.join(out_dir, "turn_stats.txt"), "w") as f:

        for split in ["train", "dev", "test"]:
            path_to_trees = os.path.join(in_dir, "turn_{}_medium.trees".format(split))
            path_to_sent_ids = os.path.join(in_dir, "turn_{}_sent_ids_medium.txt".format(split))

            # get trees and ids of turns
            trees, sent_ids = T.load_trees_with_idx(path_to_trees,
                                                    path_to_sent_ids,
                                                    strip_top=True)
            tokens = []
            sus = []
            disfluencies = []
            disfluent_turns = 0

            for turn_id in turn2sent:
                disfluencies_in_tree = 0
                if turn_id in sent_ids:
                    index_of_turn_id = sent_ids.index(turn_id)
                    sus.append(len(turn2sent[turn_id]))

                else:
                    continue
                tree = trees[index_of_turn_id]
                # print(tree)
                transcription = []

                linearized_tree = tree.linearize()
                disfluencies_in_tree = linearized_tree.count("EDITED")

                for child in tree.leaves():
                    try:
                        word = child.word
                        # print(word)
                        transcription.append(word)
                    except AttributeError:
                        # print(tree)
                        pass
                tokens.append(len(transcription))
                if disfluencies_in_tree != 0:
                    disfluent_turns += 1
                disfluencies.append(disfluencies_in_tree)

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

get_turn_stats()

def get_stats():
    dialogues_loc = "/afs/inf.ed.ac.uk/group/corpora/large/switchboard/nxt/xml/corpus-resources/dialogues.xml"
    dialogues_tree = etree.parse(open(dialogues_loc))

    total_scenarios = []

    train_scenarios = set()
    train_speakers = set()
    test_scenarios = set()
    test_speakers = set()
    dev_scenarios = set()
    dev_speakers = set()
    conv2topic = dict()

    for dialogue_xml in dialogues_tree.iter('dialogue'):
        conv = dialogue_xml.get("swbdid")
        # print(conv)
        topic_child = dialogue_xml.getchildren()[0]
        # print(child.get('href').split('#')[1])
        spkrA_child = dialogue_xml.getchildren()[1]
        spkrB_child = dialogue_xml.getchildren()[2]
        total_scenarios.append(topic_child.get('href').split('#')[1])
        conv2topic[conv] = topic_child.get('href').split('#')[1]
        if 4518 < int(conv) <= 4936: # dev
            dev_scenarios.add(topic_child.get('href').split('#')[1])
            dev_speakers.add(spkrA_child.get('href').split('#')[1])
            dev_speakers.add(spkrB_child.get('href').split('#')[1])
        elif 4003 < int(conv) <= 4153: # eval
            test_scenarios.add(topic_child.get('href').split('#')[1])
            test_speakers.add(spkrA_child.get('href').split('#')[1])
            test_speakers.add(spkrB_child.get('href').split('#')[1])
        elif int(conv[0]) == 2 or int(conv[0]) == 3: # train
            train_scenarios.add(topic_child.get('href').split('#')[1])
            train_speakers.add(spkrA_child.get('href').split('#')[1])
            train_speakers.add(spkrB_child.get('href').split('#')[1])
        else:
            continue
    out_dir = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/input_features"

    with open(os.path.join(out_dir, "stats.txt"), "w") as f:
        f.write("Train scenarios: "+ str(len(train_scenarios)) +"\n")
        f.write("Dev scenarios: " + str(len(dev_scenarios))+"\n")
        f.write("Test scenarios: " + str(len(test_scenarios))+"\n")
        f.write("Train-Dev overlap in scenarios: " + str(len(train_scenarios.intersection(dev_scenarios)))+"\n")
        f.write("Train-Test overlap in scenarios: " + str(len(train_scenarios.intersection(test_scenarios)))+"\n")
        f.write("==================================\n")
        f.write("Train speakers: "+ str(len(train_speakers))+"\n")
        f.write("Dev speakers: " + str(len(dev_speakers))+"\n")
        f.write("Test speakers: " + str(len(test_speakers))+"\n")
        f.write("Train-Dev overlap in speakers: " + str(len(train_speakers.intersection(dev_speakers)))+"\n")
        f.write("Train-Test overlap in speakers: " + str(len(train_speakers.intersection(test_speakers)))+"\n")
        f.write("==================================\n")
        f.write(str(Counter(total_scenarios).most_common(10)))

    with open(os.path.join(out_dir, "conv2topic.pickle"), "wb") as f:
        pickle.dump(conv2topic, f)
# get_stats()
def get_sents(ptb_files):
    out_dir = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/input_features"

    with open(os.path.join(out_dir, "conv2topic.pickle"), "rb") as f:
        conv2topic = pickle.load(f)
    sent_ids = []
    most_common = {'id(top353)', 'id(top335)', 'id(top341)', 'id(top322)','id(top348)',
                   'id(top356)', 'id(top312)', 'id(top357)', 'id(top349)', 'id(top351)'}
    for file_ in ptb_files:
        for sent in file_.children():
            conv,sent_num = sent.globalID.split('~')
            spk = sent.speaker
            sent_id = '_'.join((conv,spk,sent_num))
            if conv2topic[conv[2:]] in most_common:
                sent_ids.append(sent_id)
    print(len(sent_ids))
# import Treebank.PTB
# nxt_loc = "/group/corporapublic/switchboard/nxt"
# corpus = Treebank.PTB.NXTSwitchboard(path=nxt_loc)
# get_sents(corpus.train_files())
# get_sents(corpus.dev_files())
# get_sents(corpus.eval_files())