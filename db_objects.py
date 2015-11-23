from sqlalchemy.orm import mapper, relation, backref
from sqlalchemy import and_
from sqlalchemy import select
from db_tables import *
import datetime
from sqlalchemy import func #SQL functions like compress, sha1 etc
#from db import PrimaryKeyConstraint
from sqlalchemy.orm import column_property
import Bio.Seq

def add_init(myclass):
    """
    Allows the initialization of new database objects easily.

    This decorator adds a new __init__ function to the decorated class which
    can take one of two forms:
        - standard: through keywords
        - with defaults: through keywords and all fields are set to their default values

    For the second mechanism to work, the class needs to proivde a "_defaults"
    dictionary as a class member. For example, the following class:

    @add_init
    class Book(object): 

        _defaults = { 
            'ISBN'          : '978-3-16-148410-0',
            'url'           : 'http://www.example.com'
            'author'        : 'unknown',
            'title'         : '',
        }


    The added __init__ function has the signature __init__(self, **kwargs) and
    during initialization, setattr is used to try and set the value for each
    provided keyword argument.

    """

    def init_standard(self, **kwargs): 
        # we go through all arguments given as keywords and set them 
        # e.g. if init was called with (id=someid) we set here self.id = someid
        for k in kwargs:
            setattr( self, k, kwargs[k])

    def init_with_defaults(self, **kwargs): 
        for d in self.__class__._defaults:
            setattr( self, d, self.__class__._defaults[d])

        self.insert_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')

        # we go through all arguments given as keywords and set them 
        # e.g. if init was called with (id=someid) we set here self.id = someid
        for k in kwargs:
            setattr( self, k, kwargs[k])

    # Select initialization method
    if myclass.__dict__.has_key('_defaults'):
        myclass.__init__ = init_with_defaults
    else:
        myclass.__init__ = init_standard

    return myclass

def add_addfxn(myclass):
    """
    Add a few default functions to a new class

    Adds the following functions (if they are not already present) to the wrapped object:
        - add (add and commit)
        - exists (check if current id already exists)
        - addignore_setid (add to table if current object does not yet exist)
    """

    #generic addignore
    def addignore_setid(self, session):
        p = self.exists(session)

        if p is None:
            return self.add(session)
        else:
            return p

    #generic exist, will only check whether this id is already present
    def exists(self, session):
        return session.query(self.__class__).filter_by(id=self.id).first()

    #generic add, will just use session
    def add(self, session):
        session.add(self)
        session.commit()
        return self

    if not myclass.__dict__.has_key('add'):
        myclass.add = add

    if not myclass.__dict__.has_key('exists'):
        myclass.exists = exists

    if not myclass.__dict__.has_key('addignore_setid'):
        myclass.addignore_setid = addignore_setid

    return myclass

def add_mapper(table):
    """
    Simple convenience class decorator

    Instead of writing

        class User(object):
            pass
        mapper(User, usertable)

    one can write directly

        @add_mapper(usertable)
        class User(object):
            pass

    which strenghtens the assocation between the object and its associated
    database.
    """

    def wrap(myclass):
        mapper(myclass, table)
        return myclass
    return wrap

#@add_mapper(metabolite_table)
@add_addfxn
@add_init
class Metabolite(object): 
    pass

@add_mapper(hmdb_metabolite_table)
@add_addfxn
@add_init
class HMDBMetabolite(object): 
    pass

@add_mapper(t3db_metabolite_table)
@add_addfxn
@add_init
class T3DBMetabolite(object): 
    pass

@add_mapper(drugbank_metabolite_table)
@add_addfxn
@add_init
class DrugbankMetabolite(object): 
    pass

@add_addfxn
@add_init
class BiologicalOrigin(object): 
    pass

@add_addfxn
@add_init
class Disease(object): 
    pass

@add_addfxn
@add_init
class Substituent(object): 
    pass

@add_addfxn
@add_init
class ToxicCategory(object): 
    pass


mapper(Metabolite, metabolite_table, properties = {
    'id' : metabolite_table.c.metabolite_id,
    'hmdb_metabolite' : relation (HMDBMetabolite, primaryjoin=
        metabolite_table.c.metabolite_id==hmdb_metabolite_table.c.metabolite_id, 
        backref=backref('metabolite', uselist=False),
        foreign_keys=[metabolite_table.c.metabolite_id]),
    't3db_metabolite' : relation (T3DBMetabolite, primaryjoin=
        metabolite_table.c.metabolite_id==t3db_metabolite_table.c.metabolite_id, 
        backref=backref('metabolite', uselist=False),
        foreign_keys=[metabolite_table.c.metabolite_id]),
    'drugbank_metabolite' : relation (DrugbankMetabolite, primaryjoin=
        metabolite_table.c.metabolite_id==drugbank_metabolite_table.c.metabolite_id, 
        backref=backref('metabolite', uselist=False),
        foreign_keys=[metabolite_table.c.metabolite_id]),
})

mapper(Substituent, substituents_table, properties = {
    'metabolites' : relation (Metabolite,
        secondary=MetaboliteSubstituentsLink_table,
        primaryjoin=substituents_table.c.substutient_id==MetaboliteSubstituentsLink_table.c.substutient_id, 
        secondaryjoin=and_(MetaboliteSubstituentsLink_table.c.metabolite_id==metabolite_table.c.metabolite_id),
        backref='substituents',
        foreign_keys=[MetaboliteSubstituentsLink_table.c.metabolite_id,MetaboliteSubstituentsLink_table.c.substutient_id]) 
})

mapper(ToxicCategory, toxic_category_table, properties = {
    'metabolites' : relation (Metabolite,
        secondary=MetaboliteToxicCategoryLink_table,
        primaryjoin=toxic_category_table.c.toxic_category_id==MetaboliteToxicCategoryLink_table.c.toxic_category_id, 
        secondaryjoin=and_(MetaboliteToxicCategoryLink_table.c.metabolite_id==metabolite_table.c.metabolite_id),
        backref='toxic_categories',
        foreign_keys=[MetaboliteToxicCategoryLink_table.c.metabolite_id,MetaboliteToxicCategoryLink_table.c.toxic_category_id]) 
})


mapper(BiologicalOrigin, biological_origin_table, properties = {
    'metabolites' : relation (Metabolite,
        secondary=MetaboliteBiologicalOriginLink_table,
        primaryjoin=biological_origin_table.c.biological_origin_id==MetaboliteBiologicalOriginLink_table.c.biological_origin_id, 
        secondaryjoin=and_(MetaboliteBiologicalOriginLink_table.c.metabolite_id==metabolite_table.c.metabolite_id),
        backref='biological_origins',
        foreign_keys=[MetaboliteBiologicalOriginLink_table.c.metabolite_id,MetaboliteBiologicalOriginLink_table.c.biological_origin_id]) 
})

mapper(Disease, disease_table, properties = {
    'metabolites' : relation (Metabolite,
        secondary=MetaboliteDiseaseLink_table,
        primaryjoin=disease_table.c.disease_id==MetaboliteDiseaseLink_table.c.disease_id, 
        secondaryjoin=and_(MetaboliteDiseaseLink_table.c.metabolite_id==metabolite_table.c.metabolite_id),
        backref='diseases',
        foreign_keys=[MetaboliteDiseaseLink_table.c.metabolite_id,MetaboliteDiseaseLink_table.c.disease_id]) 
})

"""

from db_objects import *
m = Metabolite()
m.sum_formula="test"
m.add(session)
session.commit()

m = Metabolite()
m.sum_formula="test2"
m.add(session)
session.commit()

hm = HMDBMetabolite()
hm.metabolite_id = m.id
hm.add(session)
hm.hmdb_id = "TESTID"
session.commit()


s = Substituent()
s.name = "sub1"
s.add(session)
session.commit()

s = Substituent()
s.name = "sub2"
s.add(session)
session.commit()

m.substituents.append(s)
session.commit()

news = session.query(Substituent).filter_by(name='sub1').first()
m.substituents.append(news)
session.commit()

news = session.query(Substituent).filter_by(name='totalnew').first()
if news is None:
    # make one
    s = Substituent()
    s.name = "totalnew"
    s.substutient_id = 3
    s.add(session)
    session.commit()
    m.substituents.append(s)
    session.commit()

m.substituents.append(news)
session.commit()


b = BiologicalOrigin()
b.origin_name = "endogenous"
b.db_origin = "HMDB"
b.add(session)

m.biological_origins.append(b)
session.commit()

b = BiologicalOrigin()
b.origin_name = "food2"
b.db_origin = "HMDB"
b.add(session)
m.biological_origins.append(b)

session.commit()

"""


class Taxonomy():
    def __init__(self):
        pass

