#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGChannels, for representing EMG channels.

"""

import numpy as np
from typing import Optional


class EMGChannels:
    """
    Class for representing EMG recording channels.

    attributes to add:
    low quality channels (automatic detection)
    low quality channels (visual inspection)

    """

    def __init__(self, intan_chan_names: Optional[list[str]] = None, n_chan: int = 0):
        """
        Initialise EMGChannels object for modelling EMG channels.

        Parameters
        ----------
        intan_chan_names : list[str]
            List of original channel names (labelled by Intan hardware).
        n_chan : int
            Number of channels if channel names are not given

        Returns
        -------
        None.

        """

        if intan_chan_names is None and n_chan == 0:
            raise Exception(
                "To create an EMG channel (needle) model either a list of Intan "
                + "channel names should be given or the number of channels."
            )

        if intan_chan_names is not None:
            # original channel names
            self.intan_chan_names = intan_chan_names
            n_chan = len(intan_chan_names)

        # Create new channel labels using the channel order
        # (i.e., label channels from 1 to n channels)
        self.chan_names = [str(i) for i in np.arange(1, n_chan + 1)]

        # x, y coordinates
        self._get_chan_xy(n_chan)

        # default channels to use for the analysis (all channels)
        self.analyse_chan = np.full(n_chan, True)

    def _get_chan_xy(self, n_chan: int):
        """
        Get the channel (x, y) coordinates based on the number of channels,
        which determines the electrode's design on the needle.

        Parameters
        ----------
        n_chan : int
            Number of channels

        Returns
        -------
        None.

        """

        # Channel layout (in mm)
        CHAN_SPACING_X = 0.3  # spacing along length (defined as x axis)
        CHAN_SPACING_Y = 0.36  # spacing along width (defined as y axis)
        CHAN_SHIFT_X = 0.3  # value used to shift x axis positions

        # First column will be x coordinates (position along length)
        # Second column will be y coordinates (position along width)
        self.chan_xy = np.zeros((n_chan, 2))

        # Set x - evenly spaced, and shifted by CHAN_SHIFT_X
        self.chan_xy[:, 0] = (
            np.arange(CHAN_SPACING_X, CHAN_SPACING_X * (n_chan + 1), CHAN_SPACING_X) + CHAN_SHIFT_X
        )

        # Set y - alternating positive and negative to form zig-zag
        self.chan_xy[:, 1] = CHAN_SPACING_Y / 2
        self.chan_xy[np.arange(1, n_chan + 1, 2), 1] *= -1
