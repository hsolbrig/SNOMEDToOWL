

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
