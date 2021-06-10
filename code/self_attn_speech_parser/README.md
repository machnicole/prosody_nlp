# Running the parser

## Environment

### Python packages:

1. Create conda environment with python3.6 (or virtual environment) and activate it.
2. Install Pytorch 0.4.1 (command from https://pytorch.org/get-started/previous-versions/):
	
	`conda install pytorch=0.4.1 cuda80 -c pytorch`

3. Install requirements:

`pip install -r requirements.txt` (better to delete pytorch, as the correct version for CUDA should be selected manually.)

or

`conda install --file requirements.txt` (kaldi-io can only be installed via pip for me)

### Kaldi: for feature extraction

Use pre-installed version on DICE:

`ln -s /afs/inf.ed.ac.uk/group/teaching/asr/tools/labs/path.sh .`

`source path.sh`

To see whether it is set and where it points to, run:

`echo $KALDI_ROOT`

It is a good idea to call the `path.sh` at the beginning of all Kaldi scripts.

Not necessary, as already installed on DICE:
1. Clone the Kaldi repo: `git clone https://github.com/kaldi-asr/kaldi`
2. Install by following the instructions in the `INSTALL` file.
------------------------

### PYEVALB: for parser evaluation

1. Clone the (fork of the original) repo: `git clone https://github.com/ekayen/PYEVALB`
2. `cd PYEVALB`
3. `pip install -e .`

## Preprocessing

### Feature extraction

Need to use Python 2 with nltk and pandas installed for this (when doing the feature extraction on SWBD data).

`conda create --name py2 python=2.7`

#### Text features:

Generate PTB-style trees with nested parentheses:

1. `cd prosody_nlp/code/feature_extraction`
2. Change file paths in `nxt_proc.py` to point to correct data and output locations.
3. `python2 nxt_proc.py` for each split (train,dev,test). *NOTE: this script requires python2*
4. Change file paths in `make_alignment_dicts.py` to correct data and output locations. This includes the data directory `swb_ms98_transcriptions`, which is part of the original switchboard1 release and not included with the Switchboard NXT annotations. *NOTE: if you encounter errors with this script, try running with python2*
5. run `make_alignment_dicts.py`

Generate corresponding sentence id files:

4. Change file paths in `make_sent_ids.py`
5. `python make_sent_ids.py`

Download GloVe vectors: 

6. Download glove.6B.300d.txt from https://nlp.stanford.edu/projects/glove/

## Notes on running the aligner

It's crucial that your data has time alignments. To obtain alignments for Verbmobil, use Montreal Forced Aligner (MFA). 
Note 1): MFA won't be able to align all your data (some utterance are just too hard..) - run `removed_unaligned_ids.py` before continuing making trees, etc.
Note 2): It's crucial that ALL words are aligned, i.e. that all word are in your pronunciation dictionary. To obtain this, do the following:

1. Prevent bugs from happening by `export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/anaconda3/envs/aligner/lib/` 
2. Validate your data by calling: `mfa validate corpus_directory dictionary_path [optional_acoustic_model_path]` - this will summarize all OOV words in your data in one .txt file.
3. Use a pre-trained G2P model (from MFA) to obtain an extended pronunciation model: `mfa g2p g2p_model_path input_oov_file.txt output_oov_dict_file.txt`
4. Merge `output_oov_dict_file.txt` with your existing pronunciation dictionary (located in `dictionary_path`)
5. Align your data ` mfa align archive english.dict.txt english.zip output` (can take a couple of hours)

#### Text features Verbmobil data:

Generate PTB-style trees with nested parentheses and corresponding sentence id files:

1.  `cd prosody_nlp/code/feature_extraction`
2.  Set the paths in `sentenceIDs_recordings.py` to point to the correct data and call a language-specific function (eng or ger).
3.  run `sentenceIDs_recordings.py` to get a pickle file of a dictionary which maps sentenceIDs to the paths of their recordings (also prints out some corpus statistics).
4.  Remove sentence IDs for utterances that don't have alignments (see above).
5.  Set the paths in `vm_make_trees.py` to point to the correct data and specify the language (eng or ger).
6.  Make sure to create the output directories you specify.
7.  run `vm_make_trees.py`

The equivalent to running `make_alignment_dicts.py` as above (necessary for extracting time-aligned features lateron) is a bit more complicated:

1. The majority of Verbmobil data doesn't have alignments. Install and use Montreal Forced Aligner (MFA) to obtain word and phone alignments.
2. MFA requires the corpus to be of a specific shape. Run `zip_wavs.py` to obtain a zip of the corpus that has the right directory organisation and data.
3. Note: if MFA throws a weird error message, try this: `export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/anaconda3/envs/aligner/lib/` 
4. Unzip the corpus.zip and use the MFA to obtain alignments (in the form of TextGrid files): ` mfa align archive english.dict.txt english.zip output`. MFA requires a pronunciation dictionary (downloadable, but can create from VM data) and an acoustic model (pretrained) for the alignment. 
5. Change file paths in `make_alignment_dict_from_tg.py`. Make sure to create the directory that is specified in `outdir`. Specify the language.
6. Run `make_alignment_dict_from_tg.py`

Download GloVe vectors: 

7. Download glove.6B.300d.txt from https://nlp.stanford.edu/projects/glove/ for English data.
8. OR German glove vectors from here:https://int-emb-glove-de-wiki.s3.eu-central-1.amazonaws.com/vectors.txt (rename to `glove.6B.300d.txt` as this is hard-coded)
9. `cd prosody_nlp/code/self_attn_speech_parser/src`
10. Change `glove_pretrained_path` in `parse_model.py` such that it points to the correct directory.


#### Pitch and intensity

1. `cd prosody_nlp/code/kaldi_scripts`
2. Set the paths in `comp_all.sh` and `paths.sh` to point to the Switchboard data, the kaldi installation, and the directory where you want to output the data.
3. Run `./comp_all.sh`
4. `cd prosody_nlp/code/feature_extraction`
5. Set the variable `nsplit` in `process_kaldi_feats_splits.py` to the number of splits used to generate your kaldi features.
6. Set the variable `KALDI_SUFFIX` in `process_kaldi_feats_splits.py` to the directory of sph files.
7. Run `process_kaldi_feats_splits.py`. If you had (for example) saved the kaldi features to `raw_output` and want to save the processed kaldi features to `output`, you would use the command: `python process_kaldi_feats_splits.py --in_dir raw_output --out_dir output`.

#### Pitch and intensity Verbmobil data:
1. `cd prosody_nlp/code/feature_extraction`
2. run `create_sph_files.py` to create sph files out of the wav files (takes a lot of memory). TODO: maybe kaldi scripts are executable on wav files, too?
3. `cd prosody_nlp/code/kaldi_scripts`
4. Set the paths in `comp_all_vm.sh` to point to the VM data (sph files), the kaldi installation, and the directory where you want to output the data.
5. Run `./comp_all_vm.sh`
6. `cd prosody_nlp/code/feature_extraction`
7. Set the variable `nsplit` in `vm_process_kaldi_feats_splits.py` to the number of splits used to generate your kaldi features.
8. Set the variable `KALDI_SUFFIX` in `vm_process_kaldi_feats_splits.py` to the directory of sph files.
9. Run `vm_process_kaldi_feats_splits.py`. If you had (for example) saved the kaldi features to `raw_output` and want to save the processed kaldi features to `output`, you would use the command: `python process_kaldi_feats_splits.py --in_dir raw_output --out_dir output`.


#### Duration:

1. Place the `avg_word_stats.json` file into the data directory or create it as follows:
Create a JSON file of the average duration of each token type in the train set. Since this is based on the SWBD-NXT data, we don't include it. In order to replicate it, create a JSON of the following format using the train set (numbers are dummy values):

```
{
  "okay": {
      "count": 40,
      "mean": 0.7,	
      "std": 0.1
       },
  "uh": {
      "count": 10,
      "mean": 0.5,
      "std": 0.2,
       },
       ...
}						
```
2. `cd prosody_nlp/code/feature_extraction`
3. `python2 get_ta_stats.py --input_dir <output of make_alignment_dicts.py> --output_dir <desired output dir>`
4. Change file paths in `extract_ta_features.py` to point to extracted kaldi feats. *NOTE: if you encounter errors with this script, try running with python2*
5. `python extract_ta_features.py` (run this with python 2) [I run this by calling run_extraction.sh]

#### Duration Verbmobil data:

1. `cd prosody_nlp/code/feature_extraction`
2. `mkdir -r ta_features/stats`
3. `python2 get_ta_stats.py --input_dir '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/vm_word_times' --output_dir '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ta_features'` 
4. Change file paths in `vm_extract_ta_features.py` to point to extracted kaldi feats. *NOTE: if you encounter errors with this script, try running with python2*
5. `python vm_extract_ta_features.py` (run this with python 2) [I run this by calling vm_run_extraction.sh]


#### Pause
`calculate_pauses.py` has two requirements:
- there has to exist a directoy `swbd_word_times` (this should have been created by calling `make_alignment_dicts.py` above)
- there has to exist the file `term2pw.pickle` in the directory `data/input_features`
- to create `term2pw.pickle` run `python prep_input_dicts.py` (with correct file paths to data). This could throw an error about a missing `avg_word_stats.json` file (it should be located in the data directory). It will probably throw other errors, too - but the pickle file is all we want at the moment. So, just ignore these.

1. cd `prosody_nlp/code/self_attn_speech_parser/src`
2. `python calculate_pauses.py`

#### Pause Verbmobil data:

1. cd `prosody_nlp/code/self_attn_speech_parser/src`
2. Run `python vm_prep_input_dicts.py` (with correct file paths to data). This will throw some errors, but the pickle file `term2pw.pickle` is all we want at the moment. So, just ignore these.
3. `python vm_calculate_pauses.py`

### Feature preparation

Put all the features you have generated into a form the parser can use. Even if you are planning on only using turn-based features, you will need to generate both sets -- the turn-based features draw on the sentence-based features.

To run `python prep_input_dicts.py` in a proper way (without error messages), do these 2 things:
1) create `phone2meandur.pickle`by running `gen_phon2meandur.py`.
2) create a directory `normed_fbanks` in the `swbd_fbank_energy` directory (in my case `/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/testoutput/swbd_fbank_energy/normed_fbanks`)

1. To generate sentence-level features, run `python prep_input_dicts.py` for each split (train,dev,test). Be sure to change file paths to data.
2. Generate a directory for the turn-level features. In my case: `/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/input_features/turn_pause_dur_fixed`
3. To generate turn-level features, run `python prep_turn_dicts.py` for each split (train,dev,test). Be sure to change file paths to data.

Next, filter out turns over 270 tokens (see paper). This should be two turns in the train set, none in other sets.

3. `cd prosody_nlp/code/self_attn_speech_parser/src/`
4. Change data and output paths in `filter_long_turns.py` and make sure it is set to the train split.
5. `python filter_long_turns.py`
6. Make sure that the filtered train sent_id and trees files are the files that you use in the subsequent steps.

### Feature preparation Verbmobil data:

Put all the features you have generated into a form the parser can use. Even if you are planning on only using turn-based features, you will need to generate both sets -- the turn-based features draw on the sentence-based features.

To run `python vm_prep_input_dicts.py` in a proper way (without error messages), do these 2 things:
1. cd `prosody_nlp/code/feature_extraction`
2. Run `python2 get_mean_dur.py` to create `phone2meandur.pickle` and `avg_word_stats.json`
3. create a directory `normed_fbanks` in the `vm_fbank_energy` directory (in my case `/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/testoutput/vm_fbank_energy/normed_fbanks`)
4. `cd prosody_nlp/code/self_attn_speech_parser/src/`

1. To generate sentence-level features, run `python vm_prep_input_dicts.py` for each split (train,dev,test). Be sure to change file paths to data.
[ # TODO: Turn-based features
3. Generate a directory for the turn-level features. In my case: `/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/input_features/turn_pause_dur_fixed`
4. To generate turn-level features, run `python prep_turn_dicts.py` for each split (train,dev,test). Be sure to change file paths to data.

Next, filter out turns over 270 tokens (see paper). This should be two turns in the train set, none in other sets.

3. `cd prosody_nlp/code/self_attn_speech_parser/src/`
4. Change data and output paths in `filter_long_turns.py` and make sure it is set to the train split.
5. `python filter_long_turns.py`
6. Make sure that the filtered train sent_id and trees files are the files that you use in the subsequent steps.]


## Training

For the training to work, it's necessary to create a `models` and a `results` directory.

Train script example:

```
python src/main_sparser.py train --use-glove-pretrained --freeze \
       			   	--train-path ${DATA_DIR}/train.trees\
			   	--train-sent-id-path ${DATA_DIR}/train_sent_ids.txt \
				--dev-path ${DATA_DIR}/dev.trees \
				--dev-sent-id-path ${DATA_DIR}/dev_sent_ids.txt \
			        --prefix ${PREFIX} \ 
				--feature-path ${FEAT_DIR} \
				--model-path-base ${MODEL_DIR}/${MODEL_NAME} \
				--speech-features duration,pause,partition,pitch,fbank \
				--epochs 50 \
				--numpy-seed $SEED  >> ${RESULT_DIR}/${MODEL_NAME}.log
```

Note: `main_sparser.py` will look for a given speech feature (e.g., pause) at the path `${FEAT_DIR}/train_pause.pickle`; if you want to create subsections of the data, you can use the $PREFIX valiable to point to data at `${FEAT_DIR}/${PREFIX}train_pause.pickle`. Set this variable to '' otherwise. 

## Predicting

```
SENT_ID_PATH=${DATA_DIR}/dev_sent_ids.txt
TREE_PATH=${DATA_DIR}/dev.trees
python src/main_sparser.py test \
    --test-path ${TREE_PATH} \
    --test-sent-id-path ${SENT_ID_PATH} \
    --output-path ${OUTPUT_PATH} \
    --feature-path ${FEAT_DIR} \
    --test-prefix ${PREFIX}_dev \
    --model-path-base ${MODEL_PATH} 

```
