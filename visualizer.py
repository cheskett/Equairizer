#!/usr/bin/python
import wave
import struct
import sys
import pyaudio
import threading
import numpy as np
from math import sqrt
#from Adafruit_PWM_Servo_Driver import PWM

filename = sys.argv[1]
chunk = 500
lock = threading.Lock()
num_bands = 9
#pwm = PWM(0x40)
p = pyaudio.PyAudio()


class AudioParser:
    
    def __init__(self, filename, num_bands=None):
        self.filename = filename
        self.wave_file = wave.open(filename, 'rb')
        self.data_size = self.wave_file.getnframes()
        self.sample_rate = self.wave_file.getframerate()
        self.sample_width = self.wave_file.getsampwidth()
        self.duration = self.data_size / float(self.sample_rate)
        
        if num_bands is None:
            self.num_bands = 9
        else:
            self.num_bands = num_bands
        self.fft_averages = []
        self.stream = p.open(format =
                p.get_format_from_width(self.wave_file.getsampwidth()),
                channels = self.wave_file.getnchannels(),
                rate = self.wave_file.getframerate(),
                output = True)

        #Calculate FFT informatuon
        self.fouriers_per_second = 44.1 # Frames per second
        self.fourier_spread = 1.0/self.fouriers_per_second
        self.fourier_width = self.fourier_spread
        self.fourier_width_index = self.fourier_width * float(self.sample_rate)
        self.sample_size = self.fourier_width_index
    
        if len(sys.argv) < 3:
            self.length_to_process = int(self.duration)-1
        else:
            self.length_to_process = float(sys.argv[2])

        self.total_transforms = int(round(self.length_to_process * self.fouriers_per_second))
        self.fourier_spacing = round(self.fourier_spread * float(self.sample_rate))
        
        
    def getBandWidth(self):
        return (2.0/self.sample_size) * (self.sample_rate / 2.0)

    def freqToIndex(self, f):
        # If f (frequency is lower than the bandwidth of spectrum[0]
        if f < self.getBandWidth()/2:
            return 0
        if f > (self.sample_rate / 2) - (self.getBandWidth() / 2):
            return self.sample_size -1
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
            hiFreq = int((self.sample_rate / 2) / float(2 ** ((self.num_bands-1) - band)))
            lowBound = int(self.freqToIndex(lowFreq))
            hiBound = int(self.freqToIndex(hiFreq))
            for j in range(lowBound, hiBound):
                #avg += (fft_array[j])**2 / (hiBound - lowBound + 1)
                avg += (fft_array[j])

            avg /= (hiBound - lowBound + 1)
            #avg = np.sqrt(avg)
            self.fft_averages.append(avg)
        return self.fft_averages

    def scale_values(self, old_val):
        if old_val > 2000:
            old_val = 2000
        old_val = int(old_val)
        old_max = 2000
        old_min = 0
        new_max = 4095
        new_min = 0
        new_val = (float((old_val - old_min)) / float((old_max - old_min))) * (new_max- new_min) + new_min
        print new_val
        return int(new_val)

    def process_sample(self, sample_range):
        fft_data = abs(np.fft.fft(sample_range))
        fft_data *= ((2**.5)/self.sample_size)
        self.fft_averages = self.average_fft_bands(fft_data)
        output = ""
        #pwm.setPWM(0,0,scale_values(fft_averages[4]))
        for num in self.fft_averages:
            output = output + " " + str(int(num))
        lock.release()
        print output


    def begin(self):
        print "Sample rate: %s" % self.sample_rate
        print "Data Size: %s" % self.data_size
        print "Sample width: %s" % self.sample_width
        print "Duration: %s" % self.duration
        print "For Fourier width of "+str(self.fourier_width)+" need "+str(self.sample_size)+" samples each FFT"
        print "Doing "+str(self.fouriers_per_second)+" Fouriers per second"
        print "Total " + str(self.total_transforms * self.fourier_spread)
        print "Spacing: "+str(self.fourier_spacing)
        print "Total transforms "+str(self.total_transforms)

        data = self.wave_file.readframes(chunk)
        current_sample = ''

        while data != '':
            self.stream.write(data)
            current_sample = current_sample + data
            if len(current_sample) == self.sample_size * 2:
                pack_fmt = '%dh' % (len(current_sample) / 2)
                sound_data = struct.unpack(pack_fmt, current_sample)
                lock.acquire()
                work_thread = threading.Thread(target=self.process_sample,args=(sound_data,))
                work_thread.start()
                current_sample=''
            data = self.wave_file.readframes(chunk)

        self.wave_file.close()

player = AudioParser(filename)
player.begin()

