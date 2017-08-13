#!/bin/bash

base=/home/peter/dev/booktrack/DeepSpeech
cd $base
. $base/.env/bin/activate

#while [ 1 ]
#do

  # rebuild using current graph
  graph=$base/data/graph
  if [ -e $graph/input_graph.pb ];
  then
    rm -f $graph/input_graph.pb
    rm -f $graph/output_graph.pb
    rm -rf $graph/00000001
  fi

  # create new graph
  python3 ./export_graph.py --checkpoint_dir $base/data/ckpt --export_dir $graph

  # run wer
  python3 ./calculate_test_wer.py >> $base/wer_log.txt

#  sleep 1h

#done
