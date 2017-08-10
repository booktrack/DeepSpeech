#!/bin/bash

cd /opt/DeepSpeech
. /opt/DeepSpeech/.env/bin/activate
python3 ./calculate_test_wer.py >> /opt/DeepSpeech/wer_log.txt
