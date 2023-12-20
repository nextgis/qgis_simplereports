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

from __future__ import absolute_import
from builtins import str
from builtins import object
import os
from os import path
from qgis.PyQt.QtCore import QFileInfo, QSettings, QLocale, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox

from qgis.core import *
from qgis.core import QgsApplication

from . import simplereportswidget
from . import about_dialog

resources_path = os.path.join(
    os.path.dirname(__file__), 'resources/')
icons_path = os.path.join(
    os.path.dirname(__file__), 'icons/')


class SimpleReportsPlugin(object):
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self._translator = None
        try:
            self.QgisVersion = str(Qgis.QGIS_VERSION_INT)
        except:
            self.QgisVersion = str(Qgis.qgisVersion)[0]

        # For i18n support
        userPluginPath = QFileInfo(QgsApplication.qgisUserDatabaseFilePath()).path() + "/python/plugins/simplereports"
        systemPluginPath = QgsApplication.prefixPath() + "/python/plugins/simplereports"

        overrideLocale = QSettings().value("locale/overrideFlag", False)
        if not overrideLocale:
            localeFullName = QLocale.system().name()
        else:
            localeFullName = QSettings().value("locale/userLocale", "")

        if QFileInfo(userPluginPath).exists():
            translationPath = userPluginPath + "/i18n/simplereports_" + localeFullName + ".qm"
        else:
            translationPath = systemPluginPath + "/i18n/simplereports_" + localeFullName + ".qm"

        self.localePath = translationPath
        self.translator = QTranslator()
        self.translator.load(self.localePath)
        QCoreApplication.installTranslator(self.translator)
        # if QFileInfo(self.localePath).exists():

    def initGui(self):
        print(__class__.__name__)
        if int(self.QgisVersion) < 10900:
            qgisVersion = str(self.QgisVersion[0]) + "." + str(self.QgisVersion[2]) + "." + str(self.QgisVersion[3])
            QMessageBox.warning(self.iface.mainWindow(),
                                self.tr("Error"),
                                self.tr("Quantum GIS %s detected.\n") % (
                                    qgisVersion) +
                                self.tr(
                                    "This version of SimpleReports requires at least QGIS version 2.0. Plugin will not be enabled.")
                                )
            return None

        self.dockWidget = None

        self.actionDock = QAction(self.tr("SimpleReports"), self.iface.mainWindow())
        self.actionDock.setIcon(QIcon(icons_path + "simplereports.png"))
        self.actionDock.setWhatsThis("Simple report generator")
        self.actionDock.setCheckable(True)
        self.actionAbout = QAction(
            self.tr("About..."), self.iface.mainWindow()
        )
        self.actionAbout.setIcon(QIcon(icons_path + "about.png"))
        self.actionAbout.setWhatsThis("About SimpleReports")

        self.iface.addPluginToMenu(self.tr("SimpleReports"), self.actionDock)
        self.iface.addPluginToMenu(self.tr("SimpleReports"), self.actionAbout)
        self.iface.addToolBarIcon(self.actionDock)

        self.actionDock.triggered.connect(self.showHideDockWidget)
        self.actionAbout.triggered.connect(self.about)

        # create dockwidget
        self.dockWidget = simplereportswidget.SimpleReportsDockWidget(self)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)
        self.dockWidget.visibilityChanged.connect(self.__dockVisibilityChanged)

    def unload(self):
        self.iface.removeToolBarIcon(self.actionDock)
        self.iface.removePluginMenu(self.tr("SimpleReports"), self.actionDock)
        self.iface.removePluginMenu(self.tr("SimpleReports"), self.actionAbout)

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
        dialog = about_dialog.AboutDialog(os.path.basename(self.plugin_dir))
        dialog.exec_()

    def __dockVisibilityChanged(self):
        if self.dockWidget.isVisible():
            self.actionDock.setChecked(True)
        else:
            self.actionDock.setChecked(False)
            self.dockWidget.resetMapTool()

    def tr(self, message):
        return QCoreApplication.translate(__class__.__name__, message)
