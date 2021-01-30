import os
import trees

outdir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/code/self_attn_speech_parser/output/turn_pause_dur_fixed'
datadir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn_pause_dur_fixed'
gold_path = os.path.join(datadir,'turn_dev.UTT_SEG.trees')
id_path = os.path.join(datadir,'turn_dev_sent_ids.UTT_SEG.txt')
sp_pred_path = os.path.join(outdir,'turn_seg_72240_dev=99.37.pt_turn_dev_predicted.txt')
nonsp_pred_path = os.path.join(outdir,'turn_nonsp_seg_72240_dev=74.83.pt_turn_dev_predicted.txt')

gold_trees,gold_ids = trees.load_trees_with_idx(gold_path,id_path)
nonsp_pred_trees,gold_ids = trees.load_trees_with_idx(nonsp_pred_path,id_path)
sp_pred_trees,gold_ids = trees.load_trees_with_idx(sp_pred_path,id_path)


def const_len(const):
    const_len = 0
    for leaf in const.leaves():
        const_len += 1
    return const_len

def calc_SER(gold_ids,gold_trees,pred_trees):
    correct_preds = 0
    incorrect_preds = 0
    total_gold_bounds = 0
    
    for idnum,pred,gold in zip(gold_ids,gold_trees,pred_trees):
        if len(gold.children) > 1:
            total_gold_bounds += len(gold.children) - 1
            gold_bound_idx = set()
            pred_bound_idx = set()
            gold_prefix_len = 0
            pred_prefix_len = 0
            for gold_kid in gold.children:
                gold_prefix_len += const_len(gold_kid)
                if gold_prefix_len != const_len(gold): gold_bound_idx.add(gold_prefix_len)
            for pred_kid in pred.children:
                pred_prefix_len += const_len(pred_kid)
                if pred_prefix_len != const_len(pred): pred_bound_idx.add(pred_prefix_len)
            correct_preds += len(gold_bound_idx.intersection(pred_bound_idx))
            incorrect_preds += len(pred_bound_idx - gold_bound_idx) + len(gold_bound_idx - pred_bound_idx)

    SER = incorrect_preds/total_gold_bounds
    prec = correct_preds/(correct_preds+incorrect_preds)
    rec = correct_preds/total_gold_bounds
    f = (2*prec*rec)/(prec+rec)
    return SER,prec,rec,f

sp_SER,sp_prec,sp_rec,sp_f = calc_SER(gold_ids,gold_trees,sp_pred_trees)
nonsp_SER,nonsp_prec,nonsp_rec,nonsp_f = calc_SER(gold_ids,gold_trees,nonsp_pred_trees)

print(f'Sp SER: {sp_SER}')
print(f'Sp prec: {sp_prec}')
print(f'Sp rec: {sp_rec}')
print(f'Sp f: {sp_f}')

print(f'Nonsp SER: {nonsp_SER}')
print(f'Nonsp prec: {nonsp_prec}')
print(f'Nonsp rec: {nonsp_rec}')
print(f'Nonsp f: {nonsp_f}')



