# Copyright (c) 2016, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the Mayo Clinic nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
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
