#-----------------------------------------------------------
# Copyright (C) 2020 Daniel Muysken
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 3
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

import os 
import pip

from PyQt5.QtWidgets import QAction, QMessageBox, QFileDialog
from qgis.core import QgsProject

from .esdl import esdl_parser
from .gis import create_layer


def classFactory(iface):
    return ESDLPlugin(iface)


class ESDLPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.project = QgsProject.instance()

    def initGui(self):
        self.action = QAction('Load ESDL', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        #QMessageBox.information(None, 'Load ESDL', 'Upload an ESDL file')
        dialog = QFileDialog(None)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("*.esdl *.ESDL")
        if dialog.exec_():
            filename = dialog.selectedFiles()[0]
            asset_dict = esdl_parser(filename)
            for t in asset_dict:
                vlayer = create_layer(t, asset_dict[t])
                self.project.addMapLayer(vlayer)
        

            
            

