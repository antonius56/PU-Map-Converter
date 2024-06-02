## Map Converter

This script converts finished maps in the PU-format into editable PUMAP-files. 
It was made for older abandoned maps or for cases, where the PUMAP was accidentally not exported, 
and can be run through the following command:
```
python main.py "path/to/PU"
```

### Debug Map Comparison
The file *compare_maps.py* is a simple debug tool that compares two JSON-objects, and outputs the difference.
This allowed me to detect spots, where the *main.py* had mistakes in its converter.

It is supposed to be used by exporting a playable map (or module) and an editable map, converting the former using 
*main.py* and then checking the resulted editable map against the proper editable map.

It's run by the command:
```
python compare_maps.py "path/to/proper/PUMAP" "path/to/generated/PUMAP"
```
and required the package [jsondiff](https://pypi.org/project/jsondiff/)-package to be installed.