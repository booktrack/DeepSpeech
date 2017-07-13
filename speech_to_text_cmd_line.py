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

    if len(sys.argv) != 2:
        print("takes one argument: sound-file to convert to text")
    else:
        input_sound_file = sys.argv[1]
        temp_name = next(tempfile._get_candidate_names())

        text_output_list = deep_speech_tt(conf["DeepSpeech"], temp_name, input_sound_file, int(conf["DeepSpeech"]["silence_db"]))
        for text_out in text_output_list:
            print(text_out)
