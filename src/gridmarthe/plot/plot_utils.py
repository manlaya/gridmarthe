#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import copy
import numpy as np
from matplotlib import pyplot as plt, colors, cm


def _set_map_lims(ax, xmin, ymin, xmax, ymax, perc=.05):
    x_range = xmax - xmin
    y_range = ymax - ymin
    # and add 5% margin around bounds (2.5% on each side)
    ax.set_xlim([xmin - (perc * x_range)/2, xmax + (perc * x_range)/2])
    ax.set_ylim([ymin - (perc * y_range)/2, ymax + (perc * y_range)/2])
    return None


def _set_discrete_colormap(cmap=None, norm=None, cols=None, max_colors=20):
    # custom cbar to force categories
    if cols is not None:
        cmap = colors.ListedColormap(cols)
        max_colors = len(cols)
    elif cmap is None:
        cmap = cm.tab10 if max_colors <= 10 else cm.tab20
        cmap = colors.ListedColormap(cmap.colors[:int(max_colors)])  # subset on number of colors, if not wrong legend

    if norm is not None:
        bounds = norm.boundaries
    else:
        bounds = np.arange(1, max_colors+2)
        if len(bounds) == 1:
            bounds = np.append(bounds, [max_colors+1])
        norm = colors.BoundaryNorm(bounds, cmap.N)  # set bins to custom values

    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    return cmap, norm, sm


def _add_discrete_colorbar(fig, ax, cax, sm, bounds, labels=None, title='Layers'):
    ax_cbar = fig.colorbar(
        sm, ax=ax, cax=cax,
        orientation='vertical',
        ticks=[x+0.5 for x in bounds], # set labels in the middle of class
        label=title,
    )
    ax_cbar.ax.tick_params(size=0)

    _labels = copy(labels)
    if _labels is None:
        _labels = ['{:.0f}'.format(x) for x in bounds]
    if len(_labels) != len(bounds):
        _labels = _labels + ['none']
    ax_cbar.set_ticklabels(_labels)
    ax_cbar.ax.invert_yaxis()

    return ax_cbar
