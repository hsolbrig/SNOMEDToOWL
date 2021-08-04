import os
import unittest



# This test assumes that there is a Dicom csv and a Snapshot directory in test/data/dicom
from SNOMEDCTToOWL.RF2Filter import main

cwd = os.path.dirname(__file__)
data_dir = os.path.join(cwd, 'data')
snomed_dir = os.path.join(data_dir, 'dicom', 'Snapshot')
output_dir = os.path.join(data_dir, 'dicom', 'output')
concept_list = os.path.join(data_dir, 'dicom', 'Dicom_Subset_20170131_v1_00.csv')


class DicomListTestCase(unittest.TestCase):
    @unittest.skip("This test was never completely finished")
    def test_dicom(self):
        main([snomed_dir, output_dir, "-i", "-a", "-f", concept_list])
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
