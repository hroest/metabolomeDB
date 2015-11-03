
-- # Join all the way through -> map 20655
-- SELECT metabolites.metabolite_id, compounds.name, compounds.hmdb_id, hmdb_metabolites.name 
-- FROM compounds 
--   INNER JOIN metabolomics.hmdb_metabolites ON compounds.hmdb_id = hmdb_metabolites.hmdb_id 
--   INNER JOIN metabolomics.metabolites ON metabolomics.hmdb_metabolites.metabolite_id = metabolomics.metabolites.metabolite_id  
--   WHERE compounds.hmdb_id IS NOT NULL  LIMIT 10;

-- # Join all the way through -> map 20655
-- #################
-- ### Insert and map by hmdb key
-- #################
CREATE TABLE metabolites_foodb_compounds AS
SELECT foodb.compounds.id foodb_compounds_id, metabolites.metabolite_id
FROM foodb.compounds 
  INNER JOIN metabolomics.hmdb_metabolites ON foodb.compounds.hmdb_id = hmdb_metabolites.hmdb_id 
  INNER JOIN metabolomics.metabolites ON metabolomics.hmdb_metabolites.metabolite_id = metabolomics.metabolites.metabolite_id  
  WHERE foodb.compounds.hmdb_id IS NOT NULL;
ALTER TABLE `metabolites_foodb_compounds` ADD INDEX (`metabolite_id`);
ALTER TABLE `metabolites_foodb_compounds` ADD INDEX (`foodb_compounds_id`);

-- # we did not get all
-- # SELECT  compounds.hmdb_id 
-- # FROM compounds where compounds.hmdb_id NOT IN (select hmdb_id from metabolomics.hmdb_metabolites );
-- create temporary table t as select  distinct(hmdb_id) from compounds where compounds.hmdb_id is not NULL  ;
-- alter table t ADD INDEX (`hmdb_id`);
-- create temporary table t2 as select hmdb_id from metabolomics.hmdb_metabolites ;
-- alter table t2 ADD INDEX (`hmdb_id`);
-- select hmdb_id
-- FROM t where t.hmdb_id NOT IN (select hmdb_id from metabolomics.hmdb_metabolites );
-- select t.hmdb_id
-- FROM t left join t2 on t.hmdb_id = t2.hmdb_id where t2.hmdb_id is NULL;


-- #################
-- ### Insert and map by inchikey
-- #################
INSERT INTO metabolites_foodb_compounds (foodb_compounds_id, metabolite_id)
select compounds.id, metabolites.metabolite_id  FROM foodb.compounds  inner join metabolomics.metabolites on short_inchikey=inCHI_key where hmdb_id is NULL and  compounds.id not in (select foodb_compounds_id from metabolites_foodb_compounds);


-- # unmapped: we still have 6480 of which 3101 have no inchi key
select count(*) FROM foodb.compounds  where compounds.id not in (select foodb_compounds_id from metabolites_foodb_compounds)  ;
select count(*) FROM foodb.compounds  where compounds.id not in (select foodb_compounds_id from metabolites_foodb_compounds)  and moldb_inchi is NULL;

-- #################
-- ### Insert and map the rest of FooDB
-- #################
create temporary table foodb_mapping_table_tmp as 
select moldb_inchi, moldb_inchikey, moldb_smiles, moldb_mono_mass, moldb_formula, id foodb_compounds_id
FROM foodb.compounds  where compounds.id not in (select foodb_compounds_id from metabolites_foodb_compounds);

ALTER TABLE metabolomics.metabolites ADD COLUMN foodb_id int;
INSERT INTO metabolomics.metabolites (InCHI, InCHI_key, SMILES, monoisotopic_mass, sum_formula, foodb_id)
select moldb_inchi, moldb_inchikey, moldb_smiles, moldb_mono_mass, moldb_formula, foodb_compounds_id
FROM foodb_mapping_table_tmp;

INSERT INTO metabolomics.metabolites_foodb_compounds (foodb_compounds_id, metabolite_id)
SELECT foodb_id, metabolite_id from metabolomics.metabolites where foodb_id is not NULL;
-- # drop the index again
ALTER TABLE metabolomics.metabolites DROP COLUMN foodb_id;

-- #################
-- ### Done
-- #################
select count(*) from foodb.compounds;
select count(*) from metabolites  inner join metabolites_foodb_compounds on metabolites.metabolite_id = metabolites_foodb_compounds.metabolite_id inner join foodb.compounds on compounds.id = metabolites_foodb_compounds.foodb_compounds_id;

-- ### -> should be equal ! 

