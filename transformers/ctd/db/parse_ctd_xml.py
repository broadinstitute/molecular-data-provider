import xml.sax
import pandas as pd

data_for_df = []


class CTDHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.CurrentData = ""
        self.CurrentActor = ""
        self.ixnID = ""
        self.taxonID = ""
        self.taxonNumber = 0
        self.referencePMID = ""
        self.axnCode = {}
        self.axnDegreeCode = {}
        self.axnPosition = {}
        self.axnParentID = {}
        self.axnNumber = 0
        self.actorChemicalID = ""
        self.actorChemicalPosition = ""
        self.actorChemicalForm = ""
        self.actorChemicalFormQualifier = ""
        self.actorGeneID = ""
        self.actorGenePosition = ""
        self.actorGeneForm = ""
        self.actorGeneFormQualifier = ""
        self.actorGeneSeqid = ""
        #More than 2 actors, or when both are either chem or gene, or a different type of actor like ixn
        self.hasWrongActors = ""
        self.taxonContent = ""
        self.axnContent = {}
        self.actorChemicalContent = ""
        self.actorGeneContent = ""


    # Call when an element starts
    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "ixn":
            self.ixnID = attributes["id"]
        if tag == "taxon":
            if self.taxonID == "":
                self.taxonID = attributes["id"]
            else:
                self.taxonID = self.taxonID + "|" + attributes["id"]
        if tag == "reference":
            if self.referencePMID == "":
                self.referencePMID = attributes["pmid"]
            else:
                self.referencePMID = self.referencePMID + "|" + attributes["pmid"]
        if tag == "axn":
            if "code" in attributes:
                self.axnCode[self.axnNumber] =  attributes["code"]
            else:
                self.axnCode[self.axnNumber] = ""
            if "degreecode" in attributes:
                self.axnDegreeCode[self.axnNumber] = attributes["degreecode"]
            else:
                self.axnDegreeCode[self.axnNumber] = ""
            if "position" in attributes:
                self.axnPosition[self.axnNumber] = attributes["position"]
            else:
                self.axnPosition[self.axnNumber] = ""
            if "parentid" in attributes:
                self.axnParentID[self.axnNumber] = attributes["parentid"]
            else:
                self.axnParentID[self.axnNumber] = ""
        # Check if this is an ixn we want to save or not
        if tag == "actor":
            if attributes["type"] == "chemical" and self.actorChemicalID == "":
                self.CurrentActor = "chemical"
                self.actorChemicalID = attributes["id"][5:]
                self.actorChemicalPosition = attributes["position"]
                if "form" in attributes:
                    self.actorChemicalForm = attributes["form"]
                if "formqualifier" in attributes:
                    self.actorChemicalFormQualifier = attributes["formqualifier"]
            elif attributes["type"] == "gene" and self.actorGeneID == "":
                self.CurrentActor = "gene"
                self.actorGeneID = attributes["id"][5:]
                self.actorGenePosition = attributes["position"]
                if "form" in attributes:
                    self.actorGeneForm = attributes["form"]
                if "formqualifier" in attributes:
                    self.actorGeneFormQualifier = attributes["formqualifier"]
                if "seqid" in attributes:
                    self.actorGeneSeqid = attributes["seqid"]
            else:
                self.hasWrongActors = True

    # Call when an element ends
    def endElement(self, tag):
        self.CurrentData = ""
        self.CurrentActor = ""
        if tag == "ixn":
            #Save all to dictionary
            if self.hasWrongActors != True and self.actorChemicalID != "" and self.actorGeneID != "":
                data_entry = {}
                data_entry['IxnID'] = self.ixnID
                data_entry['ChemicalID'] = self.actorChemicalID
                data_entry['ChemicalName'] = self.actorChemicalContent
                data_entry['ChemicalPosition'] = self.actorChemicalPosition
                data_entry['ChemicalForm'] = self.actorChemicalForm
                data_entry['ChemicalFormQualifier'] = self.actorChemicalFormQualifier
                data_entry['GeneID'] = self.actorGeneID
                data_entry['GeneName'] = self.actorGeneContent
                data_entry['GenePosition'] = self.actorGenePosition
                data_entry['GeneForm'] = self.actorGeneForm
                data_entry['GeneFormQualifier'] = self.actorGeneFormQualifier
                data_entry['GeneSeqID'] = self.actorGeneSeqid
                data_entry['TaxonID'] = self.taxonID
                data_entry['TaxonName'] = self.taxonContent
                data_entry['ReferencePMIDs'] = self.referencePMID
                data_entry['AxnCode'] = ""
                data_entry['AxnDegreeCode'] = ""
                data_entry['AxnPosition'] = ""
                data_entry['AxnParentID'] = ""
                data_entry['AxnName'] = ""

                for i in list(self.axnCode.keys()):
                    data_entry_row = {}
                    data_entry_row.update(data_entry)
                    data_entry_row['AxnCode'] = self.axnCode[i]
                    data_entry_row['AxnDegreeCode'] = self.axnDegreeCode[i]
                    data_entry_row['AxnPosition'] = self.axnPosition[i]
                    data_entry_row['AxnParentID'] = self.axnParentID[i]
                    data_entry_row['AxnName'] = self.axnContent[i]
                    data_for_df.append(data_entry_row)

            #Clear all
            self.ixnID = ""
            self.taxonID = ""
            self.taxonNumber = 0
            self.referencePMID = ""
            self.axnCode = {}
            self.axnDegreeCode = {}
            self.axnPosition = {}
            self.axnParentID = {}
            self.axnNumber = 0
            self.actorChemicalID = ""
            self.actorChemicalPosition = ""
            self.actorChemicalForm = ""
            self.actorChemicalFormQualifier = ""
            self.actorGeneID = ""
            self.actorGenePosition = ""
            self.actorGeneForm = ""
            self.actorGeneFormQualifier = ""
            self.actorGeneSeqid = ""
            self.hasWrongActors = ""
            self.taxonContent = ""
            self.axnContent = {}
            self.actorChemicalContent = ""
            self.actorGeneContent = ""
        elif tag == "axn":
            self.axnNumber = self.axnNumber + 1
        elif tag == "taxon":
            self.taxonNumber = self.taxonNumber + 1

    # Call when a character is read
    def characters(self, content):
        if self.CurrentData == "taxon":
            while self.taxonNumber > self.taxonContent.count("|"):
                self.taxonContent = self.taxonContent + "|"
            self.taxonContent = self.taxonContent + content
        elif self.CurrentData == "axn":
            if self.axnNumber in self.axnContent:
                self.axnContent[self.axnNumber] = self.axnContent[self.axnNumber] + content
            else:
                self.axnContent[self.axnNumber] = content
        elif self.CurrentData == "actor":
            if self.CurrentActor == "chemical":
                self.actorChemicalContent = self.actorChemicalContent + content
            elif self.CurrentActor == "gene":
                self.actorGeneContent = self.actorGeneContent + content

# create an XMLReader
parser = xml.sax.make_parser()

parser.setFeature(xml.sax.handler.feature_namespaces, 0)

# override the default ContextHandler
Handler = CTDHandler()
parser.setContentHandler(Handler)

parser.parse("data/CTD_chem_gene_ixns_structured.xml")

df = pd.DataFrame(data_for_df)
df.to_csv('data/CTD_from_xml.csv', sep=',', index=False)
