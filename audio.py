import os
import glob
import time
import speech_recognition as sr # pip install speechrecognition
import pydub
import numpy as np
import wave
import math
import contextlib

cutOffFrequency = 400.0

def convert_mp3_to_wav():
    mp3_files = glob.glob('./RADIO/*.mp3')
    for mp3_file in mp3_files:
       wav_file = os.path.splitext(mp3_file)[0] + '.wav'
       sound = pydub.AudioSegment.from_mp3(mp3_file)
       sound.export(wav_file, format="wav")
       os.remove(mp3_file)

def running_mean(x, windowSize):
  cumsum = np.cumsum(np.insert(x, 0, 0))
  return (cumsum[windowSize:] - cumsum[:-windowSize]) / windowSize

def interpret_wav(raw_bytes, n_frames, n_channels, sample_width, interleaved = True):

    if sample_width == 1:
        dtype = np.uint8
    elif sample_width == 2:
        dtype = np.int16
    else:
        raise ValueError("Only supports 8 and 16 bit audio formats.")

    channels = np.fromstring(raw_bytes, dtype=dtype)

    if interleaved:
        channels.shape = (n_frames, n_channels)
        channels = channels.T
    else:
        channels.shape = (n_channels, n_frames)

    return channels

def reduce_noise(audios):
    for i in range(len(audios)):
        with contextlib.closing(wave.open('./RADIO/'+audios[i], 'rb')) as spf:
            sampleRate = spf.getframerate()
            ampWidth = spf.getsampwidth()
            nChannels = spf.getnchannels()
            nFrames = spf.getnframes()

            signal = spf.readframes(nFrames * nChannels)
            spf.close()
            channels = interpret_wav(signal, nFrames, nChannels, ampWidth, True)

            freqRatio = (cutOffFrequency / sampleRate)
            N = int(math.sqrt(0.196196 + freqRatio ** 2) / freqRatio)

            filtered = running_mean(channels[0], N).astype(channels.dtype)

            wav_file = wave.open('./fRADIO/'+audios[i], "w")
            wav_file.setparams((1, ampWidth, sampleRate, nFrames, spf.getcomptype(), spf.getcompname()))
            wav_file.writeframes(filtered.tobytes('C'))
            wav_file.close()

def audio_to_text():
    dir_radio = './fRADIO'
    contenido = os.listdir(dir_radio)
    audios = []
    for fichero in contenido:
        audios.append(fichero)

    r = sr.Recognizer()
    for i in range(len(audios)):
        with sr.AudioFile('./fRADIO/' + audios[i]) as recurso:
            audio = r.listen(recurso)
            try:
                print('Leyendo fichero de audio...')
                texto = r.recognize_google(audio, language='es-ES')
                time.sleep(1.5)
                print(texto)

                with open('audios.csv', 'a') as archivo:
                    archivo.write(audios[i])
                    archivo.write(';')
                    archivo.write(texto)
                    archivo.write('\n')

            except Exception as e:
                print('Ocurrio un error!')

if __name__ == '__main__':
    resp = 0
    dir_radio = 'RADIO'
    contenido = os.listdir(dir_radio)
    audios = []
    for fichero in contenido:
        audios.append(fichero)

    while resp != 4:
        print('--------------MENU--------------'
              '\n1. Convertir Audios de .mp3 a .wav'
              '\n2. Reducir ruido en audios'
              '\n3. Audio a texto '
              '\n4. Salir')
        resp = int(input('Ingrese la opción: '))
        if resp == 1:
            convert_mp3_to_wav()
        elif resp == 2:
            reduce_noise(audios)
        elif resp == 3:
            audio_to_text()
        elif resp == 4:
            exit()



