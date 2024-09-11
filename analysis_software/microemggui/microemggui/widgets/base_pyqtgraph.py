#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modification of pyqtgraph classes to provide additional plotting options.

Modifies code from pyqtgraph
https://github.com/pyqtgraph/pyqtgraph/blob/
02482118572e76b4997761dcc5f652c3335247f3/pyqtgraph/graphicsItems/AxisItem.py#L1254-L1281
which is licensed under the MIT License:

LICENSE

Copyright (c) 2012  University of North Carolina at Chapel Hill
Luke Campagnola    ('luke.campagnola@%s.com' % 'gmail')

The MIT License
Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""
from pyqtgraph import AxisItem


class EMGYAxisItem(AxisItem):
    """
    Custom version of pyqtgraph's AxisItem to allow drawing y-axis labels as different
    colours.

    Overrides AxisItem method "drawPicture"
    """

    def __init__(self, pens=None, draw_ticks=True, tick_width: float = 2, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # list of multiple pens, one per tick label
        self.pens = pens
        self.draw_ticks = draw_ticks  # whether to draw ticks
        self.tick_width = tick_width

    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
        p.setRenderHint(p.RenderHint.Antialiasing, False)
        p.setRenderHint(p.RenderHint.TextAntialiasing, True)

        # draw long line along axis
        pen, p1, p2 = axisSpec
        p.setPen(pen)
        p.drawLine(p1, p2)

        # draw ticks
        # First try to use multiple pens if available and enough pens
        if self.draw_ticks:
            if (self.pens is not None) and (len(self.pens) <= len(tickSpecs)):
                for i in range(len(tickSpecs)):
                    pen = self.pens[i]
                    pen.setWidth(self.tick_width)
                    p.setPen(pen)
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
