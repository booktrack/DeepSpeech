#!/usr/bin/env python

import os
from functools import reduce
import tempfile
import logging

from util.configuration import get_configuration
from util.speech_to_text import deep_speech_tt

from difflib import SequenceMatcher

# read system config
conf = get_configuration("settings.ini")

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':

    wer_list = []
    base_path = os.path.join(os.path.dirname(__file__), 'data/wer_test')
    test_file_list = [item for item in open(os.path.join(base_path, 'test_data.csv')).read().split('\n')]
    counter = 1
    for test_file in test_file_list:
        parts = test_file.split(',')
        if len(parts) == 2:
            filename = parts[0]
            print("checking " + filename + " (" + str(counter) + "/" + str(len(test_file_list)) + ")")
            counter += 1
            text1 = parts[1].strip().lower()

            input_sound_file = os.path.join(base_path, filename)
            temp_name = next(tempfile._get_candidate_names())
            text_output_tuple = deep_speech_tt(conf["DeepSpeech"], temp_name, input_sound_file, 60)
            text_temp = ''.join([item for item, _ in text_output_tuple])
            list = []
            for item in text_temp.split(' '):
                if item == "un":
                    list.append("unc")
                else:
                    list.append(item)
            text2 = ' '.join(list)

            m = SequenceMatcher(None, text1, text2)
            wer = 1.0 - m.ratio()
            print("         " + filename + " WER:" + str(round(wer, 5)))
            wer_list.append(wer)

    mean = reduce(lambda x, y: x + y, wer_list) / len(wer_list)
    print("\nmean WER:" + str(round(mean, 5)))
