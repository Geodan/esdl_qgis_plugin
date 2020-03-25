
from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage
from pyecore.resources.resource import HttpURI

def get_energysystem_from_esdl(fname):
    rset = ResourceSet()
    
    # Read the lastest esdl.ecore from github
    resource = rset.get_resource(HttpURI('https://raw.githubusercontent.com/EnergyTransition/ESDL/master/esdl/model/esdl.ecore'))
    esdl_model = resource.contents[0]
    rset.metamodel_registry[esdl_model.nsURI] = esdl_model
    
    # Create a dynamic model from the loaded esdl.ecore model, which we can use to build Energy Systems
    esdl = DynamicEPackage(esdl_model)
    resource = rset.get_resource(URI(fname))
    return resource.contents[0]


def esdl_parser(fname):
    es = get_energysystem_from_esdl(fname)
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
