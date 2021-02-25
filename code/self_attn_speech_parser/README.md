# Running the parser

## Environment

### Python packages:

1. Install Python 3.6
2. Create conda environment or virtual environment and activate it.
3. Install requirements:

`pip install -r requirements.txt`

or

`conda install --file requirements.txt`

### Kaldi: for feature extraction

1. Clone the Kaldi repo: `git clone https://github.com/kaldi-asr/kaldi`
2. Install by following the instructions in the `INSTALL` file.

### PYEVALB: for parser evaluation

1. Clone the (fork of the original) repo: `git clone https://github.com/ekayen/PYEVALB`
2. `cd PYEVALB`
3. `pip install -e .`

## Preprocessing

### Feature extraction

#### Pitch and intensity

1. `cd prosody_nlp/code/kaldi_scripts`
2. Set the paths in `comp_all.sh` and `paths.sh` to point to the Switchboard data, the kaldi installation, and the directory where you want to output the data.
3. Run `./comp_all.sh`

#### Pause

1. cd `prosody_nlp/code/self_attn_speech_parser/src/
2. `python calculate_pauses.py`

#### Duration:

1. Create a JSON file of the average duration of each token type in the train set. Since this is based on the SWBD-NXT data, we don't include it. In order to replicate it, create a JSON of the following format using the train set (numbers are dummy values):

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
3. Change file paths in `extract_ta_features.py` to point to extracted kaldi feats.
4. `python extract_ta_features.py`
5. `python get_ta_stats.py`

### Feature preparation

1. To generate sentence-level features, run `python prep_input_dicts.py` for each split (train,dev,test). Be sure to change file paths to data.
2. To generate turn-level features, run `python prep_turn_dicts.py` for each split (train,dev,test). Be sure to change file paths to data.

## Training

Train script example:

```

```

## Predicting

## Evaluating
