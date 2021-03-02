#!/bin/bash
# Load environment with dependencies
#source /homes/ttmt001/transitory/envs/py3.6-cpu/bin/activate

# Data paths 
#DATA_DIR=/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/input_features
DATA_DIR=/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed/seg
FEAT_DIR=/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed
MODEL_DIR=output/turn_pause_dur_fixed/seg
RESULT_DIR=output/turn_pause_dur_fixed/seg
EVAL_DIR=output/turn_pause_dur_fixed
PREFIX="turn_"

# TRAINING EXAMPLE
#{5154,54660,26229,40129,72240,95882,38976,9205,73784}
for rand_seed in 72240
do
    MODEL_NAME=turn_nonsp_seg_${rand_seed}
    SEED=${rand_seed}
    echo "Training seeding config: " $MODEL_NAME $SEED
    python src/main_sparser.py train --use-glove-pretrained --freeze \
	   --seg \
	   --train-path ${DATA_DIR}/${PREFIX}train.txt\
	   --train-sent-id-path ${DATA_DIR}/${PREFIX}train.ids \
	   --train-lbls  ${DATA_DIR}/${PREFIX}train.lbl\
	   --dev-path ${DATA_DIR}/${PREFIX}dev.txt \
	   --dev-sent-id-path ${DATA_DIR}/${PREFIX}dev.ids \
	   --dev-lbls  ${DATA_DIR}/${PREFIX}dev.lbl\
	   --prefix ${PREFIX} \
	   --feature-path ${FEAT_DIR} \
	   --model-path-base ${MODEL_DIR}/${MODEL_NAME} \
	   --sentence-max-len 270 \
	   --d-model 1536 \
	   --d-kv 96 \
	   --elmo-dropout 0.3 \
	   --morpho-emb-dropout 0.3 \
	   --num-layers 4 \
	   --num-heads 8 \
	   --epochs 50 --numpy-seed $SEED # >> ${RESULT_DIR}/${MODEL_NAME}.log
done
