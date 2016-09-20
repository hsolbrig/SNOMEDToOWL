# SNOMED CT to OWL testbed  (Under Construction)

A toolkit for generating test RF2  cases for SNOMED CT to OWL  converters and a testing kit for conversions.

## Installation

## RF2Filter
The purpose of RF2Filter is to create a subset of an RF2 Snapshot for testing purposes.

RF2Filter takes a list of SNOMED CT concept identifiers and a directory containing RF2 Snapshot files an transfers all of the rows in the RF2 files that describe or define the listed concepts into a corresponding list of RF2 files in a target directory.


**usage**: RF2Filter indir outdir  [-h] [-i] -c CONCEPTID [CONCEPTID ...] 

```
positional arguments:
  indir                Input directory
  outdir               Output directory

optional arguments:
  -h, --help            show this help message and exit
  -i, --init            Initialize the target output files
  -c CONCEPTID [CONCEPTID ...], --conceptid CONCEPTID [CONCEPTID ...]
                        List of concept identifiers to add
```

**Example**:
Create a new Snapshot with one concept (74400008):

```
(SNOMEDtoOWL) > RF2Filter /home/data/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot /home/data/test/Snapshot -i -c 74400008
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
```
(SNOMEDtoOWL) >
RF2Filter /home/data/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot /home/data/test/Snapshot -c 135007 122868007
   ...
```

## SNOMEDToOWL
SNOMEDToOWL takes a set of RF2 Snapshot files and generates the OWL equivalent according to the <u>Representation of SNOMED in OWL</u>  specification

**Usage:** SNOMEDToOWL [-h] [-o OUTPUT] [-f FORMAT] indir config

```

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


