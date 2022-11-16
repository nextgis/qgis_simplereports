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

from future import standard_library

standard_library.install_aliases()
import configparser
import os

from qgis.PyQt import uic
from qgis.PyQt.QtGui import QPixmap, QTextDocument
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox

Ui_Dialog, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/aboutdialogbase.ui'))
icons_path = os.path.join(
    os.path.dirname(__file__), 'icons/')

    
class AboutDialog(QDialog, Ui_Dialog):
  def __init__(self):
    QDialog.__init__(self)
    self.setupUi(self)

    self.btnHelp = self.buttonBox.button(QDialogButtonBox.Help)

    self.lblLogo.setPixmap(QPixmap(icons_path + "simplereports.png"))

    cfg = configparser.SafeConfigParser()
    cfg.read(os.path.join(os.path.dirname(__file__), "metadata.txt"))
    version = cfg.get("general", "version")
    self.lblVersion.setText(self.tr("Version: %s") % (version))

    doc = QTextDocument()
    doc.setHtml(self.getAboutText())
    self.textBrowser.setDocument(doc)
    self.textBrowser.setOpenExternalLinks(True)

    self.buttonBox.helpRequested.connect(self.openHelp)

  def reject(self):
    QDialog.reject(self)

  def openHelp(self):
    #~ overrideLocale = QSettings().value("locale/overrideFlag", QVariant(False)).toBool()
    #~ if not overrideLocale:
      #~ localeFullName = QLocale.system().name()
    #~ else:
      #~ localeFullName = QSettings().value("locale/userLocale", QVariant("")).toString()
#~
    #~ localeShortName = localeFullName[ 0:2 ]
    #~ if localeShortName in [ "ru", "uk" ]:
      #~ QDesktopServices.openUrl(QUrl("http://hub.qgis.org/projects/simplereports/wiki"))
    #~ else:
      #~ QDesktopServices.openUrl(QUrl("http://hub.qgis.org/projects/simplereports/wiki"))
    pass

  def getAboutText(self):
    return self.tr("""<p>Simple report generator.</p>
<p>Plugin for generating simple reports for vector layers.</p>
<p><strong>Developers</strong>: <a href="http://nextgis.org">NextGIS</a>.</p>
<p><strong>Homepage</strong>: <a href="http://hub.qgis.org/projects/simplereports">http://hub.qgis.org/projects/simplereports</a></p>
<p>Please report bugs at <a href="http://hub.qgis.org/projects/simplereports/issues">bugtracker</a></p>
""")
