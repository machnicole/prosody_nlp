#!/bin/bash

# Data paths
#DATA_DIR=/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/input_features
DATA_DIR=/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn
FEAT_DIR=/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn
MODEL_DIR=output/turn
RESULT_DIR=output/turn
EVAL_DIR=output/turn

# EVALUATION EXAMPLE
#MODEL_NAME="turn_nonsp_glove_dev=82.18.pt"
MODEL_NAME="turn_sp_glove_dev=86.04.pt"
MODEL_PATH=${MODEL_DIR}/${MODEL_NAME}

PREFIX=turn
#IDS_PREFIX=multisent_turns
IDS_PREFIX=singlesent_turns
#IDS_PREFIX=turn
SPLIT=dev

PRED_PATH=${RESULT_DIR}/${MODEL_NAME}_${IDS_PREFIX}_${SPLIT}_predicted.txt
TEST_SENT_ID_PATH=${DATA_DIR}/${IDS_PREFIX}_${SPLIT}_sent_ids.txt
TEST_PATH=${DATA_DIR}/${IDS_PREFIX}_${SPLIT}.trees
python src/main_sparser.py test \
    --test-path ${TEST_PATH} \
    --test-sent-id-path ${TEST_SENT_ID_PATH} \
    --output-path ${PRED_PATH} \
    --feature-path ${FEAT_DIR} \
    --test-prefix ${PREFIX}_${SPLIT} \
    --model-path-base ${MODEL_PATH} 

