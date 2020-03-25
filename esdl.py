
from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage
from pyecore.resources.resource import HttpURI


def get_energysystem_from_esdl(fname):
    rset = ResourceSet()
    resource = rset.get_resource(HttpURI('https://raw.githubusercontent.com/EnergyTransition/ESDL/master/esdl/model/esdl.ecore'))
    esdl_model = resource.contents[0]
    rset.metamodel_registry[esdl_model.nsURI] = esdl_model
    resource = rset.get_resource(URI(fname))
    return resource.contents[0]


def get_assets(x):
    assets = []
    if hasattr(x, 'asset'):
        if hasattr(x.asset, '__iter__'):
            for a in x.asset:
                assets.append(a)
        else:
            assets.append(x.asset)
    if hasattr(x, 'area'):
        if hasattr(x.area, '__iter__'):
            for a in x.area:
                assets += get_assets(a)
        else:
            assets += get_assets(x.area)
    return assets


def esdl_parser(fname):
    es = get_energysystem_from_esdl(fname)
    assets = get_assets(es.instance[0])
    asset_dict = {}
    for a in assets:
        t = type(a).__name__
        if t in asset_dict:
            asset_dict[t].append(a)
        else:
            asset_dict[t] = [a]
    return assets, asset_dict

