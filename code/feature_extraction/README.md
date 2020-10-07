Notes by EKN:

After using the kaldi scripts to extract:

mfccs
fbank_energy
pitch_pov

you will need to run process_kaldi_feats_splits.py to combine these into files that correspond to the original audio files.

Notes on the alignment dictionary:

info is a dict where
     keys = phonword (ids)
     values = a dict with keys:
     	    text ~ raw phonword text
	    phones ~ probably phones?
	    phone_start_times
	    phone_end_times
	    start_time
	    end_time




Next, you'll need forced alignments. Use The Penn Phonetics Lab Forced Aligner (P2FA) to be consistent with the 'Effects of style' paper.

Next run the get_ta_stats.py script and then the extract_ta_features.py script.