#!/usr/local/bin/perl -w
#
#   Copyright (c) 2016 International Health Terminology Standards Development Organisation
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OR ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License
#
#   Version 6.2, Date: 2014-11-21, Author: Kent Spackman
#   OWL API VERSION COMPATIBILITY NOTE: The version of OWL Functional Syntax is that required by OWL API 3.4.2
#	URI :  This version uses the URI specification adopted by IHTSDO. Components with an sctid are identified by:
#          http://snomed.info/id/{sctid}
#          Preferred terms and synonyms are identified by annotation properties according to an extension to the SNOMED CT URI Specification:
#          Original specification is: http://snomed.info/field/{tableName}.{fieldName}
#          Identification of a Preferred Term requires two files and thus two tables, so this structure is inadequate to represent the combination of information from 
#          the Description table and the Language Refset table. The current script uses the following form, as an arbitrary extension of the specification:
#          http://snomed.info/field/{tableName}.{fieldName}.{language-dialect}.{preferred|synonym}
#          The annotation property for a US English Preferred term is: http://snomed.info/field/Description.term.en-us.preferred
#          denoting that this is from the Description file, the term field, and in the US English language refset it is marked with acceptability = preferred.
#          The annotation property for text definitions is http://snomed.info/field/TextDefinition.term
#
# Run the script as "perl <scriptfilename> <arg0> <arg1>" where
#  <scriptfilename> is the name of the file containing this script
#  <arg0> can be KRSS, OWL, or OWLF:
#			KRSS: This produces KRSS2 which is parsable by the OWL API 3.4.2, or by CEL or other classifiers
#			OWL:  This produces the OWL XML/RDF format.
#			OWLF: This produces the OWL functional syntax, parsable by the OWL API 3.4.2
#  <arg1> is the directory containing the RF2 Snapshot subdirectories.
#           If the current directory is RF2/Snapshot, then just use dot (".") to designate the current directory, as in the following example:
# ***  EXAMPLE COMMAND FOR RUNNING THE SCRIPT: >perl tls2_StatedRelationshipsToOwlKRSS_INT_20160731.pl OWLF .
#
#
# Alternatively you can separately supply arguments for all the file names (with their directories if necessary) :
# Run the script as "perl <scriptfilename> <arg0> <arg1> <arg2> <arg3> <arg4> <arg5> <arg6>" where
#  <scriptfilename> is the name of the file containing this script
#  <arg0> can be KRSS, OWL, or OWLF:
#			KRSS: This produces KRSS2 which is parsable by the OWL API 3.4, or by CEL or other classifiers
#			OWL:  This produces the OWL XML/RDF format.
#			OWLF: This produces the OWL functional syntax, parsable by the OWL API 3.4.2
#  <arg1> is the name of the file containing the SNOMED CT RF2 Concepts Table snapshot e.g. sct2_Concept_Snapshot_INT_20160731.txt
#  <arg2> is the name of the file containing the SNOMED CT RF2 Descriptions Table snapshot e.g. sct2_Description_Snapshot_INT_20160731.txt
#  <arg3> is the name of the file containing the SNOMED CT RF2 Stated Relationships Table snapshot, e.g. sct2_StatedRelationship_Snapshot_INT_20160731.txt
#  <arg4> is the name of the file containing the SNOMED CT RF2 Text Definitions Table snapshot, e.g. sct2_TextDefinition_Snapshot-en_INT_20160731.txt
#  <arg5> is the name of the file containing the SNOMED CT RF2 Language Refset snapshot, e.g. der2_cRefset_LanguageSnapshot-en_INT_20160731.txt
#  <arg6> is the name of the output file, which is your choice but could be something like res_StatedOWLF_Core_INT_20160731.owl
#
# It outputs a description logic representation, using either OWL or KRSS syntax.
# KRSS Notes:
#    The KRSS uses "define-primitive-concept" instead of the contracted "defprimconcept", and
#    "define-concept" instead of the contracted "defconcept", and "define-primitive-role" instead
#    of the contracted "defprimrole".
# OWL Notes:
#    The OWL syntax can be either RDF/XML or OWL Functional Syntax.  The OWL sublanguage used (OWL 2 profile) is OWL 2 EL.
# The output files can be imported into an editor such as Protege using the OWL API.
# Tested with OWL API version 3.4.2 in Protege 4.3. 

# The script relies on the hierarchy under 410662002 "Concept model attribute" to specify the role hierarchies.

# The output consists of:
# 1) A set of role definitions
# 2) A set of concept definitions.

use English;
use feature qw(say);

my %fsn;
my %desc;
my %textDefs;
my %prefTerm;
my %acceptability;
my %primitive;
my %parents;
my %children;
my %rels;
my %roles;
my %rightids;
my %nevergrouped;

# -------------------------------------------------------------------------------------------
# SPECIAL DECLARATIONS for attribute hierarchy, IS A relationships, non-grouping, and right identities
# CAUTION: The values for these parameters depend on the particular release of SNOMED CT.
# Do not assume they remain stable across different releases. 
# **************************************************************
# These values are valid for:  20160731, release format 2 (RF2).
# **************************************************************
# -------------------------------------------------------------------------------------------

$conceptModelAttID = "410662002"
  ; # the SCTID of the concept at the top of the concept model attribute hierarchy
$isaID = "116680003";    # the SCTID of the IS A relationship concept
$nevergrouped{"123005000"} = "T";    # part-of is never grouped
$nevergrouped{"272741003"} = "T";    # laterality is never grouped
$nevergrouped{"127489000"} = "T";    # has-active-ingredient is never grouped
$nevergrouped{"411116001"} = "T";    # has-dose-form is never grouped
$rightid{"363701004"}      =  "127489000";    # direct-substance o has-active-ingredient -> direct-substance

$coreModuleId = "900000000000207008";
# $metadataModuleId = "900000000000012004"; # when reading in concepts, can exclude metadata module concepts
$conceptDefinedId = "900000000000073002";
$FSNId = "900000000000003001";
$DescId =  "900000000000013009";
# Setting of terms to preferred vs synonym vs not acceptable is according to Language Refset ID
$LanguageRefsetId = "900000000000509007"; # US English
# $LanguageRefsetId = "900000000000508004"; # GB English

$PreferredTermId = "900000000000548007";
$AcceptableTermId = "900000000000549004";

$rgidonly = "609096000";
$rgsctid = "id/$rgidonly"; # role group attribute SCTID

# -- Collect the needed files in a separate list #
my @dataFiles;
my $outputFile;
my $dlformat;
# -------------------------------------------------------------------------------------------
print "# Number of arguments: " . scalar (@ARGV) . "\n";
if ( @ARGV == 2)
{
  	print "[INFO] Two arguments passed. Assuming they are format and Snapshot folder location \n";
  	# Determine which format, OWL or KRSS:
  	&detectdlformat($ARGV[0]);

	# Use Snapshot folder location to get Terminology files in path	#
	my $dirname = $ARGV[1] . "/Terminology";
	opendir my($dh), $dirname or die "Couldn't open dir '$dirname': $!";

	my @files = readdir $dh;
	closedir $dh;

 	print "[INFO] Processing files in location : " . $dirname . "\n";
	foreach my $file (@files)
	{
 		if ($file =~ /_Concept_Snapshot_/) {
 			$dataFiles[0] = $dirname ."/". $file;
 			say "[INFO] Using file : " . $file . " for Concepts";
 		}elsif ($file =~ /_Description_Snapshot/) {
 			$dataFiles[1] = $dirname ."/". $file;
 			say "[INFO] Using file : " . $file . " for Descriptions";
 		}elsif ($file =~ /_StatedRelationship_Snapshot_/) {
 			$dataFiles[2] = $dirname ."/". $file;
 			say "[INFO] Using file : " . $file . " for Stated Relationships";
 		}elsif ($file =~ /_TextDefinition_Snapshot/) {
 			$dataFiles[3] = $dirname ."/". $file;
 			say "[INFO] Using file : " . $file . " for Text Definitions";
 		}else{
# 			print "[INFO] Ignoring file : " . $file . "\n";
 		}
 	}
 	
 	# now get the Language Refset filename
 	my $refsetdirname = $ARGV[1] . "/Refset/Language";
 	opendir $dh, $refsetdirname or die "Couldn't open dir '$refsetdirname': $!";
 	@files = readdir $dh;
 	closedir $dh;
 	print "[INFO] Processing files in location : " . $refsetdirname . "\n";
 	foreach my $file (@files)
 	{
 	   if ($file =~ /_cRefset_LanguageSnapshot/) {
 	      $dataFiles[4] = $refsetdirname . "/" . $file;
 	      say "[INFO] Using file : " . $file . " for Language Refset";
 	   } else {
# 	      say "[INFO] Ignoring file : " . $file;
 	   }
 	}

 	# Assign data file names by passing array values to sub routine assign_data_files
 	&assigndatafiles($dataFiles[0], $dataFiles[1], $dataFiles[2], $dataFiles[3], $dataFiles[4]);

 	# Create a file to be used as output
 	$outputFile = "snomedct_" . lc($dlformat) . ".owl";
}
elsif(@ARGV == 7)
{
  	# Determine which format, OWL, OWLF or KRSS:
  	&detectdlformat($ARGV[0]);

  	# Assign data file names by passing array values to sub routine assign_data_files
 	&assigndatafiles($ARGV[1], $ARGV[2], $ARGV[3], $ARGV[4], $ARGV[5]);

 	# Assign output file
 	$outputFile = $ARGV[6];
}
else
{
  die "[WARN] You must pass two or seven arguments! 
  \n[WARN] If you are passing two arguments, the first argument must be dl format and the second must be the data location path.
  \n[WARN] If you are passing 7 arguments, please read the documentation in the script";
}

# Sub routine for handling output formats #
sub detectdlformat
{
  	# Determine which format, OWL or KRSS:
	if ( $_[0] eq "KRSS" ) {
		$dlformat = "KRSS";
	}
	elsif ( $_[0] eq "OWL" ) {
		$dlformat = "OWL";
	}
	elsif ( $_[0] eq "OWLF" ) {    # owl functional syntax
		$dlformat = "OWLF";
	}
	else { die "I don't recognize $_[0]. Valid formats are KRSS, OWL, or OWLF.\n"; }
}

# Sub routine for assigning data files #
sub assigndatafiles
{
	$conceptsFileName     = $_[0];
	$descriptionsFileName = $_[1];
	$statedRelsFileName   = $_[2];
	$textDefFileName      = $_[3];
	$languageRefsetFileName = $_[4];
}

#-------------------------------------------------------------------------------
# File 1: The RF2 concepts table snapshot.
# Fields are: id[0], effectiveTime[1], active[2], moduleId[3], definitionStatusId[4]
#-------------------------------------------------------------------------------

open( CONCEPTS, $conceptsFileName ) || die "can't open $conceptsFileName \n";

# read input rows
while (<CONCEPTS>) {
	s/\015//g;
	s/\012//g;    # remove CR and LF characters
	@values = split( '\t', $_ );    # input file is tab delimited
	   # Filter out the header line, blank lines, and all inactive and metadata concepts
	if ( $values[0] && ( $values[2] eq "1") && ( $values[3] eq $coreModuleId ) )
	{
	    my $primdefFlag = "1";
	    if ($values[4] eq $conceptDefinedId) { $primdefFlag = "0"; }
		$primitive{ $values[0] } = $primdefFlag;
	}
}
close(CONCEPTS);

#-------------------------------------------------------------------------------
# File 5: The Language Refset. - Read it in before reading in the descriptions table
# Fields are: id[0], effectiveTime[1], active[2], moduleId[3], refsetId[4], descriptionID[5], acceptabilityId[6]
#-------------------------------------------------------------------------------

open( LANG, $languageRefsetFileName ) || die "can't open $languageRefsetFileName \n";

# read input rows
while (<LANG>) {
	s/\015//g;
	s/\012//g;    # remove CR and LF characters
	@values = split( '\t', $_ );    # input file is tab delimited
	   # Filter out the header/blank/inactive lines, and keep only core module rows for refset $LanguageRefsetId
	if ( $values[0] && ( $values[2] eq "1") && ( $values[3] eq $coreModuleId ) && ($values[4] eq $LanguageRefsetId ) )
	{
        $acceptability{ $values[5] } = $values[6];
	}
}
close(LANG);

#-------------------------------------------------------------------------------
# File 2: The RF2 descriptions table snapshot.
# Fields are: id[0], effectiveTime[1], active[2], moduleId[3], conceptId[4],
# languageCode[5], typeId[6], term[7], caseSignificanceId[8]
#-------------------------------------------------------------------------------

open( DESCRIPTIONS, $descriptionsFileName ) || die "can't open $descriptionsFileName \n";

# read input rows
while (<DESCRIPTIONS>) {
	s/\015//g;
	s/\012//g;    # remove CR and LF characters
	@values = split( '\t', $_ );    # input file is tab delimited
	   # Filter out the header line, blank lines
	if ( $values[0] && $values[2] eq "1") { # not a header line or blank line, and status is active
	   if ($values[6] eq $FSNId ) { # this is an FSN type of description
		   $fsn{ $values[4] } = &xmlify( $values[7] ); # xmlify changes & to &amp; < to &lt; > to &gt;
		   }
		elsif ($values[6] eq $DescId ) { # this is a non-FSN ordinary description
             if ( $acceptability{ $values[0] }) { # if the language refset indicates an acceptability for this description
                 if ($acceptability{ $values[0] } eq $PreferredTermId ) { # if is the preferred term
                     $prefTerm { $values[4] } = &xmlify($values[7]);
		         } elsif ( $acceptability{ $values[0] } eq $AcceptableTermId ) { # if it is acceptable
		             if ($desc{ $values[4] }) {
                         push @{ $desc{ $values[4] } },  &xmlify($values[7]); # push onto list of synonyms for this concept
                     } else {
                         $desc{ $values[4] } = [ &xmlify($values[7]) ];
                     }
		         }
		      }
		   }
	}
}
close(DESCRIPTIONS);



#-------------------------------------------------------------------------------
# File 3: The RF2 stated relationships snapshot (object-attribute-value triples with role group numbers)
# Fields are: id[0], effectiveTime[1], active[2], modeuleId[3], sourceId[4], destinationId[5], 
# relationshipGroup[6], typeId[7], characteristicTypeId[8], modifierId[9]
#-------------------------------------------------------------------------------

# create %rels which is a hash that will contain all role relationships
# roles are initially read in and stored as triplets (attribute value rolegroup)

%rels = ();

# read in relationships table: relID con1 rel con2 characteristictype refinability roleGroup

open( RELATIONSHIPS, $statedRelsFileName )
  || die "can't open $statedRelsFileName \n";

while (<RELATIONSHIPS>) {
	s/\015//g;
	s/\012//g;
	@values = split( '\t', $_ );    # input file is tab delimited
	if ( $values[2] eq "1" ) # an active stated (defining) relationship -
	{                                
		if ( $values[7] eq $isaID ) {    # an is-a relationship
			&populateParent( $values[4], $values[5] );
			&populateChildren( $values[5], $values[4] );
		}
		else {    # a defining attribute-value relationship
			&populateRels( $values[4], $values[7], $values[5], $values[6] );
		}
	}
}
close(RELATIONSHIPS);

#-------------------------------------------------------------------------------
# File 4: The Text Definitions File
# Fields are: id[0], effectiveTime[1], active[2], moduleId[3], conceptId[4], languageCode[5], typeId[6], term[7], caseSignificanceId[8]
#-------------------------------------------------------------------------------

open( TEXTDEF, $textDefFileName ) || die "can't open $textDefFileName \n";

# read input rows
while (<TEXTDEF>) {
	s/\015//g;
	s/\012//g;    # remove CR and LF characters
	@values = split( '\t', $_ );    # input file is tab delimited
	   # Filter out the header/blank/inactive lines, and keep only core module rows 
	if ( $values[0] && ( $values[2] eq "1") && ( $values[3] eq $coreModuleId )  )
	{
        $textDefs{ $values[4] } = &xmlify($values[7]);
	}
}
close(TEXTDEF);

#-------------------------------------------------------------------------------
# File 6: The Output file
#-------------------------------------------------------------------------------
#open( OUTF, ">$ARGV[4]" ) || die "can't open $ARGV[4]";
open( OUTF, ">".$outputFile ) or die "can't open output file : ".$outputFile;

&populateRoles( $children{$conceptModelAttID}, "" );

if ( $dlformat eq "OWL" ) {    # OWL RDF/XML format output
	say OUTF "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
	say OUTF "<rdf:RDF xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\"";
	say OUTF "         xmlns:rdfs=\"http://www.w3.org/2000/01/rdf-schema#\"";
	say OUTF "         xmlns:xsd=\"http://www.w3.org/2001/XMLSchema#\"";
	say OUTF "         xmlns:owl=\"http://www.w3.org/2002/07/owl#\"";
	say OUTF "         xmlns:sctp=\"http://snomed.info/field/Description.term.\""; # prefix for annotation for preferred/acceptable
	say OUTF "         xmlns:sctf=\"http://snomed.info/field/\"";
	say OUTF "         xmlns=\"http://snomed.info/\"";
	say OUTF "         xml:base=\"http://snomed.info/\">\n";


	say OUTF "    <owl:Ontology rdf:about=\"http://snomed.info/sct/900000000000207008\">";
	say OUTF "        <rdfs:label>SNOMED Clinical Terms, International Release, Stated Relationships in OWL RDF</rdfs:label>";
	say OUTF "        <owl:versionIRI rdf:resource=\"http://snomed.info/sct/900000000000207008/version/20160731\"/>";
	say OUTF "        <owl:versionInfo>International Release, Core Module, Release Date: 20160731</owl:versionInfo>";
	say OUTF "        <rdfs:comment>";
	say OUTF "Generated as OWL RDF/XML from SNOMED CT release files by Perl transform script";
	say OUTF "Input concepts file was             ", $conceptsFileName;
	say OUTF "Input stated relationships file was ", $statedRelsFileName;
	say OUTF "Input descriptions file was         ", $descriptionsFileName;
	say OUTF "Input language refset file was      ", $languageRefsetFileName;
	say OUTF "Input definitions file was          ", $textDefFileName;
		
    print OUTF "Copyright 2016 The International Health Terminology Standards Development Organisation (IHTSDO). ";
    print OUTF "All Rights Reserved. SNOMED CT was originally created by The College of American Pathologists. \\\"SNOMED\\\" and \\\"SNOMED CT\\\" ";
    print OUTF "are registered trademarks of the IHTSDO.  SNOMED CT has been created by combining SNOMED RT and a computer based nomenclature ";
    print OUTF "and classification known as Clinical Terms Version 3, formerly known as Read Codes Version 3, which was created on behalf of ";
    say   OUTF "the UK Department of Health.";
    print OUTF "This document forms part of the International Release of SNOMED CT distributed by the International Health Terminology ";
    print OUTF "Standards Development Organisation (IHTSDO), and is subject to the IHTSDO's SNOMED CT Affiliate Licence. ";
    say   OUTF "Details of the SNOMED CT Affiliate Licence may be found at www.ihtsdo.org/our-standards/licensing/.";
    print OUTF "No part of this file may be reproduced or transmitted in any form or by any means, or stored in any kind of retrieval system, ";
    print OUTF "except by an Affiliate of the IHTSDO in accordance with the SNOMED CT Affiliate Licence. Any modification of this document ";
    print OUTF "(including without limitation the removal or modification of this notice) is prohibited without the express written permission ";
    print OUTF "of the IHTSDO.  Any copy of this file that is not obtained directly from the IHTSDO (or a Member of the IHTSDO) is not ";
    print OUTF "controlled by the IHTSDO, and may have been modified and may be out of date. Any recipient of this file who has received ";
    say   OUTF "it by other means is encouraged to obtain a copy directly from the IHTSDO, or a Member of the IHTSDO.";
    say   OUTF "(Details of the Members of the IHTSDO may be found at www.ihtsdo.org/members/).";
	
	say OUTF "        </rdfs:comment>";
	say OUTF "    </owl:Ontology>\n";

	foreach $r1 ( sort keys %roles ) { &printroledefowl($r1); }

	foreach $c1 ( sort keys %primitive ) {
		&printconceptdefowl($c1) if ( not( $roles{$c1} ) );
	}

	say OUTF "</rdf:RDF>";

}
elsif ( $dlformat eq "OWLF" ) {    # OWL functional syntax output

	say OUTF "Prefix(:=<http://snomed.info/id/>)";	
	say OUTF "Prefix(sctp:=<http://snomed.info/field/Description.term.>)";
	say OUTF "Prefix(sctf:=<http://snomed.info/field/>)";
	say OUTF "Prefix(xsd:=<http://www.w3.org/2001/XMLSchema#>)";
	say OUTF "Prefix(owl:=<http://www.w3.org/2002/07/owl#>)";
	say OUTF "Prefix(xml:=<http://www.w3.org/XML/1998/namespace>)";
	say OUTF "Prefix(rdf:=<http://www.w3.org/1999/02/22-rdf-syntax-ns#>)";
	say OUTF "Prefix(rdfs:=<http://www.w3.org/2000/01/rdf-schema#>)";


	say OUTF "\n\nOntology(<http://snomed.info/sct/900000000000207008>";
    say OUTF "<http://snomed.info/sct/900000000000207008/version/20160731>";
	say OUTF "Annotation(rdfs:label \"SNOMED Clinical Terms, International Release, Stated Relationships in OWL Functional Syntax\")";
	say OUTF "Annotation(owl:versionInfo \"International Release, Core Module, Release Date: 20160731\")";
	say OUTF "Annotation(rdfs:comment \"";
	say OUTF "Generated as OWL Functional Syntax from SNOMED CT release files by Perl transform script.";
	say OUTF "Input concepts file was             ", $conceptsFileName;
	say OUTF "Input stated relationships file was ", $statedRelsFileName;
	say OUTF "Input descriptions file was         ", $descriptionsFileName;
	say OUTF "Input language refset file was      ", $languageRefsetFileName;
    say OUTF "Copyright 2016 The International Health Terminology Standards Development Organisation (IHTSDO). All Rights Reserved. SNOMED CT was originally created by The College of American Pathologists. \\\"SNOMED\\\" and \\\"SNOMED CT\\\" are registered trademarks of the IHTSDO.  SNOMED CT has been created by combining SNOMED RT and a computer based nomenclature and classification known as Clinical Terms Version 3, formerly known as Read Codes Version 3, which was created on behalf of the UK Department of Health.";
	say OUTF "This document forms part of the International Release of SNOMED CT distributed by the International Health Terminology Standards Development Organisation (IHTSDO), and is subject to the IHTSDO's SNOMED CT Affiliate Licence. Details of the SNOMED CT Affiliate Licence may be found at www.ihtsdo.org/our-standards/licensing/.";
	say OUTF "No part of this file may be reproduced or transmitted in any form or by any means, or stored in any kind of retrieval system, except by an Affiliate of the IHTSDO in accordance with the SNOMED CT Affiliate Licence. Any modification of this document (including without limitation the removal or modification of this notice) is prohibited without the express written permission of the IHTSDO.  Any copy of this file that is not obtained directly from the IHTSDO (or a Member of the IHTSDO) is not controlled by the IHTSDO, and may have been modified and may be out of date. Any recipient of this file who has received it by other means is encouraged to obtain a copy directly from the IHTSDO, or a Member of the IHTSDO.";
	say OUTF "(Details of the Members of the IHTSDO may be found at www.ihtsdo.org/members/).";
	say OUTF "        \")";
	

	foreach $r1 ( sort keys %roles ) { &printroledefowlf($r1); }

	foreach $c1 ( sort keys %primitive ) {
		&printconceptdefowlf($c1) if ( not( $roles{$c1} ) );
	}

	say OUTF ")";

}
else {    # KRSS format output

	say OUTF "(define-primitive-role $rgsctid)";
	foreach $r1 ( sort keys %roles ) { &printroledefkrss($r1); }

	foreach $c1 ( sort keys %primitive ) {
		&printconceptdefkrss($c1) if ( not( $roles{$c1} ) );
	}
}

# =====================================================
# end of main program
# =====================================================

# =====================================================
# Subroutines
# =====================================================

sub xmlify {
	my ($fsnstring) = @_;
	if ( $dlformat eq "OWL") {    # xmlify the fsn for OWL RDF/XML outputs only
		$fsnstring =~ s/&/&amp;/g;
		$fsnstring =~ s/</&lt;/g;
		$fsnstring =~ s/>/&gt;/g;
	} elsif ( $dlformat eq "OWLF"){ # cannot use double quotes in the name
		$fsnstring =~ s/"/'/g;
	}
	return $fsnstring;
}

sub populateParent {
	my ( $c1, $c2 ) = @_;

	if ( $parents{$c1} ) {

		# parents is a hash containing a list of parents of the key
		push @{ $parents{$c1} }, $c2;
	}
	else {
		$parents{$c1} = [$c2];
	}

}

sub populateChildren {
	my ( $c1, $c2 ) = @_;

	if ( $children{$c1} ) {

		# children is a hash containing a list of children of the key
		push @{ $children{$c1} }, $c2;
	}
	else {
		$children{$c1} = [$c2];
	}

}

sub populateRels {
	my ( $c1, $rel, $c2, $rg ) = @_;

	#   print "populateRels: $c1, $rel, $c2, $rg\n";
	if ( $rels{$c1} ) {
		push @{ $rels{$c1} }, [ $rel, $c2, $rg ];
	}
	else {
		$rels{$c1} = [ [ $rel, $c2, $rg ] ];
	}
}

# --------------------------------------------------------------------------
# routines for handling role (attribute) definitions
# --------------------------------------------------------------------------

sub populateRoles
{ # in: a list of roles and their parent role id and name. out: $roles{$concept} is hash of roles
	my ( $roleListPtr, $parentSCTID ) = @_;
	my $role;
	foreach $role (@$roleListPtr) {
		if ( $children{$role} ) {
			&populateRoles( $children{$role}, $role );
		}
		if ( $rightid{$role} ) {
			&populateRoleDef( $role, $fsn{$role}, $rightid{$role},
				$parentSCTID );
		}
		else {
			&populateRoleDef( $role, $fsn{$role}, "", $parentSCTID );
		}
	}
}

sub populateRoleDef {    # assumes at most one rightID, at most one parentrole.
	my ( $code, $name, $rightID, $parentrole ) = @_;
	$roles{$code}{'name'}       = $name;
	$roles{$code}{'rightID'}    = $rightID;
	$roles{$code}{'parentrole'} = $parentrole;
}

sub printroledefowl {    # print object properties of OWL RDF/XML syntax
	my ($r1) = @_;
	if ( $roles{$r1}{'parentrole'} eq "" ) {   # if there is no parent role specified
		say OUTF "<owl:ObjectProperty rdf:about=\"id/", $r1, "\">";
		say OUTF "    <rdfs:label xml:lang=\"en\">", $fsn{$r1}, "</rdfs:label>";
		if ($prefTerm{$r1}) { say OUTF "    <sctp:en-us.preferred xml:lang=\"en\">", $prefTerm{$r1}, "</sctp:en-us.preferred>"; }
		say OUTF "</owl:ObjectProperty>";
	}
	else {
		say OUTF "<owl:ObjectProperty rdf:about=\"id/", $r1, "\">";
		say OUTF "    <rdfs:label xml:lang=\"en\">", $fsn{$r1}, "</rdfs:label>";
		if ($prefTerm{$r1}) { say OUTF "    <sctp:en-us.preferred xml:lang=\"en\">", $prefTerm{$r1}, "</sctp:en-us.preferred>"; }
		say OUTF "    <rdfs:subPropertyOf rdf:resource=\"id/", $roles{$r1}{'parentrole'}, "\"/>";
		say OUTF "</owl:ObjectProperty>";
	}
	unless ( $roles{$r1}{'rightID'} eq "" ) {    # unless there is no right identity
		say OUTF "<rdf:Description>";
		say OUTF "   <rdfs:subPropertyOf rdf:resource=\"id/", $r1, "\"/>";
		say OUTF "   <owl:propertyChain rdf:parseType=\"Collection\">";
		say OUTF "      <rdf:Description rdf:about=\"id/", $r1, "\"/>";
		say OUTF "      <rdf:Description rdf:about=\"id/", $roles{$r1}{'rightID'}, "\"/>";
		say OUTF "   </owl:propertyChain>";
		say OUTF "</rdf:Description>";
	}
}

sub printroledefowlf {    # print object properties of OWL functional syntax
	my ($r1) = @_;
	say OUTF "Declaration(ObjectProperty(:",      $r1, "))";
	say OUTF "AnnotationAssertion(rdfs:label :", $r1, " \"",  $fsn{$r1}, "\")";
	if ($prefTerm{$r1}) { say OUTF "AnnotationAssertion(sctp:en-us.preferred :", $r1, " \"", $prefTerm{$r1}, "\")"; }
	if ($desc{$r1}) {
	   foreach $descrip ( @{ $desc{$r1} }) {
	      say OUTF "AnnotationAssertion(sctp:en-us.synonym :", $r1, " \"", $descrip, "\")";
	   }
	}
	unless ( $roles{$r1}{'parentrole'} eq "" ) {   # unless there is no parent role specified
		say OUTF "SubObjectPropertyOf(:", $r1, " :", $roles{$r1}{'parentrole'}, ")";
	}
	unless ( $roles{$r1}{'rightID'} eq "" ) {      # unless there is no right identity
		say OUTF "SubObjectPropertyOf(ObjectPropertyChain(:", $r1, " :", $roles{$r1}{'rightID'}, ") :", $r1, ")";
	}
}

sub printroledefkrss {
	my ($r1) = @_;
	print OUTF "(define-primitive-role id/$r1";
	unless ($roles{$r1}{'parentrole'} eq "") { # unless there is no parent role specified
		print OUTF " :parent id/$roles{$r1}{'parentrole'}";
	} 
	unless ( $roles{$r1}{'rightID'} eq "" ) {      # unless there is no right identity
        # This uses the extended KRSS syntax accepted by the CEL classifier
		print OUTF " :right-identity id/$roles{$r1}{'rightID'}";
	}
    say OUTF ")";
}

# --------------------------------------------------------------------------

sub printconceptdefowl {
	my ($c1) = @_;
	if ( $parentpointer = $parents{$c1} ) {
		$nparents = @$parentpointer;
	}
	else { $nparents = 0; }
	if ( $rels{$c1} ) { $nrels = 1; }
	else { $nrels = 0; }
	$nelements = $nparents + $nrels;
	say OUTF "<owl:Class rdf:about=\"id/", $c1, "\">";
	say OUTF "   <rdfs:label xml:lang=\"en\">", $fsn{$c1}, "</rdfs:label>";
	if ($prefTerm{$c1}) { say OUTF "    <sctp:en-us.preferred xml:lang=\"en\">", $prefTerm{$c1}, "</sctp:en-us.preferred>"; }
	if ($desc{$c1}) {
	   foreach $descrip ( @{ $desc{$c1} }) {
	      say OUTF "    <sctp:en-us.synonym xml:lang=\"en\">", $descrip, "</sctp:en-us.synonym>";
	   }
	}
	if ($textDefs{$c1}) { say OUTF "    <sctf:TextDefinition.term xml:lang=\"en\">", $textDefs{$c1}, "</sctf:TextDefinition.term>"; }
	
    if ($nelements == 0 ) { # no parent, therefore a top level node. 
	    print OUTF "</owl:Class>\n";
	} elsif ( $nelements == 1 ) {
		say OUTF "    <rdfs:subClassOf rdf:resource=\"id/", $parents{$c1}[0], "\"/>";
		say OUTF "</owl:Class>";
	} else { # more than one defining element; may be primitive or sufficiently defined
			if ( $primitive{$c1} eq "1" ) {    # use subClassOf
			    say OUTF "    <rdfs:subClassOf><owl:Class>";
			} else { # Fully defined. Use equivalentClass
		        say OUTF "    <owl:equivalentClass><owl:Class>";
			}
			say OUTF "   <owl:intersectionOf rdf:parseType=\"Collection\">";
			foreach $parentc ( @{ $parents{$c1} } ) {
				say OUTF "       <owl:Class rdf:about=\"id/", $parentc, "\"/>";
			}
			unless ( $nrels == 0 ) {
				foreach $rgptr ( @{ &grouproles( $rels{$c1} ) } ) {
					&printrolegroupowl($rgptr);
				}
			}
			say OUTF "   </owl:intersectionOf>";
			if ($primitive{$c1} eq "1") {
				say OUTF "   </owl:Class></rdfs:subClassOf>";
			} else {
				say OUTF "   </owl:Class></owl:equivalentClass>";
			}
			say OUTF "</owl:Class>";
	}
}


sub printconceptdefowlf {
	my ($c1) = @_;
	if ( $parentpointer = $parents{$c1} ) {
		$nparents = @$parentpointer;
	}
	else { $nparents = 0; }
	if ( $rels{$c1} ) { $nrels = 1; }
	else { $nrels = 0; }
	$nelements = $nparents + $nrels;
	say OUTF "Declaration(Class(:", $c1, "))";
	say OUTF "AnnotationAssertion(rdfs:label :", $c1, " \"", $fsn{$c1}, "\")";
#	say OUTF "AnnotationAssertion(owl:versionInfo :", $c1, " \"http://snomed.info/sct/900000000000207008/version/20160731/id/", $c1, "\")";
    if ($prefTerm{$c1}) { say OUTF "AnnotationAssertion(sctp:en-us.preferred :", $c1, " \"", $prefTerm{$c1}, "\")"; }
	if ($desc{$c1}) {
	   foreach $descrip ( @{ $desc{$c1} }) {
	      say OUTF "AnnotationAssertion(sctp:en-us.synonym :", $c1, " \"", $descrip, "\")";
	   }
	}
	if ($textDefs{$c1}) { say OUTF "AnnotationAssertion(sctf:TextDefinition.term :", $c1, " \"", $textDefs{$c1}, "\")"; }

	    if ($nelements == 0 ) { # no parent, therefore a top level node. No need to give SubClassOf to owl:Thing, that will happen automatically.
#	    	no-op
	    } elsif ( $nelements == 1 ) {
			say OUTF "SubClassOf(:", $c1, " :", $parents{$c1}[0], ")";
		} else { # more than one defining element; may be primitive or sufficiently defined
			if ( $primitive{$c1} eq "1" ) {    # use subClassOf
			   print OUTF "SubClassOf(:", $c1, " ObjectIntersectionOf(";
			} else {
			   print OUTF "EquivalentClasses(:", $c1, " ObjectIntersectionOf(";	
			}
			foreach $parentc ( @{ $parents{$c1} } ) {
				print OUTF ":", $parentc, " ";
			}
			print OUTF "\n";
			unless ( $nrels == 0 ) {
				foreach $rgptr ( @{ &grouproles( $rels{$c1} ) } ) {
					&printrolegroupowlf($rgptr);
				}
			}
			say OUTF "))";
		}
}


sub printrolegroupowl {
	local ($rgrp) = @_;
	$ngrps = @$rgrp;
	if ( $ngrps > 1 ) {

		say OUTF "       <owl:Restriction>";
		say OUTF "            <owl:onProperty rdf:resource=\"$rgsctid\"/>";
		say OUTF "            <owl:someValuesFrom>";
		say OUTF "                <owl:Class>";
		say OUTF "                <owl:intersectionOf rdf:parseType=\"Collection\">";
		foreach $grp (@$rgrp) {    # multiple attributes nested under RoleGroup
			say OUTF "                    <owl:Restriction>";
			say OUTF "                        <owl:onProperty rdf:resource=\"id/", $$grp[0], "\"/>";
			say OUTF "                        <owl:someValuesFrom rdf:resource=\"id/", $$grp[1], "\"/>";
			say OUTF "                    </owl:Restriction>";
		}
		say OUTF "                </owl:intersectionOf>";
		say OUTF "                </owl:Class>";
		say OUTF "            </owl:someValuesFrom>";
		say OUTF "       </owl:Restriction>";

	}
	else {    # only one group.  No need for intersectionOf or looping.
		if ( $nevergrouped{ $$rgrp[0][0] } ) {    # no need for RoleGroup
			say OUTF "       <owl:Restriction>";
			say OUTF "           <owl:onProperty rdf:resource=\"id/", $$rgrp[0][0], "\"/>";
			say OUTF "           <owl:someValuesFrom rdf:resource=\"id/", $$rgrp[0][1], "\"/>";
			say OUTF "       </owl:Restriction>";
		}
		else {    # single attribute nested under RoleGroup
			say OUTF "       <owl:Restriction>";
			say OUTF "            <owl:onProperty rdf:resource=\"$rgsctid\"/>";
			say OUTF "            <owl:someValuesFrom>";
			say OUTF "                <owl:Restriction>";
			say OUTF "                    <owl:onProperty rdf:resource=\"id/", $$rgrp[0][0], "\"/>";
			say OUTF "                    <owl:someValuesFrom rdf:resource=\"id/", $$rgrp[0][1], "\"/>";
			say OUTF "                </owl:Restriction>";
			say OUTF "            </owl:someValuesFrom>";
			say OUTF "       </owl:Restriction>";
		}
	}
}

sub printrolegroupowlf {
	local ($rgrp) = @_;
	$ngrps = @$rgrp;
	if ( $ngrps > 1 ) {
		say OUTF "       ObjectSomeValuesFrom(:$rgidonly ObjectIntersectionOf(";
		foreach $grp (@$rgrp) {
			say OUTF "                        ObjectSomeValuesFrom(:$$grp[0] :$$grp[1])";
		}
		print OUTF "))";
	}
	else {    # only one group. No need for intersectionOf or looping.
		if ( $nevergrouped{ $$rgrp[0][0] } ) {    # No need for RoleGroup
			say OUTF "       ObjectSomeValuesFrom(:$$rgrp[0][0] :$$rgrp[0][1])";
		}
		else {
			say OUTF "       ObjectSomeValuesFrom(:$rgidonly ObjectSomeValuesFrom(:$$rgrp[0][0] :$$rgrp[0][1]))";
		}
	}
}

sub printconceptdefkrss {
	my ($c1) = @_;
	if ( $parentpointer = $parents{$c1} ) {
		$nparents = @$parentpointer;
	}
	else { $nparents = 0; }
	if ( $rels{$c1} ) { $nrels = 1; }
	else { $nrels = 0; }
	$nelements = $nparents + $nrels;

	if ( $primitive{$c1} eq "1" ) {    # primitive, use define-primitive-concept
		if ( $nparents eq 0 ) {
			say OUTF "(define-primitive-concept id/$c1)";
		}
		elsif ( ( $nparents eq 1 ) && ( $nelements eq 1 ) )
		{                              # primitive defined by a single parent
			say OUTF "(define-primitive-concept id/$c1 id/$parents{$c1}[0])";
		}
		else {
			say OUTF "(define-primitive-concept id/$c1 (and ";
			foreach $parentc ( @{ $parents{$c1} } ) {
				say OUTF "   id/$parentc";
			}
			unless ( $nrels == 0 ) {
				foreach $rgptr ( @{ &grouproles( $rels{$c1} ) } ) {
					&printrolegroupkrss($rgptr);
				}
			}
			say OUTF "))";
		}
	}
	else {    #  sufficiently defined, use define-concept
		say OUTF "(define-concept id/$c1 (and";
		if ( $nelements > 1 ) {
			foreach $parentc ( @{ $parents{$c1} } ) {
				say OUTF "        id/$parentc";
			}
			unless ( $nrels == 0 ) {
				foreach $rgptr ( @{ &grouproles( $rels{$c1} ) } ) {
					&printrolegroupkrss($rgptr);
				}
			}
			say OUTF "))";
		}
		else {
			say ">>>> error >>>> nelements not > 1 for fully defined $c1";
		}
	}
}

sub printrolegroupkrss {
	local ($rgrp) = @_;
	$ngrps = @$rgrp;
	if ( $ngrps > 1 ) {
		say OUTF "       (some $rgsctid (and ";
		foreach $grp (@$rgrp) {
			say OUTF "                        (some id/$$grp[0] id/$$grp[1] )";
		}
		say OUTF "                        )";
		say OUTF "        )";
	}
	else {    # only one group. No need for intersectionOf or looping.
		if ( $nevergrouped{ $$rgrp[0][0] } ) {    # No need for RoleGroup
			say OUTF "       (some id/$$rgrp[0][0] id/$$rgrp[0][1] )";
		}
		else {
			say OUTF "       (some $rgsctid (some id/$$rgrp[0][0] id/$$rgrp[0][1] ))";
		}
	}
}

#-------------------------------------------------------------------------------
# grouproles
#-------------------------------------------------------------------------------
# Changes its rels from a list of triplets <role value groupnum>
# into a list of rolegroups, each of which is a list of <role value> pairs.
# The purpose is to eliminate role group "numbers"
# The role group as a list of att-val pairs preserves role groups independent of the groupnum
#-------------------------------------------------------------------------------

sub grouproles
{    # takes a list of role triplets (attribute value rolegroup-number)
	    # returns a list of rolegroups, which are lists of (attr value) pairs
	local ($rolesptr) = @_;
	my ( $role, $resultptr, $groupptr, %rgrp, $attr, $val, $grp );
	foreach $role (@$rolesptr) {    # $role is a pointer to a triplet
		$attr = $role->[0];
		$val  = $role->[1];
		$grp  = $role->[2];
		if ( $rgrp{$grp} ) { # if group number $grp has been encountered already
			    # change triplet into a pair and add to existing list of pairs
			push @{ $rgrp{$grp} }, [ $attr, $val ];
		}
		else {    # new list of pairs
			$rgrp{$grp} = [ [ $attr, $val ] ];
		}
	}
	@$resultptr = ();

	# @$groupptr is a list of pairs belonging to one group
	while ( ( $key, $groupptr ) = each %rgrp ) {
		if ( $key eq "0" ) {

			# group 0 indicates a single att-val pair with no other pairs
			foreach $pairptr (@$groupptr) {

				# a list of pairs with only one pair
				push @$resultptr, [ [ $pairptr->[0], $pairptr->[1] ] ];
			}
		}
		else {
			push @$resultptr, [@$groupptr];    # a list of pairs
		}
	}
	return ($resultptr);
}

