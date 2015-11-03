import MySQLdb
from sqlalchemy import MetaData, create_engine, Table
from sqlalchemy.orm import sessionmaker

dbfile = "/home/hr/projects/metabolomeDB/metabolite.cnf"
dbname = "metabolomics"

import MySQLdb
mydb = MySQLdb.connect(read_default_file=dbfile)
cursor = mydb.cursor()

def connection_creator(db):
    #this fxn will return a fxn "connect" which returns a database connector
    def connect():
        return MySQLdb.connect( read_default_file=dbfile, db=db)
    return connect


db = create_engine('mysql://', creator=connection_creator(dbname), echo = False)
mymetadata = MetaData(); mymetadata.bind = db
metabolite_table = Table('metabolites', mymetadata,autoload=True)
hmdb_metabolite_table = Table('hmdb_metabolites', mymetadata,autoload=True)
t3db_metabolite_table = Table('t3db_metabolites', mymetadata,autoload=True)

substituents_table = Table('substituents', mymetadata,autoload=True)
MetaboliteSubstituentsLink_table = Table('metabolites_substituents', mymetadata,autoload=True)
toxic_category_table = Table('toxic_categories', mymetadata,autoload=True)
MetaboliteToxicCategoryLink_table = Table('metabolites_toxic_category', mymetadata,autoload=True)

biological_origin_table = Table('biological_origin', mymetadata,autoload=True)
MetaboliteBiologicalOriginLink_table = Table('metabolites_origins', mymetadata,autoload=True)

disease_table = Table('diseases', mymetadata,autoload=True)
MetaboliteDiseaseLink_table = Table('metabolites_diseases', mymetadata,autoload=True)

# SNPFeatureLink_table = Table('feature_snp', metadata_genome, autoload=True)

Session = sessionmaker()
session = Session()

