import os
import logging
import tempfile
import subprocess

from util.spell import correction
from util.sound_splitter import split_soundfile_into_many

# globals for this speech to text system - come from config initially passed in
ffmpeg_executable = None
deepspeech_executable = None
deepspeech_graph_file = None


# read the progress file if it exists, otherwise return empty string
def get_progress(job_id: str) -> str:
    filename = os.path.join(tempfile.gettempdir(), job_id + '_progress.txt')
    if os.path.exists(filename):
        return open(filename).read()
    return ''


# the thread that will process the sound file and deliver it back to the parent
# filename will be removed at the end of this processing as it is assumed to be a scratch file
# stt_method = {'kaldi', 'pocketsphinx'}
def processing_thread(deep_speech_config, unique_id: str, filename: str, silence_db = 30):
    logging.info("starting STT(" + unique_id + ")")
    result = deep_speech_tt(deep_speech_config, unique_id, filename, silence_db=silence_db)
    logging.info("finished STT(" + unique_id + "), got " + str(len(result)) + " parts")

    # write the converted items to file for the given id
    out_filename = os.path.join(tempfile.gettempdir(), unique_id + '.txt')
    with open(out_filename, 'w') as writer:
        for item in result:
            writer.write(item[0] + "|" + str(item[1]) + "\n")
    # remove the input file after processing - this is just a temp file
    os.remove(filename)


# run the deep speech to text
# convert the file to 16KHz wav, split it around db silences
def deep_speech_tt(deep_speech_config, unique_id: str, input_sound_file: str, silence_db: int):

    global ffmpeg_executable
    global deepspeech_executable
    global deepspeech_graph_file

    if ffmpeg_executable is None:
        ffmpeg_executable = deep_speech_config["ffmpeg_executable"]
        deepspeech_executable = deep_speech_config["deepspeech_executable"]
        deepspeech_graph_file = deep_speech_config["deepspeech_graph_file"]

    # sanity check required files exist
    required_files = [input_sound_file, ffmpeg_executable, deepspeech_executable, deepspeech_graph_file]
    for file in required_files:
        if not os.path.isfile(ffmpeg_executable):
            raise ValueError("file/executable/data missing:" + file)

    temp_file_name = os.path.join(tempfile._get_default_tempdir(), unique_id + ".wav")

    # convert any soundfile using ffmpeg to the right format
    # ffmpeg -i bill_gates-TED.mp3 -acodec pcm_s16le -ac 1 -ar 16000 output.wav
    logging.debug("converting " + input_sound_file + " to the correct input format for " + unique_id)
    with open(os.devnull, 'w') as f_null:
        subprocess.call([ffmpeg_executable, "-i", input_sound_file, "-acodec", "pcm_s16le",
                         "-ac", "1", "-ar", "16000", temp_file_name], stdout=f_null, stderr=f_null)
    if not os.path.isfile(temp_file_name):
        raise ValueError("file not converted:" + input_sound_file + " for " + unique_id)

    # split the sound file into many for very long files
    logging.debug("splitting sound-file into many for " + unique_id)
    sound_file_list = split_soundfile_into_many(unique_id, temp_file_name, top_db=silence_db)
    logging.debug("split wav into " + str(len(sound_file_list)) + " parts for " + unique_id)

    # use the deepspeech native executable to convert the given wav file to text
    logging.debug("running deepspeech for " + unique_id)
    text_output_list = []
    for sound_file, interval in sound_file_list:
        process = subprocess.Popen([deepspeech_executable, deepspeech_graph_file, sound_file], stdout=subprocess.PIPE)
        out, err = process.communicate()
        if err is not None:
            raise ValueError(err)
        # change bytes back to text
        text = out.decode("utf-8")
        corrected_text = correction(text)
        text_output_list.append((corrected_text, interval))

    # cleanup - remove all temp files
    os.remove(temp_file_name)
    for sound_file, _ in sound_file_list:
        os.remove(sound_file)

    return text_output_list
