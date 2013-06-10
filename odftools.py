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

import zipfile

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *

from qgis.core import *

class ODFWriter(QObject):
  def __init__(self, parent=None):
    QObject.__init__(self)

    self.fileName = None
    self.odfFile = None
    self.fileList = None

  def setFileName(self, fileName):
    self.fileName = fileName

  def openFile(self):
    self.odfFile = zipfile.ZipFile(self.fileName, "a")
    self.fileList = self.odfFile.infolist()

  def closeFile(self):
    self.odfFile.close()

  def readDocument(self):
    return self.odfFile.read("content.xml")

  def readManifest(self):
    return self.odfFile.read("META-INF/manifest.xml")

  def writeDocument(self, doc):
    self.odfFile.writestr("content.xml", doc.encode("utf-8"))

  def writeManifest(self, doc):
    self.odfFile.writestr("META-INF/manifest.xml", doc.encode("utf-8"))

  def addPicture(self, imgPath, arcName):
    self.odfFile.write(imgPath, "Pictures/" + arcName)

class ODFParser(QObject):
  def __init__(self, parent=None):
    QObject.__init__(self)

    self.content = QDomDocument()
    self.manifest = QDomDocument()

  def setContent(self, text):
    self.content.setContent(text)

  def setManifest(self, text):
    self.manifest.setContent(text)

  def getContent(self):
    return unicode(self.content.toString())

  def getManifest(self):
    return unicode(self.manifest.toString())

  def addPictureToManifest(self, imgName):
    root = self.manifest.documentElement()

    elem = self.manifest.createElement("manifest:file-entry")
    elem.setAttribute("manifest:full-path", "Pictures/" + imgName)
    elem.setAttribute("manifest:media-type", "")

    root.appendChild(elem)

  def substitute(self, substitutions):
    if len(substitutions) > 0:
      xmlString = self.content.toString()
      for k, v in substitutions.iteritems():
        xmlString = xmlString.replace(k, self.encodeStringForXML(v))

      success, errorString, errorLine, errorColumn = self.content.setContent(xmlString, True)
      if not success:
        return False

    return True

  def encodeStringForXML(self, string):
    modifiedString = string
    modifiedStr.replace("&", "&amp;")
    modifiedStr.replace("\"", "&quot;") # maybe \&quot; ?
    modifiedStr.replace("'", "&apos;")
    modifiedStr.replace("<", "&lt;")
    modifiedStr.replace(">", "&gt;")
    return modifiedStr

  def addPictureToDocument(self, mark, imgName, width, height):
    root = self.content.documentElement()

    # check if style for graphics items exists
    stylesSection = root.firstChildElement("office:automatic-styles")
    styleFound = False
    style = stylesSection.firstChildElement("style:style")
    while not style.isNull():
      if style.attribute("style:name") == "fr1" and style.attribute("style:family") == "graphic":
        styleFound = True
        break
      style = style.nextSiblingElement()

    if not styleFound:
      style = stylesSection.ownerDocument().createElement("style:style")
      style.setAttribute("style:name", "fr1")
      style.setAttribute("style:family", "graphic")
      style.setAttribute("style:parent-style-name", "Graphics")

      props = style.ownerDocument().createElement("style:graphic-properties")
      props.setAttribute("style:wrap", "none")
      props.setAttribute("style:horizontal-pos", "center")
      props.setAttribute("style:horizontal-rel", "paragraph")

      style.appendChild(props)
      stylesSection.appendChild(style)

    docBody = root.firstChildElement("office:body")
    textBody = docBody.firstChildElement("office:text")
    child = textBody.firstChildElement("text:p")
    while not child.isNull():
      if mark.lower() in child.text().lower():
        # found marker, now replace it with image

        if child.hasChildNodes():
          cn = child.firstChild()
          child.removeChild(cn)
          cn = cn.nextSibling()

        child.setTagName("text:p")
        child.setAttribute("text:style-name", "Standard")

        drawFrame = child.ownerDocument().createElement("draw:frame")
        drawFrame.setAttribute("draw:style-name", "fr1")
        drawFrame.setAttribute("draw:name", imgName)
        drawFrame.setAttribute("text:anchor-type", "paragraph")
        drawFrame.setAttribute("svg:width", unicode(width) + "cm")
        drawFrame.setAttribute("svg:height", unicode(height) + "cm")
        drawFrame.setAttribute("draw:z-index", 0)

        drawImage = drawFrame.ownerDocument().createElement("draw:image")
        drawImage.setAttribute("xlink:href", "Pictures/" + imgName)
        drawImage.setAttribute("xlink:type", "simple")
        drawImage.setAttribute("xlink:show", "embed")
        drawImage.setAttribute("xlink:actuate", "onLoad")

        drawFrame.appendChild(drawImage)
        child.appendChild(drawFrame)
        return True

      child = child.nextSiblingElement()

    return False

  def addParagraph(self, text):
    root = self.content.documentElement()

    docBody = root.firstChildElement("office:body")
    textBody = docBody.firstChildElement("office:text")

    paragraphBody = textBody.ownerDocument().createElement("text:p")
    paragraphSpan = paragraphBody.ownerDocument().createElement("text:span")
    paragraphValue = paragraphSpan.ownerDocument().createTextNode(unicode(text))

    if len(text) > 0:
      paragraphSpan.appendChild(paragraphValue)

    paragraphBody.appendChild(paragraphSpan)
    textBody.appendChild(paragraphBody)

  def addTable(self, tableName, columns):
    root = self.content.documentElement()

    docBody = root.firstChildElement("office:body")
    textBody = docBody.firstChildElement("office:text")

    tableBody = textBody.ownerDocument().createElement("table:table")
    tableBody.setAttribute("table:name", tableName)

    tableColumns = tableBody.ownerDocument().createElement("table:table-column")
    tableColumns.setAttribute("table:number-columns-repeated", columns)

    tableBody.appendChild(tableColumns)
    textBody.appendChild(tableBody)

    return tableBody

  def addTableRow(self, table, data):
    tableRow = table.ownerDocument().createElement("table:table-row")
    for d in data:
      tableCell = tableRow.ownerDocument().createElement("table:table-cell")
      tableCell.setAttribute("office:value-type", "string")

      cellContentParagraph = tableCell.ownerDocument().createElement("text:p")
      cellContentSpan = cellContentParagraph.ownerDocument().createElement("text:span")
      if hasattr(d, "toString"):
        cellValue = cellContentSpan.ownerDocument().createTextNode(unicode(d.toString()))
      else:
        cellValue = cellContentSpan.ownerDocument().createTextNode(unicode(d))

      cellContentSpan.appendChild(cellValue)
      cellContentParagraph.appendChild(cellContentSpan)
      tableCell.appendChild(cellContentParagraph)
      tableRow.appendChild(tableCell)

    table.appendChild(tableRow)

  def writeTable(self, table):
    root = self.content.documentElement()

    docBody = root.firstChildElement("office:body")
    textBody = docBody.firstChildElement("office:text")

    textBody.appendChild(table)
