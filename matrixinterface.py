import math
import numpy

class MatrixInterface:
	max_value = 500
	@staticmethod
	def NormalizeFFTValue(FFT_value):
		if(FFT_value > MatrixInterface.max_value):
			#New high
			MatrixInterface.max_value = FFT_value
			print "New High: {}".format(MatrixInterface.max_value)
		# Take an FFT value and scale/normalize it for our 0-16 height value
		num = (61/16*math.log10(math.pow(1+int(FFT_value),2)))-6
		if(num < 0):
			num = 0
		elif(num > 16):
			num = 16
		return round(num,0)
		

	@staticmethod
	def CombineChannelAndHeight(channel,height):
		return ((channel << 5) & 224) | height

	def __init__(self):
		pass

