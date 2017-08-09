#!/usr/bin/python3

import os
import sys
import tempfile
import logging

# add this path to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from util.configuration import get_configuration
from util.speech_to_text import deep_speech_tt

# read system config
conf = get_configuration("settings.ini")

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__' :

    if len(sys.argv) != 3:
        print("takes two arguments (and the file from stdin): max_noise_db (e.g. 40) min_silence_length_in_secs (e.g. 1.0)")
    else:

        temp_name = next(tempfile._get_candidate_names())
        input_sound_file = os.path.join('/tmp', temp_name)
        with open(input_sound_file, 'wb') as writer:
            writer.write(sys.stdin.buffer.read())

        # get the directory this is ran from
        base_dir = os.path.dirname(__file__)
        graph = os.path.join(base_dir, 'data/graph/output_graph.pb')
        if not os.path.isfile(graph):
            raise ValueError("graph file not found:" + graph)

        silence_db = int(sys.argv[1])
        silence_length_in_secs = float(sys.argv[2])

        temp_name = next(tempfile._get_candidate_names())

        text_output_list = deep_speech_tt(conf["DeepSpeech"], temp_name, input_sound_file,
                                          silence_db, silence_length_in_secs, graph)
        for text_out in text_output_list:
            print(text_out)
