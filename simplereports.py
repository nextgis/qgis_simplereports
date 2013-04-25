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
from PyQt4.QtGui import *

from qgis.core import *

import simplereportswidget
import aboutdialog

import resources_rc

class SimpleReportsPlugin:
  def __init__(self, iface):
    self.iface = iface

    try:
      self.QgisVersion = unicode(QGis.QGIS_VERSION_INT)
    except:
      self.QgisVersion = unicode(QGis.qgisVersion)[ 0 ]

    # For i18n support
    userPluginPath = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/simplereports"
    systemPluginPath = QgsApplication.prefixPath() + "/python/plugins/simplereports"

    overrideLocale = QSettings().value("locale/overrideFlag", QVariant(False)).toBool()
    if not overrideLocale:
      localeFullName = QLocale.system().name()
    else:
      localeFullName = QSettings().value("locale/userLocale", QVariant("")).toString()

    if QFileInfo(userPluginPath).exists():
      translationPath = userPluginPath + "/i18n/simplereports_" + localeFullName + ".qm"
    else:
      translationPath = systemPluginPath + "/i18n/simplereports_" + localeFullName + ".qm"

    self.localePath = translationPath
    if QFileInfo(self.localePath).exists():
      self.translator = QTranslator()
      self.translator.load(self.localePath)
      QCoreApplication.installTranslator(self.translator)

  def initGui(self):
    if int(self.QgisVersion) < 10900:
      qgisVersion = str(self.QgisVersion[ 0 ]) + "." + str(self.QgisVersion[ 2 ]) + "." + str(self.QgisVersion[ 3 ])
      QMessageBox.warning(self.iface.mainWindow(),
                           QCoreApplication.translate("SimpleReports", "Error"),
                           QCoreApplication.translate("SimpleReports", "Quantum GIS %1 detected.\n").arg(qgisVersion) +
                           QCoreApplication.translate("SimpleReports", "This version of SimpleReports requires at least QGIS version 1.9.0. Plugin will not be enabled."))
      return None

    self.dockWidget = None

    self.actionDock = QAction(QCoreApplication.translate("SimpleReports", "SimpleReports"), self.iface.mainWindow())
    self.actionDock.setIcon(QIcon(":/icons/simplereports.png"))
    self.actionDock.setWhatsThis("Simple report generator")
    self.actionDock.setCheckable(True)
    self.actionAbout = QAction(QCoreApplication.translate("SimpleReports", "About SimpleReports..."), self.iface.mainWindow())
    self.actionAbout.setIcon(QIcon(":/icons/about.png"))
    self.actionAbout.setWhatsThis("About SimpleReports")

    self.iface.addPluginToMenu(QCoreApplication.translate("SimpleReports", "SimpleReports"), self.actionDock)
    self.iface.addPluginToMenu(QCoreApplication.translate("SimpleReports", "SimpleReports"), self.actionAbout)
    self.iface.addToolBarIcon(self.actionDock)

    self.actionDock.triggered.connect(self.showHideDockWidget)
    self.actionAbout.triggered.connect(self.about)

    # create dockwidget
    self.dockWidget = simplereportswidget.SimpleReportsDockWidget(self)
    self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)
    self.dockWidget.visibilityChanged.connect(self.__dockVisibilityChanged)

  def unload(self):
    self.iface.removeToolBarIcon(self.actionDock)
    self.iface.removePluginMenu(QCoreApplication.translate("SimpleReports", "SimpleReports"), self.actionDock)
    self.iface.removePluginMenu(QCoreApplication.translate("SimpleReports", "SimpleReports"), self.actionAbout)

    # remove dock widget
    self.dockWidget.close()
    del self.dockWidget
    self.dockWidget = None

  def showHideDockWidget(self):
    if self.dockWidget.isVisible():
      self.dockWidget.hide()
    else:
      self.dockWidget.show()

  def about(self):
    d = aboutdialog.AboutDialog()
    d.exec_()

  def __dockVisibilityChanged(self):
    if self.dockWidget.isVisible():
      self.actionDock.setChecked(True)
    else:
      self.actionDock.setChecked(False)
      self.dockWidget.resetMapTool()
