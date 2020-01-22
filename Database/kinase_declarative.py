#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 17:01:24 2020

@author: zho30
"""

#import library
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

#create a base object
Base = declarative_base()

#setting up the class for the table
class KinaseGeneMeta(Base):
    __tablename__ = 'kinase_gene_meta'
    protein_name = Column(String)
    uniprot_number = Column(Integer)
    uniprot_entry = Column(String)
    gene_name = Column(String, primary_key=True)
    kinase_family = Column(String)
    # gene_aliases <from backref in KinaseGeneName>
    
    #create a function to return the object as dictionary
    def to_dict(self):
        """
        Returns the KinaseGeneMeta object as a dictionary.
        """
        output = {
               "protein_name": self.protein_name,
               "uniprot_number": self.uniprot_number,
               "uniprot_entry":self.uniprot_entry,
               "gene_name": self.gene_name,
               "kinase_family": self.kinase_family
                }
        return output
    

class KinaseGeneName(Base):
    __tablename__ = 'kinase_gene_names'
    gene_name = Column(String, ForeignKey('kinase_gene_meta.gene_name'))
    gene_alias = Column(String, primary_key=True)
    meta = relationship('KinaseGeneMeta', backref=backref('gene_aliases', uselist=True))
    phosphosites = relationship('PhosphositeMeta', secondary='kinase_phosphosite_relations')
    
    def to_dict(self):
        """
        Returns the KinaseGeneName as a dictionary:
        """
        output = {
                "gene_name" : self.gene_name,
                "gene_alias" : self.gene_alias
                }
        return output


class KinaseSubcellularLocation(Base):
    __tablename__ = 'subcellular_location'
    subcellular_location_id = Column(Integer, primary_key = True)
    gene_name = Column(String, ForeignKey('kinase_gene_names.gene_alias'))
    subcellular_location = Column(String)
    kinase_meta = relationship('KinaseGeneName', backref=backref('subcellular_locations', uselist=True))
    
    def to_dict(self):
        """
        Return the KinaseSubcellularLocation as a dictionary.
        """
        output = {
                "subcellular_location_id": self.subcellular_location_id,
                "gene_name": self.gene_name,
                "subcellular_location": self.subcellular_location
                }
        return output


class SubstrateMeta(Base):
    __tablename__ = 'substrate_meta'
    substrate_id = Column(Integer, primary_key = True)
    substrate_name = Column(String)
    substrate_gene_name = Column(String)
    substrate_uniprot_entry = Column(String)
    substrate_uniprot_number = Column(Integer)
    
    def to_dict(self):
        """
        Return SubstrateMeta as a dictionary.
        """
        output = {
                "substrate_id": self.substrate_id,
                "substrate_name": self.substrate_name,
                "substrate_gene_name": self.substrate_gene_name,
                "substrate_uniprot_entry": self.substrate_uniprot_entry,
                "substrate_uniprot_number": self.substrate_uniprot_number
                }
        return output
    
class KinasePhosphositeRelations(Base):
    # a many to many relationship table between substrates and kinases
    __tablename__ = "kinase_phosphosite_relations"
    phosphosite_id = Column(Integer, ForeignKey('phosphosite_meta.phosphosite_meta_id'), primary_key=True)
    kinase_gene_id = Column(String, ForeignKey('kinase_gene_names.gene_alias'), primary_key=True)
    
    
class PhosphositeMeta(Base):
    __tablename__ = 'phosphosite_meta'
    phosphosite_meta_id = Column(Integer, primary_key=True)
    substrate_meta_id = Column(Integer, ForeignKey('substrate_meta.substrate_id'))
    substrate = relationship("SubstrateMeta", backref=backref('phosphosites', uselist=True))
    phosphosite = Column(String)
    chromosome = Column(Integer)
    karyotype_band = Column(String)
    strand = Column(Integer)
    start_position = Column(Integer)
    end_position = Column(Integer)
    neighbouring_sequences = Column(String)
    kinases = relationship('KinaseGeneName', secondary='kinase_phosphosite_relations')
    
    def to_dict(self):
        """
        Return PhosphositeMeta as a dictionary.
        """
        output = {
                "phosphosite_meta_id": self.phosphosite_meta_id,
                "substrate_meta_id": self.substrate_meta_id,
                "phosphosite": self.phosphosite,
                "chromosome": self.chromosome,
                "karyotype_band": self.karyotype_band,
                "strand": self.strand,
                "start_position": self.start_position,
                "end_position": self.end_position,
                "neighbouring_sequences": self.neighbouring_sequences,
                }
        return output
    

class Inhibitor(Base):
    __tablename__ = 'inhibitor'
    inhibitor_id = Column(Integer, primary_key=True)
    inhibitor = Column(String)
    antagonizes_gene = Column(String, ForeignKey('kinase_gene_names.gene_alias'))
    kinases = relationship('KinaseGeneName', backref=backref('inhibitors', uselist=True))
    molecular_weight = Column(Integer)
    images_url = Column(String)
    empirical_formula = Column(String)
    #references = Column(String)
    
    def to_dict(self):
        """
        Return Inhibitor as a dictionary.
        """
        output = {
                "inhibitor_id": self.inhibitor_id,
                "inhibitor": self.inhibitor,
                "antagonizes_gene": self.antagonizes_gene,
                "molecular_weight": self.molecular_weight,
                "images_url": self.images_url,
                "empirical_formula": self.empirical_formula
                }
        return output

#create an engine that stores the data in the local directory's kinase_database.db 
engine = create_engine('sqlite:///kinase_database.db')

if __name__ == '__main__':
    #create all tables in the engine
    Base.metadata.create_all(engine)