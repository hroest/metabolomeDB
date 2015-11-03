import MySQLdb
db = MySQLdb.connect(host="localhost", user="metabolomics", passwd="metabolomics", db="metabolomics")
c = db.cursor()

import sqlalchemy.types
from db_objects import *
from copy import copy
import xml.etree.cElementTree as ET #permits xml parsing trees
import sys

db_name = "HMDB"

def handle_hmdb_metabolite(elem, metabolite):

        if metabolite.hmdb_metabolite is None:
            hm = HMDBMetabolite()
            hm.metabolite_id = metabolite.id
            hm.add(session)

        hmdb_metabolite = metabolite.hmdb_metabolite

        hmdb_id = elem.find("accession")
        name = elem.find("name")
        foodb_id = elem.find("foodb_id")
        chemspider_id = elem.find("chemspider_id")
        kegg_id = elem.find("kegg_id")
        biocyc_id = elem.find("biocyc_id")
        metlin_id =elem.find("metlin_id")
        pubchem_compound_id = elem.find("pubchem_compound_id")
        het_id = elem.find("het_id")
        chebi_id = elem.find("chebi_id")

        if hmdb_id is not None: hmdb_metabolite.hmdb_id = hmdb_id.text
        if name is not None: hmdb_metabolite.name = name.text
        if foodb_id is not None: hmdb_metabolite.foodb_id = foodb_id.text
        if chemspider_id is not None and chemspider_id.text is not None: 
            hmdb_metabolite.chemspider_id = long( chemspider_id.text )
        if kegg_id is not None: hmdb_metabolite.kegg_id = kegg_id.text
        if biocyc_id is not None: hmdb_metabolite.biocyc_id = biocyc_id.text
        if metlin_id is not None and metlin_id.text is not None: 
            hmdb_metabolite.metlin_id = long( metlin_id.text )
        if pubchem_compound_id is not None and pubchem_compound_id.text is not None: 
            hmdb_metabolite.pubchem_compound_id = long(pubchem_compound_id.text)
        if het_id is not None: hmdb_metabolite.het_id = het_id.text
        if chebi_id is not None and chebi_id.text is not None: 
            hmdb_metabolite.chebi_id = long(chebi_id.text)

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

def handle_bio_origins(elem, metabolite):
        if elem.find("ontology") is not None:
            ont = elem.find("ontology")
            if ont.find("origins") is not None:
                for origin_el in ont.find("origins"):
                    origin = session.query(BiologicalOrigin).filter_by(origin_name=origin_el.text).first()
                    if origin is None:
                        origin = BiologicalOrigin()
                        origin.origin_name = origin_el.text
                        origin.db_origin = db_name
                        origin.add(session)
                        session.commit()
                    metabolite.biological_origins.append(origin)

def handle_substituents(elem, metabolite, db_origin=""):
        substituents = []
        if elem.find("taxonomy") is not None:
            for taxonomy_elem in elem.find("taxonomy"):
                if taxonomy_elem.tag == "substituents":
                    for substituent in taxonomy_elem:
                        substituents.append( substituent.text )

        for sname in substituents:
            substituent = session.query(Substituent).filter_by(name=sname).first()
            if substituent is None:
                substituent = Substituent()
                substituent.name = sname
                substituent.db_origin = db_origin
                substituent.add(session)
                session.commit()
            metabolite.substituents.append(substituent)

def handle_diseases(elem, metabolite):

        substituents = []
        if elem.find("diseases") is not None:
            for disease_el in elem.find("diseases"):
                omim_id = disease_el.find("omim_id").text
                name = disease_el.find("name").text
                disease = session.query(Disease).filter_by(omim_id=omim_id).first()
                if disease is None:
                    disease = session.query(Disease).filter_by(disease_name=name).first()
                if disease is None:
                    disease = Disease()
                    disease.disease_name = name
                    # disease.db_origin = db_name
                    disease.omim_id = omim_id
                    disease.add(session)
                    session.commit()

                metabolite.diseases.append(disease)

def handle_metabolite(elem):
        """
        Parses information for a single metabolite with a specific InCHI_key
        and molecular mass

        @note: you still may have to add the metabolite to the database,
        especially if there is no InCHI_key by which it could be mapped
        """

        molweight_term = "monisotopic_moleculate_weight" # HMDB
        chemform_term = "chemical_formula"
        inchikey_term = "inchikey"

        k = elem.find(inchikey_term)
        key = k.text
        metabolite = None
        if key is not None:
            key = key.replace("InChIKey=", "")
            assert len(key) == 27
            metabolite = session.query(Metabolite).filter_by(InCHI_key=key).first()

        if metabolite is None:
            metabolite = Metabolite()
            if key is not None:
                # Only add if we do have a key
                metabolite.InCHI_key = key
                metabolite.add(session)
            else:
                # Otherwise pass
        else:
            # already in database
            return metabolite, "Old"

        # please do not remove
        metabolite_id = metabolite.id

        metabolite.InCHI = elem.find("inchi").text
        metabolite.SMILES = elem.find("smiles").text

        if elem.find(molweight_term) is not None \
         and elem.find(molweight_term).text is not None:
            mass = float(elem.find(molweight_term).text)
            # Only change mass if it is really different
            if metabolite.monoisotopic_mass is None or \
               abs(float(metabolite.monoisotopic_mass) - mass) > 1e-5:
                metabolite.monoisotopic_mass = mass

        if elem.find(chemform_term) is not None \
           and elem.find(chemform_term).text is not None:
            metabolite.sum_formula = elem.find(chemform_term).text.encode("utf8")

        return metabolite, "New"

def parse_metabolite_elem(elem):

        metabolite, flag = handle_metabolite(elem)

        if metabolite.InCHI_key is None:

            # Handle case where no match by InCHI_key was possible, try to
            # match by HMDB key (accession):
            if elem.find("accession") is not None \
              and elem.find("accession").text is not None:

                acc_nr = elem.find("accession").text
                entry = session.query(HMDBMetabolite).filter_by(hmdb_id=acc_nr).first()

                if entry is not None:
                    # There is already a matching entry, use it instead
                    metabolite = entry.metabolite

        if flag == "Old":
            return

        metabolite.add(session)
        session.commit()

        handle_diseases(elem, metabolite)
        handle_hmdb_metabolite(elem, metabolite)
        handle_substituents(elem, metabolite)
        handle_bio_origins(elem, metabolite)

        session.commit()

def main():

    source = sys.argv[1]

    # get an iterable
    context = ET.iterparse(source, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = context.next()

    for event, elem in context:
        if event == "end" and elem.tag == "metabolite":
            parse_metabolite_elem(elem)
            # delete with all children
            elem.clear()

if __name__ == "__main__":
    main()

