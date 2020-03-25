
from PyQt5.QtCore import QVariant
from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY


def create_feature(asset):
    """
    Helper function to create a QgsFeature from an ESDL asset.
    """
    fet = QgsFeature()
    geom = asset.geometry
    if type(geom).__name__ == "Point":
        fet.setGeometry( QgsGeometry.fromPointXY(QgsPointXY(geom.lon, geom.lat)) )
    elif type(geom).__name__ == "Line":
        fet.setGeometry( QgsGeometry.fromPolylineXY( [QgsPointXY(p.lon, p.lat) for p in geom.point] ) )
    elif type(geom).__name__ == "Polygon":
        fet.setGeometry( QgsGeometry.fromPolygonXY( [[QgsPointXY(p.lon, p.lat) for p in geom.exterior.point]] ) )
    fet.setAttributes([asset.id, type(asset).__name__, asset.area.id])
    return fet


def create_layer(type_name, assets):
    # determine geometry type, default is Point
    geomname = type(assets[0].geometry).__name__
    if geomname == "Line":
        geomtype = "Linestring?crs=EPSG:4326"
    elif geomname == "Polygon":
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
    fets = [create_feature(a) for a in assets]
    pr.addFeatures(fets)
                
    # Commit changes
    vl.commitChanges()
                
    return vl
            
                
