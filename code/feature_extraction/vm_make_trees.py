import os
import re
import pickle


def do_section(out_dir, name):
    trees_file =os.path.join(out_dir, '%s.trees' % name)
    trees = open(trees_file, 'w')

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


if __name__ == '__main__':
    path_to_vm_penn_files = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/verbmobil/verbmobil_treebank/eng/penn_files/penn_files"
    filename = "cd6_00.penn"
    path_to_vm_exports = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/verbmobil/verbmobil_treebank/eng/export_files/export_files"
    out_dir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/new_trees'
    # TODO: Add something to specify train, test, and dev
    do_section(out_dir, "all")