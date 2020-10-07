#!/bin/bash
# Load environment with dependencies
#source /homes/ttmt001/transitory/envs/py3.6-cpu/bin/activate

# Data paths
DATA_DIR=/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/input_features
FEAT_DIR=/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/input_features
MODEL_DIR=output
RESULT_DIR=output
EVAL_DIR=output

# TRAINING EXAMPLE
MODEL_NAME=nonsp_bert
SEED=0
echo "Training seeding config: " $MODEL_NAME $SEED
python src/main_sparser.py train --use-bert --freeze \
    --train-path ${DATA_DIR}/train.trees\
    --train-sent-id-path ${DATA_DIR}/train_sent_ids.txt \
    --dev-path ${DATA_DIR}/dev.trees \
    --dev-sent-id-path ${DATA_DIR}/dev_sent_ids.txt \
    --prefix "" \
    --feature-path ${FEAT_DIR} \
    --model-path-base ${MODEL_DIR}/${MODEL_NAME} \
    --sentence-max-len 200 \
    --d-model 1536 \
    --d-kv 96 \
    --elmo-dropout 0.3 \
    --morpho-emb-dropout 0.3 \
    --num-layers 4 \
    --num-heads 8 \
    --epochs 50 --numpy-seed $SEED  >> ${RESULT_DIR}/${MODEL_NAME}.log


# EVALUATION EXAMPLE
#MODEL_NAME=sample
#MODEL_PATH=${MODEL_DIR}/${MODEL_NAME}

#SPLIT="sample_test"
#PRED_PATH=${RESULT_DIR}/sample_test_${MODEL_NAME}_predicted.txt
#TEST_SENT_ID_PATH=${DATA_DIR}/sample_test_sent_ids.txt
#TEST_PATH=${DATA_DIR}/sample_test.txt
#python src/main_sparser.py test \
#    --test-path ${TEST_PATH} \
#    --test-sent-id-path ${TEST_SENT_ID_PATH} \
#    --output-path ${PRED_PATH} \
#    --feature-path ${FEAT_DIR} \
#    --test-prefix $SPLIT \
#    --model-path-base ${MODEL_PATH} 


