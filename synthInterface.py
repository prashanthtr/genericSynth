# Generic sound class to store sound synthesizer files
import numpy as np
import math

class MyParam():
	def __init__(self,name,min,max, val, cb) :
		self.name=name
		self.min=min
		self.max=max
		self.val=val
		self.cb=cb

	# only store the actual value, not the normed value used for setting
	def __setParamNorm__(self, i_val) :
		self.val=self.min + i_val * (self.max - self.min);

##################################################################################################
#  the base sound model from which all synths should derive
##################################################################################################
'''
	A model has parameters, methods to get/set them, and a generate function that returns a signal.
	This is *the* interface for all synths.
'''
class MySoundModel() :

	def __init__(self,sr=16000) :
		self.param = {} # a dictionary of MyParams
		self.sr = sr # makes a single event

	def __addParam__(self, name,min,max,val, cb=None) :
		self.param[name]=MyParam(name,min,max,val, cb)


	def setParam(self, name, value) :
		self.param[name].val=value
		if self.param[name].cb is not None :
			self.param[name].cb(value)

	''' set parameters using [0,1] which gets mapped to [min, max] '''
	def setParamNorm(self, name, nvalue) :
		self.param[name].__setParamNorm__(nvalue)
		if self.param[name].cb is not None :
			self.param[name].cb(self.getParam(name))

	def getParam(self, name, prop="val") :
		if prop == "val" :
			return self.param[name].val
		if prop == "min" :
			return self.param[name].min
		if prop == "max" :
			return self.param[name].max
		if prop == "name" :
			return self.param[name].name


	''' returns list of paramter names that can be set by the user '''
	def getParams(self) :
		plist=[]
		for p in self.param :
			plist.append(self.param[p].name)
		return plist

	'''
		override this for your signal generation
	'''
	def generate(self, sigLenSecs=1) :
		return np.zeros(sigLenSecs*self.sr)

##################################################################################################
# A couple of handy-dandy UTILITY FUNCTIONS for event pattern synthesizers in particular
##################################################################################################
'''
creates a list of event times that happen with a rate of 2^r_exp
	  and deviate from the strict equal space according to irreg_exp
'''
def noisySpacingTimeList(rate_exp, irreg_exp, durationSecs) :
	# mapping to the right range units
    eps=np.power(2,rate_exp)
    irregularity=.1*irreg_exp*np.power(10,irreg_exp)
    #irregularity=.04*np.power(10,irreg_exp)
    sd=irregularity/eps

    #print("eps = {}, irreg = {}, and sd = {}".format(eps, irregularity, sd))

    linspacesteps=int(eps*durationSecs)
    linspacedur = linspacesteps/eps

    eventtimes=[(x+np.random.normal(scale=sd))%durationSecs for x in np.linspace(0, linspacedur, linspacesteps, endpoint=False)]

    return np.sort(eventtimes) #sort because we "wrap around" any events that go off the edge of [0. durationSecs]



''' convert a list of floats (time in siconds) to a signal with pulses at those time '''
def timeList2Sig(elist, sr, durationSecs) :
	numsamps=sr*durationSecs
	sig=np.zeros(numsamps)
	for nf in elist :
		sampnum=int(round(nf*sr))
		if sampnum<numsamps and sampnum >= 0 :
			sig[sampnum]=1
		else :
			print("in timeList2Sig, warning: sampnum(={}) out of range".format(sampnum))
	return sig



'''adds one (shorter) array (a) in to another (b) starting at startsamp in b'''
def addin(a,b,startsamp) :
    b[startsamp:startsamp+len(a)]=[sum(x) for x in zip(b[startsamp:startsamp+len(a)], a)]
    return b

''' Returns a chunked wav files from generated signal '''
def selectVariation(sig, sr, varNum, varDurationSecs):
        variationSamples=math.floor(sr*varDurationSecs)
        return sig[varNum*variationSamples:(varNum+1)*variationSamples]


'''Gestures are transformation function specifying changes about an aspect of a
sound over time. Used for creating amplitude envelopes or frequency sweeps.'''
def gesture(startVal, stopVal, cutOff, numSamples):
        gesture = np.zeros(numSamples)
        non_zero = np.linspace(startVal, stopVal, int(cutOff*numSamples))
        for index in range(len(non_zero)):
                gesture[index] = non_zero[index]
        return gesture
