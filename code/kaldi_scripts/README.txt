Scripts for extracting kaldi features; assumes kaldi is already properly
installed. All of these were taken from kaldi/egs/swbd/s5c, with main
modifications to the configuration files conf/fbank.config to get 40 filter
coefficients and energy.

** Don't forget to change directory names where appropriate

# Instructions:

0. Install kaldi
1. Set paths in `comp_all.sh` and `paths.sh` to point to data, kaldi installation, and output directory
2. Run `./paths.sh`
3. Run `./comp_all.sh`
