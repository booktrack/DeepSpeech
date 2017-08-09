#!/usr/bin/env python

import sys
import tempfile
import logging

from util.configuration import get_configuration
from util.speech_to_text import deep_speech_tt

# read system config
conf = get_configuration("settings.ini")

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__' :

    if len(sys.argv) != 2 and len(sys.argv) != 3 and len(sys.argv) != 4:
        print("takes up to three arguments (one parameter required): /path/to/soundfile.mp3  "
              "[noise_db_max] [min_silence_length_in_secs]")
        print("      e.g.  ./speech_to_text_cmd_line.py /test/file.ogg 30 0.5")
    else:
        input_sound_file = sys.argv[1]
        silence_db = int(conf["DeepSpeech"]["silence_db"])
        if len(sys.argv) > 2:
            silence_db = int(sys.argv[2])
        silence_length_in_secs = float(conf["DeepSpeech"]["silence_length_in_secs"])
        if len(sys.argv) > 3:
            silence_length_in_secs = float(sys.argv[3])

        temp_name = next(tempfile._get_candidate_names())

        text_output_list = deep_speech_tt(conf["DeepSpeech"], temp_name, input_sound_file,
                                          silence_db, silence_length_in_secs)
        for text_out in text_output_list:
            print(text_out)
