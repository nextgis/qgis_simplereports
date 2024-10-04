# -*- coding: utf-8 -*-

# ******************************************************************************
#
# SimpleReports
# ---------------------------------------------------------
# Simple report generator
#
# Copyright (C) 2013 NextGIS (info@nextgis.org)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/licenses/>. You can also obtain it by writing
# to the Free Software Foundation, 51 Franklin Street, Suite 500 Boston,
# MA 02110-1335 USA.
#
# ******************************************************************************

from builtins import str
from qgis.core import QgsProject, QgsMapLayer, QgsLayerTree


def getVectorLayers():
    layerMap = QgsProject.instance().mapLayers()
    layers = dict()
    for name, layer in layerMap.items():
        if layer.type() == QgsMapLayer.VectorLayer:
            if layer.id() not in list(layers.keys()):
                layers[layer.id()] = str(layer.name())
    return layers


def getVectorLayerById(layerId):
    layerMap = QgsProject.instance().mapLayers()
    for name, layer in layerMap.items():
        if layer.type() == QgsMapLayer.VectorLayer and layer.id() == layerId:
            if layer.isValid():
                return layer
            else:
                return None


def getLayerGroup(relations, lay) -> list:
    layerId = lay[0]
    node = relations.findLayer(layerId)
    group = []
    if node == None:
        return group
    else:
        group.append(node.name())
        findNodes(group, node)
        return group


def findNodes(group, node):
    parent = node.parent()
    if type(parent) == QgsLayerTree:
        return
    else:
        group.append(parent.name())
        findNodes(group, parent)
