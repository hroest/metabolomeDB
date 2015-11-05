#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
python parse_toxinsDB.py /media/data/tmp/metabo_db/t3db/all_toxins.xml 
"""


import sqlalchemy.types
from db_objects import *
from copy import copy
import xml.etree.cElementTree as ET #permits xml parsing trees

from parse_hmdb_sql import *

db_name = "T3DB"

def handle_toxdb_metabolite(elem, metabolite):
    """
    copy of handle_hmdb_metabolite
    """

    if metabolite.t3db_metabolite is None:
        hm = T3DBMetabolite()
        hm.metabolite_id = metabolite.id
        hm.add(session)

    t3db_metabolite = metabolite.t3db_metabolite

    hmdb_metabolite = t3db_metabolite

    t3db_id = elem.find("accession")
    name = elem.find("common_name")
    hmdb_id = elem.find("hmdb_id")
    drugbank_id = elem.find("drugbank_id")
    pubchem_compound_id = elem.find("pubchem_compound_id")
    chemspider_id = elem.find("chemspider_id")
    kegg_id = elem.find("kegg_id")
    uniprot_id = elem.find("uniprot_id")
    biocyc_id = elem.find("biocyc_id")
    chebi_id = elem.find("chebi_id")

    chembl_id = elem.find("chembl_id")
    omim_id = elem.find("omim_id")
    ctd_id = elem.find("ctd_id")
    stitch_id = elem.find("stitch_id")
    actor_id = elem.find("actor_id")
    pdb_id = elem.find("pdb_id")

    # metlin_id =elem.find("metlin_id")
    # het_id = elem.find("het_id")

    if hmdb_id is not None: hmdb_metabolite.hmdb_id = hmdb_id.text
    if t3db_id is not None: hmdb_metabolite.t3db_id = t3db_id.text
    if name is not None: hmdb_metabolite.name = name.text.encode("utf8")
    # if foodb_id is not None: hmdb_metabolite.foodb_id = foodb_id.text
    if chemspider_id is not None and chemspider_id.text is not None: 
        hmdb_metabolite.chemspider_id = long( chemspider_id.text )
    if kegg_id is not None: hmdb_metabolite.kegg_id = kegg_id.text
    if biocyc_id is not None: hmdb_metabolite.biocyc_id = biocyc_id.text
    ## if metlin_id is not None and metlin_id.text is not None: 
    ##     hmdb_metabolite.metlin_id = long( metlin_id.text )
    if pubchem_compound_id is not None and pubchem_compound_id.text is not None: 
        hmdb_metabolite.pubchem_compound_id = long(pubchem_compound_id.text)
    # if het_id is not None: hmdb_metabolite.het_id = het_id.text
    if chebi_id is not None and chebi_id.text is not None: 
        try:
            hmdb_metabolite.chebi_id = long(chebi_id.text)
        except ValueError:
            print "value error parsing chebi number"
            # try to remove CHEBI:
            hmdb_metabolite.chebi_id = long(chebi_id.text[6:])

    # print "omim id", omim_id, omim_id.text

    if chembl_id is not None: hmdb_metabolite.chembl_id = chembl_id.text
    if omim_id is not None: hmdb_metabolite.omim_id = omim_id.text
    if ctd_id is not None: hmdb_metabolite.ctd_id = ctd_id.text
    if stitch_id is not None: hmdb_metabolite.stitch_id = stitch_id.text
    if pdb_id is not None: hmdb_metabolite.pdb_id = pdb_id.text

    if actor_id is not None and actor_id.text is not None: 
        hmdb_metabolite.actor_id = long(actor_id.text)

    if elem.find("taxonomy") is not None:
        for taxonomy_elem in elem.find("taxonomy"):
            if taxonomy_elem.tag == "kingdom":
                hmdb_metabolite.kingdom = taxonomy_elem.text
            if taxonomy_elem.tag == "super_class":
                hmdb_metabolite.super_class = taxonomy_elem.text
            if taxonomy_elem.tag == "class":
                hmdb_metabolite.compound_class = taxonomy_elem.text
            if taxonomy_elem.tag == "sub_class":
                hmdb_metabolite.sub_class = taxonomy_elem.text

    hmdb_metabolite.add(session)
    session.commit()

def handle_toxic_categories(elem, metabolite):
    toxcats = []
    if elem.find("categories") is not None:
        for cat_elem in elem.find("categories"):
            if cat_elem.tag == "category":
                toxcats.append( cat_elem.text )

    for catname in toxcats:
        tcat = session.query(ToxicCategory).filter_by(name=catname).first() # Slow ! 
        if tcat is None:
            tcat = ToxicCategory()
            tcat.name = catname
            tcat.db_origin = db_name
            tcat.add(session)
            session.commit()
        metabolite.toxic_categories.append(tcat) # Slow !

def parse_metabolite_elem(elem):

        metabolite, flag = handle_metabolite(elem)

        if metabolite.InCHI_key is None:

            # Handle case where no match by InCHI_key was possible, try to
            # match by T3DB key (accession):
            if elem.find("accession") is not None \
              and elem.find("accession").text is not None:

                acc_nr = elem.find("accession").text
                entry = session.query(T3DBMetabolite).filter_by(t3db_id=acc_nr).first()

                if entry is not None:
                    # There is already a matching entry, use it instead
                    metabolite = entry.metabolite

        if flag == "Old":
            pass

        metabolite.add(session)
        session.commit()

        handle_toxdb_metabolite(elem, metabolite)
        handle_substituents(elem, metabolite, db_origin=db_name)
        handle_toxic_categories(elem, metabolite)

        session.commit()
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
    for event, elem in context:
        if event == "end" and elem.tag == "compound":
            i += 1
            m = parse_metabolite_elem(elem)
            print "T3DB", i, m.InCHI_key 

            # delete with all children
            elem.clear()

if __name__ == "__main__":
    main()

