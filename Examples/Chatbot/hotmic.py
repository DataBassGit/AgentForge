import logging
import os
import shutil
import sys
import wave
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pyaudio

DAY = datetime.utcnow().date().isoformat()

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh = logging.FileHandler(f"./logs/save_stream_{DAY}.log")
fh.setFormatter(fmt)
sh = logging.StreamHandler()
sh.setFormatter(fmt)
log.addHandler(sh)
log.addHandler(fh)

CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORDING_TIME_SECONDS = 30
DATA_PATH = f"./data/audio/{DAY}"
Path(DATA_PATH).mkdir(exist_ok=True)

LOCAL_TZ = ZoneInfo("Europe/Berlin")
STREAM_TIME_FROM = time(5, 55, tzinfo=LOCAL_TZ)
STREAM_TIME_TO = time(19, 0, tzinfo=LOCAL_TZ)


def record_stream_to_file(stream: pyaudio.Stream):
    start_utc = datetime.utcnow()
    current_local_time = datetime.now(tz=LOCAL_TZ).time()
    log.info(
        "Current tz time: %s. Stream from: %s Stream until: %s",
        current_local_time,
        STREAM_TIME_FROM,
        STREAM_TIME_TO,
    )
    if not (STREAM_TIME_FROM < current_local_time < STREAM_TIME_TO):
        log.warning("Not during recording time")
        return
    filename = f"{DATA_PATH}/stream_{start_utc.isoformat(timespec='seconds')}.wav"
    log.info("Writing stream to: %s", filename)
    frames = []
    start_time = datetime.utcnow()
    while (datetime.utcnow() - start_time).total_seconds() < RECORDING_TIME_SECONDS:
        data = stream.read(CHUNK_SIZE)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    wf = wave.open(filename, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()


def cleanup_old_files():
    cutoff_time = datetime.utcnow() - timedelta(minutes=30)
    for file in Path(DATA_PATH).glob("*.wav"):
        file_time = datetime.fromtimestamp(os.path.getctime(file))
        if file_time < cutoff_time:
            os.remove(file)
            log.info("Deleted file: %s", file)


def main():
    log.info("Started main")
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
    )
    record_stream_to_file(stream)
    p.terminate()
    cleanup_old_files()
    log.info("OK: finished recording")


if __name__ == "__main__":
    main()
