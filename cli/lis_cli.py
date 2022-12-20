#!/usr/bin/env python3

import os
import click
from.lis_common import setup_logging
from .genus_species_collections import ProcessCollections


@click.command()
@click.option('--taxa_list', default="../_data/taxon_list.yml", help='''Taxa.yml file. (Default: ../_data/taxon_list.yml)''')
@click.option('--collections_out', default="../_data/taxa/", help='''Output for collections.''')
def populate_jekyll(taxa_list, collections_out):
    '''CLI entry for populate-jekyll'''
    logger = setup_logging('./testme.log', '', 'populate-jekyll') 
    logger.info("Processing Collections...")
    parser = ProcessCollections(logger)  # initialize class
    logger.info("Outputting Collections...")
    parser.parse_collections(taxa_list, collections_out)  # parse_collections

@click.command()
@click.option('--taxa_list', default="../_data/taxon_list.yml", help='''Taxa.yml file. (Default: ../_data/taxon_list.yml)''')
@click.option('--nodes_out', default="/var/www/html/dscensor", help='''Output for dscensor nodes.''')
@click.option('--log_level', default="INFO", help='''Log Level to output messages. (default: INFO)''')
def populate_dscensor(taxa_list, nodes_out, log_level):
    '''CLI entry for populate-jekyll'''
    logger = setup_logging('./testme.log', log_level, 'populate-dscensor') 
    logger.info("Processing Collections...")
    parser = ProcessCollections(logger)  # initialize class
    parser.parse_collections(taxa_list)  # parse_collections
    logger.info("Creating DSCensor Nodes...")
    parser.populate_dscensor(nodes_out)  # populate JBrowse2

@click.command()
@click.option('--taxa_list', default="../_data/taxon_list.yml", help='''Taxa.yml file. (Default: ../_data/taxon_list.yml)''')
@click.option('--jbrowse_out', default="/var/www/html/jbrowse2_autodeploy", help='''Output directory for Jbrowse2. (Default: /var/www/html/jbrowse2_autodeploy)''')
@click.option('--cmds_only', is_flag=True, help='''Output commands only. Do not run Jbrowse2 just output the commands that would be run.''')
@click.option('--log_level', default="INFO", help='''Log Level to output messages. (default: INFO)''')
def populate_jbrowse2(taxa_list, jbrowse_out, cmds_only, log_level):
    '''CLI entry for populate-jbrowse2'''
    logger = setup_logging('./testme.log', log_level, 'populate-jbrowse2') 
    logger.info("Processing Collections...")
    parser = ProcessCollections(logger)  # initialize class
    parser.parse_collections(taxa_list)  # parse_collections
    logger.info("Creating JBrowse2 Config...")
    parser.populate_jbrowse2(jbrowse_out, cmds_only)  # populate JBrowse2

@click.command()
@click.option('--taxa_list', default="../_data/taxon_list.yml", help='''Taxa.yml file. (Default: ../_data/taxon_list.yml)''')
@click.option('--blast_out', default="/var/www/html/db/Genomic_Sequence_Collection", help='''Output directory for Jbrowse2. (Default: /var/www/html/db/Genomic_Sequence_Collection)''')
@click.option('--cmds_only', is_flag=True, help='''Output commands only. Do not run makeblastdb just output the commands that would be run.''')
@click.option('--log_level', default="INFO", help='''Log Level to output messages. (default: INFO)''')
def populate_blast(taxa_list, blast_out, cmds_only, log_level):
    '''CLI entry for populate-blast'''
    logger = setup_logging('./testme.log', log_level, 'populate-blast') 
    logger.info('test me')
    logger.info("Processing Collections...")
    parser = ProcessCollections(logger)  # initialize class
    parser.parse_collections(taxa_list)  # parse_collections
    logger.info("Creating BLAST DBs...")
    parser.populate_blast(blast_out, cmds_only)  # populate BLAST
