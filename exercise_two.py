import numpy as np
import math


## Question 8: Convolution no loops
def convolve(feature_map, kernels):

    if len(feature_map.shape) == 2:
        feature_map = np.reshape(feature_map, (feature_map.shape[0], feature_map.shape[1], 1))
        input_channels = 1
    else:
        input_channels = feature_map.shape[2]
    
    if len(kernels.shape) == 3:
        num_filters, KH, KW = kernels.shape
        kernels = np.reshape(kernels, (num_filters, KH, KW, 1))
    else:
        num_filters, KH, KW, kernel_channels = kernels.shape
        if kernel_channels != input_channels:
            raise ValueError(f"Kernel channels ({kernel_channels}) must match input channels ({input_channels})")


    IW = feature_map.shape[1]
    IH = feature_map.shape[0]


    OW = IW-KW+1
    OH = IH-KH+1

    start_window_row = np.repeat(np.arange(OH), OW)
    start_window_row = np.reshape(start_window_row, (OW*OH, 1))

    offsets_row = np.repeat(np.arange(KH), KW)
    offsets_row = np.reshape(offsets_row, (1, KW*KH))

    comb_row = start_window_row + offsets_row
    comb_row = np.repeat(comb_row, input_channels, axis=1)

    start_window_col = np.tile(np.arange(OW), OH)
    start_window_col = np.reshape(start_window_col, (OW*OH, 1))

    offsets_col = np.tile(np.arange(KW), KH)
    offsets_col = np.reshape(offsets_col, (1, KW*KH))

    comb_col = start_window_col + offsets_col
    comb_col = np.repeat(comb_col, input_channels, axis=1)

    channel_offsets = np.tile(np.arange(input_channels), KH*KW)
    channel_offsets = np.reshape(channel_offsets, (1, KH*KW*input_channels))

    flat_indices = comb_row * feature_map.shape[1]*feature_map.shape[2] + comb_col*feature_map.shape[2] + channel_offsets
    feature_flat = feature_map.reshape(-1)
    all_windows = feature_flat[flat_indices]

    kernels_reshaped = np.reshape(kernels, (num_filters, KH*KW*input_channels))

    outputs = all_windows@kernels_reshaped.T

    result = np.reshape(outputs.T, (num_filters, OH, OW))

    return result




## Question 9: Relu

def reluMap(feature_map):
    return np.maximum(0, feature_map)
    


# Question 10: maxpool no loops

def maxpool(feature_map, kernel_size):

    in_width = feature_map.shape[1]
    in_height = feature_map.shape[0]

    kern_width = kernel[1]
    kern_height = kernel[0]

    out_width = in_width//kern_width
    out_height = in_height//kern_height

    window_starts = np.repeat(np.arange(0, in_height, kern_height), out_width)
    window_starts = np.reshape(window_starts, (out_height*out_width,1))

    offsets = np.repeat(np.arange(kern_height), kern_width)
    offsets = np.reshape(offsets, (1,kern_width*kern_height))


    combined_row = window_starts + offsets


    window_starts_col = np.tile(np.arange(0, in_width, kern_width), out_height)
    window_starts_col = np.reshape(window_starts_col, (out_width*out_height,1))

    offsets_col = np.tile(np.arange(kern_width), kern_height)
    offsets_col = np.reshape(offsets_col, (1,kern_width*kern_height))

    combined_col = window_starts_col + offsets_col


    flat_indices = combined_row * feature_map.shape[1] + combined_col
    feature_flat = feature_map.reshape(-1)
    all_windows = feature_flat[flat_indices]


    max_vals = np.max(all_windows, axis = 1)

    result = max_vals.reshape(out_height, out_width)

    return result




## Question 11: Standardize
def scaler(feature_map, epsilon = 1e-100):
    mean = np.mean(feature_map)
    std = np.std(feature_map)
    
    return (feature_map - mean)/(std+epsilon)
    


## Question 12 (flatten and multiply matrices): 
def connectedLayer(feature_map, weights, biases):
    flattened_input = np.reshape(feature_map, -1)
    return flattened_input@weights + biases



## Question 13 softmax
def softmax(act): 
    act = math.e**act
    sumAct = np.sum(act)

    return act/sumAct

