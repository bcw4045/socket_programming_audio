import numpy as np
import pyaudio
import wave


def record_audio():
    device_count = set_input_device()
    p = pyaudio.PyAudio()
    frames = []
    print(f'Recode Starting')
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, frames_per_buffer=1024,
                    input_device_index=device_count)

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

    device_count = set_output_device()

    stream2 = p.open(format=p.get_format_from_width(width=2), channels=1, rate=16000, output=True,
                     output_device_index=device_count)
    print(len(sound_bytes))
    stream2.write(sound_bytes)
    stream2.stop_stream()
    stream2.close()
    p.terminate()
    print(f'저장된 녹음의 재생이 끝났습니다....')

def set_input_device():
    audio = pyaudio.PyAudio()
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " ‑ ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

    device_count = int(input('입력으로 사용할 디바이스의 번호를 입력해주세요 : '))
    return device_count

def set_output_device():
    audio = pyaudio.PyAudio()
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
            print("Input Device id ", i, " ‑ ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

    device_count = int(input('출력으로 사용할 디바이스의 번호를 입력해주세요 : '))
    return device_count


listening_audio()

