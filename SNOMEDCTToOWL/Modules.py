import csv
import os
import sys
from argparse import ArgumentParser, Namespace
from typing import Dict, Callable, NamedTuple, List, Optional

from SNOMEDCTToOWL.RF2Files.DirectoryWalker import DirectoryWalker
from SNOMEDCTToOWL.SNOMEDToOWL import RelationshipFilePrefix, OWLRefsetFilePrefix, ConceptFilePrefix, \
    DescriptionFilePrefix, TextDefinitionFilePrefix, LanguageFilePrefix, Fully_specified_name_sctid, \
    ModuleDependencyFilePrefix1, ModuleDependencyFilePrefix2


class ModuleVersion(NamedTuple):
    module: str
    version: str


class RF2ModuleFilter:
    def __init__(self, opts: Namespace):
        self._opts = opts                       # user options
        self._walker = DirectoryWalker(opts.indir, '', False)
        self.modules: Dict[str, str] = {}
        self.dependencies: Dict[ModuleVersion, List[ModuleVersion]] = {}
        self.walk_dependencies()
        self.walk_files()           # Pass over requested concepts adding
        self.process_results()

    def walk(self, filtr: Callable[[str], bool], processor: Callable[[Dict], bool]) -> None:
        """
        Walk the directory testing the file against filtr and invoking processor with contents if true
        :param filtr: file name tester
        :param processor: content row processor
        """
        for filedir, _, files in os.walk(self._opts.indir):
            for file in files:
                if filtr(file):
                    if self._opts.verbose:
                        print("Processing %s" % os.path.join(filedir, file))
                    with open(os.path.join(filedir, file)) as f:
                        reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
                        for row in reader:
                            if row['active'] == '1':
                                processor(row)

    def walk_dependencies(self):
        self.walk(lambda file: file.startswith(ModuleDependencyFilePrefix1) or
                               file.startswith(ModuleDependencyFilePrefix2),
                  lambda row: self._procdeprow(row))

    def _procdeprow(self, row: Dict[str, str]) -> bool:
        self.dependencies.setdefault(ModuleVersion(row['moduleId'], row['sourceEffectiveTime']), []).\
            append(ModuleVersion(row['referencedComponentId'], row['targetEffectiveTime']))
        return False

    def walk_files(self) -> None:
            self.walk(lambda file:
                      file.startswith(RelationshipFilePrefix) or
                      file.startswith(ConceptFilePrefix) or
                      file.startswith(DescriptionFilePrefix) or
                      file.startswith(TextDefinitionFilePrefix) or
                      file.startswith(LanguageFilePrefix) or
                      file.startswith(OWLRefsetFilePrefix),
                      lambda row: self._procrow(row))

    def _procrow(self, row: Dict) -> bool:
        module = row['moduleId']
        if module not in self.modules:
            self.modules[module] = ''
        return False

    def process_results(self) -> None:
        self.walk(lambda file: file.startswith(DescriptionFilePrefix), lambda row: self._map_desc(row))

    def _map_desc(self, row: Dict) -> bool:
        module_cid = row['conceptId']
        if module_cid in self.modules and int(row['typeId']) == Fully_specified_name_sctid:
            self.modules[module_cid] = row['term']
            return True
        return False

    def description_of(self, modversion: ModuleVersion) -> str:
        modname = self.modules.get(modversion.module, 'NAME UNKNOWN')
        return f"{modversion.module}({modversion.version if modversion.version else 'No Version'}):" \
               f" {modname if modname else 'UNDEFINED'}"


def genargs() -> ArgumentParser:
    """
    Generate an input string parser
    :return: parser
    """
    parser = ArgumentParser("List unique module identifiers from RF2 files")
    parser.add_argument("indir", help="RF2 base directory - typically path to Snapshot'")
    parser.add_argument("-v", "--verbose", help="List files being processed", action="store_true")
    return parser


def main(argv: Optional[List[str]] = None):
    opts = genargs().parse_args(argv)

    if not os.path.isdir(opts.indir):
        print("Input directory {} doesn't exist".format(opts.indir), file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(os.path.join(opts.indir, "Terminology")) or \
       not os.path.isdir(os.path.join(opts.indir, "Refset")):
        print("Input directory {} is not an RF2 directory".format(opts.indir))
        sys.exit(1)

    modules = RF2ModuleFilter(opts)
    for module, name in modules.modules.items():
        print(f"{module}: {name}")
    for modversion, dependencies in modules.dependencies.items():
        print()
        print(f"{modules.description_of(modversion)} requires:")
        for dependency in dependencies:
            print(f"\t{modules.description_of(dependency)}")

