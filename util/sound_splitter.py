import os
import librosa
import logging
import tempfile


# top_db : number > 0, The threshold (in decibels) below reference to consider as silence
# frame_length : int > 0, The number of samples per analysis frame
# hop_length : int > 0, The number of samples between analysis frames
def _split_sound_file(filename: str, top_db=20, frame_length=4096, hop_length=512, sr=8000):
    # load the soundfile
    y, sr = librosa.load(filename, mono=True, sr=sr)
    i_vals = librosa.effects.split(y, top_db=top_db, frame_length=frame_length, hop_length=hop_length)
    return y, i_vals


# split a sound-file across multiple sound-files
def split_soundfile_into_many(job_id: str, sound_filename: str, top_db=20, frame_length=4096, hop_length=512, sr=16000):
    # split the file
    logging.debug("splitting file " + sound_filename)
    y, intervals = _split_sound_file(sound_filename, sr=sr, top_db=top_db, frame_length=frame_length, hop_length=hop_length)

    # save the temp sections of the file (the splits)
    logging.debug("writer file splits for " + sound_filename)
    counter = 0
    filename_list = []
    for interval in intervals:
        filename = os.path.join(tempfile.gettempdir(), job_id + '_' + str(counter) + '.wav')
        logging.debug("writing " + filename)
        librosa.output.write_wav(filename, y[interval[0]:interval[1]], sr)
        filename_list.append((filename, interval[0]))
        counter += 1

    return filename_list
