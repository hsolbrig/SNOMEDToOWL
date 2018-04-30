import csv


class RF2DictWriter(csv.DictWriter):
    """
    DictWriter wrapper with "with" idiom to close the output file
    """
    def __init__(self, f, *args, **argv):
        self._f = f
        csv.DictWriter.__init__(self, f, *args, **argv)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._f.close()
