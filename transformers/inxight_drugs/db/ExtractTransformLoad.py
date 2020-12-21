############################################################ 
# In this file, there are three classes, each with their own
# Single Responsibility:
# 
#   1. Extracts data from the Inxight:Drugs REST API
#   2. Transforms (translates) the extracted data into a form
#       ready for persistence into a relational database
#   3. Loads (persists) data into the Inxight_Drugs database
#
# HOW TO USE:
# Sequentially uncomment the function calls in the main() 
# function and execute as instructed in any of the associated 
# notes
############################################################


accimport requests
import sqlite3
import json
request_headers = {}


###############################################################
# This class Extracts data from the Inxight REST API
###############################################################
class Extractor():

    def downloadStructureJSON(api_url, done):
        print("downloading")
        request_headers = "application/json"
        response = requests.get(api_url, request_headers)
        json_obj = json.loads(response.content.decode('utf-8'))
        if done == False:
            global jsonTemp 
            jsonTemp = json_obj["content"]
        for content in json_obj["content"]:
            if done == True:
                jsonTemp.append(content)
        if json_obj.get("nextPageUri"):
            Extractor.downloadStructureJSON(json_obj["nextPageUri"], True)
            api_url = None
        else:
            # save JSON Object json_obj into a json file.
            with open('structure.json', 'w') as json_file:
                json.dump(jsonTemp, json_file)
            print("DONE")


    def readStructureJSONfromFile(filePath):
        dataframe = list()
        with open(filePath) as f:
            json_obj = json.load(f)
        for content in json_obj["content"]:
            id                = None
            digest            = None
            smiles            = None
            formula           = None
            opticalActivity   = None
            atropisomerism    = None
            stereoCenters     = 0
            definedStereo     = 0
            ezCenters         = 0
            charge            = 0
            mwt               = 0.0
            stereochemistry   = None
            InChIKey          = None
            stereoComments    = None
            propertiesData = None 
            if  content.get("deprecated") == False:
                id = content.get("id")
                digest = content.get("digest")
                smiles = content.get("smiles")
                formula  = content.get("formula")
                opticalActivity   = content.get("opticalActivity")
                atropisomerism    = content.get("atropisomerism")
                stereoCenters     = content.get("stereoCenters")
                definedStereo     = content.get("definedStereo")
                ezCenters         = content.get("ezCenters")
                charge            = content.get("charge")
                mwt               = content.get("mwt")
                stereochemistry   = content.get("stereochemistry") 
                stereoComments    = content.get("stereoComments")  
            #   Tuple of all structure column data           
                data = (id, digest, smiles, formula, opticalActivity, atropisomerism, 
                    stereoCenters, definedStereo, ezCenters, charge, mwt, stereochemistry, stereoComments)
                dataframe.append(data)
        # end for-loop
        # persist all collected data
        InxightDataLoader.persistStructureData(dataframe)


#   filePath = location of Code JSON file
    def readCodeJSONfromFile(filePath):
        dataframe = list()
        with open(filePath) as f:
            json_obj = json.load(f)
        for content in json_obj["content"]:
            uuid            = None
            _type           = None
            codeSystem      = None
            comments        = None
            code            = None
            url             = None
            codeText        = None
            
            if  content.get("deprecated") == False:
                uuid = content.get("uuid")
                _type = content.get("type")
                codeSystem    = content.get("codeSystem")
                comments      = content.get("comments")
                code          = content.get("code")
                url           = content.get("url")
                codeText      = content.get("codeText") 
            #   Tuple of all codes column data           
                data = (uuid, _type, codeSystem, comments, 
                    code, url, codeText)
                dataframe.append(data)
        # end for-loop
        # persist all collected data
        InxightDataLoader.persistCodeData(dataframe)


#   filePath = location of Name JSON file
    def readNameJSONfromFile(filePath):
        dataframe = list()
        with open(filePath) as f:
            json_obj = json.load(f)
        for content in json_obj["content"]:
            uuid              = None
            name              = None
            _type             = None
            preferred         = None
            displayName       = None

            if  content.get("deprecated") == False:
                uuid  = content.get("uuid")
                name  = content.get("name")
                _type = Transformer.decodeNameTypes(content.get("type"))
                preferred        = content.get("preferred")
                displayName      = content.get("displayName")
            #   Tuple of all names column data           
                data = (uuid, name, _type, preferred, displayName)
                dataframe.append(data)
        # end for-loop
        # persist all collected data
        InxightDataLoader.persistNameData(dataframe)


#   filePath = location of Reference JSON file
    def readReferenceJSONfromFile(filePath):
        dataframe = list()
        with open(filePath) as f:
            json_obj = json.load(f)
        for content in json_obj["content"]:
            uuid            = None
            citation        = None
            id              = None
            docType         = None
            publicDomain    = None
            url             = None
            uploadedFile    = None
            
            if  content.get("deprecated") == False:
                uuid     = content.get("uuid")
                citation = content.get("citation")
                id       = content.get("id")
                docType  = content.get("docType")
                publicDomain = content.get("publicDomain")
                url          = content.get("url")
                uploadedFile = content.get("uploadedFile") 
            #   Tuple of all references column data           
                data = (uuid, citation, id, docType, 
                    publicDomain, url, uploadedFile)
                dataframe.append(data)
        # end for-loop
        # persist all collected data
        InxightDataLoader.persistReferenceData(dataframe)


# Fix problem with "nextPageUri" from the Inxight response
    def repairURL(uri):
        uriText = str(uri)
        uriList = uriText.split("&application/json")
        return uriList[0] + uriList[1]


# Generic function - iterative instead of recursive
    def downloadJSON(api_url, filename, initialize):
        print("downloading iteratively")
        request_headers = "application/json"
        download = True
        #############################################################
        while download == True:
            response = requests.get(api_url, request_headers)
            json_obj = json.loads(response.content.decode('utf-8'))
            if initialize == True:                      # initialize the JSON for appending data
                global jsonTemp 
                jsonStr = '{"content": []}'    
                jsonTemp = json.loads(jsonStr)
                initialize = False
            for content in json_obj["content"]:         # add content to the JSON
                jsonTemp["content"].append(content)
            if json_obj.get("nextPageUri"):
                api_url = Extractor.repairURL(json_obj["nextPageUri"])      # need to repair the uri
                print(api_url)
            else:
                download = False                        # stop downloading
                print("DONE")
        #############################################################
        # save JSON Object json_obj into a json file.
        with open(filename, 'w') as json_file:
            json.dump(jsonTemp, json_file)


    def readMixture_in_SubstanceJSONfromFile(filePath):
        dataframe_mixtures = list()
        dataframe_components = list()
        print("extracting")
        with open(filePath) as f:
            json_obj = json.load(f)
        for content in json_obj["content"]:
            parentSubstance_refuuid = None
            if  content.get("deprecated") == False:                 # if substance is not deprecated
                if content.get("mixture"):     
                    mixture_id    = content.get("mixture").get("uuid")
                    if(content.get("mixture").get("parentSubstance")):
                        parentSubstance_refuuid = content.get("mixture").get("parentSubstance").get("refuuid")
                    components = content.get("mixture").get("components")
                #   reminder: each mixture
                    mixtures_data = (mixture_id, parentSubstance_refuuid)
                    dataframe_mixtures.append(mixtures_data)
                    for component in components:
                    #   reminder: each component is different by uuid, substance.refuuid and type
                        components_data = (component.get("uuid"), mixture_id, component.get("substance").get("refuuid"), component.get("type") )
                        dataframe_components.append(components_data) 
        InxightDataLoader.persistMixturesData(dataframe_mixtures)
        InxightDataLoader.persistComponentsData(dataframe_components)


    def readSubstanceJSONfromFile(filePath):
        dataframe = list()
        df_properties = list()
        print("extracting")
        with open(filePath) as f:
            json_obj = json.load(f)
        for content in json_obj["content"]:
            uuid            = None                
            definitionType  = None
            definitionLevel = None
            substanceClass  = None
            status          = None
            approvalID      = None
            UNII            = None
            structurallyDiverse = None
            protein             = None
            nucleicAcid         = None
            _names              = None
            _references         = None
            _codes              = None
            _relationships      = None
            _name               = None
            _properties         = None
            mixture             = None
            _moieties           = None
            structure           = None
            polymer             = None
            propertiesData = None
            if  content.get("deprecated") == False:
                uuid = content.get("uuid")
                definitionType = content.get("definitionType")
                definitionLevel = content.get("definitionLevel")
                substanceClass = content.get("substanceClass")
                status = content.get("status")
                approvalID = content.get("approvalID")
                UNII = content.get("_approvalIDDisplay")
                _name  = content.get("_name")
                _references = content.get("_references").get("href")
                if content.get("structurallyDiverse"):
                    structurallyDiverse = content.get("structurallyDiverse").get("uuid")
                if content.get("protein"):
                    protein = content.get("protein").get("uuid")
                if content.get("nucleicAcid"):
                    nucleicAcid = content.get("nucleicAcid").get("uuid")
                if content.get("_names"):
                    _names = content.get("_names").get("href")
                if content.get("_codes"):
                    _codes = content.get("_codes").get("href")
                if content.get("_relationships"):
                    _relationships = content.get("_relationships").get("href")
                if content.get("_properties"):    
                    _properties  = content.get("_properties").get("href")
                    propertiesData = (content.get("uuid"), content.get("_properties").get("href"))
                    df_properties.append(propertiesData)
                if content.get("mixture"):     
                    mixture  = content.get("mixture").get("uuid")
                if content.get("_moieties"):
                    _moieties  = content.get("_moieties").get("href")
                if content.get("structure"):
                    structure  = content.get("structure").get("id")
                if content.get("polymer"):
                    polymer  = content.get("polymer").get("uuid")
            #   Tuple of all substance column data
                data = (uuid, definitionType, definitionLevel, substanceClass, 
                    status, approvalID, UNII, structurallyDiverse, protein, nucleicAcid, _names,  _references,
                    _codes, _relationships, _name, _properties, mixture, _moieties, structure, polymer)
                dataframe.append(data)
        # end for-loop
        # persist all collected data
        InxightDataLoader.persistSubstanceData(dataframe)
        print("Done")
    #   manipulate properties data and persist as substance attributes data
        Transformer.wrangle_substance_properties(df_properties)


    def readSubstanceJSON(api_url):
        dataframe = list()
        df_properties = list()
        print("extracting")
        request_headers = "application/json"
        response = requests.get(api_url, request_headers)
        json_obj = json.loads(response.content.decode('utf-8'))
        for content in json_obj["content"]:
            uuid            = None                
            definitionType  = None
            definitionLevel = None
            substanceClass  = None
            status          = None
            approvalID      = None
            UNII            = None
            structurallyDiverse = None
            protein             = None
            nucleicAcid         = None
            _names              = None
            _references         = None
            _codes              = None
            _relationships      = None
            _name               = None
            _properties         = None
            mixture             = None
            _moieties           = None
            structure           = None
            polymer             = None

            propertiesData = None
            if  content.get("deprecated") == False:
                uuid = content.get("uuid")
                definitionType = content.get("definitionType")
                definitionLevel = content.get("definitionLevel")
                substanceClass = content.get("substanceClass")
                status = content.get("status")
                approvalID = content.get("approvalID")
                UNII = content.get("_approvalIDDisplay")
                _name  = content.get("_name")
                _references = content.get("_references").get("href")
                if content.get("structurallyDiverse"):
                    structurallyDiverse = content.get("structurallyDiverse").get("uuid")
                if content.get("protein"):
                    protein = content.get("protein").get("uuid")
                if content.get("nucleicAcid"):
                    nucleicAcid = content.get("nucleicAcid").get("uuid")
                if content.get("_names"):
                    _names = content.get("_names").get("href")
                if content.get("_codes"):
                    _codes = content.get("_codes").get("href")
                if content.get("_relationships"):
                    _relationships = content.get("_relationships").get("href")
                if content.get("_properties"):    
                    _properties  = content.get("_properties").get("href")
                    propertiesData = (content.get("uuid"), content.get("_properties").get("href"))
                    df_properties.append(propertiesData)
                if content.get("mixture"):     
                    mixture  = content.get("mixture").get("uuid")
                if content.get("_moieties"):
                    _moieties  = content.get("_moieties").get("href")
                if content.get("structure"):
                    structure  = content.get("structure").get("id")
                if content.get("polymer"):
                    polymer  = content.get("polymer").get("uuid")
            #   Tuple of all substance column data
                data = (uuid, definitionType, definitionLevel, substanceClass, 
                    status, approvalID, UNII, structurallyDiverse, protein, nucleicAcid, _names,  _references,
                    _codes, _relationships, _name, _properties, mixture, _moieties, structure, polymer)

                dataframe.append(data)
        # end for-loop
        # persist all collected data
        InxightDataLoader.persistSubstanceData(dataframe)
        if json_obj.get("nextPageUri"):
            print(json_obj.get("nextPageUri"))
            Extractor.readSubstanceJSON(json_obj["nextPageUri"], True)
            api_url = None
            request_headers = None
        else:
            print("Done")
    #   manipulate properties data and persist as substance attributes data
        Transformer.wrangle_substance_properties(df_properties)


    def readRelationshipsfromFile(filePath):
        request_headers = "application/json"
        for content in json_obj["content"]:
            if (content.get("_relationships")):
                api_url = content["_relationships"]["href"]
        response = requests.get(api_url, request_headers)
        json_obj_relate = json.loads(response.content.decode('utf-8'))
        for item in json_obj_relate:
            for key in item.keys():
                keySet.add(key)


    def readNucleicAcidfromFile(filePath):
        dataframe_nucleic_acid = list()
        dataframe_sequence = list()
        dataframe_sugar = list()
        with open(filePath) as f:
            json_obj = json.load(f)
        for content in json_obj["content"]:
            data_n_acid = None
            if (content.get("nucleicAcid") and content.get("nucleicAcid").get("deprecated") == False):
                data_n_acid = (content.get("nucleicAcid").get("uuid"), 
                               content.get("uuid"), 
                               content.get("nucleicAcid").get("sequenceType"), 
                               content.get("nucleicAcid").get("nucleicAcidType"),
                               content.get("nucleicAcid").get("sequenceOrigin"))
                dataframe_nucleic_acid.append(data_n_acid)
                for sequence in content.get("nucleicAcid").get("subunits"):  # for persisting to nucleic_acid_sequence table
                    data_seq = None
                    if(sequence.get("deprecated") == False):
                        data_seq = (sequence.get("uuid"),
                                    content.get("nucleicAcid").get("uuid"),
                                    int (sequence.get("subunitIndex")),
                                    sequence.get("sequence"),
                                    int( sequence.get("length") )
                                    )
                        dataframe_sequence.append(data_seq)
                for sugar in content.get("nucleicAcid").get("sugars"):
                    data_sugar = None
                    if (sugar.get("deprecated") == False):
                        data_sugar = (sugar.get("uuid"),
                                      content.get("nucleicAcid").get("uuid"),
                                      sugar.get("sugar"),
                                      sugar.get("sitesShorthand"))
                        dataframe_sugar.append(data_sugar)
        InxightDataLoader.persistNucleicAcids(dataframe_nucleic_acid)
        InxightDataLoader.persistSequences(dataframe_sequence)
        InxightDataLoader.persistSugars(dataframe_sugar)


    def readTopLevelReferencesfromFile(filePath, entity_type):
            request_headers = "application/json"
            dataframe_references = list()
            with open(filePath) as f:
                json_obj = json.load(f)
            print("extracting")
            for content in json_obj["content"]:
                data_refs = None
                if (content.get("_references")):
                    response = requests.get(content.get("_references").get("href"), request_headers)
                    json_obj_references = json.loads(response.content.decode('utf-8'))
                    for reference in json_obj_references:
                        data_refs = (content.get("uuid"), reference.get("uuid"), entity_type)
                        dataframe_references.append(data_refs)
                elif (content.get("references")):
                    uuid = None
                    if(content.get("uuid")):
                        uuid = content.get("uuid")
                    elif (content.get("id")):
                        uuid = content.get("id")
                    for reference in content.get("references"):
                        data_refs = (uuid, reference, entity_type)
                        dataframe_references.append(data_refs)
            print("done")
            return dataframe_references


    def readProteinfromFile(filePath):
        dataframe_protein = list()
        dataframe_sequence = list()
        with open(filePath) as f:
            json_obj = json.load(f)
        for content in json_obj["content"]:
            data_protein = None
            _disulfideLinks = None
            _glycosylationType = None
            if (content.get("protein") and content.get("protein").get("deprecated") == False):
                if content.get("protein").get("_disulfideLinks"):
                    _disulfideLinks = content.get("protein").get("_disulfideLinks").get("shorthand")
                if content.get("protein").get("_glycosylation").get("type"):
                    _glycosylationType = content.get("protein").get("_glycosylation").get("type")
                data_protein = (content.get("protein").get("uuid"), 
                               content.get("uuid"), 
                               content.get("protein").get("proteinType"),
                               content.get("protein").get("proteinSubType"),
                               content.get("protein").get("sequenceType"), 
                               content.get("protein").get("sequenceOrigin"),
                               _disulfideLinks,
                               _glycosylationType)
                dataframe_protein.append(data_protein)
                for sequence in content.get("protein").get("subunits"):  # for persisting to protein_sequences table
                    data_seq = None
                    if(sequence.get("deprecated") == False):
                        data_seq = (sequence.get("uuid"),
                                    content.get("protein").get("uuid"),
                                    int (sequence.get("subunitIndex")),
                                    sequence.get("sequence"),
                                    int( sequence.get("length") )
                                    )
                        dataframe_sequence.append(data_seq)
        InxightDataLoader.persistProteins(dataframe_protein)
        InxightDataLoader.persistProteinSequences(dataframe_sequence)


    def readStructurallyDiversefromFile(filePath):
        dataframe_diverse = list()
        with open(filePath) as f:
            json_obj = json.load(f)
        for content in json_obj["content"]:
            data_diverse = None
            developmentalStage = None
            infraSpecificName  = None
            fractionName       = None
            part               = None
            infraSpecificType  = None
            fractionMaterialType  = None
            sourceMaterialState   = None
            hybridSpeciesMaternalOrganism  = None
            hybridSpeciesPaternalOrganism  = None
            if (content.get("structurallyDiverse") and content.get("structurallyDiverse").get("deprecated") == False):
                if content.get("structurallyDiverse").get("developmentalStage"):
                    developmentalStage = content.get("structurallyDiverse").get("developmentalStage")
                if content.get("structurallyDiverse").get("infraSpecificName"):
                    infraSpecificName = content.get("structurallyDiverse").get("infraSpecificName")
                if content.get("structurallyDiverse").get("fractionName"):
                    fractionName = content.get("structurallyDiverse").get("fractionName")
                for item in content.get("structurallyDiverse").get("part"):     # assuming there is only 1 part
                    part = item

                if content.get("structurallyDiverse").get("parentSubstance"):
                    parentSubstance = content.get("structurallyDiverse").get("parentSubstance").get("refuuid") 

                if content.get("structurallyDiverse").get("infraSpecificType"):
                    infraSpecificType = content.get("structurallyDiverse").get("infraSpecificType") 
                if content.get("structurallyDiverse").get("fractionMaterialType"):
                    fractionMaterialType = content.get("structurallyDiverse").get("fractionMaterialType")    
                if content.get("structurallyDiverse").get("sourceMaterialState"):
                    sourceMaterialState = content.get("structurallyDiverse").get("sourceMaterialState")                  
                if content.get("structurallyDiverse").get("hybridSpeciesMaternalOrganism"):
                    hybridSpeciesMaternalOrganism = content.get("structurallyDiverse").get("hybridSpeciesMaternalOrganism").get("refuuid") 
                if content.get("structurallyDiverse").get("hybridSpeciesPaternalOrganism"):
                    hybridSpeciesPaternalOrganism = content.get("structurallyDiverse").get("hybridSpeciesPaternalOrganism").get("refuuid")                   
                data_diverse = (content.get("structurallyDiverse").get("uuid"), 
                               content.get("uuid"), 
                               content.get("structurallyDiverse").get("sourceMaterialClass"),
                               content.get("structurallyDiverse").get("sourceMaterialType"),
                               developmentalStage,
                               infraSpecificName,
                               content.get("structurallyDiverse").get("organismFamily"),
                               content.get("structurallyDiverse").get("organismGenus"),
                               content.get("structurallyDiverse").get("organismSpecies"),
                               fractionName,
                               part,
                               content.get("structurallyDiverse").get("partLocation"),
                               parentSubstance,
                               infraSpecificType,
                               fractionMaterialType,
                               sourceMaterialState,
                               hybridSpeciesMaternalOrganism,
                               hybridSpeciesPaternalOrganism)
                dataframe_diverse.append(data_diverse)
        InxightDataLoader.persistStructurallyDiverse(dataframe_diverse)


    def readPolymerfromFile(filePath):
        dataframe_polymers = list()
        with open(filePath) as f:
            json_obj = json.load(f)
        for content in json_obj["content"]:
            data_polymers   = None
            polymerClass    = None
            polymerSubclass = None
            polymerGeometry = None
            sourceType      = None
            if (content.get("polymer") and content.get("polymer").get("deprecated") == False):
                if content.get("polymer").get("classification"):
                    polymerClass    = content.get("polymer").get("classification").get("polymerClass")
                    polymerGeometry = content.get("polymer").get("classification").get("polymerGeometry")
                    sourceType      = content.get("polymer").get("classification").get("sourceType")
                    for subclass in content.get("polymer").get("classification").get("polymerSubclass"):
                        polymerSubclass = subclass                  # assuming there is only 1 polymerSubclass
                data_polymers = (content.get("polymer").get("uuid"), 
                               content.get("uuid"), 
                               polymerClass,
                               polymerSubclass,
                               polymerGeometry,
                               sourceType,
                               content.get("polymer").get("displayStructure").get("id"),
                               content.get("polymer").get("idealizedStructure").get("id")
                            )
                dataframe_polymers.append(data_polymers)
        InxightDataLoader.persistPolymer(dataframe_polymers)


    def readNamesIDfromFile(filePath):
        request_headers = "application/json"
        print("extracting")
        with open(filePath) as f:
            json_obj = json.load(f)
        for content in json_obj["content"]:
            uuid = None
            df_names = list()                
            if  content.get("deprecated") == False:
                uuid = content.get("uuid")
                _name = content.get("_name")
                if content.get("_names"):
                    response = requests.get(content.get('_names').get('href'), request_headers)
                    json_obj_names = json.loads(response.content.decode('utf-8'))
                    for name in json_obj_names:
                        data_name = None
                        if name.get("uuid"):
                            data_name = (uuid, name.get("uuid"))
                            df_names.append(data_name)
                InxightDataLoader.persistNameIds(df_names)





 


###############################################################
# This class Transforms data extracted from the Inxight REST API
###############################################################
class Transformer():

#   This function wrangles properties JSON data that can be inserted into the 
#   substance_attributes table, containing name-value pairs for substances.
#   In general, name = (value field name + name) and value = (value.field + value.units)
    def wrangle_substance_properties(df_properties): 
        df_name_value = list()
        request_headers = "application/json"

        for ind in df_properties:  # for each collected substance "properties"
            uuid = ind[0]          #  - the substance id
            api_url = ind[1]       #  - the href given for the _properties
            print(api_url)
            response = requests.get(api_url, request_headers)
            json_obj_props = json.loads(response.content.decode('utf-8'))
            for item in json_obj_props:
                if(item.get('parameters')):
                    for item2 in item.get('parameters'):  # there are multiple parameters with values 
                        if (item2.get('value')):          # sometimes 'parameters' has 'value' key, sometimes it does not.
                            keyList = list()
                            for key in item2['value'].keys():
                                if key not in ['uuid', 'created', 'createdBy', 'admin', 'lastEdited', 'lastEditedBy', 'deprecated', 'references', 'access', 'type', 'units']:
                                    keyList.append(key)
                            for newKey in keyList:
                                # e.g., newKey = high, low, or average
                                if item2.get('value').get('units'):
                                    try:
                                        data = (uuid, newKey + " " + item2['name'], str(item2['value'][newKey]) + " " + item2['value']['units'])
                                    except Exception as E:
                                        print('Error2', item2, E)
                                else:
                                    data = (uuid, newKey + " " + item2['name'], str(item2['value'][newKey]) )               
                        else:                             # there is no 'value' key under parameters
                            if (item2.get('name')):       # but there is a 'name' key
                                data = (uuid, item2['name'], item2['name'] )  
                        df_name_value.append(data) 

                if(item.get('value')):
                    keyList = list()
                    for key in item['value'].keys():
                        if key not in ['uuid', 'created', 'createdBy', 'admin', 'lastEdited', 'lastEditedBy', 'deprecated', 'references', 'access', 'type', 'units']:
                            keyList.append(key)
                    for newKey in keyList:
                        # e.g., newKey = high, low, or average
                        if item.get('value').get('units'):
                                data = (uuid, newKey + " " + item['name'], str(item['value'][newKey]) + " " + item['value']['units'])
                        else:
                                data = (uuid, newKey + " " + item['name'], str(item['value'][newKey]) )               
                        df_name_value.append(data)     
        InxightDataLoader.persistSubstanceAttributes(df_name_value)


#   This function wrangles structure hrefs into structure uuids
    def wrangle_structure_hrefs(df_hrefs): 
        print("wrangling")
        df_structures = list()
        for href in df_hrefs:
            request_headers = "application/json"
            response = requests.get(href[0], request_headers)
            json_obj = json.loads(response.content.decode('utf-8'))
            id_data = ( json_obj.get("id"), href[1] )         # structure id, substance id
            df_structures.append(id_data)
        return df_structures


    def decodeNameTypes(typeName):
        nameMap = {"GSRS Name":"GSRS Name",
                  "Other":"Other",
                  "Trivial Name":"Trivial Name",
                  "bn":"Brand Name",
                  "cd":"Code",
                  "cn":"Common Name",
                  "of": "Official Name",
                  "sys":"Systematic Name"}
        fullName = nameMap[typeName]
        return fullName


#   This function wrangles relationship hrefs into relationship data set
    def wrangle_relationship_hrefs(df_hrefs): 
        print("wrangling")
        df_relationships = list()
        
        for href in df_hrefs:
            uuid                  = None
            refuuid               = None
            orginatorUuid         = None       # same as uuid?
            _type                 = None 
            mediatorSubstance_id  = None 
            interactionType       = None  
            average               = None 
            high                  = None 
            low                   = None   
            units                 = None 
            qualification         = None
            comments              = None
            request_headers = "application/json"
            response = requests.get(href[0], request_headers)
            json_obj = json.loads(response.content.decode('utf-8'))
            for item in json_obj:
                if item.get("deprecated") == False:
                    uuid            = item.get("uuid")
                    refuuid         = item.get("relatedSubstance").get("refuuid")
                    orginatorUuid   = item.get("originatorUuid")
                    _type           = item.get("type")
                    if(item.get("mediatorSubstance")):
                        mediatorSubstance_id = item.get("mediatorSubstance").get("refuuid")
                    interactionType = item.get("interactionType")
                    if(item.get("amount")):
                        average = item.get("amount").get("average")
                        high    = item.get("amount").get("high")
                        low     = item.get("amount").get("low")
                        units   = item.get("amount").get("units")
                    if(item.get("qualification")):
                        qualification  = item.get("qualification")
                    comments= item.get("comments")
                    id_data = ( uuid, 
                                refuuid, 
                                orginatorUuid,   # same as uuid?
                                _type, 
                                mediatorSubstance_id, 
                                interactionType, 
                                qualification,
                                average, 
                                high,  
                                low,  
                                units,
                                comments,
                                href[1] )        # relationship id,... substance id
                df_relationships.append(id_data)
        return df_relationships


#   This function wrangles code hrefs into code uuids
    def wrangle_code_hrefs(df_hrefs): 
        print("wrangling")
        df_codes = list()
        for href in df_hrefs:
            request_headers = "application/json"
            response = requests.get(href[0], request_headers)
            json_obj = json.loads(response.content.decode('utf-8')) 
            for element in json_obj:
                id_data = ( href[1], element.get("uuid") )         #  substance id, code id
                df_codes.append(id_data)
        return df_codes










###############################################################
# This class contains common code for Loading data into the 
# Inxight_Drugs database for later access by MolePro Transformers
###############################################################
class InxightDataLoader():
    def get_db():
            db = sqlite3.connect("/Users/lchung/Documents/broadgit/scb-kp-dev/transformers/inxight_drugs/python-flask-server/data/Inxightdb.db",
                detect_types=sqlite3.PARSE_DECLTYPES
            ) # SQLite database file is located in the python-flask-server/data directory
            db.row_factory = sqlite3.Row
            return db


    def close_db(self, e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()


    def persistSubstanceData(df_substances):
        query1 = """ 
        INSERT INTO substances ( uuid, definitionType, definitionLevel, substanceClass, 
        status, approvalID, UNII, structurallyDiverse, protein, nucleicAcid, _names,  _references,
        _codes, _relationships, _name, _properties, mixture, _moieties, structure_id, polymer) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        connection = InxightDataLoader.get_db()   
        try:
            cursor = connection.executemany(query1, df_substances)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()


    def persistStructureData(df_structures):
        query2 = """ 
        INSERT INTO structures ( id, digest, smiles, formula, opticalActivity, atropisomerism, 
                    stereoCenters, definedStereo, ezCenters, charge, mwt, stereochemistry, stereoComments) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        connection = InxightDataLoader.get_db()   
        try:
            cursor = connection.executemany(query2, df_structures)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()


    def persistCodeData(df_codes):
        query5 = """ 
        INSERT INTO codes (uuid, type, codeSystem, comments, 
                    code, url, codeText)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        connection = InxightDataLoader.get_db()   
        try:
            cursor = connection.executemany(query5, df_codes)
        except Exception as E:
            print('Error in persistCodeData()', E)
        else:
            connection.commit()


    def persistNameData(df_names):
        query7 = """ 
        INSERT INTO names (uuid, name, type, preferred, displayName)
        VALUES (?, ?, ?, ?, ?)
        """
        connection = InxightDataLoader.get_db()   
        try:
            cursor = connection.executemany(query6, df_names)
        except Exception as E:
            print('Error in persistNameData()', E)
        else:
            connection.commit()


#(uuid, citation, id, docType, publicDomain, url, uploadedFile)
    def persistReferenceData(df_references):
        query7 = """ 
        INSERT INTO _references (uuid, citation, id, docType, publicDomain, url, uploadedFile)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        connection = InxightDataLoader.get_db()   
        try:
            cursor = connection.executemany(query7, df_references)
        except Exception as E:
            print('Error in persistReferenceData()', E)
        else:
            connection.commit()

    
#   temporary throwaway function to get all hrefs in substances.structure_id column
#   NOT a permanent solution
    def get_structures_hrefs():
        df_hrefs = list()
        query4 = """ 
            SELECT uuid, structure_id 
            FROM substances
            WHERE NOT structure_id ISNULL;
            """
        connection  = InxightDataLoader.get_db() 
        cur = connection.execute(query4)        
        for row in cur.fetchall():
            hrefs_links = (row['structure_id'],row['uuid'])
            df_hrefs.append(hrefs_links)    
        return df_hrefs


#   Replace temporary hrefs in substances.structure_id
    def updateSubstanceStructures(df_structures):
        query3 = """
        UPDATE substances
        SET structure_id = ?
        WHERE uuid= ?;
        """  
        connection = InxightDataLoader.get_db()   
        try:
            cursor = connection.executemany(query3, df_structures)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()   


#   This is a generic function and should be able to persist tuples of substance_id, name, and value
    def persistSubstanceAttributes(df_attributes):
        query2 = """ 
        INSERT INTO substance_attributes (substance_id, name, value) 
        VALUES (?, ?, ?)
        """
        connection = InxightDataLoader.get_db()   
        try:
            cursor = connection.executemany(query2, df_attributes)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()


#   function to get all UNII and uuid in substances table as step 1 to copy PubChem and InchiKey 
#   to corresponding Structure table columns
    def getUNII():
        query8 = """ 
            SELECT UNII, structure_id 
            FROM substances
            WHERE NOT structure_id ISNULL;
        """
        connection = InxightDataLoader.get_db()   
        try:
            cursor = connection.executemany(query2, df_attributes)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()


    def get_relationships_hrefs():
        df_hrefs = list()
        query9 = """ 
            SELECT uuid, _relationships 
            FROM substances
            WHERE NOT _relationships ISNULL;
            """
        connection  = InxightDataLoader.get_db() 
        cur = connection.execute(query9)        
        for row in cur.fetchall():
            hrefs_links = (row['_relationships'],row['uuid'])
            df_hrefs.append(hrefs_links)    
        return df_hrefs


    def persistRelationshipData(df_relationships):
        query10 = """ 
        INSERT INTO relationships (uuid, relatedSubstance_id, originatorUuid,type,mediatorSubstance_id,
                    interactionType, qualification, amount_average, amount_high, amount_low, amount_units,
                    comments, substance_id ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        connection = InxightDataLoader.get_db()   
        print("persisting")
        try:
            cursor = connection.executemany(query10, df_relationships)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()


    def  persistMixturesData(dataframe_mixtures):
        query11 = """ 
        INSERT INTO mixtures (uuid, parentSubstance_refuuid ) 
        VALUES (?,?)
        """
        connection = InxightDataLoader.get_db()   
        print("persisting")
        try:
            cursor = connection.executemany(query11, dataframe_mixtures)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()



    def  persistComponentsData(dataframe_components):
        query12 = """
        INSERT INTO components (uuid, mixture_id, refuuid, type)                 
        VALUES (?, ?, ?, ?)
        """
        connection = InxightDataLoader.get_db()   
        print("persisting")
        try:
            cursor = connection.executemany(query12, dataframe_components)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()


    #   Replace temporary hrefs in substances.code_id
    def updateSubstanceCodes(df_codes):
        query13 = """
        UPDATE substances
        SET code_id = ?
        WHERE uuid= ?;
        """  
        connection = InxightDataLoader.get_db()   
        try:
            cursor = connection.executemany(query13, df_codes)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()   


#   temporary throwaway function to get all hrefs in substances._code_id column
#   NOT a permanent solution
    def get_code_hrefs():
        df_hrefs = list()
        query12 = """ 
            SELECT uuid, code_id 
            FROM substances
            WHERE NOT code_id ISNULL;
            """
        connection  = InxightDataLoader.get_db() 
        cur = connection.execute(query12)        
        for row in cur.fetchall():
            hrefs_links = (row['code_id'],row['uuid'])
            df_hrefs.append(hrefs_links)    
        return df_hrefs

   
    def  persistCodesData(dataframe_codes):
        query13 = """
        INSERT INTO substance_codes (substance_id, code_id)                 
        VALUES (?, ?)
        """
        connection = InxightDataLoader.get_db()   
        print("persisting")
        try:
            cursor = connection.executemany(query13, dataframe_codes)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()


    def get_pubchem_inchikey():
        df_structures = list()
        query14 = """
        SELECT substances.UNII, substances.structure_id, PUBCHEM,INCHIKEY 
        FROM substances
        LEFT JOIN unii_lookup on substances.UNII = unii_lookup.UNII
        WHERE NOT substances.structure_id ISNULL;
        """
        connection  = InxightDataLoader.get_db() 
        cur = connection.execute(query14)  
        count = 0      
        for row in cur.fetchall():
            count = count + 1
            structure = ( row['INCHIKEY'], row['PUBCHEM'], row['structure_id'] )
            if(count < 20):
                print(structure)
            df_structures.append(structure)    
        return df_structures

    
    def updateStructures(df_pubchem_inchikey):
        query15 = """
        UPDATE structures
        SET inChIKey = ?, pubChem = ?
        WHERE id = ?;
        """  
        connection = InxightDataLoader.get_db()   
        try:
            cursor = connection.executemany(query15, df_pubchem_inchikey)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()   




    def  persistNucleicAcids(dataframe_nucleic_acid):
        query16 = """
        INSERT INTO nucleic_acids (uuid, substance_id, sequenceType, nucleicAcidType, sequenceOrigin)                 
        VALUES (?, ?, ?, ?, ?)
         """
        connection = InxightDataLoader.get_db()   
        print("persisting")
        try:
            cursor = connection.executemany(query16, dataframe_nucleic_acid)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()


    def  persistSequences(dataframe_sequence):
        query17 = """
        INSERT INTO nucleic_acid_sequences (uuid, nucleic_acid_id, subunitIndex, sequence, length)                 
        VALUES (?, ?, ?, ?, ?)
         """
        connection = InxightDataLoader.get_db()   
        print("persisting")
        try:
            cursor = connection.executemany(query17, dataframe_sequence)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()


    def  persistSugars(dataframe_sugar):
        query18 = """
        INSERT INTO nucleic_acid_sugars (uuid, nucleic_acid_id, sugar, sitesShorthand)                 
        VALUES (?, ?, ?, ?)
         """
        connection = InxightDataLoader.get_db()   
        print("persisting")
        try:
            cursor = connection.executemany(query18, dataframe_sugar)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()


    def  persistEntityReferences(dataframe_entity_references):
        query19 = """
        INSERT INTO entity_references (entity_id, reference_id, entity_type)                 
        VALUES (?, ?, ?)
         """
        connection = InxightDataLoader.get_db()   
        print("persisting")
        try:
            cursor = connection.executemany(query19, dataframe_entity_references)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()


    def  persistProteins(dataframe_protein):
        query20 = """
        INSERT INTO proteins (uuid, substance_id, proteinType, proteinSubType, sequenceType, sequenceOrigin, disulfideLinks, glycosylationType)                 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
         """
        connection = InxightDataLoader.get_db()   
        print("persisting")
        try:
            cursor = connection.executemany(query20, dataframe_protein)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()


    def  persistProteinSequences(dataframe_sequence):
        query21 = """
        INSERT INTO protein_sequences (uuid, protein_id, subunitIndex, sequence, length)                 
        VALUES (?, ?, ?, ?, ?)
         """
        connection = InxightDataLoader.get_db()   
        print("persisting")
        try:
            cursor = connection.executemany(query21, dataframe_sequence)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()


    def  persistStructurallyDiverse(dataframe_diverse):
        query22 = """
        INSERT INTO structurallyDiverse (uuid, substance_id, sourceMaterialClass, sourceMaterialType, developmentalStage, infraSpecificName, organismFamily, organismGenus,
    organismSpecies, fractionName, part, partLocation, parentSubstance_refuuid, infraSpecificType, fractionMaterialType,
    sourceMaterialState, hybridSpeciesMaternalOrganism, hybridSpeciesPaternalOrganism)                 
        VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
         """
        connection = InxightDataLoader.get_db()   
        print("persisting")
        try:
            cursor = connection.executemany(query22, dataframe_diverse)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()


    def  persistPolymer(dataframe_polymer):
        query23 = """
        INSERT INTO polymers (uuid, substance_id, polymerClass, polymerSubclass, polymerGeometry, sourceType, displayStructure_id, idealizedStructure_id)                 
        VALUES ( ?, ?, ?, ?, ?, ?, ?, ?)
         """
        connection = InxightDataLoader.get_db()   
        print("persisting")
        try:
            cursor = connection.executemany(query23, dataframe_polymer)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()


    def persistNameIds(dataframe_name):
        query24 = """
        INSERT INTO substance_names (substance_id, name_id)                 
        VALUES (?, ?)
         """
        connection = InxightDataLoader.get_db()   
        print("persisting")
        try:
            cursor = connection.executemany(query24, dataframe_name)
        except Exception as E:
            print('Error', E)
        else:
            connection.commit()



def main():
###########################################################################
# Sequentially uncomment the function calls in this main() function 
# and execute as instructed in any of the associated notes
# Then RE-COMMENT the executed function before uncommenting the next 
# function
###########################################################################
    # Extractor.readSubstanceJSON("https://drugs.ncats.io/api/v1/substances?top=1000")


    # Extractor.readSubstanceJSONfromFile("substance1.json")


    # Extractor.readStructureJSONfromFile("structure.json") 


    # df_structures = Transformer.wrangle_structure_hrefs(InxightDataLoader.get_structures_hrefs())
    # InxightDataLoader.updateSubstanceStructures(df_structures)


    # Extractor.downloadJSON("https://drugs.ncats.io/api/v1/substances?top=1000", "substances2.json", True) 
    # Extractor.downloadJSON("https://drugs.ncats.io/api/v1/structures?top=1000", "structure.json", True) 
    # Extractor.downloadJSON("https://drugs.ncats.io/api/v1/references?top=1000", "reference.json", True)
    # Extractor.downloadJSON("https://drugs.ncats.io/api/v1/names?top=1000", "name.json", True) 
    # Extractor.downloadJSON("https://drugs.ncats.io/api/v1/codes?top=1000", "code.json", True) 


    # Extractor.readSubstanceJSONfromFile("substance2.json")
    # Extractor.readCodeJSONfromFile("code.json")
    # Extractor.readNameJSONfromFile("name.json")
    # Extractor.readReferenceJSONfromFile("reference.json")


    # df_relationships = Transformer.wrangle_relationship_hrefs(InxightDataLoader.get_relationships_hrefs())
    # InxightDataLoader.persistRelationshipData(df_relationships)


    # Extractor.readMixture_in_SubstanceJSONfromFile("substance2.json")


################  replace codes href with codes id #########################
    # df_codes = Transformer.wrangle_code_hrefs(InxightDataLoader.get_code_hrefs())
    # InxightDataLoader.persistCodesData(df_codes)


################ Copy PUBCHEM and INCHIKEY TO Structures table ################################################
# (1) Uncomment the following 2 function calls:
#     InxightDataLoader.get_pubchem_inchikey()
#     InxightDataLoader.updateStructures(df_UNII)
# (2) Execute main( ) function
###############################################################################################################
    #df_UNII = InxightDataLoader.get_pubchem_inchikey()
    #InxightDataLoader.updateStructures(df_UNII)


    # Extractor.readNucleicAcidfromFile("substance2.json")


################# Extract References from JSON files ##########################################################
# Execute Extractor.readTopLevelReferencesfromFile() on each of the named .json files (e.g., substance2.json)
# by:
# (1) uncommenting one of the calls to the Extractor.readTopLevelReferencesfromFile() function 
# (2) leaving InxightDataLoader.persistEntityReferences(dataframe_entity_references) uncommmented for each call 
#     to Extractor.readTopLevelReferencesfromFile() function
# (3) Execute main( ) function 
# (4) comment the executed function and repeat with next function call
###############################################################################################################
    # dataframe_entity_references = Extractor.readTopLevelReferencesfromFile("substance2.json", "substances")
    # dataframe_entity_references = Extractor.readTopLevelReferencesfromFile("name.json", "names")
    # dataframe_entity_references = Extractor.readTopLevelReferencesfromFile("structure.json", "structures")
    # dataframe_entity_references = Extractor.readTopLevelReferencesfromFile("code.json", "codes")
    # InxightDataLoader.persistEntityReferences(dataframe_entity_references)


    # Extractor.readProteinfromFile("substance2.json")


    # Extractor.readStructurallyDiversefromFile("substance2.json")


    # Extractor.readPolymerfromFile("substance2.json")


    # Extractor.readNamesIDfromFile("substance2.json")

    

if __name__ == "__main__":
    main()