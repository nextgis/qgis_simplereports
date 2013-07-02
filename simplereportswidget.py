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
from PyQt4.QtXml import *

from qgis.core import *

import areamaptool
import odftools
import simplereports_utils as utils

from .ui.ui_simplereportswidgetbase import Ui_DockWidget

import resources_rc

class SimpleReportsDockWidget(QDockWidget, Ui_DockWidget):
  def __init__(self, plugin):
    QDockWidget.__init__(self, None)
    self.setupUi(self)

    self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

    self.plugin = plugin
    self.iface = plugin.iface
    self.canvas = self.iface.mapCanvas()

    self.mapTool = None
    self.prevMapTool = None
    self.extent = None
    self.layers = None

    self.btnMapTool.setIcon(QIcon(":/icons/selectaoi.png"))

    self.layerRegistry = QgsMapLayerRegistry.instance()
    self.layerRegistry.layerWasAdded.connect(self.__addLayer)
    self.layerRegistry.layerWillBeRemoved.connect(self.__removeLayer)
    self.canvas.extentsChanged.connect(self.__updateExtents)

    self.btnMapTool.clicked.connect(self.triggerMapTool)
    self.btnGenerate.clicked.connect(self.createReport)
    self.rbExtentCanvas.toggled.connect(self.selectAOI)
    self.rbExtentUser.toggled.connect(self.selectAOI)

    self.manageGui()

  def manageGui(self):
    self.__updateLayers()

    self.btnMapTool.setEnabled(False)

    self.mapTool = areamaptool.AreaMapTool(self.canvas)
    self.prevMapTool = self.canvas.mapTool()

    self.mapTool.rectangleCreated.connect(self.__getRectangle)

    self.leScale.setValidator(QDoubleValidator(self.leScale))

  def triggerMapTool(self):
    if self.btnMapTool.isChecked():
      self.canvas.setMapTool(self.mapTool)
    else:
      self.resetMapTool()

  def selectAOI(self):
    if self.rbExtentUser.isChecked():
      self.btnMapTool.setEnabled(True)
    else:
      self.btnMapTool.setEnabled(False)
      self.btnMapTool.setChecked(False)
      self.resetMapTool(True)
      self.extent = self.canvas.extent()

  def createReport(self):
    if self.extent is None:
      QMessageBox.warning(self,
                          self.tr("Empty AOI"),
                          self.tr("Area of interest is not set. Please specify it and try again.")
                         )
      return

    settings = QSettings("NextGIS", "SimpleReports")
    lastDirectory = settings.value("lastReportDir",  ".")

    fName = QFileDialog.getSaveFileName(self,
                                        self.tr("Save file"),
                                        lastDirectory,
                                        self.tr("OpenDocument Text (*.odt *.ODT)")
                                       )
    if fName == "":
      return

    if not fName.lower().endswith(".odt"):
      fName += ".odt"

    templateFile = QFile(":/resources/schema-template.odt")
    if templateFile.open(QIODevice.ReadOnly):
      outFile = QFile(fName)
      if outFile.open(QIODevice.WriteOnly):
        outFile.write(templateFile.readAll())
      outFile.close()
    templateFile.close()

    # get selected layers
    layerNames = dict()
    for i in xrange(self.lstLayers.topLevelItemCount()):
      item = self.lstLayers.topLevelItem(i)
      if item.checkState(0) == Qt.Checked:
        layerNames[item.text(0)] = item.data(0, Qt.UserRole)

    self.progressBar.setRange(0, len(layerNames) + 1)

    # generate map image
    if not self.renderSchema(layerNames):
      QMessageBox.warning(self,
                          self.tr("Image not found"),
                          self.tr("Cannot load schema map from temporary file")
                         )
      return

    self.progressBar.setValue(self.progressBar.value() + 1)
    QCoreApplication.processEvents()

    # open template
    writer = odftools.ODFWriter()
    writer.setFileName(unicode(fName))
    writer.openFile()

    parser = odftools.ODFParser()
    parser.setContent(writer.readDocument())
    parser.setManifest(writer.readManifest())

    # add image
    writer.addPicture(QDir.tempPath() + "/schema-test.png", "schema.png")
    parser.addPictureToManifest("schema.png")
    parser.addPictureToDocument("@schema@", "schema.png", 35.297, 24.993)

    # find placeholder
    te = parser.getTextElement()
    tp = parser.findPlaceholder("@tables@")

    # create attribute table for each layer
    f = QgsFeature()
    for k, v in layerNames.iteritems():
      layer = utils.getVectorLayerById(v)
      myAttrs = dict()
      attrNames = []
      for i in xrange(len(layer.pendingAllAttributesList())):
        if layer.editType(i) != QgsVectorLayer.Hidden:
          myAttrs[i] = layer.attributeDisplayName(i)
          attrNames.append(layer.pendingFields()[i].name())

      tableTitle = parser.addParagraph(k)
      table = parser.addTable(k, len(myAttrs))

      # table header
      parser.addTableRow(table, myAttrs.values())

      # table data
      request = QgsFeatureRequest()
      request.setFilterRect(self.canvas.mapRenderer().mapToLayerCoordinates(layer, self.extent))
      request.setFlags(QgsFeatureRequest.NoGeometry)
      request.setSubsetOfAttributes(myAttrs.keys())
      fit = layer.getFeatures(request)
      while fit.nextFeature(f):
        attrs = f.attributes()
        tmp = []
        for i in myAttrs.keys():
          tmp.append(attrs[i])
        parser.addTableRow(table, tmp)

      # write table to file
      te.insertBefore(tableTitle, tp)
      te.insertBefore(table, tp)
      te.insertBefore(parser.addParagraph(""), tp)

      self.progressBar.setValue(self.progressBar.value() + 1)
      QCoreApplication.processEvents()

    # remove placeholder
    te.removeChild(tp)

    writer.writeManifest(parser.getManifest())
    writer.writeDocument(parser.getContent())
    writer.closeFile()

    self.progressBar.setRange(0, 1)
    self.progressBar.setValue(0)

    QMessageBox.information(self,
                            self.tr("Completed"),
                            self.tr("Report generated successfully")
                           )
    self.mapTool.reset()

  def renderSchema(self, selectedLayers):
    templateFile = QFile(":/resources/schema-graphics.qpt")
    if not templateFile.open(QIODevice.ReadOnly | QIODevice.Text):
      QMessageBox.warning(self,
                          self.tr("Template load error"),
                          self.tr("Cannot read load composition template from file:\n%1")
                          .arg(templateFile.errorString())
                         )
      return False

    myTemplate = QDomDocument()
    success, errorString, errorLine, errorColumn = myTemplate.setContent(templateFile, True)
    if not success:
      QMessageBox.warning(self,
                          self.tr("Template load error"),
                          self.tr("Parse error at line %d, column %d:\n%s") % (errorLine, errorColumn, errorString)
                         )
      myTemplate = None
      templateFile.close()
      return False

    templateFile.close()

    # prepare composition
    renderer = QgsMapRenderer()

    layers = []
    for layer in self.canvas.layers():
      layers.append(unicode(layer.id()))

    # substitutions
    substitutions = {"title" : "QGIS"}
    if self.leTitle.text() != "":
      substitutions["title"] = self.leTitle.text()

    composition = QgsComposition(self.canvas.mapRenderer())
    composition.loadFromTemplate(myTemplate, substitutions)

    ln = []
    for k, v in selectedLayers.iteritems():
      ln.append(utils.getVectorLayerById(v).name())

    legend = composition.getComposerItemById("Legend0")
    legend.updateLegend()
    lm = legend.model()
    for r in xrange(lm.rowCount()):
      i = lm.item(r, 0)
      if i is not None and i.text() not in ln:
        lm.removeRow(i.index().row(), i.index().parent())

    myMap = composition.getComposerMapById(0)
    myMap.setNewExtent(self.extent)
    if self.leScale.text() != "":
      myMap.setNewScale(float(self.leScale.text()))
    img = composition.printPageAsRaster(0)
    img.save(QDir.tempPath() + "/schema-test.png")
    return True

  def resetMapTool(self, clear=False):
    self.mapTool.reset(clear)
    self.canvas.unsetMapTool(self.mapTool)
    if self.prevMapTool != self.mapTool:
      self.canvas.setMapTool(self.prevMapTool)

  def __getRectangle(self):
    self.extent = self.mapTool.rectangle()

  def __addLayer(self, layer):
    if layer.id() not in self.layers.keys():
      self.layers[layer.id()] = unicode(layer.name())
      self.__updateLayers()

  def __removeLayer(self, layerId):
    del self.layers[layerId]
    self.__updateLayers()

  def __updateLayers(self):
    if self.layers is None:
      self.layers = utils.getVectorLayers()

    if len(self.layers) == 0:
      self.lstLayers.clear()
      return

    relations = self.iface.legendInterface().groupLayerRelationship()

    self.lstLayers.blockSignals(True)
    self.lstLayers.clear()
    for lay in sorted(self.layers.iteritems(), cmp=locale.strcoll, key=operator.itemgetter(1)):
      group = utils.getLayerGroup(relations, lay[0])

      item = QTreeWidgetItem(self.lstLayers)
      if (group is not None) and (group != ""):
        item.setText(0, "%s - %s" % (lay[1], group))
      else:
        item.setText(0, lay[1])
      item.setData(0, Qt.UserRole, lay[0])
      item.setCheckState(0, Qt.Unchecked)
    self.lstLayers.blockSignals(False)

  def __updateExtents(self):
    if not self.rbExtentUser.isChecked():
      self.extent = self.canvas.extent()
