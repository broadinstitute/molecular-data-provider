# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.classes.base_model_ import Model
from openapi_server import util


class CompoundInfoIdentifiers(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, chebi=None, chembl=None, drugbank=None, pubchem=None, mesh=None, hmdb=None, unii=None, kegg=None, gtopdb=None, chembank=None, drugcentral=None, cas=None, mychem_info=None):  # noqa: E501
        """CompoundInfoIdentifiers - a model defined in OpenAPI

        :param chebi: The chebi of this CompoundInfoIdentifiers.  # noqa: E501
        :type chebi: str
        :param chembl: The chembl of this CompoundInfoIdentifiers.  # noqa: E501
        :type chembl: str
        :param drugbank: The drugbank of this CompoundInfoIdentifiers.  # noqa: E501
        :type drugbank: str
        :param pubchem: The pubchem of this CompoundInfoIdentifiers.  # noqa: E501
        :type pubchem: str
        :param mesh: The mesh of this CompoundInfoIdentifiers.  # noqa: E501
        :type mesh: str
        :param hmdb: The hmdb of this CompoundInfoIdentifiers.  # noqa: E501
        :type hmdb: str
        :param unii: The unii of this CompoundInfoIdentifiers.  # noqa: E501
        :type unii: str
        :param kegg: The kegg of this CompoundInfoIdentifiers.  # noqa: E501
        :type kegg: str
        :param gtopdb: The gtopdb of this CompoundInfoIdentifiers.  # noqa: E501
        :type gtopdb: str
        :param chembank: The chembank of this CompoundInfoIdentifiers.  # noqa: E501
        :type chembank: str
        :param drugcentral: The drugcentral of this CompoundInfoIdentifiers.  # noqa: E501
        :type drugcentral: str
        :param cas: The cas of this CompoundInfoIdentifiers.  # noqa: E501
        :type cas: str
        :param mychem_info: The mychem_info of this CompoundInfoIdentifiers.  # noqa: E501
        :type mychem_info: str
        """
        self.openapi_types = {
            'chebi': str,
            'chembl': str,
            'drugbank': str,
            'pubchem': str,
            'mesh': str,
            'hmdb': str,
            'unii': str,
            'kegg': str,
            'gtopdb': str,
            'chembank': str,
            'drugcentral': str,
            'cas': str,
            'mychem_info': str
        }

        self.attribute_map = {
            'chebi': 'chebi',
            'chembl': 'chembl',
            'drugbank': 'drugbank',
            'pubchem': 'pubchem',
            'mesh': 'mesh',
            'hmdb': 'hmdb',
            'unii': 'unii',
            'kegg': 'kegg',
            'gtopdb': 'gtopdb',
            'chembank': 'chembank',
            'drugcentral': 'drugcentral',
            'cas': 'cas',
            'mychem_info': 'mychem_info'
        }

        self._chebi = chebi
        self._chembl = chembl
        self._drugbank = drugbank
        self._pubchem = pubchem
        self._mesh = mesh
        self._hmdb = hmdb
        self._unii = unii
        self._kegg = kegg
        self._gtopdb = gtopdb
        self._chembank = chembank
        self._drugcentral = drugcentral
        self._cas = cas
        self._mychem_info = mychem_info

    @classmethod
    def from_dict(cls, dikt) -> 'CompoundInfoIdentifiers':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The compound_info_identifiers of this CompoundInfoIdentifiers.  # noqa: E501
        :rtype: CompoundInfoIdentifiers
        """
        return util.deserialize_model(dikt, cls)

    @property
    def chebi(self):
        """Gets the chebi of this CompoundInfoIdentifiers.

        ChEBI id of the compound (CURIE).  # noqa: E501

        :return: The chebi of this CompoundInfoIdentifiers.
        :rtype: str
        """
        return self._chebi

    @chebi.setter
    def chebi(self, chebi):
        """Sets the chebi of this CompoundInfoIdentifiers.

        ChEBI id of the compound (CURIE).  # noqa: E501

        :param chebi: The chebi of this CompoundInfoIdentifiers.
        :type chebi: str
        """

        self._chebi = chebi

    @property
    def chembl(self):
        """Gets the chembl of this CompoundInfoIdentifiers.

        ChEMBL id of the compound (CURIE).  # noqa: E501

        :return: The chembl of this CompoundInfoIdentifiers.
        :rtype: str
        """
        return self._chembl

    @chembl.setter
    def chembl(self, chembl):
        """Sets the chembl of this CompoundInfoIdentifiers.

        ChEMBL id of the compound (CURIE).  # noqa: E501

        :param chembl: The chembl of this CompoundInfoIdentifiers.
        :type chembl: str
        """

        self._chembl = chembl

    @property
    def drugbank(self):
        """Gets the drugbank of this CompoundInfoIdentifiers.

        DrugBank id of the compound (CURIE).  # noqa: E501

        :return: The drugbank of this CompoundInfoIdentifiers.
        :rtype: str
        """
        return self._drugbank

    @drugbank.setter
    def drugbank(self, drugbank):
        """Sets the drugbank of this CompoundInfoIdentifiers.

        DrugBank id of the compound (CURIE).  # noqa: E501

        :param drugbank: The drugbank of this CompoundInfoIdentifiers.
        :type drugbank: str
        """

        self._drugbank = drugbank

    @property
    def pubchem(self):
        """Gets the pubchem of this CompoundInfoIdentifiers.

        PubChem CID of the compound (CURIE).  # noqa: E501

        :return: The pubchem of this CompoundInfoIdentifiers.
        :rtype: str
        """
        return self._pubchem

    @pubchem.setter
    def pubchem(self, pubchem):
        """Sets the pubchem of this CompoundInfoIdentifiers.

        PubChem CID of the compound (CURIE).  # noqa: E501

        :param pubchem: The pubchem of this CompoundInfoIdentifiers.
        :type pubchem: str
        """

        self._pubchem = pubchem

    @property
    def mesh(self):
        """Gets the mesh of this CompoundInfoIdentifiers.

        MeSH id of the compound (CURIE).  # noqa: E501

        :return: The mesh of this CompoundInfoIdentifiers.
        :rtype: str
        """
        return self._mesh

    @mesh.setter
    def mesh(self, mesh):
        """Sets the mesh of this CompoundInfoIdentifiers.

        MeSH id of the compound (CURIE).  # noqa: E501

        :param mesh: The mesh of this CompoundInfoIdentifiers.
        :type mesh: str
        """

        self._mesh = mesh

    @property
    def hmdb(self):
        """Gets the hmdb of this CompoundInfoIdentifiers.

        HMDB id of the compound (CURIE).  # noqa: E501

        :return: The hmdb of this CompoundInfoIdentifiers.
        :rtype: str
        """
        return self._hmdb

    @hmdb.setter
    def hmdb(self, hmdb):
        """Sets the hmdb of this CompoundInfoIdentifiers.

        HMDB id of the compound (CURIE).  # noqa: E501

        :param hmdb: The hmdb of this CompoundInfoIdentifiers.
        :type hmdb: str
        """

        self._hmdb = hmdb

    @property
    def unii(self):
        """Gets the unii of this CompoundInfoIdentifiers.

        UNII id of the compound (CURIE).  # noqa: E501

        :return: The unii of this CompoundInfoIdentifiers.
        :rtype: str
        """
        return self._unii

    @unii.setter
    def unii(self, unii):
        """Sets the unii of this CompoundInfoIdentifiers.

        UNII id of the compound (CURIE).  # noqa: E501

        :param unii: The unii of this CompoundInfoIdentifiers.
        :type unii: str
        """

        self._unii = unii

    @property
    def kegg(self):
        """Gets the kegg of this CompoundInfoIdentifiers.

        KEGG id of the compound (CURIE).  # noqa: E501

        :return: The kegg of this CompoundInfoIdentifiers.
        :rtype: str
        """
        return self._kegg

    @kegg.setter
    def kegg(self, kegg):
        """Sets the kegg of this CompoundInfoIdentifiers.

        KEGG id of the compound (CURIE).  # noqa: E501

        :param kegg: The kegg of this CompoundInfoIdentifiers.
        :type kegg: str
        """

        self._kegg = kegg

    @property
    def gtopdb(self):
        """Gets the gtopdb of this CompoundInfoIdentifiers.

        Guide to PHARMACOLOGY id of the compound (CURIE).  # noqa: E501

        :return: The gtopdb of this CompoundInfoIdentifiers.
        :rtype: str
        """
        return self._gtopdb

    @gtopdb.setter
    def gtopdb(self, gtopdb):
        """Sets the gtopdb of this CompoundInfoIdentifiers.

        Guide to PHARMACOLOGY id of the compound (CURIE).  # noqa: E501

        :param gtopdb: The gtopdb of this CompoundInfoIdentifiers.
        :type gtopdb: str
        """

        self._gtopdb = gtopdb

    @property
    def chembank(self):
        """Gets the chembank of this CompoundInfoIdentifiers.

        ChemBank id of the compound (CURIE).  # noqa: E501

        :return: The chembank of this CompoundInfoIdentifiers.
        :rtype: str
        """
        return self._chembank

    @chembank.setter
    def chembank(self, chembank):
        """Sets the chembank of this CompoundInfoIdentifiers.

        ChemBank id of the compound (CURIE).  # noqa: E501

        :param chembank: The chembank of this CompoundInfoIdentifiers.
        :type chembank: str
        """

        self._chembank = chembank

    @property
    def drugcentral(self):
        """Gets the drugcentral of this CompoundInfoIdentifiers.

        DrugCentral id of the compound (CURIE).  # noqa: E501

        :return: The drugcentral of this CompoundInfoIdentifiers.
        :rtype: str
        """
        return self._drugcentral

    @drugcentral.setter
    def drugcentral(self, drugcentral):
        """Sets the drugcentral of this CompoundInfoIdentifiers.

        DrugCentral id of the compound (CURIE).  # noqa: E501

        :param drugcentral: The drugcentral of this CompoundInfoIdentifiers.
        :type drugcentral: str
        """

        self._drugcentral = drugcentral

    @property
    def cas(self):
        """Gets the cas of this CompoundInfoIdentifiers.

        CAS id of the compound (CURIE).  # noqa: E501

        :return: The cas of this CompoundInfoIdentifiers.
        :rtype: str
        """
        return self._cas

    @cas.setter
    def cas(self, cas):
        """Sets the cas of this CompoundInfoIdentifiers.

        CAS id of the compound (CURIE).  # noqa: E501

        :param cas: The cas of this CompoundInfoIdentifiers.
        :type cas: str
        """

        self._cas = cas

    @property
    def mychem_info(self):
        """Gets the mychem_info of this CompoundInfoIdentifiers.

        myChem.info id of the compound.  # noqa: E501

        :return: The mychem_info of this CompoundInfoIdentifiers.
        :rtype: str
        """
        return self._mychem_info

    @mychem_info.setter
    def mychem_info(self, mychem_info):
        """Sets the mychem_info of this CompoundInfoIdentifiers.

        myChem.info id of the compound.  # noqa: E501

        :param mychem_info: The mychem_info of this CompoundInfoIdentifiers.
        :type mychem_info: str
        """

        self._mychem_info = mychem_info
