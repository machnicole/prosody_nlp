import pandas as pd
import os

datadir = '/afs/inf.ed.ac.uk/group/project/prosody/prosody_nlp/data/input_features/turn/'

# Load dev conversation ids:
dev_turn_ids = [l.strip() for l in open(os.path.join(datadir,'turn_dev_sent_ids_medium.txt')).readlines()]
dev_trees = [l.strip() for l in open(os.path.join(datadir,'turn_dev_medium.trees')).readlines()]

id2tree = dict(zip(dev_turn_ids,dev_trees))

dev_convs = set()
for iden in dev_turn_ids:
    convid = int(iden.split('_')[0].replace('sw',''))
    dev_convs.add(convid)



metadata_f = os.path.join(datadir,'swda-metadata.csv')

# Sort conversations + sides into dictionaries
sex_dict = {'FEMALE':[],
               'MALE':[]}

generation_dict = {'greatest':[],
                   'silent':[],
                   'boom':[],
                   'x':[],
                   'mill':[]}

education_dict = {0:[],
                  1:[],
                  2:[],
                  3:[],
                  9:[]}

region_dict = {'MIXED':[],
               'NEW_ENGLAND':[],
               'NORTH_MIDLAND':[],
               'NORTHERN':[],
               'NYC':[],
               'SOUTH_MIDLAND':[],
               'SOUTHERN':[],
               'UNK':[],
               'WESTERN':[]}

df = pd.read_csv(metadata_f)
for i,row in df.iterrows():
    conv_num = row['conversation_no']
    if conv_num in dev_convs:
        for spk,direction in zip(('A','B'),('from','to')):
            # By sex
            sex = row[f'{direction}_caller_sex']
            sex_dict[sex].append((conv_num,spk))
            # By generation
            gen = row[f'{direction}_caller_birth_year']
            if gen > 1901 and gen < 1928:
                generation_dict['greatest'].append((conv_num,spk))
            elif gen > 1927 and gen < 1946:
                generation_dict['silent'].append((conv_num,spk))
            elif gen > 1945 and gen < 1965:
                generation_dict['boom'].append((conv_num,spk))
            elif gen > 1964 and gen < 1981:
                generation_dict['x'].append((conv_num,spk))
            elif gen > 1980 and gen < 1997:
                generation_dict['mill'].append((conv_num,spk))
            # By education
            ed = row[f'{direction}_caller_education']
            education_dict[ed].append((conv_num,spk))
            # By region
            reg = row[f'{direction}_caller_dialect_area']
            reg = '_'.join(reg.split())
            region_dict[reg].append((conv_num,spk))


demo_dicts = [sex_dict,region_dict,education_dict,generation_dict]

for dictionary in demo_dicts:
    for feature in dictionary:
        out_ids = os.path.join(datadir,f'turn_dev_sent_ids_{feature}.txt')
        out_trees = os.path.join(datadir,f'turn_dev_{feature}.trees')
        with open(out_ids,'w') as fids:
            with open(out_trees,'w') as ftrees:
                for conv,spk in dictionary[feature]:
                    relevant_turns = [turn for turn in dev_turn_ids if f'{conv}_{spk}' in turn]
                    for turn in relevant_turns:
                        fids.write(turn)
                        fids.write('\n')
                        ftrees.write(id2tree[turn])
                        ftrees.write('\n')


