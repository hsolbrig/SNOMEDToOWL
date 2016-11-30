# SNOMED CT to OWL testbed  (Under Construction)

A toolkit for generating test RF2  cases for SNOMED CT to OWL  converters and a testing kit for conversions.

## Requirements
* [python 3](https://www.python.org/) -- this has been tested with python 3.5.0
* A [SNOMED CT](http://www.ihtsdo.org/snomed-ct) [RF2](https://confluence.ihtsdotools.org/display/DOCRELFMT/2.2.+Release+Format+2+-+Introduction) release.  (US Citizens can download an image from the [NLM Site](https://www.nlm.nih.gov/healthit/snomedct/index.html))

## Installation
Set up a python3 virtual environment:

```bash
> virtualenv scttoowl -p python3
> . scttoowl/bin/activate
(scttoowl) > pip install SNOMEDToOWL
```

## RF2Filter
The purpose of RF2Filter is to create a subset of an RF2 Snapshot for testing purposes.

RF2Filter takes a list of SNOMED CT concept identifiers and a directory containing RF2 Snapshot files an transfers all of the rows in the RF2 files that describe or define the listed concepts into a corresponding list of RF2 files in a target directory.


**usage**: RF2Filter indir outdir  [-h] [-i] [-t] [--children] -c CONCEPTID [CONCEPTID ...] 

```text
Extract selected SNOMED-CT RF2 concepts

positional arguments:
  indir                 Location of existing RF2 Snapshot directory
  outdir                Target directory for filtered RF2 content

optional arguments:
  -h, --help            show this help message and exit
  -i, --init            Initialize the target output files
  -a, --doancestors     Add touched concept ancestors
  --children            Add direct children of selected concepts
  -c CONCEPTID [CONCEPTID ...], --conceptid CONCEPTID [CONCEPTID ...]
                        List of concept identifiers to add
```

**Example**:
Create a new Snapshot with one concept (74400008):

```bash
(scttoowl) > RF2Filter /home/data/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot /home/data/test/Snapshot -i -c 74400008
Build transitive closure
Processing /Users/data/data/terminology/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot/Terminology/sct2_Relationship_Snapshot_INT_20160731.txt
Filtering files
Processing /Users/data/data/terminology/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot/Terminology/sct2_Relationship_Snapshot_INT_20160731.txt
Processing /Users/data/data/terminology/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot/Terminology/sct2_StatedRelationship_Snapshot_INT_20160731.txt
Processing /Users/data/data/terminology/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot/Terminology/sct2_Concept_Snapshot_INT_20160731.txt
Processing /Users/data/data/terminology/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot/Terminology/sct2_Description_Snapshot-en_INT_20160731.txt
Processing /Users/data/data/terminology/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot/Terminology/sct2_TextDefinition_Snapshot-en_INT_20160731.txt
Processing /Users/data/data/terminology/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot/Refset/Language/der2_cRefset_LanguageSnapshot-en_INT_20160731.txt
```

Add concepts 135007 and 122868007 to the output list:

```bash
(scttoowl) >
RF2Filter /home/data/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot /home/data/test/Snapshot -c 135007 122868007
   ...
```

Extract all of the concepts that are used to define `75570004 | Viral pneumonia |`:

```bash
(scttoowl) >
RF2Filter /home/data/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot /home/data/test/vp -a -i -c 75570004 --children
     ...
``` 

## SNOMEDToOWL
SNOMEDToOWL takes a set of RF2 Snapshot files and generates the OWL equivalent according to the <u>Representation of SNOMED in OWL</u>  specification

**Usage:** SNOMEDToOWL [-h] [-o OUTPUT] [-f FORMAT] indir config

```text

positional arguments:
  indir                 Input directory - typically SNOMED CT Snapshot root
  config                Configuration file name

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file (Default: stdout)
  -f FORMAT, --format FORMAT
                        Output format (Default: turtle
```

### Example

```bash

(scttoowl) > curl https://raw.githubusercontent.com/hsolbrig/SNOMEDToOWL/master/test/conf/en_all_intl.json > en_all_intl.json

(scttoowl) > SNOMEDToOWL /home/data/test/Snapshot en_all_intl.json -o output.ttl

Creating transitive relationships
Processing RF2 files
Processing der2_cRefset_LanguageSnapshot-en_INT_20160731.txt
Processing sct2_Concept_Snapshot_INT_20160731.txt
Processing sct2_Description_Snapshot-en_INT_20160731.txt
Processing sct2_StatedRelationship_Snapshot_INT_20160731.txt
Processing sct2_TextDefinition_Snapshot-en_INT_20160731.txt
Generating OWL concepts
Generating OWL properties
Writing output.ttl
```
### Configuration File

The SNOMEDToOWL configuration file defines additional parameters that aren't currently available in the SNOMED CT RF2 release.  These parameters consist of:

| **Name** | **Function** | **Example** |
|:----|:--------|:-------|
|  MODULE    | Identifier of the module to be transformed. Concepts defined in this module are converted to OWL.  Forms the `owl:ontology` URI.   | 900000000000207008  |
| VERSION    |  The ontology version identifier. Forms the `owl:versionIRI` in combination with MODULE  |         20160131 |
| VERSION_DESCRIPTION   |   Short description of the ontology  version, that becomes the `owl:versionInfo`    |  "International Release, Core Module, Release Date: 20160131" |
| LANGUAGES | List of Language Refset Identifiers to be included in the OWL representation | [900000000000509007, 900000000000508004] |
| LANGUAGE_MAP | Map from Language Identifier to [BCP-47 Tags for Identifying Languages](https://tools.ietf.org/html/bcp47) | {"900000000000509007" : "en-us",  "900000000000508004" : "en-gb} |
| MODULE_LABEL | label for owl ontology | "SNOMED Clinical Terms, International Release, Stated Relationships in OWL RDF" |
| MODULE_DESCRIPTION | Description of owl ontology |  "Generated as OWL RDF/XML from SNOMED CT release files" |
| MODULE_COPYRIGHT | Copyright notice to include in ontology header | "Copyright 2016 The International Health Terminology Standards Development Organisation (IHTSDO).", "All Rights Reserved. SNOMED CT was originally created by The College of American Pathologists. \"SNOMED\" and", ' "SNOMED CT" are registered trademarks of the IHTSDO.  SNOMED CT has been created by combining SNOMED RT', ... "Licence. Details of the SNOMED CT Affiliate Licence may be found at www.ihtsdo.org/our-standards/licensing/" |
| NEVER_GROUPED | List of SCT attributes that (should) never appear in a role group | [123005000, 272741003, 127489000, 411116001] |
| RIGHT_ID | A list of "right identities", in the form `{"p11": p12}, ..., {"pn1":pn2}` that are mapped to an `owl:propertyChain` axiom in the form `p1 ∘ p2 SubPropertyOf p1`  .  The example represents the assertion: `'Direct substance (attribute)' ∘ 'Has active ingredient (attribute)' SubPropertyOf 'Direct substance (attribute)'` | { "363701004": 127489000 } |
| USE_STATED_RELATIONSHIPS | If `true` or absent, use the stated relationships file.  If `false`, use the (inferred) relationships file | false |

