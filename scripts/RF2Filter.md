# RF2Filter
The purpose of RF2Filter is to create a subset of an RF2 Snapshot for testing purposes.

RF2Filter takes a list of SNOMED CT concept identifiers and a directory containing RF2 Snapshot files an transfers all of the rows in the RF2 files that describe or define the listed concepts into a corresponding list of RF2 files in a target directory.


**usage**: RF2Filter [-h] [-i] [-a] [-c] [-d] indir outdir [conceptid [conceptid ...]]

```text
Extract selected SNOMED-CT RF2 concepts

positional arguments:
  indir              Location of existing RF2 Snapshot directory
  outdir             Target directory for filtered RF2 content
  conceptid          List of concept identifiers to extract

optional arguments:
  -h, --help         show this help message and exit
  -i, --init         Initialize the target output files
  -a, --ancestors    Add touched concept ancestors
  -c, --children     Add direct children of selected concepts
  -d, --descendants  Add children, children of children, etc of selected
                     concepts```
```

**Example**:
Create a new Snapshot with one concept (74400008):

```bash
(scttoowl) > RF2Filter -i /home/data/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot localsnapshot 74400008
Build transitive closure list
Processing /home/data/data/terminology/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot/Terminology/sct2_Relationship_Snapshot_INT_20160731.txt
Filtering files
Processing /home/data/data/terminology/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot/Terminology/sct2_Relationship_Snapshot_INT_20160731.txt
Processing /home/data/data/terminology/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot/Terminology/sct2_StatedRelationship_Snapshot_INT_20160731.txt
Adding 202 concepts
Processing /home/data/data/terminology/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot/Terminology/sct2_Concept_Snapshot_INT_20160731.txt
Processing /home/data/data/terminology/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot/Terminology/sct2_Description_Snapshot-en_INT_20160731.txt
Processing /home/data/data/terminology/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot/Terminology/sct2_TextDefinition_Snapshot-en_INT_20160731.txt
Processing /home/data/data/terminology/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot/Refset/Language/der2_cRefset_LanguageSnapshot-en_INT_20160731.txt
```

Add concepts 135007 and 122868007 to the output:

```bash
(scttoowl) >
RF2Filter /home/data/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot /home/data/test/Snapshot localsnapshot 135007 122868007
   ...
```

Extract all of the concepts that are used to define `75570004 | Viral pneumonia |`:

```bash
(scttoowl) >
RF2Filter -i -a -c /home/data/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot pheumoniaSnapshot 75570004
     ...
``` 

Extract all of concepts in the neighborhood of `74400008 | Appendicitis |` and its descendants:

```bash
(scttoowl) >
RF2Filter -i -a -c -d /home/data/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot appendicitisSnapshot 74400008 
     ...
``` 