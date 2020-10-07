with open('dev.times','r') as f:
    timelines = [l.strip() for l in f.readlines()]
with open('../input_features/dev_sent_ids.txt','r') as f:
    id_lines = [l.strip() for l in f.readlines()]

time_ids = []
for line in timelines:
    conv,spk,sent,_,_,_ = line.split('\t')
    sent = sent.split('~')[-1]
    time_ids.append('_'.join([conv,spk,sent]))

time_ids = sorted(time_ids)
id_lines = sorted(id_lines)



with open ('dev_sent_ids_from_times_file.txt','w') as f:
    for line in time_ids:
        f.write(f'{line}\n')
