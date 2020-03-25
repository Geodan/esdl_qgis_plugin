
from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage
from pyecore.resources.resource import HttpURI

def esdl_parser(fname):
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
