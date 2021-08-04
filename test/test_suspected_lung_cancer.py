import os
import unittest

# This test assumes that there is a Dicom csv and a Snapshot directory in test/data/dicom
from rdflib import Graph, URIRef, RDF, OWL, RDFS

from SNOMEDCTToOWL.RF2Filter import main as rf2main
from SNOMEDCTToOWL.SNOMEDToOWL import main as owlmain
from SNOMEDCTToOWL.SNOMEDToOWLConstants import ConceptFilePrefix, Concept_model_attribute_sctid, SCT, \
    Concept_model_data_attribute_sctid, Concept_model_object_attribute_sctid

cwd = os.path.dirname(__file__)
data_dir = os.path.join(cwd, 'data', 'slc')
snomed_dir = os.path.join(data_dir, 'Snapshot')
terminology_dir = os.path.join(snomed_dir, 'Terminology')
output_dir = os.path.join(data_dir, 'output')
conf_file = os.path.join(data_dir, 'conf.json')
owl_file = os.path.join(output_dir, 'slc.owl')

datap_root = SCT[str(Concept_model_data_attribute_sctid)]
objectp_root = SCT[str(Concept_model_object_attribute_sctid)]

# True means redo the RF2 filter output
FORCE_REGEN = False

class SuspectedLungCancerIssueTest(unittest.TestCase):
    """ When we load the neighborhood of Suspected Lung Cancer (162573006) from the July 2021 distribution,
    We don't pick up all of the object properties (example: 410662002)
    """
    def test_filter(self):
        self.assertTrue(os.path.exists(snomed_dir) and os.path.exists(os.path.join(snomed_dir, 'Terminology')),
                        msg=f"You have to link {snomed_dir} to "
                            f"SnomedCT_InternationalRF2_PRODUCTION_20210731T120000Z/Snapshot (or later)")
        regen_needed = True
        if os.path.exists(terminology_dir):
            for fn in os.listdir(terminology_dir):
                if fn.startswith(ConceptFilePrefix):
                    regen_needed = False
                    break
        if regen_needed or FORCE_REGEN:
            print(f"Regenerating {output_dir}")
            rf2main(["-i", "-a", "-d", snomed_dir, output_dir, "162573006"])
        owlmain([output_dir, conf_file, "-o", owl_file])
        ontology = Graph()
        ontology.load(owl_file, format="turtle")
        subjs = [s for s in ontology.subjects() if isinstance(s, URIRef)]
        self.assertNotIn(SCT[str(Concept_model_attribute_sctid)], subjs,
                         msg="Object/DatatypeProperty root should never be emitted")
        self.assertIn(datap_root, subjs,
                      msg = "Concept model data attribute should be the root of the DataProperty branch")
        self.assertIn(objectp_root, subjs,
                      msg = "Concept model object attribute should be the root of the ObjectProperty branch")
        # sct:762705008 a owl:ObjectProperty ;
        #     rdfs:label "Concept model object attribute (attribute)"@en .
        self.assertEqual(OWL.ObjectProperty, ontology.value(objectp_root, RDF.type, any=False))
        self.assertIn("Concept model object attribute", str(ontology.value(objectp_root, RDFS.label, any=False)))
        # sct:762706009 a owl:DatatypeProperty ;
        #     rdfs:label "Concept model data attribute (attribute)"@en ;
        #     skos:prefLabel "Concept model data attribute"@en-GB,
        #         "Concept model data attribute"@en-US .
        self.assertEqual(OWL.DatatypeProperty, ontology.value(datap_root, RDF.type, any=True))
        self.assertIn("Concept model data attribute", str(ontology.value(datap_root, RDFS.label, any=False)))


if __name__ == '__main__':
    unittest.main()
