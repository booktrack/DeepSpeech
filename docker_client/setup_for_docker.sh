#!/bin/bash

# this file copies the required files for the docker build from the data directory into a local data directory
# here.  This is because running docker from the root of this project with its potentially millions of speech
# files causes Docker to send these as docker context files, slowing down the process of building the images
# significantly.  This file must be run from within the docker_client directory!!!

if [ ! -e "../data/graph/output_graph.pb" ]; then
  echo "cannot find ../data/graph/output_graph.pb.  Make sure you run export_graph.py, see ../README.md"
  exit 1
fi

mkdir -p data/lm
mkdir data/graph
mkdir data/spell

cp ../data/lm/lm.binary data/lm/
cp ../data/graph/output_graph.pb data/graph/
cp ../data/spell/words.txt data/spell/
