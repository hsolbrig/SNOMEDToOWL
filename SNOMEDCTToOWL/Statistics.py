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
#     Neither the name of the <ORGANIZATION> nor the names of its contributors
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


class Statistics:
    def __init__(self):
        self.num_concepts = self.stat_var()
        self.num_properties = self.stat_var()
        self.num_labels = self.stat_var()
        self.num_prefnames = self.stat_var()
        self.num_synonyms = self.stat_var()
        self.num_definitions = self.stat_var()
        self.num_subclassof = self.stat_var()
        self.num_equivalentclass = self.stat_var()
        self.num_rolegreoups = self.stat_var()
        self.num_ungrouped = self.stat_var()
        self.num_propchains = self.stat_var()

    class stat_var:
        def __init__(self):
            self.v = 0

        def inc(self):
            self.v += 1

        def __str__(self):
            return str(self.v)

    def __str__(self):
        return '\t' + '\n\t'.join(["{}: {}".format(k.replace("num_", "").capitalize(), self.__dict__[k]) for
                                   k in sorted(self.__dict__.keys())])
