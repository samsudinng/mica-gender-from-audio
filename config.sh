feats_flag="y"      # "y"/"n" flag to keep kaldi-feature files after inference
wavs_flag="n"       # "y"/"n" flag to keep .wav audio files after inference
nj=4                # Number of parallel processes for kaldi steps
vad_overlap=0       # % overlap in VAD-segments (range: 0-1, 0 for no overlap) (single segment is 0.64s)
gender_overlap=0    # % overlap in GENDER-segment 
