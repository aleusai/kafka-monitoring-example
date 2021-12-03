import time
import random as rd
import numpy as np
import os
from json import dumps
from kafka import KafkaProducer


def sample_number_of_calls(number_of_calls_mean):
    '''
    This function samples a Poisson distribution for the number of call per minute
    param number_of_calls_mean: number_of_calls_mean in a 1 minute
    return: number of calls per minute
    '''
    return np.random.poisson(number_of_calls_mean, 1)[0]


def sample_call_duration(scale_parameter):
    '''
    This function sampls an exponential distribution for a call duration
    param scale_parameter: scale_parameter
    return: sampled value
    '''
    duration_in_seconds = 0
    while duration_in_seconds == 0:
        # we only keep durations > 0
        duration_in_seconds = int(np.random.exponential(
            scale=scale_parameter, size=None)*60)
    return duration_in_seconds


def random_phone_number():
    '''
    This function generates a random phone number
    '''
    number = ''
    for _ in range(7):
        number = number + str(rd.randint(0, 9))
    return ''.join(['0041', number])


def get_epoch_time(call_duration):
    '''
    This function calculates the start of the call from its 
    duration. It is assumed that the call finished and its record was sent by 
    the producer i.e. the start of the call is now - call_duration
    param phone_number: phone number, a string
    return call time (int)
    '''
    return int(time.time()) - call_duration


def get_calls_info():
    '''
    This function returns a batch of generated calls
    return list
    '''
    call_duration_scale_parameter = os.environ.get(
        'CALL_DURATION_SCALE_PARAMETER', 2)
    # number of calls per min
    number_of_calls_mean = os.environ.get('NUMBER_OF_CALLS_MEAN', 10) 
    number_of_calls_per_minute = sample_number_of_calls(number_of_calls_mean)
    messages_list = []

    for _ in range(number_of_calls_per_minute):
        call_duration = sample_call_duration(call_duration_scale_parameter)
        called_phone_number = random_phone_number()
        caller_phone_number = random_phone_number()  # message key
        start_call_epoch_time = get_epoch_time(call_duration)
        message = {'key': caller_phone_number, 'value': {'called_phone_number': called_phone_number,
                                                         'start_call_epoch_time': start_call_epoch_time, 'call_duration': call_duration}}
        messages_list.append(message)

    print(f'************ batch_len {number_of_calls_per_minute}' )
    return messages_list
