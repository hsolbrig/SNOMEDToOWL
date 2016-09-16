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
import csv
import os


class RF2Filter:
    def proc_directory(self, directory: str) -> None:

        print("Creating transitive file")
        for subdir, _, files in os.walk(directory):
            for file in files:
                self._proc_transitive_file(file, subdir)

        print("Creating concepts list")
        for subdir, _, files in os.walk(directory):
            for file in files:
                if Concepts.filtr(file, self._context)
                self._proc_file(file, subdir, self._concepts) or \
                    self._proc_file(file, subdir, self._descriptions) or \
                    self._proc_file(file, subdir, self._languages) or \
                    self._proc_file(file, subdir, self._relationships)

# Accept a list of concepts, two directories (one for originals, one for target), an initialize flag, and a
# transitive flag
# Load the original files
# Open/create the target files (clear if initalize flag)
# For each concept in the list of concepts:
#   Add concept to target
#   Add all descriptions / definitions / language entries
#   Add all relationship entries where concept is the subject
#   For each typeId concept:
#       Add concept and FSN
#       If transitive, add ancestor concepts and FSN's
#   For each destinationId concept:
#       Add concept and FSN
#       If transitive, add ancestor concepts and FSN'1
