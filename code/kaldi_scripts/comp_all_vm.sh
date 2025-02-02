#!/bin/bash
source kaldi_path.sh # contains KALDI_ROOT

#KALDI_ROOT=/afs/inf.ed.ac.uk/group/project/prosody/kaldi # kaldi location
NUM=$1

#maindir=/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/testoutput # output location
##sdir=/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/sample_sph_files # VM location
#sdir=/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/sample_sph_files # VM location

# English
#maindir=/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_eng_kaldi_output # output location
#maindir=/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_eng_kaldi_exp_output
#sdir=/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_eng_wavs # VM location
#my_data_list=/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/input_features/all_clean_sent_ids.txt
#sdir=/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_eng_ch1 # VM location
#my_data_list=/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_eng_ch1/data.txt

# German
maindir=/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_ger_kaldi_output # output location
sdir=/afs/inf.ed.ac.uk/group/msc-projects/s2096077/vm_ger_wavs # VM location
my_data_list=/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/data/vm/ger/input_features/all_clean_sent_ids.txt

swdir=${KALDI_ROOT}/src/featbin
utils=${KALDI_ROOT}/egs/swbd/s5c/utils
## make list of files to process
#find $sdir -iname '*.sph' | sort > sph.flist
##find $sdir -iname 'sw0410*.sph' | sort > sph.flist
#sed -e 's?.*/??' -e 's?.sph??' sph.flist | paste - sph.flist > sph.scp
#
#sph2pipe=$KALDI_ROOT/tools/sph2pipe_v2.5/sph2pipe
#
#[ ! -x $sph2pipe ] \
#  && echo "Could not execute the sph2pipe program at $sph2pipe" && exit 1;
#
#awk -v sph2pipe=$sph2pipe '{
#  printf("%s %s -f wav -p -c 1 %s |\n", $1, sph2pipe, $2);
#}' < sph.scp | sort > wav.scp || exit 1;
##side A - channel 1, side B - channel 2
#
#awk '{print $1}' wav.scp \
#  | perl -ane '$_ =~ m:^(\S+)$: || die "bad label $_";
#               print "$1-$2 $1 $2\n"; ' \
#	 > reco2file_and_channel || exit 1;
#


sox=`which sox`
if [ $? -ne 0 ] ; then
  echo "Could not find sox binary. Add it to PATH"
  exit 1;
fi

for file in `cat $my_data_list | sort -u` ; do
  echo "$file $sox $sdir/$file.wav -r 8000 -c 1 -b 16 -t wav - downsample |"
#  echo "$file $sdir/$file.wav"
done | sort -u > wav.scp

awk '{print $1}' wav.scp \
  | perl -ane '$_ =~ m:^(\S+)$: || die "bad label $_";
               print "$1-$2 $1 $2\n"; ' \
	 >> reco2file_and_channel || exit 1;

mfccdir=$maindir/mfcc
pitchdir=$maindir/pitch_pov
fbankdir=$maindir/fbank_energy
nj=8
cmd=$utils/run.pl
mfcc_config=conf/mfcc.conf
pitch_config=conf/pitch.conf
fbank_config=conf/fbank.conf
compress=true

data=$sdir
logdir=$maindir/log

# use "name" as part of name of the archive.
name=`basename $data`

mkdir -p $mfccdir || exit 1;
mkdir -p $pitchdir || exit 1;
mkdir -p $fbankdir || exit 1;
mkdir -p $logdir || exit 1;

if [ -f $maindir/feats.scp ]; then
    mkdir -p $maindir/.backup
    echo "$0: moving $maindir/feats.scp to $maindir/.backup"
    mv $maindir/feats.scp $maindir/.backup
fi

cp wav.scp $maindir/
scp=$maindir/wav.scp
required="$scp $mfcc_config $pitch_config $fbank_config"

for f in $required; do
    if [ ! -f $f ]; then
        echo "make_mfcc.sh: no such file $f"
        exit 1;
    fi
done

split_scps=""
for n in $(seq $nj); do
    split_scps="$split_scps $logdir/wav_${name}.$n.scp"
done

$utils/split_scp.pl $scp $split_scps || exit 1;


# You have to use the ",t" modifier on the output, for instance
# copy-feats scp:feats.scp ark,t:-

# compute mfccs here

#$cmd JOB=1:$nj $logdir/make_mfcc_${name}.JOB.log \
#$swdir/compute-mfcc-feats --verbose=2 --config=$mfcc_config \
#scp,p:$logdir/wav_${name}.JOB.scp ark:- \| \
#$swdir/copy-feats --compress=$compress ark:- \
#ark,scp:$mfccdir/raw_mfcc_$name.JOB.ark,$mfccdir/raw_mfcc_$name.JOB.scp \
#|| exit 1;
#
#$cmd JOB=1:$nj $logdir/copy_text_${name}.JOB.log \
#$swdir/copy-feats ark:$mfccdir/raw_mfcc_$name.JOB.ark ark,t:$mfccdir/raw_mfcc_$name.JOB.txt \
#|| exit 1;
#
#if [ -f $logdir/.error.$name ]; then
#  echo "Error producing MFCC features for $name:"
#  tail $logdir/make_mfcc_${name}.1.log
#  exit 1;
#fi
#
## concatenate the .scp files together.
#for n in $(seq $nj); do
#  cat $mfccdir/raw_mfcc_$name.$n.scp || exit 1;
#done > $maindir/feats.scp

echo "Starting to create pitch features..."
# compute pitch feats (+pov) here
$cmd JOB=1:$nj $logdir/make_pitch_${name}.JOB.log \
$swdir/compute-kaldi-pitch-feats --verbose=2 --config=$pitch_config \
scp,p:$logdir/wav_${name}.JOB.scp ark:- \| \
$swdir/process-kaldi-pitch-feats ark:- ark:- \| \
$swdir/copy-feats --compress=$compress ark:- \
ark,scp:$pitchdir/raw_pitch_$name.JOB.ark,$pitchdir/raw_pitch_$name.JOB.scp \
|| exit 1;

$cmd JOB=1:$nj $logdir/copy_text_${name}.JOB.log \
$swdir/copy-feats ark:$pitchdir/raw_pitch_$name.JOB.ark ark,t:$pitchdir/raw_pitch_$name.JOB.txt \
|| exit 1;

if [ -f $logdir/.error.$name ]; then
  echo "Error producing pitch features for $name:"
  tail $logdir/make_pitch_${name}.1.log
  exit 1;
fi

# concatenate the .scp files together.
for n in $(seq $nj); do
  cat $pitchdir/raw_pitch_$name.$n.scp || exit 1;
done > $maindir/feats.scp

echo "Done."
echo "Starting to create intensity features..."

## compute fbank (+energy) here
$cmd JOB=1:$nj $logdir/make_fbank_${name}.JOB.log \
$swdir/compute-fbank-feats --verbose=2 --config=$fbank_config \
scp,p:$logdir/wav_${name}.JOB.scp ark:- \| \
$swdir/copy-feats --compress=$compress ark:- \
ark,scp:$fbankdir/raw_fbank_$name.JOB.ark,$fbankdir/raw_fbank_$name.JOB.scp \
|| exit 1;

$cmd JOB=1:$nj $logdir/copy_text_${name}.JOB.log \
$swdir/copy-feats ark:$fbankdir/raw_fbank_$name.JOB.ark ark,t:$fbankdir/raw_fbank_$name.JOB.txt \
|| exit 1;

if [ -f $logdir/.error.$name ]; then
  echo "Error producing fbank features for $name:"
  tail $logdir/make_fbank_${name}.1.log
  exit 1;
fi

# concatenate the .scp files together.
for n in $(seq $nj); do
  cat $fbankdir/raw_fbank_$name.$n.scp || exit 1;
done > $maindir/feats.scp

rm $logdir/wav_${name}.*.scp  2>/dev/null

echo "Succeeded creating features for $name"

