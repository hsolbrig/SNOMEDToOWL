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
from typing import Callable, Dict

from SNOMEDCTToOWL.RF2Files.RF2DictWriter import RF2DictWriter


class DirectoryWalker:
    def __init__(self, indir: str, outdir: str, init: bool):
        """
        Directory walking utility
        :param indir: directory root to walk from
        :param outdir: output directory root to walk to
        :param init: If true, remove existing content in output files
        """
        self._indir = indir if indir.endswith(os.path.sep) else indir + os.path.sep
        self._outdir = outdir if outdir.endswith(os.path.sep) else outdir + os.path.sep
        self._init = init

    def walk(self, filtr: Callable[[str], bool], processor: Callable[[Dict], bool]) -> None:
        """
        Walk the directory testing the file against filtr and invoking processor with contents if true
        :param filtr: file name tester
        :param processor: content row processor
        """
        for filedir, _, files in os.walk(self._indir):
            for file in files:
                if filtr(file):
                    print("Processing %s" % os.path.join(filedir, file))
                    with open(os.path.join(filedir, file)) as f:
                        reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
                        with self._create_writer(filedir, file, reader) as writer:
                            for row in reader:
                                if processor(row):
                                    writer.writerow(row)

    def _create_writer(self, filedir, file, inreader: csv.DictReader) -> RF2DictWriter:
        outdir = filedir.replace(self._indir, self._outdir)
        os.makedirs(outdir, exist_ok=True)
        output_file = os.path.join(filedir.replace(self._indir, self._outdir), file)
        is_new = self._init or not os.path.exists(output_file)
        writer = RF2DictWriter(open(output_file, 'w' if is_new else 'a'),
                               fieldnames=inreader.fieldnames, dialect=csv.excel_tab)
        if is_new:
            writer.writeheader()
        return writer
