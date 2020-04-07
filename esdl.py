
import sys 
sys.setrecursionlimit(5000)

from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage
from pyecore.resources.resource import HttpURI


def get_energysystem_from_esdl(fname):
    """
    Helper function for esdl_parser. It takes the name of an ESDL file 
    and returns the EnergySystem object (root of the ESDL tree).
    """
    rset = ResourceSet()
    resource = rset.get_resource(HttpURI('https://raw.githubusercontent.com/EnergyTransition/ESDL/master/esdl/model/esdl.ecore'))
    esdl_model = resource.contents[0]
    rset.metamodel_registry[esdl_model.nsURI] = esdl_model
    resource = rset.get_resource(URI(fname))
    return resource.contents[0]


def get_assets(x):
    """
    Helper function for esdl_parser. It recursively traverses
    an ESDL tree and returns a list with all assets in the tree.
    """
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
    """
    Parses an ESDL file and returns all energy assets within that file,
    both ordered per class in a dictionary and as a list.
    """
    es = get_energysystem_from_esdl(fname)
    asset_struct = []
    for inst in es.instance:
        assets = get_assets(inst)
        asset_dict = {}
        for a in assets:
            t = type(a).__name__
            if t in asset_dict:
                asset_dict[t].append(a)
            else:
                asset_dict[t] = [a]
        asset_struct.append((inst.name, assets, asset_dict))
    return asset_struct

