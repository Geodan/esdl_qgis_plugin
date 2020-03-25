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

from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QAction, QMessageBox, QFileDialog
from qgis.core import QgsProject, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY, QgsCategorizedSymbolRenderer

try:
    import pyecore
except ModuleNotFoundError:
    pip.main(['install', 'pyecore'])

from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage
from pyecore.resources.resource import HttpURI
#from xmlresource import XMLResource


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
            asset_dict = self.esdl_parser(filename)
            for t in asset_dict:
                self.create_layer(t, asset_dict[t])
    
    def esdl_parser(self, fname):
        rset = ResourceSet()
        # Assign files with the .esdl extension to the XMLResource instead of default XMI
        #rset.resource_factory['esdl'] = lambda uri: XMLResource(uri)  

        # Read the lastest esdl.ecore from github
        resource = rset.get_resource(HttpURI('https://raw.githubusercontent.com/EnergyTransition/ESDL/master/esdl/model/esdl.ecore'))
        esdl_model = resource.contents[0]
        print('Namespace: {}'.format(esdl_model.nsURI))
        rset.metamodel_registry[esdl_model.nsURI] = esdl_model
        # Create a dynamic model from the loaded esdl.ecore model, which we can use to build Energy Systems
        esdl = DynamicEPackage(esdl_model)
        resource = rset.get_resource(URI(fname))
        es = resource.contents[0]
        assets = {}
        ar = es.instance[0].area
        for a in ar.asset:
            t = type(a).__name__
            if t in assets:
                assets[t].append(a)
            else:
                assets[t] = [a]
        for ar2 in ar.area:
            for a in ar2.asset:
                t = type(a).__name__
                if t in assets:
                    assets[t].append(a)
                else:
                    assets[t] = [a]
        return(assets)
        
    def create_layer(self, type_name, assets):
        # create layer
        if type(assets[0].geometry).__name__ == "Point":
            geomtype = "Point?crs=EPSG:4326"
        elif type(assets[0].geometry).__name__ == "Line":
            geomtype = "Linestring?crs=EPSG:4326"
        elif type(assets[0].geometry).__name__ == "Polygon":
            geomtype = "Polygon?crs=EPSG:4326"
        else:
            geomtype = "Point?crs=EPSG:4326"
        vl = QgsVectorLayer(geomtype, type_name, "memory")
        pr = vl.dataProvider()
        
        # Enter editing mode
        vl.startEditing()

        # add fields
        pr.addAttributes([ 
                    QgsField("id", QVariant.String),
                    QgsField("type", QVariant.String),
                    QgsField("area_id",  QVariant.String)
                        ])

        # add a feature
        fets = []
        for a in assets:
            fet = QgsFeature()
            if type(a.geometry).__name__ == "Point":
                fet.setGeometry( QgsGeometry.fromPointXY(QgsPointXY(a.geometry.lon, a.geometry.lat)) )
            elif type(a.geometry).__name__ == "Line":
                fet.setGeometry( QgsGeometry.fromPolylineXY( [QgsPointXY(p.lon, p.lat) for p in a.geometry.point] ) )
            elif type(a.geometry).__name__ == "Polygon":
                fet.setGeometry( QgsGeometry.fromPolygonXY( [[QgsPointXY(p.lon, p.lat) for p in a.geometry.exterior.point]] ) )
            fet.setAttributes([a.id, type_name, a.area.id])
            fets.append(fet)
        
        pr.addFeatures(fets)
        
        # Commit changes
        vl.commitChanges()
        
        self.project.addMapLayer(vl)
                
            
            

