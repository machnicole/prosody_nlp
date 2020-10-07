#!/bin/bash

data_dir=/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data

while read line; do
    echo $line
    python extract_ta_features.py --input_dir $data_dir/swbd_word_times/ --output_dir $data_dir/ta_features/ --file_id ${line} --speaker A
    python extract_ta_features.py --input_dir $data_dir/swbd_word_times/ --output_dir $data_dir/ta_features/ --file_id ${line} --speaker B    
done <file_ids.txt
