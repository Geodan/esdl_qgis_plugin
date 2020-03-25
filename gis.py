
from PyQt5.QtCore import QVariant
from qgis.core import QgsProject, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY, QgsCategorizedSymbolRenderer


def create_feature(a, type_name):
    fet = QgsFeature()
    if type(a.geometry).__name__ == "Point":
        fet.setGeometry( QgsGeometry.fromPointXY(QgsPointXY(a.geometry.lon, a.geometry.lat)) )
    elif type(a.geometry).__name__ == "Line":
        fet.setGeometry( QgsGeometry.fromPolylineXY( [QgsPointXY(p.lon, p.lat) for p in a.geometry.point] ) )
    elif type(a.geometry).__name__ == "Polygon":
        fet.setGeometry( QgsGeometry.fromPolygonXY( [[QgsPointXY(p.lon, p.lat) for p in a.geometry.exterior.point]] ) )
    fet.setAttributes([a.id, type_name, a.area.id])
    return fet


def create_layer(type_name, assets):
        # determine geometry type, default is Point
        if type(assets[0].geometry).__name__ == "Line":
            geomtype = "Linestring?crs=EPSG:4326"
        elif type(assets[0].geometry).__name__ == "Polygon":
            geomtype = "Polygon?crs=EPSG:4326"
        else:
            geomtype = "Point?crs=EPSG:4326"
        
        # create layer
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

        # add features
        fets = [create_feature(a, type_name) for a in assets]
        pr.addFeatures(fets)
        
        # Commit changes
        vl.commitChanges()
        
        return vl
        
                
