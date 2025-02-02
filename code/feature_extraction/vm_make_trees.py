import os
import re
import pickle
import trees
import string

def do_section(out_dir_trees, out_dir_ids, name, lang):
    trees_file =os.path.join(out_dir_trees, '%s.trees' % name)
    trees = open(trees_file, 'w')

    ids_file = os.path.join(out_dir_ids, '%s_sent_ids.txt' % name)
    sentence_ids = open(ids_file, 'w')

    with open('sentence_id2recording_{}_new.pickle'.format(lang), 'rb') as handle:
        sentence_id2recording = pickle.load(handle)

    for tree_filename in os.listdir(path_to_vm_penn_files):
        id_prefix = tree_filename.split(".")[0]
        with open(os.path.join(path_to_vm_penn_files, tree_filename), "r",
                          encoding="ISO-8859-1") as penn_file:

            for line in penn_file:
                get_sent_id = re.search('%% sent.\sno.\s(\d+)', line)

                if get_sent_id:
                    sentence_id = get_sent_id.group(1)
                    # print(get_sent_id.group(1))
                    # build a new tree for this sentence
                    # only if there is also a recording for it
                    if id_prefix+"_"+sentence_id in sentence_id2recording:
                        tree = []
                        sentence_ids.write('{}\n'.format(id_prefix+"_"+sentence_id))
                        continue
                    else:
                        tree = None
                        continue
                if line == "\n":
                    if tree:
                        trees.write('{}\n'.format(' '.join(tree)))
                        continue
                    else:
                        continue
                    # stop building the tree
                if type(tree) == list:
                    items = line.strip().split()
                    # start of syntax tree
                    if items == ['('] and tree == []:
                        tree.append("(TOP")
                    # ignore punctuation
                    elif ",)" in items or ".)" in items or "?)" in items:
                        pass
                    else:
                        for entry in items:
                            if entry[0] == "(": # non-terminal
                                if ":" in entry:
                                    # remove grammatical function tag
                                    clean_entry = entry.split(":")[0]
                                else:
                                    clean_entry = entry
                            else:
                                clean_entry = entry
                            tree.append(clean_entry)

def check_tree(tree):
    try:
        assert tree.count("(") == tree.count(")")
        assert tree.count("(") > 1 # tree must contain more than (TOP )
    except AssertionError:
        return False
    return True

def clean_tree(tree): # remove punctuation and lower-case terminals
    def clean_terminal(terminal):
        terminal = terminal.lower()
        terminal = terminal.translate(str.maketrans('', '', string.punctuation))
        return terminal

    tokens = tree.replace("(", " ( ").replace(")", " ) ").split()

    def helper(index):
        nodes = []

        while index < len(tokens) and tokens[index] == "(":
            paren_count = 0
            while tokens[index] == "(":
                index += 1
                paren_count += 1

            label = tokens[index]
            index += 1

            if tokens[index] == "(":
                children, index = helper(index)
                nodes.append(trees.InternalTreebankNode(label, children))
            else:
                word = tokens[index]
                index += 1
                nodes.append(trees.LeafTreebankNode(label, clean_terminal(word)))

            while paren_count > 0:
                #print(tokens[index-3:index+3])
                try:
                    assert tokens[index] == ")"
                except AssertionError:
                    print("tokens", tokens[index-3:index+3])
                    print("index", index)
                    print("tokens[index]", tokens[index])
                    raise
                index += 1
                paren_count -= 1

        return nodes, index

    nodes, index = helper(0)
    assert index == len(tokens)

    return nodes[0].linearize()

def split(out_dir_trees, out_dir_ids, lang):
    if lang == "eng":
        test_sentence_ids = ["cd6_00_"+str(number) for number in range(1, 1251)]
        dev_sentence_ids = ["cd8_00_" + str(number) for number in range(1, 1251)]
    elif lang == "ger":
        test_sentence_ids = ["cd15_"+str(number) for number in range(1, 1246)]
        dev_sentence_ids = ["cd20_" + str(number) for number in range(1, 1246)]
    else:
        raise TypeError

    test_trees_file =os.path.join(out_dir_trees, '%s.trees' % "test")
    test_trees = open(test_trees_file, 'w')
    train_trees_file =os.path.join(out_dir_trees, '%s.trees' % "train")
    train_trees = open(train_trees_file, 'w')
    dev_trees_file =os.path.join(out_dir_trees, '%s.trees' % "dev")
    dev_trees = open(dev_trees_file, 'w')

    all_clean_trees_file =os.path.join(out_dir_trees, '%s.trees' % "all_clean")
    all_clean_trees = open(all_clean_trees_file, 'w')

    test_sentence_id_file =os.path.join(out_dir_ids, '%s_sent_ids.txt' % "test")
    test_sentence_id_file_open = open(test_sentence_id_file, 'w')
    train_sentence_id_file =os.path.join(out_dir_ids, '%s_sent_ids.txt' % "train")
    train_sentence_id_file_open = open(train_sentence_id_file, 'w')
    dev_sentence_id_file =os.path.join(out_dir_ids, '%s_sent_ids.txt' % "dev")
    dev_sentence_id_file_open = open(dev_sentence_id_file, 'w')

    all_clean_sentence_id_file =os.path.join(out_dir_ids, '%s_sent_ids.txt' % "all_clean")
    all_clean_sentence_id_file_open = open(all_clean_sentence_id_file, 'w')

    with open(os.path.join(out_dir_ids, 'all_sent_ids.txt')) as sentence_id_file:
        with open(os.path.join(out_dir_trees,
                               'all.trees')) as trees_file:
            all_sentence_ids = sentence_id_file.readlines()
            all_trees = trees_file.readlines()
            for i, sentence_id in enumerate(all_sentence_ids):
                if sentence_id.strip() in test_sentence_ids:
                    if check_tree(all_trees[i]):
                        test_trees.write(clean_tree(all_trees[i])+"\n")
                        test_sentence_id_file_open.write(sentence_id)
                        all_clean_trees.write(clean_tree(all_trees[i])+"\n")
                        all_clean_sentence_id_file_open.write(sentence_id)
                elif sentence_id.strip() in dev_sentence_ids:
                    if check_tree(all_trees[i]):
                        dev_trees.write(clean_tree(all_trees[i])+"\n")
                        dev_sentence_id_file_open.write(sentence_id)
                        all_clean_trees.write(clean_tree(all_trees[i])+"\n")
                        all_clean_sentence_id_file_open.write(sentence_id)
                else:
                    if check_tree(all_trees[i]):
                        train_trees.write(clean_tree(all_trees[i])+"\n")
                        train_sentence_id_file_open.write(sentence_id)
                        all_clean_trees.write(clean_tree(all_trees[i])+"\n")
                        all_clean_sentence_id_file_open.write(sentence_id)








if __name__ == '__main__':
    # # English data
    # lang = "eng"
    # path_to_vm_penn_files = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/verbmobil/verbmobil_treebank/eng/penn_files/penn_files"
    # # filename = "cd6_00.penn"
    # path_to_vm_exports = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/verbmobil/verbmobil_treebank/eng/export_files/export_files"
    # out_dir_trees = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/new_trees'
    # out_dir_ids = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/'

    # German data
    lang = "ger"
    path_to_vm_penn_files = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/verbmobil/verbmobil_treebank/ger/penn_files/penn_files"
    path_to_vm_exports = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/verbmobil/verbmobil_treebank/ger/export_files/export_files"
    out_dir_trees = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/new_trees'
    out_dir_ids = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/'

    do_section(out_dir_trees, out_dir_ids, "all", lang)
    split(out_dir_trees, out_dir_ids, lang)

# run this to test the parser:
# python src/main_sparser.py train --use-glove-pretrained --freeze --train-path /afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/new_trees/train.trees --train-sent-id-path /afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/train_sent_ids.txt --dev-path /afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/new_trees/dev.trees --dev-sent-id-path /afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/dev_sent_ids.txt --prefix '' --feature-path /afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features --model-path-base /afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/code/self_attn_speech_parser/models/vm_eng_no_speech_model --sentence-max-len 200 --d-model 1536 --d-kv 96 --morpho-emb-dropout 0.3 --num-layers 4 --num-heads 8 --epochs 50 --numpy-seed 1234
# problem: line 168 AssertionError in trees.py