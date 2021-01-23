from PYEVALB import scorer
import itertools
import random
import os
import pickle
import time

num_resamples = 10**5

def get_p_value(baseline_f,experiment_f,ids):
    print(experiment_f.split('/')[-1])
    gold_lines = [l.strip() for l in open(gold_f).readlines()]
    experiment_lines = [l.strip() for l in open(experiment_f).readlines()]
    baseline_lines = [l.strip() for l in open(baseline_f).readlines()]

    assert len(gold_lines)==len(ids)
    assert len(gold_lines)==len(experiment_lines)
    assert len(gold_lines)==len(baseline_lines)

    num_lines = len(gold_lines)


    scr = scorer.Scorer()
    print('Calculate baseline...')
    fullset_experiment_f1 = scr.get_f1_from_list(gold_lines,experiment_lines)
    fullset_baseline_f1 = scr.get_f1_from_list(gold_lines,baseline_lines)

    fullset_delta = abs(fullset_experiment_f1 - fullset_baseline_f1)

    big_diffs = 0

    id2matched = {'experiment':{},
                  'baseline':{}}
    id2gold = {'experiment':{},
               'baseline':{}}
    id2test = {'experiment':{},
               'baseline':{}}

    model2output = {'experiment':experiment_lines,
                    'baseline':baseline_lines}

    print('Store bracket scores ...')
    for model in ('experiment','baseline'):
        test_lines = model2output[model]
        for i,turn in enumerate(ids):
            gold_line = gold_lines[i]
            test_line = test_lines[i]
            mat,gol,tes = scr.get_bracket_counts_from_tree(gold_line,test_line)
            id2matched[model][turn] = mat
            id2gold[model][turn] = gol
            id2test[model][turn] = tes
        
    idxs = [i for i in range(len(gold_lines))]
    print('Resample ...')
    for i in range(num_resamples):
        if i%100000==1:
            print(i)
        gold_resamples = []
        experiment_resamples = []
        baseline_resamples = []
        resample_idx = random.choices(idxs,k=len(idxs))
        resampled_turns = []
        for idx in resample_idx:
            resampled_turns.append(ids[idx])

        gold_brackets = sum([id2gold['experiment'][turn] for turn in resampled_turns])
        experiment_matched_brackets = sum([id2matched['experiment'][turn] for turn in resampled_turns])
        experiment_test_brackets = sum([id2test['experiment'][turn] for turn in resampled_turns])
        experiment_rec = experiment_matched_brackets/gold_brackets
        experiment_prec = experiment_matched_brackets/experiment_test_brackets
        experiment_f1 = ((2*experiment_rec*experiment_prec)/(experiment_rec+experiment_prec))*100

    
        baseline_matched_brackets = sum([id2matched['baseline'][turn] for turn in resampled_turns])
        baseline_test_brackets = sum([id2test['baseline'][turn] for turn in resampled_turns])
        baseline_rec = baseline_matched_brackets/gold_brackets
        baseline_prec = baseline_matched_brackets/baseline_test_brackets
        baseline_f1 = ((2*baseline_rec*baseline_prec)/(baseline_rec+baseline_prec))*100

        #if experiment_f1 - baseline_f1 > (2*fullset_delta):
        curr_delta = abs(experiment_f1 - baseline_f1)
        if curr_delta > (2*fullset_delta):
            big_diffs += 1
    print(f'p-value estimate: {big_diffs/num_resamples}')





output_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/code/self_attn_speech_parser/output/turn_pause_dur_fixed'
data_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed'
gold_f = os.path.join(data_dir,'gold.txt')

# Basic pros/nonpros comparison
baseline_f = os.path.join(output_dir,'turn_medium_sp_glove_72240_dev=91.38.pt_turn_dev_predicted.txt')


ids = [l.strip() for l in open(os.path.join(data_dir,'turn_dev_sent_ids_medium.txt')).readlines()]

    
experiments = [os.path.join(output_dir,"turn_medium_nonsp_glove_72240_dev=86.82.pt_turn_dev_predicted.txt"),
               
#               os.path.join(output_dir,"turn_medium_sp_glove_ab_pitch_72240_dev=91.43.pt_turn_dev_predicted.txt"),
#               os.path.join(output_dir,"turn_medium_sp_glove_ab_pause_72240_dev=91.07.pt_turn_dev_predicted.txt"),
#               os.path.join(output_dir,"turn_medium_sp_glove_ab_fbank_72240_dev=91.12.pt_turn_dev_predicted.txt"),
#               os.path.join(output_dir,"turn_medium_sp_glove_ab_duration_72240_dev=91.32.pt_turn_dev_predicted.txt"),

#               os.path.join(output_dir,"turn_sp_glove_dur_only_72240_dev=86.96.pt_turn_dev_predicted.txt"),
#               os.path.join(output_dir,"turn_sp_glove_fbank_only_72240_dev=90.80.pt_turn_dev_predicted.txt"),
#               os.path.join(output_dir,"turn_sp_glove_pause_only_72240_dev=86.93.pt_turn_dev_predicted.txt"),
#               os.path.join(output_dir,"turn_sp_glove_pitch_only_72240_dev=91.20.pt_turn_dev_predicted.txt")

]




for ex in experiments:
    get_p_value(baseline_f,ex,ids)

