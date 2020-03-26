from typing import Dict, Set

from .RF2File import RF2File
from .Transitive import Transitive
from SNOMEDCTToOWL.TransformationContext import TransformationContext
from SNOMEDCTToOWL.SNOMEDToOWLConstants import *


class Relationship:
    """ A RF2 stated relationship or relationship entry

    Properties:
        * sourceId -- concept identifier of the subject
        * typeId -- concept identifier of the predicate (if not IS a)
        * destinationId -- concept identifier of the target
        * relationshipGroup -- group the assertion belongs to

    Filters:
        * active -- only active relationships (active=='1') are included
        * characteristicTypeId -- only descendants of 900000000000006009 |Defining relationship| (stated, inferred)
                                are included in the transformation.
        * moduleId --  NOT used as a filter because fully defined definitions have to be complete to be valid
        * modifierId -- only the existential modifier, 900000000000451002 |Some|, is included in the transformation
    """

    def __init__(self, row):
        self.sourceId = int(row["sourceId"])
        self.destinationId = int(row["destinationId"])
        self.typeId = int(row["typeId"])
        self.relationshipGroup = int(row["relationshipGroup"])


class Relationships(RF2File):
    relationship_prefix = RelationshipFilePrefix

    def __init__(self):
        self._parents = {}          # Dict[sourceId, Set[destinationId]
        self._entries = {}          # Dict[sourceId, Dict[relationshipGroup, Set[Relationship]]

    @classmethod
    def filtr(cls, fname: str, context: TransformationContext) -> bool:
        return fname.startswith(Relationships.relationship_prefix)

    def add(self, row: Dict, _: TransformationContext, transitive: Transitive) -> None:
        """
        Add an RF2 relationship or statedrelationship row
        :param row: row to add -- already tested for active
        :param _: unused
        :param transitive: Transitive relationship closure
        """
        sourceid = int(row['sourceId'])
        relid = int(row['characteristicTypeId'])
        if not transitive.is_descendant_of(relid, Additional_relationship_sctid) and \
           not transitive.is_descendant_of(relid, Qualifying_relationship_scitd) and \
           int(row['modifierId']) == Some_sctid:
            if int(row['typeId']) == Is_a_sctid:
                self._parents.setdefault(sourceid, set()).add(int(row['destinationId']))
            else:
                self._entries.setdefault(sourceid, {})\
                    .setdefault(int(row['relationshipGroup']), set())\
                    .add(Relationship(row))

    def parents(self, concept: SCTID) -> Set[SCTID]:
        """
        Return the direct parents of the concept.  Only assertions in the relationship file are returned
        :param concept: child concept
        :return: set of parents
        """
        return self._parents.get(concept, set())

    def groups(self, concept: SCTID) -> Dict[int, Set[Relationship]]:
        """
        Return a dictionary that maps relationship group identifier to a set of Relationship entries
        :param concept: source councept identifier
        :return: dictionary, key = relationship group (int), data = Set(Relationship)
        """
        return self._entries.get(concept, {})
