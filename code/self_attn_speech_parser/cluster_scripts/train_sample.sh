#!/bin/bash
python src/main_sparser.py train --use-glove-pretrained --freeze \
       			   	--train-path sample_data/sample_train.txt\
			   	--train-sent-id-path sample_data/sample_train_sent_ids.txt \
				--dev-path sample_data/sample_dev.txt \
				--dev-sent-id-path sample_data/sample_dev_sent_ids.txt \
			    --prefix '' \
				--feature-path sample_data \
				--model-path-base models/sample_model \
				--speech-features duration,pause,partition,pitch,fbank \
				--sentence-max-len 270 \
				--d-model 1536 \
				--d-kv 96 \
				--morpho-emb-dropout 0.3 \
				--num-layers 4 \
				--num-heads 8 \
				--epochs 50 \
				--numpy-seed $SEED  >> results/sample_model.log
