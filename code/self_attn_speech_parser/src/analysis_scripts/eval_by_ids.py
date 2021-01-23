from PYEVALB import scorer
import os
import tempfile
import trees
import statistics

# written in order to eval disfluent vs fluent sentences

datadir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed'
output_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/code/self_attn_speech_parser/output/turn_pause_dur_fixed'

id_file = os.path.join(datadir,'turn_dev_sent_ids_medium.txt')
gold_trees = os.path.join(datadir,'turn_dev_medium.trees')
gold_trees,all_ids = trees.load_trees_with_idx(gold_trees,id_file)

prefixes = ['nonsp_',
            'sp_',
            'dur_only_',
            'fbank_only_',
            'pause_only_',
            'pitch_only_']
            

fluencies = ['fluent','disfluent']

pred_trees_list = [os.path.join(output_dir,"turn_medium_nonsp_glove_72240_dev=86.82.pt_turn_dev_predicted.txt"),
                   os.path.join(output_dir,"turn_medium_sp_glove_72240_dev=91.38.pt_turn_dev_predicted.txt"),
                   os.path.join(output_dir,"turn_sp_glove_dur_only_72240_dev=86.96.pt_turn_dev_predicted.txt"),
                   os.path.join(output_dir,"turn_sp_glove_fbank_only_72240_dev=90.80.pt_turn_dev_predicted.txt"),
                   os.path.join(output_dir,"turn_sp_glove_pause_only_72240_dev=86.93.pt_turn_dev_predicted.txt"),
                   os.path.join(output_dir,"turn_sp_glove_pitch_only_72240_dev=91.20.pt_turn_dev_predicted.txt")]

for fluency in fluencies:
    for pred_trees_f,prefix in zip(pred_trees_list,prefixes):


        pred_trees,all_ids = trees.load_trees_with_idx(pred_trees_f,id_file)


        subset_ids = set([l.strip() for l in open(os.path.join(datadir,f'{fluency}_dev_sent_ids.txt')).readlines()])
        #subset_ids = [l.strip() for l in open(os.path.join(datadir,'turn_dev_sent_ids_medium.txt')).readlines()]

        id2gold = dict(zip(all_ids,gold_trees))
        id2pred = dict(zip(all_ids,pred_trees))

        temp_dir = tempfile.TemporaryDirectory(prefix="evalb-")
        gold_path = os.path.join(temp_dir.name, "gold.txt")
        predicted_path = os.path.join(temp_dir.name, "predicted.txt")

        lens = []

        with open(gold_path,'w') as goldf:
            with open(predicted_path,'w') as predf:
                for idnum in all_ids:
                    if idnum in subset_ids:
                        goldf.write(id2gold[idnum].linearize())
                        goldf.write('\n')
                        predf.write(id2pred[idnum].linearize())
                        predf.write('\n')
                        turn_len = 0
                        for leaf in id2gold[idnum].leaves():
                            turn_len += 1
                        lens.append(turn_len)

           
        output_path = os.path.join(output_dir, f'{prefix}{fluency}_output.txt')
        scr = scorer.Scorer()
        scr.evalb(gold_path,predicted_path,output_path)
temp_dir.cleanup()
        
