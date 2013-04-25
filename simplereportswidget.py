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

import locale
import operator

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

import simplereports_utils as utils

from .ui.ui_simplereportswidgetbase import Ui_DockWidget

class SimpleReportsDockWidget(QDockWidget, Ui_DockWidget):
  def __init__(self, plugin):
    QDockWidget.__init__(self, None)
    self.setupUi(self)

    self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

    self.plugin = plugin
    self.iface = plugin.iface

    self.manageGui()

  def manageGui(self):
    # temporatily hide template selector
    #self.label.hide()
    #self.leTemplate.hide()
    #self.btnSelectTemplate.hide()

    layers = utils.getVectorLayers()
    relations = self.iface.legendInterface().groupLayerRelationship()

    self.lstLayers.blockSignals(True)
    for lay in sorted(layers.iteritems(), cmp=locale.strcoll, key=operator.itemgetter(1)):
      group = utils.getLayerGroup(relations, lay[0])

      item = QTreeWidgetItem(self.lstLayers)
      if group != "":
        item.setText(0, QString("%1 - %2").arg(lay[1]).arg(group))
      else:
        item.setText(0, QString("%1").arg(lay[1]))
      item.setData(0, Qt.UserRole, lay[0])
      item.setCheckState(0, Qt.Unchecked)
    self.lstLayers.blockSignals(False)

  def reject(self):
    QDialog.reject(self)

  def accept(self):
    pass
