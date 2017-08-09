#!/usr/bin/env python

import os
import json
from flask import Flask
from flask import request
import tempfile
import uuid
import logging
from multiprocessing import Pool

from util.configuration import get_configuration
from util.logger import setup_logging
from util.check_path import check_path
from util.speech_to_text import processing_thread, get_progress

# setup this program's logger
config = get_configuration(os.path.join(os.path.dirname(__file__), "settings.ini"))
setup_logging(config)

# 8000 bytes minimum size (1 second at 8KHz)
min_size_in_bytes_of_soundfile = 8000
# preset Maximum size
max_size_in_bytes_of_soundfile = int(config["Service"]["max_upload_size_in_mb"]) * 1024 * 1000
# the pool for handling processing requests in parallel / async
pool = Pool(int(config["Service"]["pool_size"]))


app = Flask(__name__)


# start a new speech to text processing
# example use:
# curl -X POST -F "file=@/home/peter/dev/data/r_nixon_short.wav" http://localhost:8111/api/v1/start_deep_speech_to_text
@app.route('/api/v1/start_deep_speech_to_text', methods=['GET', 'POST'])
def start_deep_speech_to_text():
    silence_db = request.args.get('silence_db', int(config["DeepSpeech"]["silence_db"]), int)
    silence_length_in_secs = request.args.get('silence_length_in_secs', float(config["DeepSpeech"]["silence_length_in_secs"]), float)
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file:
                sound_filename = file.filename
                parts = sound_filename.split('.')
                if len(parts) < 2:
                    return json.dumps({'error': "invalid filename, must have file-type extension (e.g. '.mp3')"})
                else:
                    # save the binary data to disk for processing
                    unique_id = uuid.uuid4().__str__()
                    filename = os.path.join(tempfile.gettempdir(), unique_id + '.' + parts[-1])
                    check_path(filename, tempfile.gettempdir())  # security, check path is ok
                    file.save(filename)
                    # async process the request
                    pool.apply_async(processing_thread, (config["DeepSpeech"], unique_id, filename, silence_db, silence_length_in_secs))
                    # in the meantime return the query id
                    return json.dumps({"id": unique_id, "links": [
                                       {"rel": "results", "type": "application/json", "title": "Speech to Text results", "href": "/api/v1/get_speech_to_text?id=" + unique_id }
                                    ]})

        return json.dumps({'error': 'sound-file-upload missing file'})

    return '''
    <!doctype html>
    <title>DeepSpeech to Text Service [GET]</title>
    <h1>Upload Sound File to DeepSpeech</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


# check for a given ID if the system has finished processing it
# example: curl -X GET http://localhost:8111/api/v1/get_speech_to_text?id=10505678-56a2-4828-a21e-f88b6b9e5060
# returns {"message": "busy"} (see below) if not yet available, otherwise returns {"data": [(text: str, abs_time_in_secs: float)]}
@app.route('/api/v1/get_speech_to_text', methods=['GET'])
def get_speech_to_text():
    job_id = request.args['id']
    if len(job_id) != 36:
        return json.dumps({'message': 'invalid id'})
    else:
        text_filename = os.path.join(tempfile.gettempdir(), job_id + '.txt')
        check_path(text_filename, tempfile.gettempdir())  # security, check path is ok
        if os.path.isfile(text_filename):
            result = []
            with open(text_filename) as reader:
                for line in reader:
                    parts = line.strip().split('|')
                    if len(parts) == 2:
                        result.append((parts[0], float(parts[1])))
            return json.dumps({"data": result, "links": [
                               {"rel": "self", "type": "application/json", "title": "Speech to Text results", "href": "/api/v1/get_speech_to_text?id=" + job_id}
                               ]})
        else:
            # do we have a progress indicator?
            message = get_progress(job_id)
            if len(message) > 0:
                return json.dumps({'message': 'progress:' + message, "links": [
                                    {"rel": "self", "type": "application/json", "title": "Speech to Text results", "href": "/api/v1/get_speech_to_text?id=" + job_id}
                                 ]})
            else:
                return json.dumps({'message': 'id not found, invalid id?'})


if __name__ == '__main__':
    logger = logging.getLogger("ds-logger")
    logger.info("!!! RUNNING in TEST/DEBUG mode, not PRODUCTION !!!")
    app.run(host="0.0.0.0", port=int(config["Service"]["port"]))
