
## DeepSpeech client

The required files for the docker build need to be FIRST COPIED from the data directory into a local data directory.
This is because running docker from the root of this project with its potentially millions of speech
files causes Docker to send these as docker context files, slowing down the process of building the images
significantly.

## docker build
```
cd docker_client
./setup_for_docker.sh
docker build -t dsclient .
```

## docker run
The run takes an input stream of an audio file that can be processed by ffmpeg and a two parameters for detecting silences.
The first parameter (40 in the example below) is the maximum noise level in decibels (suggest values of 10 through 60)
The second parameter (1.5 in the below example) is the minimum length of a silence in seconds.
```
cat app/data/1284-1180-0010.wav | docker run --rm -i dsclient 40 1.5
```
example output
```
('un knocked at the door of the house and a chubby pleasant faced woman dressed all in blu opened it and greeted the visitors with a smile', 0.0)
```
