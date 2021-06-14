distro=$(lsb_release -sd)
if [[ ${distro} == *Ubuntu* ]]; then
    export KALDI_ROOT="/afs/inf.ed.ac.uk/group/teaching/asr/tools/kaldi-ubuntu"
else
    export KALDI_ROOT="/afs/inf.ed.ac.uk/group/teaching/asr/tools/kaldi"
fi

[ -f $KALDI_ROOT/tools/env.sh ] && . $KALDI_ROOT/tools/env.sh
export PATH=$PWD/utils/:$KALDI_ROOT/tools/openfst/bin:$KALDI_ROOT/tools/irstlm/bin/:$KALDI_ROOT/tools/google-cloud-sdk/bin:$PWD:$PATH

[ ! -f $KALDI_ROOT/tools/config/common_path.sh ] && echo >&2 "The standard file $KALDI_ROOT/tools/config/common_path.sh is not present -> Exit!" && exit 1
. $KALDI_ROOT/tools/config/common_path.sh

export LD_LIBRARY_PATH=$KALDI_ROOT/tools/openfst/lib:$KALDI_ROOT/tools/openfst/lib/fst:$KALDI_ROOT/tools/irstlm/lib:$LD_LIBRARY_PATH
export LC_ALL=C

export FST=$KALDI_ROOT/tools/openfst
export LD_LIBRARY_PATH=$FST/lib:$FST/lib/fst:$LD_LIBRARY_PATH
