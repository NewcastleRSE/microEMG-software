#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGChannels, for representing EMG channels.

"""

import numpy as np


class EMGChannels:
    """
    Class for representing EMG recording channels.

    attributes to add:
    low quality channels (automatic detection)
    low quality channels (visual inspection)

    """

    def __init__(self, intan_chan_names: list[str]):
        """
        Initialise EMGChannels object for modelling EMG channels.

        Parameters
        ----------
        intan_chan_names : list[str]
            List of original channel names (labelled by Intan hardware).

        Returns
        -------
        None.

        """
        # original channel names
        self.intan_chan_names = intan_chan_names

        # Create new channel labels using the channel order
        # (i.e., label channels from 1 to n channels)
        self.chan_names = [
            "channel " + str(i) for i in np.arange(1, len(intan_chan_names) + 1)
        ]

        # x, y coordinates
        self._get_chan_xy()

    def _get_chan_xy(self):
        """
        Get the channel (x, y) coordinates based on the number of channels,
        which determines the electrode's design.

        Returns
        -------
        None.

        """

        # Channel layout (in mm)
        CHAN_SPACING_X = 0.3  # spacing along length (defined as x axis)
        CHAN_SPACING_Y = 0.36  # spacing along width (defined as y axis)
        CHAN_SHIFT_X = 0.3  # value used to shift x axis positions

        n_chan = len(self.chan_names)

        # First column will be x coordinates (position along length)
        # Second column will be y coordinates (position along width)
        self.chan_xy = np.zeros((n_chan, 2))

        # Set x - evenly spaced, and shifted by CHAN_SHIFT_X
        self.chan_xy[:, 0] = (
            np.arange(CHAN_SPACING_X, CHAN_SPACING_X * (n_chan + 1), CHAN_SPACING_X)
            + CHAN_SHIFT_X
        )

        # Set y - alternating positive and negative to form zig-zag
        self.chan_xy[:, 1] = CHAN_SPACING_Y / 2
        self.chan_xy[np.arange(1, n_chan + 1, 2), 1] *= -1
