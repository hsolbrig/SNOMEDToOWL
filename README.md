# SNOMED CT to OWL testbed  (Deprecated)

A toolkit for generating test RF2 cases for SNOMED CT to OWL  converters and a testing kit for conversions.

As of July, 2019, SNOMED International added the OWL Refset -- a set of [OWL Functional Syntax Axioms](https://www.w3.org/TR/owl2-syntax/) in tabular form that represent a
superset of what was previously contained in the combination of the Concept and Stated Relationship tables.  This tool no longer generates valid OWL from post July 2019 
SNOMED releases.

It should be noted, however, that the OWL Refset does not:
1) Define annotation properties (e.g. `rdfs:label`, `skos:prefLabel`, `skos:altLabel` and `skos:definition`). The script referenced below
does a reasonable job of providing `rdfs:label` assertions, but adding the rest of the contents of the Description file and Language refset
still needs to be developed. (*Note: it is possible that tools now exist to do all of this -- see the [SNOMED Github Site](https://github.com/IHTSDO))
2) Provide some of the additional functionality contained within -- [RF2Filter](scripts/RF2Filter.md) in particular

## In the short term, some may find the [OWLRefsetToOWL](scripts/OWLRefsetToOWL.sh) script useful.

## History
* 0.4.0 - Deprecated as no longer applicable
* 0.3.1 - Add additional core metadata concepts to support 2018 release
* 0.3.2 - Add two further metadata concepts and `Modules` functio

[![Latest Version](https://pypip.in/version/SNOMEDToOWL/badge.svg)](https://pypi.python.org/pypi/SNOMEDToOWL/)
[![Pyversions](https://pypip.in/py_versions/SNOMEDToOWL/badge.svg)](https://pypi.python.org/pypi/SNOMEDToOWL/)
[![Latest Version](https://pypip.in/license/SNOMEDToOWL/badge.svg)](https://pypi.python.org/pypi/SNOMEDToOWL/)


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