# SNOMED CT to OWL testbed  (Under Construction)

A toolkit for generating test RF2  cases for SNOMED CT to OWL  converters and a testing kit for conversions.

## History
* 0.3.1 - Add additional core metadata concepts to support 2018 release

[![PyPi](https://version-image.appspot.com/pypi/?name=SNOMEDToOWL)](https://pypi.python.org/pypi/SNOMEDToOWL)

[![Pyversions](https://img.shields.io/pypi/pyversions/SNOMEDToOWL.svg)](https://pypi.python.org/pypi/SNOMEDToOWL)

## Requirements
* [python 3](https://www.python.org/) -- this has been tested with python 3.6.4
* [virtualenv](https://pypi.python.org/pypi/virtualenv) -- useful but not absolutely necessary 
* A [SNOMED CT](http://www.ihtsdo.org/snomed-ct) [RF2](https://confluence.ihtsdotools.org/display/DOCRELFMT/2.2.+Release+Format+2+-+Introduction) release.  (US Citizens can download an image from the [NLM Site](https://www.nlm.nih.gov/healthit/snomedct/index.html))


## Installation
### Option 1: Setup as a python 3 virtual environment
(Assumes virtualenv has been installed)

```bash
> virtualenv scttoowl -p python3
> . scttoowl/bin/activate
(scttoowl) > pip install SNOMEDToOWL
```

### Option 2:  Install SNOMEDToOWL directly
(Assumes that you are running Python 3)

```bash
> python --version
 Python 3.x.y
> pip install SNOMEDToOWL
```

## Modules
* [SNOMEDToOWL](scripts/SNOMEDToOWL.md) -- Convert an RF2 Snapshot distribution into OWL
* [RF2Filter](scripts/RF2Filter.md) -- extract selected concepts from an RF2 distribution
* [CompareRDF](scripts/CompareRDF.md) -- Compare two RDF/OWL files

[Notes on module imports](Modules.md)