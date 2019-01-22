###
###
###     Script to predict gender of audio segment
###     using vggish-embeddings extracted at 0.96s
###     frame-level
###     
###     Arguments:
###     1) expt_dir   : Output directory which contains
###         'features' and 'VAD' directories
###     2) model_file : Gender model trained on Keras.
###
###     Output:
###     1) timestamps-file : in the format 
###         "start-time(s) end-time(s) Gender(M/F)"
###         for each audio file
###     2) posterior-file  : Gender model output 
###         at frame-level for each file (0-->M, 1-->F)
###

import numpy as np
np.warnings.filterwarnings('ignore')
import os, sys
from scipy import signal as sig
os.environ["CUDA_VISIBLE_DEVICES"]=""
os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')
import keras
sys.stderr = stderr
import tensorflow as tf
from keras.models import load_model
import keras.backend as K
config=tf.ConfigProto(intra_op_parallelism_threads=16, inter_op_parallelism_threads=16)
import warnings
warnings.filterwarnings("ignore")
#from train_gender import FullyConnected
#config = tf.ConfigProto()
#config.gpu_options.per_process_gpu_memory_fraction = 0.2

def generate_single_example(example):
    context_features = {'movie_id': tf.FixedLenFeature([], tf.string)}
    sequence_features = {'audio_embedding': tf.FixedLenSequenceFeature([], tf.string)}

    context_parsed, sequence_parsed = tf.parse_single_sequence_example(example, 
        context_features = context_features, sequence_features = sequence_features)

    normalized_feature = tf.divide(
                tf.decode_raw(sequence_parsed['audio_embedding'], tf.uint8),
                tf.constant(255, tf.uint8))
    shaped_feature = tf.reshape(tf.cast(normalized_feature, tf.float32),
                                    [-1, 128])
    
    return context_parsed['movie_id'], shaped_feature


def main():
    expt_dir = sys.argv[1]
    vad_ts_dir = os.path.join(expt_dir, 'VAD/timestamps/')
    write_post = os.path.join(expt_dir, 'GENDER/posteriors/')
    write_ts   = os.path.join(expt_dir, 'GENDER/timestamps/')
    feats_path = os.path.join(expt_dir, 'features/vggish/')
    
    if not os.path.exists(write_post):
        os.makedirs(write_post)
    if not os.path.exists(write_ts):
        os.makedirs(write_ts)

    tfr_file = os.listdir(feats_path)
    tfr_paths = [feats_path + x for x in tfr_file]
    reader = tf.TFRecordReader()
    file_queue = tf.train.string_input_producer(tfr_paths, num_epochs=1, shuffle=False)
    with tf.Session(config=config) as sess:
        K.set_session(sess)
        _, ser_example = reader.read(file_queue)
        sess.run(tf.global_variables_initializer())
        sess.run(tf.local_variables_initializer())
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord)
        model = load_model(sys.argv[2])
        gender = {'0':'M','1':'F'}
        used = []

        while 1:
            try:
                context, sequence = generate_single_example(ser_example)
                [movie, feats] = sess.run([context, sequence])
                pred = model.predict(feats)

                fpost = open(os.path.join(write_post, movie + '.post'),'w')
                for label in pred:
                    fpost.write('{0:0.2f}\n'.format(label[1]))
                fpost.close()
                
                vad_data = [x.rstrip().split() for x in open(os.path.join(vad_ts_dir, movie + '.ts'), 'r').readlines()]
                vad_times = [[float(x[0]), float(x[1])] for x in vad_data]
#                gender_labels = sig.medfilt(np.round(pred), 3)
                gender_labels = np.round([np.repeat(x[1],96) for x in pred]).flatten()
                
                fts = open(os.path.join(write_ts, movie + '.ts'),'w')

                for seg in vad_times:
                    start = int(seg[0]*100)
                    end = int(seg[1]*100)
                    if start>=end or end > len(gender_labels):
                        continue
                    gender_seg = int(np.median(gender_labels[start:end]))
                    fts.write('{}\t{}\t{}\n'.format(seg[0], seg[1], gender[str(gender_seg)]))
                fts.close()
            except:
                coord.request_stop()
                coord.join(threads)
                sess.close()
                break
if __name__ == '__main__':
    main()
