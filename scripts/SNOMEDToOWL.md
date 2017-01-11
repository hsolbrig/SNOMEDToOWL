# SNOMEDToOWL
SNOMEDToOWL takes a set of RF2 Snapshot files and generates the OWL equivalent according to the [Representation of SNOMED in OWL](https://confluence.ihtsdotools.org/display/mag/Representation+of+SNOMED+in+OWL.v0.1) specification.

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

## Example
In the following example, we pull the ```sct_core_us_gb.json``` configuration file from the github site, which generates the stated core module from SNOMED CT International, assuming 20160731 distribution. We then run it against an RF2 snapshot directory which, in this example, is in ```/home/data/test/Snapshot```.

```bash

(scttoowl) > curl https://raw.githubusercontent.com/hsolbrig/SNOMEDToOWL/master/SNOMEDCTToOWL/conf/sct_core_us_gb.json > sct_core_us_gb.json

(scttoowl) > SNOMEDToOWL /home/data/test/Snapshot sct_core_us_gb.json -o output.ttl

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
## Configuration File

The SNOMEDToOWL configuration file defines additional parameters that aren't currently available in the SNOMED CT RF2 release.  These parameters consist of:

| **Name** | **Function** | **Example** |
|:----|:--------|:-------|
|  MODULE    | Identifier of the module to be transformed. Concepts defined in this module are converted to OWL.  Forms the `owl:ontology` URI.   | 900000000000207008 410662002  |
| VERSION    |  The ontology version identifier. Forms the `owl:versionIRI` in combination with MODULE  |         20160131 |
| VERSION_DESCRIPTION   |   Short description of the ontology  version, that becomes the `owl:versionInfo`    |  "International Release, Core Module, Release Date: 20160131" |
| LANGUAGES | List of Language Refset Identifiers to be included in the OWL representation | [900000000000509007, 900000000000508004] |
| LANGUAGE_MAP | Map from Language Identifier to [BCP-47 Tags for Identifying Languages](https://tools.ietf.org/html/bcp47) | {"900000000000509007" : "en-us",  "900000000000508004" : "en-gb} |
| MODULE_LABEL | label for owl ontology | "SNOMED Clinical Terms, International Release, Stated Relationships in OWL RDF" |
| MODULE_DESCRIPTION | Description of owl ontology |  "Generated as OWL RDF/XML from SNOMED CT release files" |
| MODULE_COPYRIGHT | Copyright notice to include in ontology header | "Copyright 2016 The International Health Terminology Standards Development Organisation (IHTSDO).", "All Rights Reserved. SNOMED CT was originally created by The College of American Pathologists. \"SNOMED\" and", ' "SNOMED CT" are registered trademarks of the IHTSDO.  SNOMED CT has been created by combining SNOMED RT', ... "Licence. Details of the SNOMED CT Affiliate Licence may be found at www.ihtsdo.org/our-standards/licensing/" |
| NEVER_GROUPED | List of SCT attributes that (should) never appear in a role group | [123005000, 272741003, 127489000, 411116001] |
| RIGHT_ID | A list of "right identities", in the form `{"p11": p12}, ..., {"pn1":pn2}` that are mapped to an `owl:propertyChain` axiom in the form `p1 ∘ p2 SubPropertyOf p1`  .  The example represents the assertion: `'Direct substance (attribute)' ∘ 'Has active ingredient (attribute)' SubPropertyOf 'Direct substance (attribute)'` | { "363701004": 127489000 } |
| USE_STATED_RELATIONSHIPS | If `true`, use the stated relationships file.  If `false`, use the (inferred) relationships file | false |
| SKOS_DESCRIPTIONS | If `true`, emit skos:prefLabel, skos:altLabel and skos:definition instead of sctf:Description.<lang>.preferred, sctf:Description.<lang>.synonym and sctf:TextDefinition.<lang> and put the full lang code (e.g. en-US) on the literal instead of just "en"




