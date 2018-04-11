# mica-gender-from-audio
This tool can be used for noise-robust gender identification from audio. Two parallel systems are implemented for this purpose: 1) Voice Activity Detection (VAD) and 2) Gender classification of speech segments. VAD is implemented using a recurrent neural-network (BLSTM) trained on movie audio, while gender classification is implemented using a deep neural network architecture trained on a subset of AudioSet dataset. The input to the VAD system are 23 dimensional  log-Mel filterbank features corresponding to a 10ms frame (with 15 frames context), and the input to the gender system is a pre-trained embedding (link to VGGish) corresponding to a 960ms segment. The gender segments, in the form of timestamps, are obtained via masking the gender predictions by the VAD labels obtained.
##