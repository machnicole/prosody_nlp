import os
import json
import pickle
# English
# avg_dur_dir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm'
# stat_dir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ta_features/stats'
# out_dir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features'
# phone2meandur_file = os.path.join(out_dir,'phone2meandur.pickle')

# German
avg_dur_dir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger'
stat_dir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/ta_features/stats'
out_dir = '/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features'
phone2meandur_file = os.path.join(out_dir,'phone2meandur.pickle')

# word_stats is a dictionary of the form:
# word_stats[k] = [len(v), np.mean(v), np.std(v)]
word_stats = pickle.load(open(os.path.join(stat_dir, 'word_raw_stats.pickle'), "rb"))
# phone_stats is a dictionary of the form:
# phone_stats[k] = [len(v), np.mean(v), np.std(v)]
phone_stats = pickle.load(open(os.path.join(stat_dir, 'phone_raw_stats.pickle'), "rb"))

word_stats_dict = {}
for word, stats in word_stats.items():
    assert len(stats) == 3
    word_stats_dict[word] = {"count": stats[0],
                             "mean": stats[1],
                             "std": stats[2]}

word_stats_json = json.dumps(word_stats_dict)

with open(os.path.join(avg_dur_dir,'avg_word_stats.json'),'w') as f:
    f.write(word_stats_json)

phone2meandur = {}
for phone, stats in phone_stats.items():
    assert len(stats) == 3
    meandur = stats[1]
    phone2meandur[phone] = meandur

with open(phone2meandur_file,'wb') as f:
    pickle.dump(phone2meandur,f)
