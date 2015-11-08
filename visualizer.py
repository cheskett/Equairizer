#!/usr/bin/python
import wave
import struct
import sys
import pyaudio
import threading
import numpy as np
from math import sqrt
from Adafruit_PWM_Servo_Driver import PWM

filename = sys.argv[1]
chunk = 500
lock = threading.Lock()
num_bands = 9
pwm = PWM(0x40)
p = pyaudio.PyAudio()

if __name__ == '__main__':

# Open the wave file and get info
    wave_file = wave.open(filename, 'rb')
    data_size = wave_file.getnframes()
    sample_rate = wave_file.getframerate()
    sample_width = wave_file.getsampwidth()
    duration = data_size / float(sample_rate)

    fft_averages = []
    stream = p.open(format =
            p.get_format_from_width(wave_file.getsampwidth()),
            channels = wave_file.getnchannels(),
            rate = wave_file.getframerate(),
            output = True)

    #Calculate FFT informatuon
    fouriers_per_second = 44.1 # Frames per second
    fourier_spread = 1.0/fouriers_per_second
    fourier_width = fourier_spread
    fourier_width_index = fourier_width * float(sample_rate)
    sample_size = fourier_width_index
    if len(sys.argv) < 3:
        length_to_process = int(duration)-1
    else:
        length_to_process = float(sys.argv[2])

    total_transforms = int(round(length_to_process * fouriers_per_second))
    fourier_spacing = round(fourier_spread * float(sample_rate))

    def getBandWidth():
        return (2.0/sample_size) * (sample_rate / 2.0)

    def freqToIndex(f):
        # If f (frequency is lower than the bandwidth of spectrum[0]
        if f < getBandWidth()/2:
            return 0
        if f > (sample_rate / 2) - (getBandWidth() / 2):
            return sample_size -1
        fraction = float(f) / float(sample_rate)
        index = round(sample_size * fraction)
        return index


    def average_fft_bands(fft_array):
        del fft_averages[:]
        for band in range(0, num_bands):
            avg = 0.0
            if band == 0:
                lowFreq = int(0)
            else:
                lowFreq = int(int(sample_rate / 2) / float(2 ** (num_bands - band)))
            hiFreq = int((sample_rate / 2) / float(2 ** ((num_bands-1) - band)))
            lowBound = int(freqToIndex(lowFreq))
            hiBound = int(freqToIndex(hiFreq))
            for j in range(lowBound, hiBound):
                #avg += (fft_array[j])**2 / (hiBound - lowBound + 1)
                avg += (fft_array[j])

            avg /= (hiBound - lowBound + 1)
            #avg = np.sqrt(avg)
            fft_averages.append(avg)
        return fft_averages

    def scale_values(old_val):
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

    def process_sample(sample_range):
        fft_data = abs(np.fft.fft(sample_range))
        fft_data *= ((2**.5)/sample_size)
        fft_averages = average_fft_bands(fft_data)
        output = ""
        pwm.setPWM(0,0,scale_values(fft_averages[4]))
        for num in fft_averages:
            output = output + " " + str(int(num))
        lock.release()
        print output


    def begin():
        print "Sample rate: %s" % sample_rate
        print "Data Size: %s" % data_size
        print "Sample width: %s" % sample_width
        print "Duration: %s" % duration
        print "For Fourier width of "+str(fourier_width)+" need "+str(sample_size)+" samples each FFT"
        print "Doing "+str(fouriers_per_second)+" Fouriers per second"
        print "Total " + str(total_transforms * fourier_spread)
        print "Spacing: "+str(fourier_spacing)
        print "Total transforms "+str(total_transforms)

        data = wave_file.readframes(chunk)
        current_sample = ''

        while data != '':
            stream.write(data)
            current_sample = current_sample + data
            if len(current_sample) == sample_size * 2:
                pack_fmt = '%dh' % (len(current_sample) / 2)
                sound_data = struct.unpack(pack_fmt, current_sample)
                lock.acquire()
                work_thread = threading.Thread(target=process_sample,args=(sound_data,))
                work_thread.start()
                current_sample=''
            data = wave_file.readframes(chunk)

        wave_file.close()

    begin()

