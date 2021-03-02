#!/bin/bash

# Data paths
#DATA_DIR=/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/input_features
DATA_DIR=/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed/seg
FEAT_DIR=/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed/
MODEL_DIR=output/turn_pause_dur_fixed/seg
RESULT_DIR=output/turn_pause_dur_fixed/seg
EVAL_DIR=output/turn_pause_dur_fixed/seg

# EVALUATION EXAMPLE

SPLIT="dev"
PREFIX="turn"


#MODEL_NAME="turn_sp_seg_72240_dev=99.71.pt"
MODEL_NAME="turn_nonsp_seg_72240_dev=73.31.pt"
MODEL_PATH=${MODEL_DIR}/${MODEL_NAME}

echo $MODEL_NAME
PRED_PATH=${RESULT_DIR}/${MODEL_NAME}_${PREFIX}_${SPLIT}_predicted.txt
python src/main_sparser.py test \
       --test-path ${DATA_DIR}/${PREFIX}_${SPLIT}.txt \
       --test-sent-id-path ${DATA_DIR}/${PREFIX}_${SPLIT}.ids \
       --test-lbls  ${DATA_DIR}/${PREFIX}_${SPLIT}.lbl\
       --output-path ${PRED_PATH} \
       --feature-path ${FEAT_DIR} \
       --test-prefix ${PREFIX}_${SPLIT} \
       --model-path-base ${MODEL_PATH} 
