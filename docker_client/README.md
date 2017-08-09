
## DeepSpeech client

The required files for the docker build need to be FIRST COPIED from the data directory into a local data directory.
This is because running docker from the root of this project with its potentially millions of speech
files causes Docker to send these as docker context files, slowing down the process of building the images
significantly.

FIRST RUN `setup_for_docker.sh` from the `docker_client` directory.


## docker build
```
docker build -t dsclient .
```

## docker run
```
cat app/data/1284-1180-0010.wav | docker run --rm -i dsclient
```
example output
```
('un knocked at the door of the house and a chubby pleasant faced woman dressed all in blu opened it and greeted the visitors with a smile', 0.0)
```
