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
from .gis import create_layer, create_port_layer


def classFactory(iface):
    """
    Function that is called by QGIS. It creates the plugin.
    """
    return ESDLPlugin(iface)


class ESDLPlugin:
    """
    Basic QGIS plugin implementation.
    """
    def __init__(self, iface):
        """
        Initiates the plugin by coupling it to the QGIS interface and
        create a project.
        """
        self.iface = iface
        self.project = QgsProject.instance()
        self.root = self.project.layerTreeRoot()

    def initGui(self):
        """
        Creates the button in the toolbar.
        """
        self.action = QAction('Load ESDL', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        """
        Removes the icon from the toolbar if the plugin is deactivated.
        """
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        """
        Main function of the plugin.
        Opens file dialog, parses the selected ESDL file, 
        puts the assets in layers and adds them to the project.
        """
        dialog = QFileDialog(None)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("*.esdl *.ESDL")
        if dialog.exec_():
            filename = dialog.selectedFiles()[0]
            main_group = self.root.insertGroup(0, filename)
            asset_struct = esdl_parser(filename)
            for instance_name, assets, asset_dict in asset_struct:
                group = main_group.addGroup(instance_name)
                for t in asset_dict:
                    vlayer = create_layer(t, asset_dict[t])
                    self.project.addMapLayer(vlayer, False)
                    group.addLayer(vlayer)
                portlayer = create_port_layer(assets)
                self.project.addMapLayer(portlayer, False)
                group.addLayer(portlayer)
        

            
            

