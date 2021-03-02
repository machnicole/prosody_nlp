from PYEVALB import scorer
import os

data = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed'
out =  '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/code/self_attn_speech_parser/output/turn_pause_dur_fixed'



models = ['turn_sp_glove_dur_only_72240_dev=86.96.pt',\
          'turn_sp_glove_pause_only_72240_dev=86.93.pt',\
          'turn_sp_glove_fbank_only_72240_dev=90.80.pt',\
          'turn_sp_glove_pitch_only_72240_dev=91.20.pt']

gold_path = os.path.join(data,'turn_dev_medium.trees')
for model in models:
    predicted_path = os.path.join(out,f'{model}_turn_dev_predicted.txt')
    output_path = os.path.join(out,f'{model}.eval')
    scr = scorer.Scorer()
    scr.evalb_debug(gold_path,predicted_path,output_path)
