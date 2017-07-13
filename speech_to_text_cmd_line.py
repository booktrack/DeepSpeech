#!/usr/bin/env python

# this file uses the lm.bin and log likelyhood defined by it to correct speech output back to "English"

import os
import sys
import tempfile
import subprocess
import logging

from util.spell import correction
from util.sound_splitter import split_soundfile_into_many

ffmpeg_executable = '/usr/bin/ffmpeg'
deepspeech_executable = "/usr/local/bin/deepspeech"
deepspeech_graph = "/opt/DeepSpeech/data/graph/output_graph.pb"

if __name__ == '__main__' :

    if len(sys.argv) != 2:
        print("takes one argument: sound-file to convert to text")
    else:
        input_sound_file = sys.argv[1]
        temp_name = next(tempfile._get_candidate_names())
        temp_file_name = os.path.join(tempfile._get_default_tempdir(), temp_name + ".wav")

        required_files = [input_sound_file, ffmpeg_executable, deepspeech_executable, deepspeech_graph]

        for file in required_files:
            if not os.path.isfile(ffmpeg_executable):
                raise ValueError("file/executable/data missing:" + file)


        # convert any soundfile using ffmpeg to the right format
        # ffmpeg -i bill_gates-TED.mp3 -acodec pcm_s16le -ac 1 -ar 16000 output.wav
        logging.debug("converting " + input_sound_file + " to the correct input format")
        with open(os.devnull, 'w') as f_null:
            subprocess.call([ffmpeg_executable, "-i", input_sound_file, "-acodec", "pcm_s16le",
                             "-ac", "1", "-ar", "16000", temp_file_name], stdout=f_null, stderr=f_null)
        if not os.path.isfile(temp_file_name):
            raise ValueError("file not converted:" + input_sound_file)

        # split the sound file into many for very long files
        logging.debug("splitting sound-file into many")
        sound_file_list = split_soundfile_into_many(temp_name, temp_file_name)
        logging.debug("split into " + str(sound_file_list) + " parts")

        # use the deepspeech native executable to convert the given wav file to text
        #
        logging.debug("running deepspeech")
        raw_output_list = []
        counter = 1
        for sound_file, interval in sound_file_list:
            logging.debug("prcessing " + str(counter) + " of " + str(len(sound_file_list)) )
            process = subprocess.Popen([deepspeech_executable, deepspeech_graph, sound_file], stdout=subprocess.PIPE)
            out, err = process.communicate()
            if err is not None:
                raise ValueError(err)
            # change bytes back to text
            text = out.decode("utf-8")
            raw_output_list.append((text, interval))
            counter += 1

        # and output the corrected text
        for text, interval in raw_output_list:
            print(correction(text) + "|" + str(interval))
