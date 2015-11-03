-- CREATE USER 'metabolomics'@'localhost' IDENTIFIED BY 'metabolomics';
-- GRANT ALL PRIVILEGES ON metabolomics.* TO 'metabolomics'@'localhost';

-- CREATE DATABASE metabolomics;

--  DROP DATABASE metabolomics;
--  CREATE DATABASE metabolomics;
--  USE metabolomics;

CREATE TABLE metabolites 
(
metabolite_id int NOT NULL AUTO_INCREMENT,
InCHI text,
InCHI_key varchar(255),
SMILES text,
monoisotopic_mass double,
sum_formula varchar(255),
PRIMARY KEY (metabolite_id)
);
ALTER TABLE `metabolites` ADD INDEX (`InCHI_key`);

CREATE TABLE hmdb_metabolites
(
metabolite_id int,
hmdb_id varchar(255),
name varchar(255),
fooddb_id varchar(255),
chemspider_id int,
kegg_id varchar(255),
biocyc_id varchar(255),
metlin_id int,
pubchem_compound_id int,
chebi_id int,
het_id varchar(255),
kingdom varchar(255),
super_class varchar(255),
compound_class varchar(255),
sub_class varchar(255),
PRIMARY KEY (metabolite_id)
);
ALTER TABLE `hmdb_metabolites` ADD INDEX (`hmdb_id`);

CREATE TABLE metabolites_substituents 
(
metabolite_id int,
substutient_id int
);
ALTER TABLE `metabolites_substituents` ADD INDEX (`metabolite_id`);
ALTER TABLE `metabolites_substituents` ADD INDEX (`substutient_id`);

CREATE TABLE substituents 
(
substutient_id int NOT NULL AUTO_INCREMENT,
name varchar(255),
db_origin varchar(255),
PRIMARY KEY (substutient_id)
);
ALTER TABLE `substituents` ADD INDEX (`name`);

CREATE TABLE metabolites_origins 
(
metabolite_id int,
biological_origin_id int
);
ALTER TABLE `metabolites_origins` ADD INDEX (`metabolite_id`);
ALTER TABLE `metabolites_origins` ADD INDEX (`biological_origin_id`);

CREATE TABLE biological_origin 
(
biological_origin_id int NOT NULL AUTO_INCREMENT,
origin_name varchar(255),
db_origin varchar(255),
PRIMARY KEY (biological_origin_id)
);
ALTER TABLE `biological_origin` ADD INDEX (`origin_name`);


CREATE TABLE metabolites_diseases
(
metabolite_id int,
disease_id int
);
ALTER TABLE `metabolites_diseases` ADD INDEX (`metabolite_id`);
ALTER TABLE `metabolites_diseases` ADD INDEX (`disease_id`);

CREATE TABLE diseases 
(
disease_id int NOT NULL AUTO_INCREMENT,
disease_name varchar(255),
omim_id varchar(255),
PRIMARY KEY (disease_id)
);
ALTER TABLE `diseases` ADD INDEX (`disease_name`);



-- ------------------------
-- v 2.0
-- ------------------------

CREATE TABLE t3db_metabolites
(
metabolite_id int,
t3db_id varchar(255),
name varchar(255),
fooddb_id varchar(255),
chemspider_id int,
kegg_id varchar(255),
biocyc_id varchar(255),
pubchem_compound_id int,
chebi_id int,
actor_id int,
chembl_id varchar(255),
omim_id varchar(255),
ctd_id varchar(255),
stitch_id varchar(255),
pdb_id varchar(255),
kingdom varchar(255),
super_class varchar(255),
compound_class varchar(255),
sub_class varchar(255),
PRIMARY KEY (metabolite_id)
);
ALTER TABLE `t3db_metabolites` ADD INDEX (`t3db_id`);

CREATE TABLE metabolites_toxic_category 
(
metabolite_id int,
toxic_category_id int
);
ALTER TABLE `metabolites_toxic_category` ADD INDEX (`metabolite_id`);
ALTER TABLE `metabolites_toxic_category` ADD INDEX (`toxic_category_id`);

CREATE TABLE toxic_categories 
(
toxic_category_id int NOT NULL AUTO_INCREMENT,
name varchar(255),
db_origin varchar(255),
PRIMARY KEY (toxic_category_id)
);
ALTER TABLE `toxic_categories` ADD INDEX (`name`);

