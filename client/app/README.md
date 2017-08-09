
## DeepSpeech client

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
