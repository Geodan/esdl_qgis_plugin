
from PyQt5.QtCore import QVariant
from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY, QgsLineSymbol


def get_profile_from_port(port):
    """
    Function that takes an ESDL port object of an asset and
    puts main attributes into QGIS attributes of the asset.
    
    Not working in all cases...
    """
    inPortProfileValue, inPortProfileUnit = None, None
    try:
        if hasattr(port, '__iter__'):
            for p in port:
                if type(p).__name__ == 'InPort' and hasattr(p, 'profile'):
                    inPortProfileValue = p.profile[0].value
                    inPortProfileUnit = (
                        str(p.profile[0].profileQuantityAndUnit.multiplier) + 
                        str(p.profile[0].profileQuantityAndUnit.unit) + "/" + 
                        str(p.profile[0].profileQuantityAndUnit.perTimeUnit)
                    )
        elif type(port).__name__ == 'InPort' and hasattr(port, 'profile'):
            inPortProfileValue = port.profile[0].value
            inPortProfileUnit = (
                str(port.profile[0].profileQuantityAndUnit.multiplier) + 
                str(port.profile[0].profileQuantityAndUnit.unit) + "/" + 
                str(port.profile[0].profileQuantityAndUnit.perTimeUnit)
            )
    except (AttributeError, IndexError) as error:
        pass
    return [inPortProfileValue, inPortProfileUnit]


def create_feature(asset, attributes):
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
        
    attribute_values = [getattr(asset, at, None) for at in attributes]
    if hasattr(asset, "port"):
        attribute_values += get_profile_from_port(asset.port)
    fet.setAttributes(attribute_values)
    
    return fet


def create_layer(type_name, assets):
    """
    This function creates a vector layer of ESDL assets of one 
    particular class. It takes the name of the class and a list with
    all assets of that class. It returns a vector layer with an 
    appropriate geometry for that class.
    """
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
    type2Qtype = {int: QVariant.Int, str: QVariant.String, 
                  float: QVariant.Double, bool: QVariant.Bool}
    attributes = [at for at in dir(assets[0]) if type(getattr(assets[0], at)) in type2Qtype]
    Qattributes = [ QgsField(at, type2Qtype.get(type(getattr(assets[0], at)))) for at in attributes ]
    if hasattr(assets[0], "port"):
        Qattributes.append(QgsField('inPortProfileValue', QVariant.Double))
        Qattributes.append(QgsField('inPortProfileUnit', QVariant.String))
    pr.addAttributes(Qattributes)
                
    # add features
    fets = [create_feature(a, attributes) for a in assets]
    pr.addFeatures(fets)
                
    # Commit changes
    vl.commitChanges()
                
    return vl
            

# Functions to add ESDL in- and outport connections to a QGIS layer
###################################################################

def get_port_geom(geom1, geom2):
    """
    Helper function for create_port_layer
    
    Takes the geometries of two ESDL assets that are connected by ports 
    and returns coordinates of two points in the geometries, 
    such that a line can be drawn between the assets.
    """
    lon1, lat1 = None, None
    if hasattr(geom1, 'lon'):
        lon1, lat1 = geom1.lon, geom1.lat
    elif hasattr(geom1, 'point'):
        lon1, lat1 = geom1.point[0].lon, geom1.point[0].lat
    elif hasattr(geom1, 'exterior') and hasattr(geom1.exterior, 'point'):
        lon1, lat1 = geom1.exterior.point[0].lon, geom1.exterior.point[0].lat
    lon2, lat2 = None, None
    if hasattr(geom2, 'lon'):
        lon2, lat2 = geom2.lon, geom2.lat
    elif hasattr(geom2, 'point'):
        lon2, lat2 = geom2.point[-1].lon, geom2.point[-1].lat
    elif hasattr(geom2, 'exterior') and hasattr(geom2.exterior, 'point'):
        lon2, lat2 = geom2.exterior.point[0].lon, geom2.exterior.point[0].lat
    return [lon1, lat1, lon2, lat2]
    

def get_port_connection(p):
    """
    Helper function for create_port_layer
    
    Takes an ESDL InPort object and returns alle the connections the port has.
    """
    ports = []
    if type(p).__name__ == 'InPort' and hasattr(p, 'connectedTo'):
        if hasattr(p.connectedTo, '__iter__'):
            for pct in p.connectedTo:
                ports.append([p.id, p.energyasset.id, pct.id, pct.energyasset.id,
                              get_port_geom(p.energyasset.geometry, pct.energyasset.geometry)])
        elif hasattr(p.connectedTo, 'energyasset'):
            pct = p.connectedTo
            ports.append([p.id, p.energyasset.id, pct.id, pct.energyasset.id,
                          get_port_geom(p.energyasset.geometry, pct.energyasset.geometry)])
    return ports


def create_port_layer(assets):
    """
    Takes a list of all ESDL assets in the file and searches for assets 
    that are connected by ports. A vector layer of type Linestring is 
    created containing dashed lines between the connected assets.
    """
    ports = []
    for asset in assets:
        if hasattr(asset, "port"):
            if hasattr(asset.port, '__iter__'):
                for p in asset.port:
                    ports += get_port_connection(p)
            else:
                ports += get_port_connection(asset.port)
    
    vl = QgsVectorLayer("Linestring?crs=EPSG:4326", "Ports", "memory")
    pr = vl.dataProvider()
    vl.startEditing()
                
    # add fields
    pr.addAttributes([ 
        QgsField('inPort_id', QVariant.String),
        QgsField('inAsset_id', QVariant.String),
        QgsField('outPort_id', QVariant.String),
        QgsField('outAsset_id', QVariant.String)
    ])
                
    # add features
    fets = []
    for pc in ports:
        fet = QgsFeature()
        fet.setAttributes(pc[:4])
        if not None in pc[4]:
            fet.setGeometry( QgsGeometry.fromPolylineXY( [QgsPointXY(pc[4][0], pc[4][1]), QgsPointXY(pc[4][2], pc[4][3])] ) )
        fets.append(fet)
    pr.addFeatures(fets)
    
    vl.commitChanges()
    
    symbol = QgsLineSymbol.createSimple({'line_style': 'dash', 'color': 'grey'})
    vl.renderer().setSymbol(symbol)
    #vl.triggerRepaint()
                
    return vl

###################################################################
