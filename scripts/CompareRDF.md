# CompareRDF
CompareRDF is used to compare two RDF/OWL files.  Its primary purpose is to verify that the output of the "Spackman OWL script" and a third party conversion utility (e.g. SNOMEDToOWL) produce the same results.

## Usage

```text
CompareRDF [-h]
                  [-f1 {trig,nquads,hturtle,rdfa1.1,json-ld,trix,nt,xml,html,mdata,rdfa1.0,n3,microdata,rdfa,turtle}]
                  [-f2 {trig,nquads,hturtle,rdfa1.1,json-ld,trix,nt,xml,html,mdata,rdfa1.0,n3,microdata,rdfa,turtle}]
                  [-p] [-nh]
                  file1 file2

Compare two OWL RDF files

positional arguments:
  file1                 RDF File 1
  file2                 RDF File 2

optional arguments:
  -h, --help            show this help message and exit
  -f1 {trig,nquads,hturtle,rdfa1.1,json-ld,trix,nt,xml,html,mdata,rdfa1.0,n3,microdata,rdfa,turtle}
                        File 1 format
  -f2 {trig,nquads,hturtle,rdfa1.1,json-ld,trix,nt,xml,html,mdata,rdfa1.0,n3,microdata,rdfa,turtle}
                        File 2 format
  -p                    Print progress and timing information
  -nh, --noheader       Omit ontology header comparison
```

## Example:
The following example:

1. Uses RF2Filter to extract concept ```74400008 | Appendicitis |``` and its neighborhood into a local RF2 directory
2. Uses the [modified Spackman perl script](modifiedPerlScript.pl) to generate an output (snomedct_owl.owl) for comparison.
3. Uses [SNOMEDToOWL](SNOMEDToOWL.md) to generate an equivalent according to the official transformation rules.
4. Compares the outputs ignoring the header information.

```bash
> RF2Filter -i -a -c -d ~/data/terminology/SNOMEDCT/SnomedCT_RF2Release_INT_20160731/Snapshot appendicitisSnapshot 74400008
Build transitive closure list
     ...
> modifiedPerlScript.pl appendicitisSnapshot OWL
# Number of arguments: 2
[INFO] Two arguments passed. Assuming they are format and Snapshot folder location
[INFO] Processing files in location : appendicitisSnapshot/Terminology
[INFO] Using file : sct2_Concept_Snapshot_INT_20160731.txt for Concepts
[INFO] Using file : sct2_Description_Snapshot-en_INT_20160731.txt for Descriptions
[INFO] Using file : sct2_StatedRelationship_Snapshot_INT_20160731.txt for Stated Relationships
[INFO] Using file : sct2_TextDefinition_Snapshot-en_INT_20160731.txt for Text Definitions
[INFO] Processing files in location : appendicitisSnapshot/Refset/Language
[INFO] Using file : der2_cRefset_LanguageSnapshot-en_INT_20160731.txt for Language Refset
> curl https://raw.githubusercontent.com/hsolbrig/SNOMEDToOWL/master/SNOMEDCTToOWL/conf/sct_core_us.json > sct_core_us.json
> SNOMEDToOWL appendicitisSnapshot sct_core_us.json -o appendicitis.ttl
Creating transitive relationships
Processing RF2 files
Processing der2_cRefset_LanguageSnapshot-en_INT_20160731.txt
Processing sct2_Concept_Snapshot_INT_20160731.txt
Processing sct2_Description_Snapshot-en_INT_20160731.txt
Processing sct2_StatedRelationship_Snapshot_INT_20160731.txt
Processing sct2_TextDefinition_Snapshot-en_INT_20160731.txt
Generating OWL concepts
Generating OWL properties
Adding localized descriptions
Writing appendicitis.ttl
> CompareRDF -f1 xml -f2 turtle snomedct_owl.owl appendicitis.ttl
      ...
```