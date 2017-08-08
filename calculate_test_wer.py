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


def calc_wer(t1: str, t2: str):
    parts_1 = t1.split(' ')
    parts_2 = t2.split(' ')
    if len(parts_1) == len(parts_2):
        num_wrong = 0.0
        for i in range(0, len(parts_1)):
            if parts_1[i] != parts_2[i]:
                num_wrong += 1.0
        return num_wrong / len(parts_1)
    return -1.0  # can't in sequence


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

            wer = calc_wer(text1, text2)
            if wer == -1.0:
                print("using SequenceMatcher()")
                m = SequenceMatcher(None, text1, text2)
                wer = 1.0 - m.ratio()
            wer_list.append(wer)
            print("         " + filename + " WER:" + str(round(wer, 5)))
            if wer > 0.1:
                print(text1)
                print(text2)
                print()

    mean = reduce(lambda x, y: x + y, wer_list) / len(wer_list)
    print("\nmean WER:" + str(round(mean, 5)))
