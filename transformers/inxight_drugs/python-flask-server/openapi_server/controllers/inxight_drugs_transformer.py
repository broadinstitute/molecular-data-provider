from flask import g
from collections import defaultdict
from transformers.transformer import Transformer
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection
import sqlite3
import re
import json

SOURCE = 'Inxight:Drugs'

#########################################################################
# 1. This class provides all the Inxight_Drugs information about the  
# substances in the request query to the Inxight_Drugs Transformer REST API
# The Producer function takes each name and returns an element of substance
# information
# GitHub Issue #52 The producers should accept name, InChIKeys, 
# and native CURIES (RXCUI, UNII, CID) as input.
#########################################################################
class Inxight_SubstancesProducer(Transformer):

    variables = ['substances']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/substances_transformer_info.json')
    #   TO DO annotate the substances_transformer_info.json file
        self.update_info_file('info/substances_transformer_info.json')

    def update_info_file(self, infoFile):
        search = None
        with open(infoFile) as f:
            json_obj = json.load(f)
        Inxight_Drugs_DataSupply.get_substance_counts(self, json_obj)
        with open(infoFile, 'w') as json_file:
            json.dump(json_obj, json_file,  sort_keys=True,indent=4, separators=(',', ': ')) # save to file with prettifying


#   Invoked by Transformer.transform(query) method because "function":"producer" is specified in the openapi.yaml file
    def produce(self, controls):
        substance_list = []
        names = controls['substances'].split(';')
    #   find substance data for each substance name that was submitted
        for name_value in names:
            name_value = name_value.strip()
            Inxight_Drugs_DataSupply.find_substance(self, substance_list, name_value)
            
    #   send back to the REST client the entire list of the substances' data (attributes & synonyms)
        return substance_list




#########################################################################
#
# 2. RelationshipTransformer takes an UNII value and gives back all
#  connected substances, including any mixtures and components of the UNII substance.
#
#########################################################################
class Inxight_DrugsRelationshipTransformer(Transformer):

    variables = ['substances']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/relationships_transformer_info.json')
    #   TO DO annotate the relationships_transformer_info.json file
        self.update_info_file('info/relationships_transformer_info.json')


    def update_info_file(self, infoFile):
        search = None
        with open(infoFile) as f:
            json_obj = json.load(f)
        Inxight_Drugs_DataSupply.get_relationship_types(self, json_obj, search)
        Inxight_Drugs_DataSupply.get_substance_counts(self, json_obj)
        with open(infoFile, 'w') as json_file:
            json.dump(json_obj, json_file, sort_keys=True, indent=4, separators=(',', ': ')) # save to file with indent prettifying


    def map(self, collection, controls):
        related_list = []
    #   find relationship data for each substance that were submitted
        for substance in collection:
            if 'unii' in substance.identifiers:
                substance.identifiers['unii']  # if the substance has no unii id, then get a KeyError now
                Inxight_Drugs_DataSupply.get_relationships(self, related_list, substance)
    #   send back to the REST client the entire list of related substances (substances that interact with the drugs)
        return related_list




############################################################################
# 3. This class provides all the Inxight_Drugs information about the  
# drugs in the request query to the Inxight_Drugs Transformer REST API
# The Producer function takes each name and returns an element of drug
# information including the RXCUI and biolink_class of Drug
#
############################################################################
class Inxight_DrugsTransformer(Transformer):

    variables = ['substances']   # for use in controls['substances']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/drugs_transformer_info.json')
    #   TO DO annotate the drugs_transformer_info.json file
        self.update_info_file('info/drugs_transformer_info.json')


    def update_info_file(self, infoFile):    
        with open(infoFile) as f:
            json_obj = json.load(f)
        Inxight_Drugs_DataSupply.get_drug_counts(self, json_obj)
        with open(infoFile, 'w') as json_file:
            json.dump(json_obj, json_file,  sort_keys=True,indent=4, separators=(',', ': ')) # save to file with prettifying


    def produce(self, controls):
        drug_list = []
        names = controls['substances'].split(';')
    #   find relationship data for each substance that were submitted
        for name_value in names:
            name_value = name_value.strip()
            Inxight_Drugs_DataSupply.find_substance(self, drug_list, name_value)
        drug_list = Inxight_Drugs_DataSupply.get_drug_info(self, drug_list)

    #   send back to the REST client the entire list of the drugs' data (attributes & synonyms)
        return drug_list




#########################################################################
#
# 4. This Active Ingredients Transformer take a drug's RXCUI value  
# and returns the drug's active ingredients & their biolink class
#
#########################################################################
class Inxight_DrugsActiveIngredientsTransformer(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/drugs_active_ingredients_transformer_info.json')
    #   TO DO annotate the drugs_active_ingredients_transformer_info.json file
        self.update_info_file('info/drugs_active_ingredients_transformer_info.json')


    def update_info_file(self, infoFile):    
        search = """ relationships.type LIKE ("%ACTIVE%") 
                AND NOT relationships.type LIKE ("%INACTIVE%")
                AND NOT relationships.type LIKE ("%PARENT->%")
                AND NOT relationships.type LIKE ("%PRODRUG->%")
                AND NOT relationships.type LIKE ("%RACEMATE->%")
                AND NOT relationships.type LIKE ("%SUBSTANCE->%")  
                AND NOT relationships.type LIKE ("%METABOLITE ACTIVE%") 
                AND NOT relationships.type LIKE ("%METABOLITE LESS ACTIVE%") 
                AND NOT relationships.type LIKE ("%ACTIVE CONSTITUENT ALWAYS PRESENT%")"""
        with open(infoFile) as f:
            json_obj = json.load(f)
        Inxight_Drugs_DataSupply.get_relationship_types(self, json_obj, search)
        Inxight_Drugs_DataSupply.get_drug_counts(self, json_obj)
        with open(infoFile, 'w') as json_file:
            json.dump(json_obj, json_file, sort_keys=True,indent=4, separators=(',', ': ')) # save to file with prettifying


    def map(self, collection, controls):
        related_list = []
    #   find relationship data for each drug that were submitted
        for drug in collection:
            if 'rxnorm' in drug.identifiers:
                Inxight_Drugs_DataSupply.get_active_ingredients(self, related_list, drug)
    #   send back to the REST client the entire list of active ingredients (substances in the drugs)
        return related_list




###############################################################
# This class contains common code for retrieving substances
# relationships and drugs based on the request query
# to the Inxight_Drugs Transformer REST API 
###############################################################
class Inxight_Drugs_DataSupply():

    def get_db():
        if 'db' not in g:
            g.db = sqlite3.connect("data/Inxightdb.db",
                    detect_types=sqlite3.PARSE_DECLTYPES
            ) # SQLite database file is located in the python-flask-server/data directory
            g.db.row_factory = sqlite3.Row
        return g.db


    def close_db(self, e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()


#   Get the substance's synonyms and attributes data
    def find_substance(self, substance_list, name_value):
        search_column = '_name'                 # by default, assume a search for substance by name
        inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')

    #   check if submitted name is native CURIE, e.g., CID:2244
    #   or InChiKey e.g., BSYNRYMUTXBXSQ-UHFFFAOYSA-N
    #   or else just a substance name
        if name_value.find(':') > -1:
            if name_value.find('UNII') > -1:    # a search for substance by UNII, i.e., column 'substanceUNII'
                search_column = 'substanceUNII'
            elif name_value.find('CID') > -1:   # a search for substance by CID, i.e., column 'structurePubChem'
                search_column = 'structurePubChem'
            name = name_value.split(":",1)[1].strip()
        elif inchikey_regex.match(name_value) is not None:
            search_column = 'structureInChiKey' # a search for substance by inchikey, i.e., column 'structureInChiKey'
            name = name_value
        else:
            name = name_value
            search_column = '_name'

        """
            Find substance by a name
        """
        query1 = """
            SELECT DISTINCT 
                substances.uuid AS uuid,
                substanceClass,
                substances.UNII AS substanceUNII,
                _name,
                structurallyDiverse,
                protein,
                nucleicAcid,
                mixture,
                polymer,
                structure_id,
                formula,
                opticalActivity,
                atropisomerism,
                stereoCenters,
                definedStereo,
                ezCenters,
                charge,
                mwt AS molecularWeight,
                stereochemistry,
                structures.InChiKey AS structureInChiKey,
                structures.pubChem AS structurePubChem,
                RXCUI,
                NCBI,
                stereoComments
            FROM substances
            LEFT JOIN structures ON substances.structure_id = structures.id
            LEFT JOIN unii_lookup ON substances.UNII = unii_lookup.UNII
            WHERE {search_column} = ?;
        """.format(search_column=search_column)
        connection = Inxight_Drugs_DataSupply.get_db() 
        if search_column is not None:
            cur = connection.execute(query1, (name,))
        #   for each hit (i.e., of the same substance name, an unlikely but possible occurrence)
        for row in cur.fetchall():
                uuid = row["uuid"]
                inchikey = None
                biolink_class = None
                substanceClass = row['substanceClass']
        #       Create identifiers by annotating ids with appropriate CURIE 
                id = "UNII:" + row['substanceUNII']
                identifiers = {'unii':id}
                if  (row['structureInChiKey']):
                    identifiers["inchikey"]  = row['structureInChiKey']    
                if  (row['structurePubChem']):
                    identifiers["pubchem"]  = "CID:" +  row['structurePubChem'] 
        #       Select the correct biolink_class based on substanceClass
                if(row['substanceClass'] in ['structurallyDiverse', 'polymer', 'protein', 'nucleicAcid', 'chemical', 'mixture']):
                    biolink_class = Inxight_Drugs_DataSupply.get_biolink_class( row['substanceClass'], row['structureInChiKey'] )
                substance = Element(
                    id = id,
                    biolink_class = biolink_class,
                    identifiers = identifiers,
                    names_synonyms = [Names(name=name_value,
                                                synonyms=[],
                                                source=SOURCE)], # add names & synonyms from the database
                    attributes = [
                            Attribute(
                                name='query name', 
                                value=name_value,
                                provided_by=self.info.name, 
                                source=SOURCE
                                ),
                    ],
                    connections = [],
                    source = self.info.name
                )
            #   Append additional attributes collected from Inxight:Drugs substances & unii tables 
                attributes_list= ['substanceClass', 'formula', 'opticalActivity', 'atropisomerism', 'stereoCenters', 'definedStereo', 'ezCenters', 'charge', 'molecularWeight', 'stereochemistry', 'NCBI']
                for attribute in attributes_list:
                    if row[attribute] is not None and len(row[attribute].strip())>0: 
                        if attribute != 'NCBI':
                            substance.attributes.append(
                            Attribute(
                                provided_by=self.info.name,
                                name= attribute,
                                value= str(row[attribute]),
                                source= SOURCE,
                                type= attribute
                                )
                            )
                        else:
                            substance.attributes.append(
                            Attribute(
                                provided_by=self.info.name,
                                name= 'OrganismTaxon',
                                value= 'NCBITaxon:' + row[attribute],
                                source= SOURCE,
                                type= 'biolink:OrganismTaxon'
                                )
                        )
                if biolink_class != 'ignore':
                    substance_list.append(substance)
                # Append synonyms to the substance
                    Inxight_Drugs_DataSupply.get_names_synonyms(uuid, substance)
                # Append references to the substance
                    Inxight_Drugs_DataSupply.get_references(self, uuid, substance)
                # Append codes as refererences to the substance
                    Inxight_Drugs_DataSupply.get_codes(self, uuid, substance)

                ##### Need to put this in a dictionary with protein, polymer, nucleic acid, ...
                    if substanceClass == 'protein':
                        Inxight_Drugs_DataSupply.get_protein_info(self, uuid, substance)
                    elif substanceClass == 'nucleicAcid':
                        Inxight_Drugs_DataSupply.get_nucleicAcid_info(self, uuid, substance)


    def get_names_synonyms(uuid, substance):  
        """
            Build names and synonyms list
        """
    #   Query for data to fill the Names class.
        query2 = """ 
            SELECT 
                names.name AS name, 
                names.type AS type,
                names.preferred, 
                names.displayName
            FROM substance_names
            JOIN names ON substance_names.name_id = names.uuid
            WHERE substance_id = ? ;
        """
    #   Dictionary to collect the lists of synonyms (aliases) and their respective sources.
        synonyms_dictionary = defaultdict(list)
        connection = Inxight_Drugs_DataSupply.get_db()
        cur2 = connection.execute(query2,(uuid,))
        for row in cur2.fetchall():
        #   powerful statement to build a dictionary (a map) of name types with name lists
            synonyms_dictionary[row['type']].append(row['name'])

        for syn_type, syn_list in synonyms_dictionary.items():
            substance.names_synonyms.append(
                Names(
                    name = syn_list[0] if len(syn_list) == 1 else  None,
                    synonyms = syn_list if len(syn_list) > 1 else  None,
                    source = syn_type+'@Inxight:Drugs',
                )
            )


#   codes from Inxight:Drugs provide information that are also references
    def get_codes(self, uuid, substance):
        """
            Add codes as references to attributes
        """
        query3 = """ 
            SELECT 
                _name,
                type,
                codeSystem,
                comments,
                code,
                url,
                codeText
            FROM substances
            JOIN substance_codes ON substances.uuid = substance_codes.substance_id
            JOIN codes ON substance_codes.code_id = codes.uuid
            WHERE substances.uuid = ?;
        """
        connection = Inxight_Drugs_DataSupply.get_db() 
        cur3 = connection.execute(query3, (uuid,))
        for row in cur3.fetchall():
            reference = row['comments']
            url = row['url']
            source = row['codeSystem']+'@'+SOURCE
            if reference is None:
                reference = url
            if(url):
                substance.attributes.append(
                    Attribute(
                        name = 'code',
                        value = reference,
                        type = 'reference',
                        source = source,
                        url = url,
                        provided_by = self.info.name
                    )
                ) 


    def get_references(self, uuid, substance):
        """
            Add references to attributes
        """
        query4 = """ 
            SELECT 
                _references.uuid, 
                citation, 
                id, 
                docType, 
                publicDomain, 
                url, 
                uploadedFile
            FROM entity_references
            JOIN _references ON entity_references.reference_id = _references.uuid
            WHERE entity_references.entity_id = ? ;
        """
        connection = Inxight_Drugs_DataSupply.get_db() 
        cur4 = connection.execute(query4, (uuid,))
        for row in cur4.fetchall():
            reference = row['citation']
            url = row['url']
            if (str(row['citation']).lower().find('http:') > -1  and str(row['url']).lower().find('http:') == -1 ):
                reference = row['url']  # swap
                url = row['citation']   # swap
            if( url is not None and len(str(url).strip()) > 0 ):
                if reference is None:
                    reference = url
                substance.attributes.append(
                    Attribute(
                        name = 'reference',
                        value = reference,
                        type = 'reference',
                        source = SOURCE,
                        url = url,
                        provided_by = self.info.name
                    )
                ) 


    def get_relationships(self, relationship_list, substance):
        #   substance is a mixture that must have components
            Inxight_Drugs_DataSupply.get_components(self, relationship_list, substance) 
            # also check if it is a component 
            Inxight_Drugs_DataSupply.get_mixtures(self, relationship_list, substance) 

            substance_unii = substance.identifiers['unii'].split(":",1)[1].strip()
            source_element_id = substance.identifiers['unii']
            """
            Find relationships to other substances by a substance UNII
            """
            query5 = """
            SELECT 
                substances._name AS substance_name,
                substances.mixture,
                relationships.type AS relationships_type,
                relationships.mediatorSubstance_id,
                relationships.interactionType AS interaction_type,
                relationships.qualification,
                relationships.amount_average AS average,
                relationships.amount_high AS high,
                relationships.amount_low AS low,
                relationships.amount_units,
                relationships.comments,
                related.uuid AS related_uuid,
                related._name AS related_substance,
                related.UNII AS related_substance_unii,
                related.substanceClass,
                unii_lookup.RXCUI AS relatedRXCUI,
                unii_lookup.PUBCHEM AS relatedPUBCHEM,
                unii_lookup.INCHIKEY AS InChiKey,
                unii_lookup.NCBI
            FROM substances
            JOIN relationships ON substances.uuid = relationships.substance_id
            JOIN substances AS related ON relationships.relatedSubstance_id = related.uuid
            LEFT JOIN unii_lookup ON related.UNII = unii_lookup.UNII
            WHERE substances.UNII = ?; 
        """
            connection = Inxight_Drugs_DataSupply.get_db() 
            cur5 = connection.execute(query5, (substance_unii,))

            for row in cur5.fetchall():                         # loop for each related substance found
                id = "UNII:"+str(row['related_substance_unii'])
                name = row['related_substance']
            #   Create identifiers by annotating ids with appropriate CURIE prefix
                identifiers = {'unii':id}
                if  (row['InChiKey']):
                    identifiers["inchikey"]  = row['InChiKey']    
                if  (row['relatedPUBCHEM']):
                    identifiers["pubchem"]  = "CID:" +  row['relatedPUBCHEM'] 
                biolink_class = Inxight_Drugs_DataSupply.get_biolink_class( row['substanceClass'], row['InChiKey'])
                if  row['relatedRXCUI'] and biolink_class == 'Drug':
                    identifiers["rxnorm"]  = "RXCUI:" +  row['relatedRXCUI'] 

                related_substances = Element(
                    id = id,
                    biolink_class = biolink_class,
                    identifiers = identifiers,
                    names_synonyms = [Names(name=name,
                                            synonyms=[],
                                            source=SOURCE)], # add name & later synonyms from the database
                    attributes = [],
                    connections = [],
                    source = self.info.name
                )
            #   Append additional attributes collected from Inxight:Drugs substances & unii tables 
                attributes_list= ['substanceClass', 'NCBI']
                for attribute in attributes_list:
                    if row[attribute] is not None and len(row[attribute].strip())>0: 
                        if attribute != 'NCBI':
                            related_substances.attributes.append(
                                Attribute(
                                    provided_by=self.info.name,
                                    name= attribute,
                                    value= str(row[attribute]),
                                    source= SOURCE,
                                    type= attribute
                                )
                            )
                        else: # NCBI id
                            related_substances.attributes.append(
                            Attribute(
                                provided_by=self.info.name,
                                name= 'OrganismTaxon',
                                value= 'NCBITaxon:' + row[attribute],
                                source= SOURCE,
                                type= 'biolink:OrganismTaxon'
                                )
                            )                
                relationship  = Connection(
                                    source_element_id = source_element_id,
                                    type = row['relationships_type'],
                                    relation = row['relationships_type'],
                                    evidence_type = "",
                                    attributes = []
                                )
            #   Append additional attributes collected from Inxight:Drugs relationships table 
                attributes_list= ['interaction_type', 'comments']
                for attribute in attributes_list:
                    if row[attribute] is not None and len(row[attribute].strip())>0:
                        relationship.attributes.append(
                        Attribute(
                            provided_by=self.info.name,
                            name= attribute,
                            value= str(row[attribute]),
                            source= SOURCE,
                            type= attribute
                            )
                        )
                if(row['qualification']):
                    attributes_list= ['average', 'high', 'low']
                    for attribute in attributes_list:
                        if row[attribute] is not None and len(row[attribute].strip()) > 0:
                            # e.g., attribute.name: average IC50 (NANOMOLAR), attribute.value: 2.7
                            name  = attribute + ' ' + str(row['qualification']) + ' (' + str(row['amount_units']) + ')'
                            value = str(row[attribute])
                            relationship.attributes.append(
                            Attribute(
                                provided_by=self.info.name,
                                name  = name,
                                value = value,
                                source= SOURCE,
                                type  = name
                                )
                            )

                related_substances.connections.append(relationship)
                if biolink_class != 'ignore':
                    relationship_list.append(related_substances)


    def get_biolink_class(substanceClass, inchiKey):
        #   structurallyDiverse - MolecularEntity
        #   polymer - 'MolecularEntity'
        #   protein - 'Protein'
        #   mixture - 'ChemicalSubstance' it they have InChIKey
        #   mixture - 'MolecularEntity' it they don't have InChIKey
        #   concept - ignore, don't return data for the input substance
        #   nucleicAcid - 'GenomicEntity'
        #   chemical - 'ChemicalSubstance'
            biolinkClass = None
            biolinkClass_dict = {
                'structurallyDiverse':'MolecularEntity',
                'polymer':'MolecularEntity',
                'protein':'Protein',
                'mixture_InChiKey':'ChemicalSubstance',
                'mixture_NoInChiKey':'MolecularEntity',
                'concept':'ignore',
                'nucleicAcid' :'GenomicEntity',
                'chemical':'ChemicalSubstance'
            }
        #   When there are two kinds of mixtures
            if(substanceClass == 'mixture' and inchiKey):
                substanceClass = 'mixture_InChiKey'
            elif(substanceClass == 'mixture' and inchiKey == None ):
                substanceClass = 'mixture_NoInChiKey'   
        #   Select the correct biolink_class based on substanceClass
            if(substanceClass in ['structurallyDiverse', 'polymer', 'protein', 'mixture_InChiKey', 'mixture_NoInChiKey', 'concept', 'nucleicAcid', 'chemical']):
                biolinkClass = biolinkClass_dict[substanceClass]
            return biolinkClass


    def get_drug_info(self, substance_list):
        """
        Find RXCUI & PT by a substance UNII
        """
        query6 = """
            SELECT 
                UNII,
                PT AS preferredTerm,
                RN,
                EC,
                NCIT,
                RXCUI,
                PUBCHEM,
                ITIS,
                NCBI,
                PLANTS,
                GRIN,
                MPNS,
                INN_ID,
                MF,
                INCHIKEY,
                SMILES,
                INGREDIENT_TYPE
            FROM unii_lookup
            WHERE UNII = ?;
        """
        drug_list = []
        for drug in substance_list:
            connection = Inxight_Drugs_DataSupply.get_db() 
            cur6 = connection.execute(query6, (drug.identifiers['unii'].split(":",1)[1].strip(),))
            set_biolink_class = None
            if(len(self.variables) > 1 and self.variables[1]):
                set_biolink_class = self.variables[1]
            add_drug = False
            for row in cur6.fetchall(): 
                if row['RXCUI'] is not None and row['RXCUI'] != '':
                    add_drug = True
                drug.identifiers = {'rxnorm': 'RXCUI:' + row['RXCUI']}
                drug.id = 'RXCUI:' + row['RXCUI']
                drug.attributes.append(
                    Attribute(
                        provided_by=self.info.name,
                        name= 'preferred term',
                        value= row['preferredTerm'],
                        source= SOURCE,
                        type= 'preferred term'
                    )
                )
                drug.biolink_class = 'Drug'
            if add_drug:
                drug_list.append(drug)
        return drug_list



    def get_active_ingredients(self, related_list, drug):
        drug_rxcui = drug.identifiers['rxnorm'].split(":",1)[1].strip()
        source_element_id = drug.id.strip()
        query7 = """
            SELECT DISTINCT
                unii_lookup.PT,
                unii_lookup.RXCUI,
                unii_lookup.PUBCHEM,
                unii_lookup.NCBI,
                substances._name,
                relatedSubstances._name AS related_substance,
                relatedSubstances.uuid AS related_substance_uuid,
                relatedSubstances.UNII AS related_substance_unii,
                relatedSubstances.substanceClass AS related_substance_class,
                relationships.type AS relationships_type,
                relationships.qualification,
                relationships.amount_average AS average,
                relationships.amount_high AS high,
                relationships.amount_low AS low,
                relationships.amount_units,
                unii_lookup.INCHIKEY AS InChiKey,
                unii_lookup.INGREDIENT_TYPE
            FROM unii_lookup
            JOIN substances ON unii_lookup.UNII = substances.UNII
            LEFT JOIN relationships ON substances.uuid = relationships.substance_id
            JOIN substances AS relatedSubstances ON relationships.relatedSubstance_id = relatedSubstances.uuid
            WHERE
                relationships.type LIKE ("%ACTIVE%") 
                AND NOT relationships.type LIKE ("%INACTIVE%")
                AND NOT relationships.type LIKE ("%PARENT->%")
                AND NOT relationships.type LIKE ("%PRODRUG->%")
                AND NOT relationships.type LIKE ("%RACEMATE->%")
                AND NOT relationships.type LIKE ("%SUBSTANCE->%")  
                AND NOT relationships.type LIKE ("%METABOLITE ACTIVE%") 
                AND NOT relationships.type LIKE ("%METABOLITE LESS ACTIVE%") 
                AND NOT relationships.type LIKE ("%ACTIVE CONSTITUENT ALWAYS PRESENT%")
                AND RXCUI = ?; 
        """
        connection = Inxight_Drugs_DataSupply.get_db() 
        cur7 = connection.execute(query7, (drug_rxcui,))

        for row in cur7.fetchall():                         # loop for each related substance found
            id = "UNII:"+str(row['related_substance_unii'])
            uuid = row['related_substance_uuid']
            identifiers = {'unii':id}
            if row['InChiKey']:
                identifiers['inchikey'] = row['InChiKey']
            if  (row['PUBCHEM']):
                identifiers["pubchem"]  = "CID:" +  row['PUBCHEM'] 
            name = row['related_substance']
            biolink_class = Inxight_Drugs_DataSupply.get_biolink_class( row['related_substance_class'], row['InChiKey'])
            relationships_type = row['relationships_type']
            if  row['RXCUI'] and biolink_class == 'Drug':
                identifiers["rxnorm"]  = "RXCUI:" +  row['RXCUI'] 
            substance = Element(
                    id = id,
                    biolink_class = biolink_class,
                    identifiers = identifiers,
                    names_synonyms = [Names(name=name,
                                            synonyms=[],
                                            source=SOURCE)], # add name & later synonyms from the database
                    attributes = [],
                    connections = [],
                    source = self.info.name
            )
          # Append synonyms to the substance
            Inxight_Drugs_DataSupply.get_names_synonyms(uuid, substance)
            relationship  = Connection(
                            source_element_id = source_element_id,
                            type = relationships_type,
                            relation = "has_active_ingredient",
                            evidence_type = "",
                            attributes = []
                            )
            if(row['qualification']):
            #   active ingredients attributes
                attributes_list= ['average', 'high', 'low']
                for attribute in attributes_list:
                    if row[attribute] is not None and len(row[attribute].strip()) > 0:
                        name  = attribute + ' ' + str(row['qualification']) + ' (' + str(row['amount_units']) + ')'
                        value = str(row[attribute])
                        relationship.attributes.append(
                        Attribute(
                            provided_by=self.info.name,
                            name  = name,
                            value = value,
                            source= SOURCE,
                            type  = name
                            )
                        )
            substance.connections.append(relationship)
            if biolink_class != 'ignore':    # the ingredient is not a "concept"
                related_list.append(substance)


    def get_protein_info(self, uuid, substance):
        """
            Add protein information to attributes
        """
        query8 = """
                SELECT DISTINCT
                    substances.uuid,
                    proteinType,
                    proteinSubType,
                    sequenceType,
                    sequenceOrigin,
                    disulfideLinks,
                    glycosylationType,
                    sequence,
                    length
                FROM substances
                JOIN proteins ON substances.uuid = proteins.substance_id
                JOIN protein_sequences ON proteins.uuid = protein_sequences.protein_id
                WHERE substances.uuid = ?;
            """
        connection = Inxight_Drugs_DataSupply.get_db() 
        cur8 = connection.execute(query8, (uuid,))
        for row in cur8.fetchall():
        #   Append additional attributes collected from Inxight:Drugs substances table 
            attributes_list= ['proteinType', 'proteinSubType', 'sequenceType', 'sequenceOrigin', 'disulfideLinks', 'glycosylationType', 'sequence', 'length']
            for attribute in attributes_list:
                if row[attribute] is not None and len(str(row[attribute]).strip())>0:
                    substance.attributes.append(
                    Attribute(
                        provided_by=self.info.name,
                        name= attribute,
                        value= str(row[attribute]),
                        source= SOURCE,
                        type= attribute
                    )
                )           


    def get_nucleicAcid_info(self, uuid, substance):
        """
            Add Nucleic Acid information to attributes
        """
        query9 = """
            SELECT DISTINCT
                substances.uuid,
                nucleicAcidType,
                sequenceType,
                sequenceOrigin,
                sequence,
                length
            FROM substances
            JOIN nucleic_acids ON substances.uuid = nucleic_acids.substance_id
            JOIN nucleic_acid_sequences ON nucleic_acids.uuid = nucleic_acid_sequences.nucleic_acid_id
            WHERE substances.uuid = ?;
            """
        connection = Inxight_Drugs_DataSupply.get_db() 
        cur9 = connection.execute(query9, (uuid,))
        for row in cur9.fetchall():
        #   Append additional attributes collected from Inxight:Drugs substances table 
            attributes_list= ['nucleicAcidType', 'sequenceType', 'sequenceOrigin',  'sequence', 'length']
            for attribute in attributes_list:
                if row[attribute] is not None and len(str(row[attribute]).strip())>0:
                    substance.attributes.append(
                    Attribute(
                        provided_by=self.info.name,
                        name= attribute,
                        value= str(row[attribute]),
                        source= SOURCE,
                        type= attribute
                    )
                )         

    def get_components(self, relationship_list, substance):
        substance_unii = substance.identifiers['unii'].split(":",1)[1].strip()
        source_element_id = substance.identifiers['unii']
        """
            Get omponents that are "part of" the substance mixture,
            so append components to the relationship_list
            and annotate their Connection per biolink:
            (https://biolink.github.io/biolink-model/docs/part_of)
        """
        query13 = """
            SELECT 
                substances._name AS substance_name,
                component_substances.uuid AS component_uuid,
                component_substances._name AS component_substance,
                component_substances.UNII AS component_substance_unii,
                component_substances.substanceClass,
                unii_lookup.RXCUI AS component_RXCUI,
                unii_lookup.PUBCHEM AS component_PUBCHEM,
                unii_lookup.INCHIKEY AS component_InChiKey,
                unii_lookup.NCBI AS component_NCBI
            FROM substances
            JOIN mixtures ON substances.mixture = mixtures.uuid
            JOIN components ON mixtures.uuid = components.mixture_id
            JOIN substances AS component_substances ON components.refuuid = component_substances.uuid
            LEFT JOIN unii_lookup ON component_substances.UNII = unii_lookup.UNII 
            WHERE substances.UNII = ?;
            """
        connection = Inxight_Drugs_DataSupply.get_db() 
        cur13 = connection.execute(query13, (substance_unii,))
        for row in cur13.fetchall():                         # loop for each component substance found
            id = "UNII:"+str(row['component_substance_unii'])
            name = row['component_substance']
        #   Create identifiers by annotating ids with appropriate CURIE prefix
            identifiers = {'unii':id}
            if  (row['component_InChiKey']):
                identifiers["inchikey"]  = row['component_InChiKey']    
            if  (row['component_PUBCHEM']):
                identifiers["pubchem"]  = "CID:" +  row['component_PUBCHEM'] 
            
            biolink_class = Inxight_Drugs_DataSupply.get_biolink_class( row['substanceClass'], row['component_InChiKey'])
            if  row['component_RXCUI'] and biolink_class == 'Drug':
                    identifiers["rxnorm"]  = "RXCUI:" +  row['component_RXCUI'] 

            connection = Connection(
                                    source_element_id = source_element_id,
                                    type = 'part_of',
                                    relation = 'part_of',
                                    evidence_type = "",
                                    attributes = []
                                )
            component = Element(
                id = id,
                biolink_class = biolink_class,
                identifiers = identifiers,
                names_synonyms = [Names(name=name,
                                        synonyms=[],
                                        source=SOURCE)], # add name & later synonyms from the database
                attributes = [],
                connections = [connection],
                source = self.info.name
            )
            if biolink_class != 'ignore':
                relationship_list.append(component)


    def get_mixtures(self, relationship_list, substance):
        substance_unii = substance.identifiers['unii'].split(":",1)[1].strip()
        source_element_id = substance.identifiers['unii']
        """
            Get mixtures that "has part" that includes the substance as a component,
            so append any mixtures to the relationship_list
            and annotate their Connection per biolink: 
            (https://biolink.github.io/biolink-model/docs/has_part.html)
        """
        query14 = """
            SELECT 
                substances._name AS substance_name,
                mixture_substances.uuid AS mixture_uuid,
                mixture_substances._name AS mixture_substance,
                mixture_substances.UNII AS mixture_substance_unii,
                mixture_substances.substanceClass,
                unii_lookup.RXCUI AS mixture_RXCUI,
                unii_lookup.PUBCHEM AS mixture_PUBCHEM,
                unii_lookup.INCHIKEY AS mixture_InChiKey,
                unii_lookup.NCBI AS mixture_NCBI
            FROM substances
            JOIN components ON substances.uuid = components.refuuid
            JOIN mixtures ON components.mixture_id = mixtures.uuid
            JOIN substances AS mixture_substances ON mixtures.uuid = mixture_substances.mixture
            LEFT JOIN unii_lookup ON mixture_substances.UNII = unii_lookup.UNII 
            WHERE substances.UNII = ?   ;
            """
        connection = Inxight_Drugs_DataSupply.get_db() 
        cur14 = connection.execute(query14, (substance_unii,))
        for row in cur14.fetchall():                         # loop for each mixture substance found
            id = "UNII:"+str(row['mixture_substance_unii'])
            name = row['mixture_substance']
        #   Create identifiers by annotating ids with appropriate CURIE prefix
            identifiers = {'unii':id}
            if  (row['mixture_InChiKey']):
                identifiers["inchikey"]  = row['mixture_InChiKey']    
            if  (row['mixture_PUBCHEM']):
                identifiers["pubchem"]  = "CID:" +  row['mixture_PUBCHEM'] 
            
            biolink_class = Inxight_Drugs_DataSupply.get_biolink_class( row['substanceClass'], row['mixture_InChiKey'])
            if  row['mixture_RXCUI'] and biolink_class == 'Drug':
                    identifiers["rxnorm"]  = "RXCUI:" +  row['mixture_RXCUI'] 

            connection = Connection(
                                    source_element_id = source_element_id,
                                    type = 'has_part',
                                    relation = 'has_part',
                                    evidence_type = "",
                                    attributes = []
                                )
            mixture = Element(
                id = id,
                biolink_class = biolink_class,
                identifiers = identifiers,
                names_synonyms = [Names(name=name,
                                        synonyms=[],
                                        source=SOURCE)], # add name & later synonyms from the database
                attributes = [],
                connections = [connection],
                source = self.info.name
            )
            if biolink_class != 'ignore':
                relationship_list.append(mixture)





    def get_relationship_types(self, json_obj, search_string):  
        if search_string is not None:
            search = search_string
        else: 
            search = '1 = 1'
        """
            get all the relationship types of substances
        """
        query10 = """
            SELECT DISTINCT
                relationships.type
            FROM relationships 
            WHERE {search}
            GROUP BY relationships.type;
            """.format(search=search)
        connection = sqlite3.connect("data/Inxightdb.db",
                    detect_types=sqlite3.PARSE_DECLTYPES
        ) # SQLite database file is located in the python-flask-server/data directory
        connection.row_factory = sqlite3.Row
        cur10 = connection.execute(query10)
        json_obj["knowledge_map"]["predicates"][0]["relations"].clear()  # step 1, clear the list of old relations
        for row in cur10.fetchall():
        #   step 2, fill the list of relations 
            json_obj["knowledge_map"]["predicates"][0]["relations"].append(row["type"])


    def get_substance_counts(self, json_obj):  
        """
            count all the undeprecated rows in substances table
        """
        query11 = """
            SELECT COUNT ( DISTINCT uuid ) AS "Number of substances" 
            FROM substances;
            """
        connection = sqlite3.connect("data/Inxightdb.db",
                    detect_types=sqlite3.PARSE_DECLTYPES
        ) # SQLite database file is located in the python-flask-server/data directory
        connection.row_factory = sqlite3.Row
        cur11 = connection.execute(query11)
        json_obj["knowledge_map"]["nodes"]["ChemicalSubstance"]["count"] = -1  # step 1, clear the old count
        for row in cur11.fetchall():
        #   step 2, fill the count value 
            json_obj["knowledge_map"]["nodes"]["ChemicalSubstance"]["count"] = (row["Number of substances"])


    def get_drug_counts(self, json_obj):  
        """
            count all the substances that are drugs
        """
        query12 = """
            SELECT COUNT ( DISTINCT uuid ) AS "Number of drugs" 
            FROM substances
            JOIN unii_lookup ON substances.UNII = unii_lookup.UNII
            WHERE NOT RXCUI ISNULL AND LENGTH(RXCUI) > 0;
            """
        connection = sqlite3.connect("data/Inxightdb.db",
                    detect_types=sqlite3.PARSE_DECLTYPES
        ) # SQLite database file is located in the python-flask-server/data directory
        connection.row_factory = sqlite3.Row
        cur12 = connection.execute(query12)
        json_obj["knowledge_map"]["nodes"]["Drug"]["count"] = -1  # step 1, clear the old count
        for row in cur12.fetchall():
        #   step 2, fill the count value 
            json_obj["knowledge_map"]["nodes"]["Drug"]["count"] = (row["Number of drugs"])


       
