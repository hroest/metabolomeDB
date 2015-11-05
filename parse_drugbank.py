#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
python parse_drugbank.py /media/data/tmp/metabo_db/drugbank/drugbank.xml
"""

import sqlalchemy.types
from db_objects import *
from copy import copy
import xml.etree.cElementTree as ET #permits xml parsing trees

from parse_hmdb_sql import *

db_name = "drugbank"

def handle_drugbank_metabolite(elem):
    """
    Parses information for a single metabolite with a specific InCHI_key
    and molecular mass

    @note: you still may have to add the metabolite to the database,
    especially if there is no InCHI_key by which it could be mapped
    """

    molweight_term = "monisotopic_moleculate_weight" # HMDB
    chemform_term = "chemical_formula"
    inchikey_term = "inchikey"

    properties = elem.find("{http://www.drugbank.ca}experimental-properties")
    mw = None
    sumformula = None
    for ch in properties:
        # if ch.find("{http://www.drugbank.ca}kind").text == "Molecular Weight":
        #     mw = ch.find("{http://www.drugbank.ca}value").text
        if ch.find("{http://www.drugbank.ca}kind").text == "Molecular Formula":
            sumformula = ch.find("{http://www.drugbank.ca}value").text

    properties = elem.find("{http://www.drugbank.ca}calculated-properties")
    smiles = None
    inchi = None
    inchikey = None
    if properties is not None:
        for ch in properties:
            if ch.find("{http://www.drugbank.ca}kind").text == "SMILES":
                smiles = ch.find("{http://www.drugbank.ca}value").text
            if ch.find("{http://www.drugbank.ca}kind").text == "InChI":
                inchi = ch.find("{http://www.drugbank.ca}value").text
            if ch.find("{http://www.drugbank.ca}kind").text == "InChIKey":
                inchikey = ch.find("{http://www.drugbank.ca}value").text
            if ch.find("{http://www.drugbank.ca}kind").text == "Monoisotopic Weight":
                mw = float(ch.find("{http://www.drugbank.ca}value").text)
            if ch.find("{http://www.drugbank.ca}kind").text == "Molecular Formula":
                sumformula = ch.find("{http://www.drugbank.ca}value").text

    if mw is None and sumformula is not None:
        try:
            import molmass
            from molmass.molmass import Formula
            try:
                f = Formula(sumformula)
                mw = float(f.isotope.mass)
            except molmass.molmass.FormulaError:
                pass
                print "Could not resolve sumformula", sumformula
        except ImportError:
            pass

    thisId = None
    for db_id in elem.findall("{http://www.drugbank.ca}drugbank-id"):
        if thisId is None:
            thisId = db_id.text
        # Prefer primary id
        if "primary" in db_id.attrib:
            thisId = db_id.text

    # Try to find the drugbank id in the database ... 
    drugbank_metabolite = session.query(DrugbankMetabolite).filter_by(drugbank_id=thisId).first()

    if drugbank_metabolite is None:
        drugbank_metabolite = DrugbankMetabolite()
        drugbank_metabolite.drugbank_id = thisId

        if inchikey is not None:
            key = inchikey
            metabolite = session.query(Metabolite).filter_by(InCHI_key=key).first()
            if metabolite is None:
                metabolite = Metabolite()
            else:
                if metabolite.drugbank_metabolite is not None:
                    print "  WARNING: We already have a drugbank entry for %s (which is %s)" % (
                        metabolite.InCHI_key, metabolite.drugbank_metabolite.drugbank_id)
                    return metabolite, "Error"
        else:
            metabolite = Metabolite()

        if metabolite.monoisotopic_mass is None or \
           abs(float(metabolite.monoisotopic_mass) - mw) > 1e-5:
            metabolite.monoisotopic_mass = mw
        if sumformula is not None:
            metabolite.sum_formula = sumformula.encode("utf8")

        metabolite.SMILES = smiles
        metabolite.InChI = inchi
        metabolite.InCHI_key = inchikey

        metabolite.add(session)
        session.commit()
        drugbank_metabolite.metabolite_id = metabolite.id
    else:
        metabolite = drugbank_metabolite.metabolite

    cas = elem.find("{http://www.drugbank.ca}cas-number")
    if cas is not None and cas.text is not None: drugbank_metabolite.cas_number = cas.text

    name = elem.find("{http://www.drugbank.ca}name")
    if name is not None and name.text is not None: drugbank_metabolite.name = name.text.encode("utf8")

    indication = elem.find("{http://www.drugbank.ca}indication")
    if indication is not None and indication.text is not None: drugbank_metabolite.indication = indication.text.encode("utf8")

    identifiers = elem.find("{http://www.drugbank.ca}external-identifiers")
    for ch in identifiers:
        resource = ch.find("{http://www.drugbank.ca}resource").text
        identifier = ch.find("{http://www.drugbank.ca}identifier").text
        if resource == 'UniProtKB':
            drugbank_metabolite.uniprot_id = identifier
        if resource == 'KEGG Drug':
            drugbank_metabolite.kegg_drug = identifier
        if resource == 'PharmGKB':
            drugbank_metabolite.pharmgkb = identifier
        if resource == 'Wikipedia':
            drugbank_metabolite.wikipedia = identifier
        if resource == 'Drugs Product Database (DPD)':
            drugbank_metabolite.dpd = identifier
        if resource == 'National Drug Code Directory':
            drugbank_metabolite.drug_code = identifier

    if elem.find("{http://www.drugbank.ca}classification") is not None:
        for taxonomy_elem in elem.find("{http://www.drugbank.ca}classification"):
            if taxonomy_elem.tag.endswith("direct-parent"):
                drugbank_metabolite.direct_parent = taxonomy_elem.text
            if taxonomy_elem.tag.endswith("kingdom"):
                drugbank_metabolite.kingdom = taxonomy_elem.text
            if taxonomy_elem.tag.endswith("superclass"):
                drugbank_metabolite.super_class = taxonomy_elem.text
            if taxonomy_elem.tag.endswith("class"):
                drugbank_metabolite.compound_class = taxonomy_elem.text
            if taxonomy_elem.tag.endswith("subclass"):
                drugbank_metabolite.sub_class = taxonomy_elem.text

    drugbank_metabolite.add(session)
    session.commit()

    return metabolite, "None"

def handle_substituents(elem, metabolite, db_origin="", element_name="taxonomy"):
    substituents = []
    if elem.find(element_name) is not None:
        for taxonomy_elem in elem.find(element_name):
            if taxonomy_elem.tag.endswith("substituent"):
                substituents.append( taxonomy_elem.text )

    for sname in substituents:
        substituent = session.query(Substituent).filter_by(name=sname).first()
        if substituent is None:
            substituent = Substituent()
            substituent.name = sname
            substituent.db_origin = db_origin
            substituent.add(session)
            session.commit()
        metabolite.substituents.append(substituent)

def parse_metabolite_elem(elem):

        metabolite, flag = handle_drugbank_metabolite(elem)
        if flag == "Error":
            return metabolite
        handle_substituents(elem, metabolite, db_origin=db_name, element_name="{http://www.drugbank.ca}classification")
        return metabolite

def main():

    source = sys.argv[1]

    # get an iterable
    context = ET.iterparse(source, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = context.next()

    i = 0
    nesting = 0
    for event, elem in context:

        if event == "start" and elem.tag == "{http://www.drugbank.ca}drug": nesting += 1
        if event == "end" and elem.tag == "{http://www.drugbank.ca}drug": nesting -= 1

        if event == "end" and elem.tag == "{http://www.drugbank.ca}drug" and nesting == 0:
            i += 1
            m = parse_metabolite_elem(elem)
            print "Drugbank", i, m.InCHI_key 

            # delete with all children
            elem.clear()

if __name__ == "__main__":
    main()

