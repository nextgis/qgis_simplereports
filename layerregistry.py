# -*- coding: utf-8 -*-

#******************************************************************************
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
#******************************************************************************

from PyQt4.QtCore import *

from qgis.core import *

class LayerRegistry(QObject):

  layersChanged = pyqtSignal()

  _instance = None
  _iface = None
  layers = dict()

  @staticmethod
  def instance():
    if LayerRegistry._instance == None:
      LayerRegistry._instance = LayerRegistry()
    return LayerRegistry._instance

  @staticmethod
  def setIface(iface):
    LayerRegistry._iface = iface

  def __init__(self):
    QObject.__init__(self)
    if LayerRegistry._instance != None:
      return

    LayerRegistry.layers = self.getAllLayers()
    LayerRegistry._instance = self
    QgsMapLayerRegistry.instance().removeAll.connect.(self.removeAllLayers)
    QgsMapLayerRegistry.instance().layerWasAdded.connect(self.layerAdded)
    QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.removeLayer)

  def getAllLayers(self):
     return QgsMapLayerRegistry.instance().mapLayers().values()

  def layerAdded(self, layer):
     LayerRegistry.layers.append(layer)
     self.layersChanged.emit()

  def removeLayer(self, layerId):
     LayerRegistry.layers = filter( lambda x: x.id() != layerId, LayerRegistry.layers)
     self.layersChanged.emit()

  def removeAllLayers(self):
     LayerRegistry.layers = dict()
     self.layersChanged.emit()
