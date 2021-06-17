import os

data_dir = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/input_features"
out_dir = "/afs/inf.ed.ac.uk/group/msc-projects/s2096077/swbd/reduced"

train_size=21980
test_size=1250
dev_size=1248

train_ids = "train_sent_ids.txt"
test_ids = "test_sent_ids.txt"
dev_ids = "dev_sent_ids.txt"

train_trees = os.path.join("new_trees", "train.trees")
test_trees = os.path.join("new_trees", "test.trees")
dev_trees = os.path.join("new_trees", "dev.trees")

def create_reduced_file(data_dir, filename, out_dir, size):
    # print(os.path.join(data_dir, filename))
    with open(os.path.join(data_dir, filename), "r") as file:
        new_data = file.readlines()[:size]
    with open(os.path.join(out_dir, filename), "w") as new_file:
        new_file.writelines(new_data)

create_reduced_file(data_dir, train_ids, out_dir, train_size)
create_reduced_file(data_dir, train_trees, out_dir, train_size)
create_reduced_file(data_dir, test_ids, out_dir, test_size)
create_reduced_file(data_dir, test_trees, out_dir, test_size)
create_reduced_file(data_dir, dev_ids, out_dir, dev_size)
create_reduced_file(data_dir, dev_trees, out_dir, dev_size)

