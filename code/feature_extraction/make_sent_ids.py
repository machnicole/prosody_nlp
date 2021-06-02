import pandas as pd
import os


def extract_ids_from_time_file(infile,outfile):
    df = pd.read_csv(infile,sep='\t')

    with open(outfile,'w') as f:
        for i,row in df.iterrows():
            spk = row[1]
            conv,sent_num = row[2].split('~')
            sent_id = '_'.join((conv,spk,sent_num))
            f.write(sent_id)
            f.write('\n')
        
def main():
    # in_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/trees'
    # Not sure whether it's actually correct to specify trees here - the data in trees existed already
    # (we are not replicating something here)
    in_dir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/trees'
    # out_dir = '/afs/inf.ed.ac.uk/group/project/prosody/parsing/prosody_nlp/data/input_features'
    out_dir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/input_features'
    splits = ['train','dev','test']
    for spl in splits:
        extract_ids_from_time_file(os.path.join(in_dir,spl+'.times'),os.path.join(out_dir,spl+'_sent_ids.txt'))
                            
if __name__=="__main__":
    main()
