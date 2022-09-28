import numpy as np
import pyaudio


def record_audio():
    p = pyaudio.PyAudio()
    frames = []
    print(f'Recode Starting')
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

    for i in range(0, int(1024 / 1024 * 30)):  # 시간 초를 정해두고 녹음 받음
        data = stream.read(1024)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    print(f'Recode Finishing')
    return frames


def listening_audio():
    p = pyaudio.PyAudio()
    frames = record_audio()

    sound = np.array(frames)
    sound_bytes = sound.tobytes()
    stream2 = p.open(format=pyaudio.paInt16, channels=1, rate=1024, output=True)
    print(sound_bytes)
    print(len(sound_bytes))
    stream2.write(sound_bytes)
    stream2.stop_stream()
    stream2.close()
    p.terminate()
    print(f'저장된 녹음의 재생이 끝났습니다....')





listening_audio()

