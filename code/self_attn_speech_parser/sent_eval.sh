#!/bin/bash

# Data paths
#DATA_DIR=/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/input_features
DATA_DIR=/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/sentence
FEAT_DIR=/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/sentence
MODEL_DIR=output/sentence
RESULT_DIR=output/sentence
EVAL_DIR=output/sentence

# EVALUATION EXAMPLE
#MODEL_NAME="sp_glove_dev=91.24.pt"
MODEL_NAME="nonsp_glove_dev=90.87.pt"
MODEL_PATH=${MODEL_DIR}/${MODEL_NAME}

PREFIX=
IDS_PREFIX=multisent
SPLIT=dev

#PRED_PATH=${RESULT_DIR}/${MODEL_NAME}_${IDS_PREFIX}_${SPLIT}_predicted.txt
PRED_PATH=${RESULT_DIR}/${MODEL_NAME}_${SPLIT}_predicted_evalb.txt
#TEST_SENT_ID_PATH=${DATA_DIR}/${IDS_PREFIX}_${SPLIT}_sent_ids.txt
TEST_SENT_ID_PATH=${DATA_DIR}/${SPLIT}_sent_ids.txt
#TEST_PATH=${DATA_DIR}/${IDS_PREFIX}_${SPLIT}.trees
TEST_PATH=${DATA_DIR}/${SPLIT}.trees
python src/main_sparser.py test \
    --test-path ${TEST_PATH} \
    --test-sent-id-path ${TEST_SENT_ID_PATH} \
    --output-path ${PRED_PATH} \
    --feature-path ${FEAT_DIR} \
    --test-prefix ${SPLIT} \
    --model-path-base ${MODEL_PATH} 

