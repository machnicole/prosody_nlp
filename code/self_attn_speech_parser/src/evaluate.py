import math
import os.path
import re
import subprocess
import tempfile
import numpy as np
import trees

from PYEVALB import scorer

class FScore(object):
    def __init__(self, recall, precision, fscore, complete_match, tagging_accuracy=100):
        self.recall = recall
        self.precision = precision
        self.fscore = fscore
        self.complete_match = complete_match
        self.tagging_accuracy = 100

    def __str__(self):
        if self.tagging_accuracy < 100:
            return "(Recall={:.2f}, Precision={:.2f}, FScore={:.2f}, CompleteMatch={:.2f}, TaggingAccuracy={:.2f})".format(
                self.recall, self.precision, self.fscore, self.complete_match, self.tagging_accuracy)
        else:
            return "(Recall={:.2f}, Precision={:.2f}, FScore={:.2f}, CompleteMatch={:.2f})".format(
                self.recall, self.precision, self.fscore, self.complete_match)

def seg_fscore(golds,preds,is_train=True):
    fscore = FScore(math.nan, math.nan, math.nan, math.nan)

    pred_pos = 0
    true_pos = 0
    gold_pos = 0
    for gold,pred in zip(golds,preds):
        txt = gold[0]
        lbl = np.array([int(l) for l in gold[1]])
        pred = np.array([1 if i=='1' else 0 for i in pred])
        pred_pos += np.sum(pred)
        match = lbl==pred
        pred1 = pred==1
        true_pos += np.sum(match&pred1) # fixing bug: should both match the lbl and be 1
        gold_pos += np.sum(lbl)
        #if true_pos > 1: import pdb;pdb.set_trace()
    fscore.recall = 100*true_pos/gold_pos
    if pred_pos == 0:
        fscore.precision = 0
        fscore.fscore = 0
    else:
        fscore.precision = 100*true_pos/pred_pos
        fscore.fscore = (2*fscore.precision*fscore.recall)/(fscore.precision+fscore.recall)
    return fscore
        
        

        
def evalb(evalb_dir, gold_trees, predicted_trees, ref_gold_path=None, is_train=True):
    """
    assert os.path.exists(evalb_dir)
    evalb_program_path = os.path.join(evalb_dir, "evalb")
    evalb_spmrl_program_path = os.path.join(evalb_dir, "evalb_spmrl")
    assert os.path.exists(evalb_program_path) or os.path.exists(evalb_spmrl_program_path)

    if os.path.exists(evalb_program_path):
        evalb_param_path = os.path.join(evalb_dir, "nk.prm")
    else:
        evalb_program_path = evalb_spmrl_program_path
        evalb_param_path = os.path.join(evalb_dir, "spmrl.prm")

    assert os.path.exists(evalb_program_path)
    assert os.path.exists(evalb_param_path)
    """
    
    temp_dir = tempfile.TemporaryDirectory(prefix="evalb-")
    print("Temporary dir", temp_dir)

    assert len(gold_trees) == len(predicted_trees)
    for gold_tree, predicted_tree in zip(gold_trees, predicted_trees):
        assert isinstance(gold_tree, trees.TreebankNode)
        assert isinstance(predicted_tree, trees.TreebankNode)
        gold_leaves = list(gold_tree.leaves())
        predicted_leaves = list(predicted_tree.leaves())
        assert len(gold_leaves) == len(predicted_leaves)
        assert all(
            gold_leaf.word == predicted_leaf.word
            for gold_leaf, predicted_leaf in zip(gold_leaves, predicted_leaves))

    gold_path = os.path.join(temp_dir.name, "gold.txt")
    predicted_path = os.path.join(temp_dir.name, "predicted.txt")
    output_path = os.path.join(temp_dir.name, "output.txt")

 
    with open(gold_path, "w") as outfile:
        if ref_gold_path is None:
            for tree in gold_trees:
                outfile.write("{}\n".format(tree.linearize()))
        else:
            # For the SPMRL dataset our data loader performs some modifications
            # (like stripping morphological features), so we compare to the
            # raw gold file to be certain that we haven't spoiled the evaluation
            # in some way.
            with open(ref_gold_path) as goldfile:
                outfile.write(goldfile.read())

    with open(predicted_path, "w") as outfile:
        for tree in predicted_trees:
            try:
                outfile.write("{}\n".format(tree.linearize()))
            except:
                import sys
                sys.setrecursionlimit(10**6)
                outfile.write("{}\n".format(tree.linearize()))


            
    """
    data_dir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features'
    perm_gold_path = os.path.join(data_dir, "sent_based_gold.txt")
    perm_predicted_path = os.path.join(data_dir, "sent_based_predicted.txt")

    with open(perm_gold_path, "w") as outfile:
        for tree in gold_trees:
            outfile.write("{}\n".format(tree.linearize()))
    with open(perm_predicted_path, "w") as outfile:
        for tree in predicted_trees:
            outfile.write("{}\n".format(tree.linearize()))
    """
            
#    command = "{} -p {} {} {} > {}".format(
#       evalb_program_path,
#        evalb_param_path,
#        gold_path,
#        predicted_path,
#        output_path,
#    )
#   print(f'evalb shell command: {command}')
    #subprocess.run(command, shell=True)


    scr = scorer.Scorer()
    scr.evalb(gold_path,predicted_path,output_path)

    # debug:
    subprocess.run("wc {}".format(predicted_path), shell=True)
    subprocess.run("wc {}".format(output_path), shell=True)

    fscore = FScore(math.nan, math.nan, math.nan, math.nan)

    """
    with open(output_path) as infile:
        for line in infile:
            match = re.match(f"Number of sentence\s+=\s+(\d+\.\d+)", line)
            if match:
                print(f'Number of sentences evaled: {match.group(1)}')
            match = re.match(r"Bracketing Recall\s+=\s+(\d+\.\d+)", line)
            if match:
                print("MATCH")
                fscore.recall = float(match.group(1))
            match = re.match(r"Bracketing Precision\s+=\s+(\d+\.\d+)", line)
            if match:
                fscore.precision = float(match.group(1))
            match = re.match(r"Bracketing FMeasure\s+=\s+(\d+\.\d+)", line)
            if match:
                fscore.fscore = float(match.group(1))
            match = re.match(r"Complete match\s+=\s+(\d+\.\d+)", line)
            if match:
                fscore.complete_match = float(match.group(1))
            match = re.match(r"Tagging accuracy\s+=\s+(\d+\.\d+)", line)
            if match:
                fscore.tagging_accuracy = float(match.group(1))
                break
    """
    with open(output_path) as infile:
        for line in infile:
            match = re.match(f"Number of sentence:\s+(\d+\.\d+)", line)
            if match:
                print(f'Number of sentences evaled: {match.group(1)}')
            match = re.match(r"Bracketing Recall:\s+(\d+\.\d+)", line)
            if match:
                print("MATCH")
                fscore.recall = float(match.group(1))
            match = re.match(r"Bracketing Precision:\s+(\d+\.\d+)", line)
            if match:
                fscore.precision = float(match.group(1))
            match = re.match(r"Bracketing FMeasure:\s+(\d+\.\d+)", line)
            if match:
                fscore.fscore = float(match.group(1))
            match = re.match(r"Complete match:\s+(\d+\.\d+)", line)
            if match:
                fscore.complete_match = float(match.group(1))
            match = re.match(r"Tagging accuracy:\s+(\d+\.\d+)", line)
            if match:
                fscore.tagging_accuracy = float(match.group(1))
                break
    #"""

    success = (
        not math.isnan(fscore.fscore) or
        fscore.recall == 0.0 or
        fscore.precision == 0.0)

    if success:
        #temp_dir.cleanup()
        print("Successfully parsed in:", predicted_path)
    else:
        print("Error reading EVALB results.")
        print("Gold path: {}".format(gold_path))
        print("Predicted path: {}".format(predicted_path))
        print("Output path: {}".format(output_path))
        import pdb;pdb.set_trace()
    return fscore
