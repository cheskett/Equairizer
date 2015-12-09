#!/usr/bin/python
import wave
import struct
import sys
from os import path
import pyaudio
import threading
import numpy as np
from math import sqrt
from matrixinterface import MatrixInterface
import serial
# from Adafruit_PWM_Servo_Driver import PWM

PRE_NORM = False

chunk = 500
lock = threading.Lock()
p = pyaudio.PyAudio()
class AudioParser:
    def __init__(self, filename=None, num_bands=None):
        if filename is None:
            return
        self.ser = serial.Serial('/dev/ttyACM0', 9600)
        self.filename = filename
        self.wave_file = wave.open(filename, 'rb')
        self.data_size = self.wave_file.getnframes()
        self.sample_rate = self.wave_file.getframerate()
        self.sample_width = self.wave_file.getsampwidth()
        self.duration = self.data_size / float(self.sample_rate)
        self.stop_event = threading.Event()
        self.fouriers_per_second = 44.1 / 2  # Frames per second
        self.fourier_spread = 1.0 / self.fouriers_per_second
        self.fourier_width = self.fourier_spread
        self.fourier_width_index = self.fourier_width * float(self.sample_rate)
        self.sample_size = self.fourier_width_index

        self.in_file = open(path.join(path.dirname(path.dirname(path.abspath(filename))), "songdata",
                                      path.basename(filename).split('.')[0] + '.txt'), 'r')

        if num_bands is None:
            self.num_bands = 9
        else:
            self.num_bands = num_bands
        self.stream = p.open(format=
                             p.get_format_from_width(self.wave_file.getsampwidth()),
                             channels=self.wave_file.getnchannels(),
                             rate=self.wave_file.getframerate(),
                             output=True)

    def play_audio(self):
        data = self.wave_file.readframes(chunk)
        current_sample = ''

        while data != '':
            if self.stop_event.isSet():
                self.stream.write(data)
                current_sample = current_sample + data
                if len(current_sample) == self.sample_size * 2:
                    current_sample = current_sample + data
                    input_data = []
                    read_data = self.in_file.readline().strip('\n')
                    input_data = read_data.split()
                    output = ""
                    for ind, num in enumerate(input_data):
                        norm_val = num
                        if(not PRE_NORM):
                            norm_val = int(MatrixInterface.NormalizeFFTValue(int(num)))
                        channel = ind
                        data = MatrixInterface.CombineChannelAndHeight(ind,int(norm_val))
                        self.ser.write(chr(int(data)))
                        output+= "{}: {} | ".format(channel, int(norm_val))
                    print output

                    current_sample = ''
                data = self.wave_file.readframes(chunk)
            else:
                self.stop_event.wait()

        self.wave_file.close()

    def begin(self):
        self.stop_event.set()
        play_thread = threading.Thread(target=self.play_audio, args=())
        # play_thread.daemon = True
        play_thread.start()

    def pause(self):
        self.stop_event.clear()

    def resume(self):
        self.stop_event.set()


class AudioProcessor:
    def __init__(self, filename=None, num_bands=None):
        if filename is None:
            return
        self.filename = filename
        self.wave_file = wave.open(filename, 'rb')
        self.data_size = self.wave_file.getnframes()
        self.sample_rate = self.wave_file.getframerate()
        self.sample_width = self.wave_file.getsampwidth()
        self.duration = self.data_size / float(self.sample_rate)
        self.stop_event = threading.Event()

        self.out_file = open(path.join(path.dirname(path.dirname(path.abspath(filename))), "songdata",
                                       path.basename(filename).split('.')[0] + '.txt'), 'w')

        if num_bands is None:
            self.num_bands = 9
        else:
            self.num_bands = num_bands
        self.fft_averages = []
        self.stream = p.open(format=
                             p.get_format_from_width(self.wave_file.getsampwidth()),
                             channels=self.wave_file.getnchannels(),
                             rate=self.wave_file.getframerate(),
                             output=True)

        # Calculate FFT informatuon
        self.fouriers_per_second = 44.1 / 2  # Frames per second
        self.fourier_spread = 1.0 / self.fouriers_per_second
        self.fourier_width = self.fourier_spread
        self.fourier_width_index = self.fourier_width * float(self.sample_rate)
        self.sample_size = self.fourier_width_index

        if len(sys.argv) < 3:
            self.length_to_process = int(self.duration) - 1
        else:
            self.length_to_process = float(sys.argv[2])

        self.total_transforms = int(round(self.length_to_process * self.fouriers_per_second))
        self.fourier_spacing = round(self.fourier_spread * float(self.sample_rate))

    def getBandWidth(self):
        return (2.0 / self.sample_size) * (self.sample_rate / 2.0)

    def freqToIndex(self, f):
        # If f (frequency is lower than the bandwidth of spectrum[0]
        if f < self.getBandWidth() / 2:
            return 0
        if f > (self.sample_rate / 2) - (self.getBandWidth() / 2):
            return self.sample_size - 1
        fraction = float(f) / float(self.sample_rate)
        index = round(self.sample_size * fraction)
        return index

    def average_fft_bands(self, fft_array):
        del self.fft_averages[:]
        for band in range(0, self.num_bands):
            avg = 0.0
            if band == 0:
                lowFreq = int(0)
            else:
                lowFreq = int(int(self.sample_rate / 2) / float(2 ** (self.num_bands - band)))
            hiFreq = int((self.sample_rate / 2) / float(2 ** ((self.num_bands - 1) - band)))
            lowBound = int(self.freqToIndex(lowFreq))
            hiBound = int(self.freqToIndex(hiFreq))
            for j in range(lowBound, hiBound):
                # avg += (fft_array[j])**2 / (hiBound - lowBound + 1)
                avg += (fft_array[j])

            avg /= (hiBound - lowBound + 1)
            # avg = np.sqrt(avg)
            self.fft_averages.append(avg)
        return self.fft_averages

    def _process_sample(self, sample_range):
        fft_data = abs(np.fft.fft(sample_range))
        fft_data *= ((2 ** .5) / self.sample_size)
        self.fft_averages = self.average_fft_bands(fft_data)
        output = ""
        for num in self.fft_averages:
            val = num
            if(PRE_NORM):
                val = MatrixInterface.NormalizeFFTValue(int(num))
            output = output + " " + str(int(val))
        self.out_file.write(output + '\n')
        print output

    def process_file(self):

        data = self.wave_file.readframes(chunk)

        current_sample = ''

        while data != '':
            current_sample = current_sample + data
            if len(current_sample) == self.sample_size * 2:
                pack_fmt = '%dh' % (len(current_sample) / 2)
                sound_data = struct.unpack(pack_fmt, current_sample)
                self._process_sample(sound_data)
                current_sample = ''
            data = self.wave_file.readframes(chunk)
        self.wave_file.close()
        self.out_file.close()

# filename = sys.argv[1]
# player = AudioParser(filename)
# player.begin()
