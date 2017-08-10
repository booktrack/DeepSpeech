#!/usr/bin/env python

import os
from functools import reduce
import tempfile
import logging
import datetime

from util.configuration import get_configuration
from util.speech_to_text import deep_speech_tt

from difflib import SequenceMatcher

# read system config
conf = get_configuration("settings.ini")

logging.basicConfig(level=logging.INFO)


# calculate the word error rate really simply and naively
# from the number of matching words - if the number of words doesn't match, return -1.0 for failure
# otherwise return 0.0 for a perfect match and 1.0 for a perfect mismatch
def calc_wer(t1: str, t2: str):
    parts_1 = t1.split(' ')
    parts_2 = t2.split(' ')
    if len(parts_1) == len(parts_2):  # pre-requisite
        num_wrong = 0.0
        for i in range(0, len(parts_1)):
            if parts_1[i] != parts_2[i]:
                num_wrong += 1.0
        return num_wrong / len(parts_1), num_wrong, len(parts_1)
    else:
        num_wrong = 0.0
        i1 = 0
        i2 = 0
        while i1 < len(parts_1) and i2 < len(parts_2):
            if parts_1[i1] != parts_2[i2]:
                num_wrong += 1.0
                if i1 + 1 < len(parts_1) and parts_1[i1 + 1] == parts_2[i2]:
                    i1 += 1
                elif i2 + 1 < len(parts_2) and parts_1[i1] == parts_2[i2 + 1]:
                    i2 += 1
                else:
                    i1 += 1
                    i2 += 1
            else:
                i1 += 1
                i2 += 1
        largest = max(len(parts_1), len(parts_2))
        return num_wrong / largest, num_wrong, largest


# return the date time formatted, e.g. "2017-08-10, 14:34:04"
def get_time_str():
    return datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")


if __name__ == '__main__':

    wer_list = []
    base_path = os.path.join(os.path.dirname(__file__), 'data/wer_test')
    test_file_list = [item for item in open(os.path.join(base_path, 'test_data.csv')).read().strip().split('\n')]
    counter = 1
    total_errors = 0
    total_words = 0
    for test_file in test_file_list:
        if len(test_file) > 0:
            parts = test_file.split(',')
            if len(parts) == 2:
                filename = parts[0]
                print("|---------------------------------------------------------------------------- " + get_time_str())
                print("| checking " + filename + " (" + str(counter) + "/" + str(len(test_file_list)) + ")", end=',')
                counter += 1
                text1 = parts[1].strip().lower()

                input_sound_file = os.path.join(base_path, filename)
                temp_name = next(tempfile._get_candidate_names())
                text_output_tuple = deep_speech_tt(conf["DeepSpeech"], temp_name, input_sound_file, 60)
                text2 = ''.join([item for item, _ in text_output_tuple])

                wer, errs, count = calc_wer(text1, text2)
                wer_list.append(wer)
                total_errors += errs
                total_words += count

                c_wer = total_errors / total_words
                print(" WER:" + str(round(wer, 5)) + ", cumulative WER:" + str(round(c_wer, 5)))
                print("| " + text1)
                print("| " + text2)

    # cumulative word error rate - total number of errors over the total number of words
    c_wer = total_errors / total_words
    mean = reduce(lambda x, y: x + y, wer_list) / len(wer_list)
    print("|---------------------------------------------------------------------------------------------")
    print("| average WER:" + str(round(mean, 5)) + ", final WER:" + str(round(c_wer, 5)))
    print("|---------------------------------------------------------------------------------------------")
