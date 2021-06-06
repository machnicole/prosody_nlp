#!/bin/bash

#data_dir=/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data
data_dir=/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm

python vm_extract_ta_features.py --input_dir $data_dir/vm_word_times/ --output_dir $data_dir/ta_features/ --sentence_id 0

