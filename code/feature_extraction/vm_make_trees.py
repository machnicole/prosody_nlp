import os
import re
import pickle


def do_section(out_dir_trees, out_dir_ids, name):
    trees_file =os.path.join(out_dir_trees, '%s.trees' % name)
    trees = open(trees_file, 'w')

    ids_file = os.path.join(out_dir_ids, '%s_sent_ids.txt' % name)
    sentence_ids = open(ids_file, 'w')

    with open('sentence_id2recording_eng.pickle', 'rb') as handle:
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

def split(out_dir_trees, out_dir_ids):
    test_sentence_ids = ["cd6_00_"+str(number) for number in range(1, 1251)]
    print(test_sentence_ids)
    dev_sentence_ids = ["cd8_00_" + str(number) for number in range(1, 1251)]

    test_trees_file =os.path.join(out_dir_trees, '%s.trees' % "test")
    test_trees = open(test_trees_file, 'w')
    train_trees_file =os.path.join(out_dir_trees, '%s.trees' % "train")
    train_trees = open(train_trees_file, 'w')
    dev_trees_file =os.path.join(out_dir_trees, '%s.trees' % "dev")
    dev_trees = open(dev_trees_file, 'w')

    test_sentence_id_file =os.path.join(out_dir_ids, '%s_sent_ids.txt' % "test")
    test_sentence_id_file_open = open(test_sentence_id_file, 'w')
    train_sentence_id_file =os.path.join(out_dir_ids, '%s_sent_ids.txt' % "train")
    train_sentence_id_file_open = open(train_sentence_id_file, 'w')
    dev_sentence_id_file =os.path.join(out_dir_ids, '%s_sent_ids.txt' % "dev")
    dev_sentence_id_file_open = open(dev_sentence_id_file, 'w')

    with open(os.path.join(out_dir_ids, 'all_sent_ids.txt')) as sentence_id_file:
        with open(os.path.join(out_dir_trees,
                               'all.trees')) as trees_file:
            all_sentence_ids = sentence_id_file.readlines()
            all_trees = trees_file.readlines()
            for i, sentence_id in enumerate(all_sentence_ids):
                if sentence_id.strip() in test_sentence_ids:
                    print("test")
                    test_trees.write(all_trees[i])
                    test_sentence_id_file_open.write(sentence_id)
                elif sentence_id.strip() in dev_sentence_ids:
                    dev_trees.write(all_trees[i])
                    dev_sentence_id_file_open.write(sentence_id)
                else:
                    train_trees.write(all_trees[i])
                    train_sentence_id_file_open.write(sentence_id)








if __name__ == '__main__':
    path_to_vm_penn_files = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/verbmobil/verbmobil_treebank/eng/penn_files/penn_files"
    filename = "cd6_00.penn"
    path_to_vm_exports = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/verbmobil/verbmobil_treebank/eng/export_files/export_files"
    out_dir_trees = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/new_trees'
    out_dir_ids = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/'
    # TODO: Add something to specify train, test, and dev
    do_section(out_dir_trees, out_dir_ids, "all")
    split(out_dir_trees, out_dir_ids)