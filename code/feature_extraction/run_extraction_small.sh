#!/bin/bash

#data_dir=/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data
data_dir=/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data

python extract_ta_features.py --input_dir $data_dir/swbd_word_times/ --output_dir $data_dir/ta_features/ --file_id 4101 --speaker A
python extract_ta_features.py --input_dir $data_dir/swbd_word_times/ --output_dir $data_dir/ta_features/ --file_id 4101 --speaker B

