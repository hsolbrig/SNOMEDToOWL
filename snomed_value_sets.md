# Process for creating SNOMED Subsets from simple lists

The task:  Take a list of SNOMED CT concept codes such as [test/data/Dicom_Subset_20170131_v1_00.csv]() and produce the
following artifacts:

1) A minimal hierarchical list of concept codes that represents this list's relative position within SNOMED itself.  As
an example, [129509006 | Glutamate (13-N) (substance) |](http://snomed.info/id/129509006) and
 [129512009 | Carbon (11-C) raclopride (substance) |](http://snomed.info/id/129512009) would both appear as siblings
 under the first proximal shared parent ([89457008 | Radioactive isotope (substance) |](http://snomed.info/9457008))
 
 
+ ([89457008 | Radioactive isotope (substance) |](http://snomed.info/9457008))
  + [129512009 | Carbon (11-C) raclopride (substance) |](http://snomed.info/id/129512009)
  + [129509006 | Glutamate (13-N) (substance) |](http://snomed.info/id/129509006)

We will need to decide which labeling to associate with them (FSN, maybe?) (Preferred name?)

2) 
       