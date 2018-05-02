from typing import Dict, Set
from SNOMEDCTToOWL.SNOMEDToOWLConstants import RelationshipFilePrefix


class Transitive:
    relationship_prefix = RelationshipFilePrefix

    def __init__(self):
        self._children = {}         # parent -> set(children) Dict[int, Set[int]]
        self._parents = {}          # child -> set(parents)   Dict[int, Set[int]]
        self.__desc_cache = {}      # parent -> set(descendants)
        self.__ancestor_cache = {}  # child -> set(ancestors)

    @classmethod
    def filtr(cls, fname: str) -> bool:
        """
        Return true if this is a computed relationship file.  Transitivity is always based on computed
        :param fname: file name to test
        :return: true if it should be processed
        """
        return fname.startswith(cls.relationship_prefix)

    def add(self, row: Dict) -> None:
        """
        Add an RF2 relationship row to the Transitive file
        :param row: row to add -- already tested for active
        """
        child = int(row["sourceId"])
        parent = int(row["destinationId"])
        self._children.setdefault(parent, set()).add(child)
        self._parents.setdefault(child, set()).add(parent)

    def descendants_of(self, parent: int) -> Set[int]:
        """
        Return all descendants of parent
        :param parent: parent concept
        :return: set of concepts
        """
        return self._children.get(parent, set())\
            .union(*[self.descendants_of(x) for x in self._children.get(parent, set())])

    def is_descendant_of(self, desc: int, parent: int) -> bool:
        """
        Determine whether desc is a descendant of parent
        :param desc: descendant to test
        :param parent: parent concept
        :return: True or False
        """
        if parent not in self.__desc_cache:
            self.__desc_cache[parent] = self.descendants_of(parent)
        return desc in self.__desc_cache[parent]

    def is_descendant_or_self_of(self, desc: int, parent: int) -> bool:
        """
        Determine whether desc is a descendant of the parent or is the parent itself
        :param desc: descendant to test
        :param parent: parent concept
        :return: True or False
        """
        return self.is_descendant_of(desc, parent) or desc == parent

    def ancestors_of(self, child: int) -> Set[int]:
        return self._parents.get(child, set())\
            .union(*[self.ancestors_of(x) for x in self._parents.get(child, set())])

    def is_ancestor_of(self, ancestor: int, child: int) -> bool:
        if child not in self.__ancestor_cache:
            self.__ancestor_cache[child] = self.ancestors_of(child)
        return ancestor in self.__ancestor_cache[child]
