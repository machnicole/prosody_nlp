#!/bin/bash

# Data paths
#DATA_DIR=/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/input_features
DATA_DIR=/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed/seg
FEAT_DIR=/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed/seg
#MODEL_DIR=output/turn_pause_dur_fixed
MODEL_DIR=output/sentence_pause_dur_fixed
RESULT_DIR=output/turn_pause_dur_fixed/seg
EVAL_DIR=output/turn_pause_dur_fixed/seg


# EVALUATION EXAMPLE

SPLIT="dev"
PREFIX="turn"

MODEL_NAME="sp_glove_72240_dev=91.10.pt"
#MODEL_NAME="nonsp_glove_72240_dev=90.25.pt"
MODEL_PATH=${MODEL_DIR}/${MODEL_NAME}

#SEG_MODEL="nonsp_glove_72240_dev=73.31.pt"
SEG_MODEL="sp_glove_72240_dev=99.71.pt"

echo $MODEL_NAME
PRED_PATH=${RESULT_DIR}/${SEG_MODEL}_parsed.txt
TEST_SENT_ID_PATH=${DATA_DIR}/${SPLIT}_sent_ids_for_parser.txt
TEST_PATH=${DATA_DIR}/${SPLIT}_for_parser.trees
python src/main_sparser.py test \
    --test-path ${TEST_PATH} \
    --test-sent-id-path ${TEST_SENT_ID_PATH} \
    --output-path ${PRED_PATH} \
    --feature-path ${FEAT_DIR} \
    --test-prefix ${SPLIT} \
    --model-path-base ${MODEL_PATH} 
