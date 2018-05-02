from typing import Dict

from .Transitive import Transitive
from SNOMEDCTToOWL.TransformationContext import TransformationContext


class RF2File:
    prefix = None

    @classmethod
    def filtr(cls, fname: str, context: TransformationContext) -> bool:
        """
        Return true if fname is a valid instance of the file for the target type
        :param fname: file name (no directory)
        :param context: transformation context variables
        :return: True if fname is RF2 file of given type
        """
        return cls.prefix and fname.startswith(cls.prefix)

    def add(self, row: Dict, context: TransformationContext, transitive: Transitive) -> None:
        """
        Add RF2 entry row if needed
        :param row: RF2 row to add
        :param context: transformation context
        :param transitive: transitive file for parent checks
        """
        return
