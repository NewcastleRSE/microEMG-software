#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 16:16:00 2024

@author: Gabrielle
"""
from pyqtgraph import AxisItem


class EMGAxisItem(AxisItem):
    """
    Custom version of pyqtgraph's AxisItem to allow drawing y-axis labels as different
    colours.

    Overrides AxisItem method "drawPicture"
    """

    def __init__(self, pens=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # list of multiple pens, one per tick label
        self.pens = pens

    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
        p.setRenderHint(p.RenderHint.Antialiasing, False)
        p.setRenderHint(p.RenderHint.TextAntialiasing, True)

        # draw long line along axis
        pen, p1, p2 = axisSpec
        p.setPen(pen)
        p.drawLine(p1, p2)
        # p.translate(0.5,0)  ## resolves some damn pixel ambiguity

        # draw ticks
        # First try to use multiple pens if available and enough pens
        if (self.pens is not None) and (len(self.pens) <= len(tickSpecs)):
            for i in range(len(tickSpecs)):
                p.setPen(self.pens[i])
                p.drawLine(tickSpecs[i][1], tickSpecs[i][2])
        else:
            for pen, p1, p2 in tickSpecs:
                p.setPen(pen)
                p.drawLine(p1, p2)

        # Draw all text
        if self.style["tickFont"] is not None:
            p.setFont(self.style["tickFont"])
        p.setPen(self.textPen())
        bounding = self.boundingRect().toAlignedRect()
        p.setClipRect(bounding)

        # First try drawing using multiple pens if available and enough pens
        if (self.pens is not None) and (len(self.pens) <= len(textSpecs)):
            for i in range(len(textSpecs)):
                p.setPen(self.pens[i])
                p.drawText(textSpecs[i][0], int(textSpecs[i][1]), textSpecs[i][2])
        else:
            for rect, flags, text in textSpecs:
                p.drawText(rect, int(flags), text)
