# esdl_qgis_plugin

This plugin parses an ESDL file and visualizes it in QGIS. ESDL (energy systems description language) is an xml based format used for describing energy systems (see https://energytransition.gitbook.io/).

It requires the python library pyEcore to be installed. Which can be installed through pip. For Windows this has to be done through the OSGeo4W shell: 
1. Open OSGeo4W shell (packed with QGIS in the start menu)
2. Type py3_env. This should print paths of your QGIS Python installation.
3. Use Python’s pip to install the library: python -m pip install pyecore
see also: https://landscapearchaeology.org/2018/installing-python-packages-in-qgis-3-for-windows/
On linux and OS X QGIS uses the default python version, so typing "python -m pip install pyecore" will suffice.

When the plugin is installed and enabled a "Load ESDL" button appears in the QGIS toolbar. Clicking on it will produce a file selection window, where an ESDL file (*.esdl) can be selected. The energy assets will then be parsed and if they contain geometries visualized on the map.
