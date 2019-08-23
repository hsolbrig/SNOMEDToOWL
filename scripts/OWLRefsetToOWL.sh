#! /usr/bin/bash
# Note: Join assumes the file is sorted
# Run this in an RF2 SNOMED Snapshot/Terminology directory
OWLFILE=sct2_sRefset_OWLExpressionSnapshot_*.txt
DESCFILE=sct2_Description_Snapshot-*.txt
CIDFILE=$(mktemp)
RAWOWLFILE=$(mktemp)

for OWLFILE in sct2_sRefset_OWLExpressionSnapshot_*.txt; do
  [ -e "$OWLFILE" ] || continue

  for DESCFILE in sct2_Description_Snapshot-*.txt; do
    [ -e "$DESCFILE" ] || continue

    # Extract all the OWL -- only works on Snapshot
    # field 3 is active flag, field 7 is actual OWL
    cut -f3,7 $OWLFILE | grep ^1 | cut -f2 > $RAWOWLFILE

    # 1: Emit prefixes
    grep ^Prefix $RAWOWLFILE
    # 2: Emit ontology header (sans closing paren)
    #    Note: This assumes only ONE paren -- '$' doesn't work on Mac sed
    grep -h ^Ontology $RAWOWLFILE | sed "s/)//"
    # 3: Emit everything else
    grep -v ^Ontology $RAWOWLFILE | grep -v ^Prefix

    # Add FSNs
    # Extract all of the active concept identifiers
    cut -f3,6 $OWLFILE | grep ^1 | cut -f2 | sort > $CIDFILE
    # We also need the root concept, which is NOT the subject of any refset entries
    echo "138875005" >> $CIDFILE
    # 1       2          *3*     4         *5*         *6*     *7*     *8*       9
    # id effectiveTime active moduleId conceptId languageCode typeId term caseSignificanceId
    cut -f3,5-8 $DESCFILE | grep ^1 | cut -f2-5 | grep "\t900000000000003001\t" | cut -f1,2,4 | sort | sed 's/\"/\\\"/g' | join - $CIDFILE | sed "s/^\([^ ]*\) \([^ ]*\) \(.*\)/AnnotationAssertion(rdfs:label :\1 \"\3\"@\2)/"

    # Emit closing bracket
    echo ")"
    rm $CIDFILE $RAWOWLFILE
  done
done
