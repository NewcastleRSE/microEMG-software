#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A Class, EMGPreprocSettings, for configuring and storing EMG preprocessing
settings (applied to EMGData)

"""


class EMGPreprocSettings:
    '''
    Class for storing EMG preprocessing settings.
    
    Attributes to add:
    mains noise removal, automatic bad channel detection
    Consider keeping the channels removed/labelled as "bad" a channel attribute
    (limit this class to settings that can directly be applied to any EMG 
     recording)
        
    '''
    
    def __init__(self, filtered: bool=False, 
                 filter_settings: None|dict = None):
        # Initialise preprocessing settings
        # Default is no preprocessing settings applied
        # TODO: documentation (once other preprocessing settings are added to initialisation)
        
        # Filter settings
        self.filtered = filtered
        if filter_settings is None:
            self.filter_settings = {}
        else:
            self.filter_settings = filter_settings