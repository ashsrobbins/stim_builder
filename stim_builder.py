import numpy as np  
import matplotlib.pyplot as plt
import braingeneers
from braingeneers.analysis.analysis import SpikeData, read_phy_files
import braingeneers.data.datasets_electrophysiology as ephys
import scipy.io as sioa
import scipy
from scipy.ndimage import gaussian_filter1d
#!pip install powerlaw
import glob
import pandas as pd

# Now we want to build a square wave, where it is positive first, then negative, lets 
# make a function that does that starting at a specific timepoint in t

def insert_square_wave(sig,time):
    '''Deflects positively at *time* for 20 samples (1ms) then deflects negatively for 20 samples, 
    then returns to normal'''
    sig[time:time+20] = 1
    sig[time+20:time+40] = -1
    return sig

# t = np.arange(0,fs*60)/fs
# sig = np.zeros_like(t)

# sig2 = insert_square_wave(sig,1*fs) #insert it 1s in

# plt.plot(t,sig2)
# plt.xlim([0,2])
# plt.xlabel('seconds')
# plt.ylabel('amplitude')
# plt.show()

# # Well we may need to zoom more, remember this is *tiny*, we are in the milliseconds here

# plt.plot(t,sig2)
# plt.xlim([.99,1.01])# 200ms around the time we inserted
# plt.xlabel('seconds')
# plt.ylabel('amplitude')
# plt.show()


# Ok that looks good. Well, we should modify the function so we can change the duty cycle (length of the phases)
# Also we want to scale this!

def insert_square_wave_advanced(sig,time,phase_length=20, amplitude=1):
    '''Deflects positively at *time* for 20 samples (1ms) then deflects negatively for 20 samples, 
    then returns to normal'''
    sig[time:time+phase_length] = amplitude
    sig[time+phase_length:time+phase_length*2] = -amplitude
    return sig

# Ok looking better


# t = np.arange(0,fs*1)/fs #We do 1 second this time :shrug:
# sig = np.zeros_like(t)

# sig2 = insert_square_wave_advanced(sig,100,phase_length=8, amplitude=2) #insert it 1s in
# sig2 = insert_square_wave_advanced(sig2,200,phase_length=4, amplitude=1)
# sig2 = insert_square_wave_advanced(sig2,400,phase_length=100, amplitude=.8)

# # Well we may need to zoom more, remember this is *tiny*, we are in the milliseconds here

# plt.plot(t,sig2)
# plt.xlim([0,.035])# 200ms around the time we inserted
# plt.xlabel('seconds')
# plt.ylabel('amplitude')
# plt.show()



# How to define a sequence
# --Warning, the length of the sequence should not be longer than the period
# What this means, if you are trying to stimulation 10 times per second (10Hz)
# You cannot create a stimulation pattern that is 1 second long 


# We will be using different code, but the logic is the same



# For 'stim' command:
# ('stim', [neuron inds], amplitude, frames per phase)
# Phase is half a period, 1 frame is 50us

# For 'delay'
# ('delay', frames_delay)
# 1 frames_delay is 50us
# 20 frames_delay is 1ms

# For 'next'
# ('next', None)
# This command acts as a placeholder to move to the next timepoint in the time_arr or the next
# period triggered by the freq_Hz


# Assume we want this pattern
# neuron 0, 150mv, 200us per phase
# 5ms delay
# neuron 1,2, 200mv, 200us per phase
# 20ms delay
# neurons 0-4, 150mv, 200us per phase
# 10ms delay
# Repeat 10 times






def _create_stim_pulse_sequence(stim_list, freq_Hz=10, time_arr = None,max_time_s = 10, repeat=3):
    """
    Creates a stim pulse sequence, parallels the real code that will run on the Maxwell
    
    Params:
    stim_list - list of tuples indicating the commands to run
            ------------------------------------------------
            For 'stim' command:
            ('stim', [neuron inds], mv, us per phase)

            For 'delay'
            ('delay', frames_delay)
            
            For 'next'
            ('next', None)
            This command acts as a placeholder to move to the next timepoint in the time_arr or the next
            period triggered by the freq_Hz
            -------------------------------------------------
    freq_Hz - frequency to call the top stim_list in
            *Note* this takes priority over time_arr
    time_arr - array of time values that will be when the stimulations occur in order
    
    max_time_s - time in seconds to stimulate
    
    
    Returns:
    sig - np.array -- shape=(n_neurons, timesteps) of what the signal will look like
    t - np.array   -- shape=(timesteps) of time in seconds
    """
    
    # Since this is fake, only parallels the code on the device,
    # We have to make our own time
    # And simulate what the stimulation will look like
    
    # Setup
    fs = 20000
    n_neurons = 5
    # if time_arr is None:
    #     t = np.arange(0,fs*max_time_s)/fs
    t = np.arange(0,fs*max_time_s)/fs # time in seconds
    sig = np.zeros(shape=(n_neurons,t.shape[0]))

    if len(stim_list) and stim_list[-1] != ('next', None):
        stim_list.append(('next', None))

    stim_list = stim_list*repeat
    
    # This would be generated in *real time*
    if freq_Hz is not None:
        # Until the time is right to stimulation the sequence
        frame_period = int(fs/freq_Hz)
        for time in t[::frame_period]:
            print('Time', time)
            time_frames = int(time*fs)
            
            
            if len(stim_list) == 0:
                print("Stim list is empty, returning")
                return sig,t
            
            #Build the sequence
            command = None
            
            while (command != 'next' and len(stim_list) > 0):
                print('Trying to pop from stim_list', stim_list)
                command, *params = stim_list.pop(0) # Get first thing off list
                if command == 'stim':
                    neurons, amplitude, phase_length = params
                    
                    # Change signal for each neuron
                    for n in neurons:
                        sig[n,:] = insert_square_wave_advanced(sig[n,:],time_frames,phase_length, amplitude=amplitude)
                    time_frames += phase_length*2
                    
                if command == 'delay':
                    time_frames += params[0]
                    
                #double checking here
                if command == 'next':
                    break 
                    
        
        return sig,t
    return sig, t
                    

# # if __name__ == "__main__":



# stim_list = []
# fs_ms = 20 # Good for converting frames to ms
# fs_us = .2

# # seq = ('stim',[0],150,int(200*fs_us)) # Its weird this is in frames, how can this be more human readable
# # stim_list.append(seq)
# # seq = ('delay',fs_ms*5)
# # stim_list.append(seq)

# # seq = ('stim',[1,2],200,4)
# # stim_list.append(seq)
# # seq = ('delay',fs_ms*20)
# # stim_list.append(seq)

# # seq = ('stim',[0,1,2,3,4],150,4)
# # stim_list.append(seq)
# # seq = ('delay',fs_ms*20)
# # stim_list.append(seq)

# # seq = ('next',None)
# # stim_list.append(seq)

# # stim_list=stim_list*10 # repeat

# seq = ('stim',[0],150,int(200*fs_us)) # Its weird this is in frames, how can this be more human readable
# stim_list.append(seq)
# seq = ('delay',fs_ms*5)
# stim_list.append(seq)

# seq = ('stim',[1],150,int(200*fs_us)) # Its weird this is in frames, how can this be more human readable
# stim_list.append(seq)
# seq = ('delay',fs_ms*5)
# stim_list.append(seq)

# seq = ('stim',[2],150,int(200*fs_us)) # Its weird this is in frames, how can this be more human readable
# stim_list.append(seq)
# seq = ('delay',fs_ms*5)
# stim_list.append(seq)

# seq = ('stim',[3],150,int(200*fs_us)) # Its weird this is in frames, how can this be more human readable
# stim_list.append(seq)
# seq = ('delay',fs_ms*5)
# stim_list.append(seq)

# seq = ('stim',[4],150,int(200*fs_us)) # Its weird this is in frames, how can this be more human readable
# stim_list.append(seq)
# seq = ('delay',fs_ms*5)
# stim_list.append(seq)

# seq = ('next',None)
# stim_list.append(seq)

# stim_list=stim_list*10 # repeat

# # for s in stim_list:
# #     print(s)




#     sig,t = _create_stim_pulse_sequence(stim_list, freq_Hz=10)

#     # Plot the stim signal
#     plt.plot(t,sig.T)
#     plt.legend(['a','b','c','d','e'])
#     plt.xlim(0,.5)
#     plt.show()







# Now here we want to be able to save the stim_list to a file