#!/usr/bin/env python3

import os
import sys
import yaml
import json
import pathlib
import requests
import subprocess
from html.parser import HTMLParser


class ProcessCollections():
    '''Parses Collections from the datastore at https://data.legumeinfo.org'''

    def __init__(self, logger=None, datastore_url="https://data.legumeinfo.org", jbrowse_url=""):
        self.logger = logger
        if self.logger:
            self.logger.info('logger initialized')
        self.collections = []  # get collections for writing site
        self.datastore_url = datastore_url  # URL to search for collections
        self.jbrowse_url = jbrowse_url  # domain for jbrowse sessions
        self.out_dir = "/var/www/html/jbrowse_autodeploy"  # out dir for jbrowse2 tracks
        self.files = {}  # get types for making jbrowse2
        self.file_objects = []  # make a list of all file objects to write for DSCensor nodes
        self.collection_types = ["genomes", "annotations", "diversity", "expression",
                                 "genetic", "markers", "synteny", "genome_alignments"]  # types to search for

    def parse_attributes(self, response_text):  # inherited from Sammyjava 
        '''parses attributes returned from HTMLParser. Credit to SammyJava'''
        collections = []
#        relationships = {'genomes': {}, 'annotations': {}}  # establish related objects

        class CollectionsParser(HTMLParser):
            '''HTMLParser for Collections'''

            def handle_starttag(self, tag, attrs):
                '''Feed from HTMLParser'''
                for attr in attrs:
                    if((attr[0]=='href' and "/annotations/" in attr[1])
                            or (attr[0]=='href' and "/diversity/" in attr[1])
                            or (attr[0]=='href' and "/expression/" in attr[1])
                            or (attr[0]=='href' and "/genetic/" in attr[1])
                            or (attr[0]=='href' and "/genomes/" in attr[1])
                            or (attr[0]=='href' and "/markers/" in attr[1])
                            or (attr[0]=='href' and "/synteny/" in attr[1])
                            or (attr[0]=='href' and "/genome_alignments/" in attr[1])):
                        collections.append(attr[1])
        CollectionsParser().feed(response_text)  # populate collections
        self.collections = collections  # set self.collections

    def get_attributes(self, parts):
        '''parse parts return url components'''
        gensp = f'{parts[1].lower()[:3]}{parts[2][:2]}'  # make gensp
        strain = parts[-2]  # get strain and key information
        return (gensp, strain)
 
    def process_collections(self, cmds_only, mode):
        '''General method to create a jbrowse-components config or populate a blast db using mode'''
        logger = self.logger
        pathlib.Path(self.out_dir).mkdir(parents=True, exist_ok=True)
        for collectionType in self.collection_types:
            for file in self.files[collectionType]:
               # jbrowse add-assembly -a alis -n "full name" --out /path/to/jbrowse2 URL
                cmd = ''
                url = self.files[collectionType][file]['url']
                if not url:  # do not take objects with no defined link
                    continue
                name = self.files[collectionType][file]['name']
                genus = self.files[collectionType][file]['genus']
                parent = self.files[collectionType][file]['parent']
                species = self.files[collectionType][file]['species']
                infraspecies = self.files[collectionType][file]['infraspecies']
                filetype = url.split('.')[-3]  # get file type from datastore file name
                self.file_objects.append({'filename' : name, 'filetype' : filetype, 'url' : url, 'counts' : '',
                                          'genus' : genus, 'species' : species, 'origin' : 'LIS', 
                                          'infraspecies' : infraspecies, 'derived_from' : parent})
                if collectionType == 'genomes':  # add genome
                    if mode == "jbrowse":  # for jbrowse
                        cmd = f'jbrowse add-assembly -a {name} --out {self.out_dir}/ -t bgzipFasta --force'
                        cmd += f' -n "{genus.capitalize()} {species} {infraspecies} {collectionType.capitalize()}" {url}'
                    elif mode == "blast":  # for blast
                        cmd = f'set -o pipefail -o errexit -o nounset; curl {url} | gzip -dc'  # retrieve genome and decompress
                        cmd += f'| makeblastdb -parse_seqids -out {self.out_dir}/{name} -hash_index -dbtype nucl -title "{genus.capitalize()} {species} {infraspecies} {collectionType.capitalize()}"'
                if collectionType == 'annotations':  # add annotation
                    if mode == "jbrowse":  # for jbrowse
                        cmd = f'jbrowse add-track -a {parent} --out {self.out_dir}/ --force'
                        cmd += f' -n "{genus.capitalize()} {species} {infraspecies} {collectionType.capitalize()}" {url}'
                    elif mode == "blast":  # for blast
                        if not url.endswith('faa.gz'):
                            continue
                        cmd = f'set -o pipefail -o errexit -o nounset; curl {url} | gzip -dc'  # retrieve genome and decompress
                        cmd += f'| makeblastdb -parse_seqids -out {self.out_dir}/{name} -hash_index -dbtype prot -title "{genus.capitalize()} {species} {infraspecies} {collectionType.capitalize()}"'
#Quick Note: Change senteny and diversity cmd jbrowse lines later. They are like this for now just to see if it will even work.
                if collectionType == 'genome_alignments':  # add pair-wise paf files
                    if mode == "jbrowse":  # for jbrowse
                        cmd = f"jbrowse add-track --assemblyNames {','.join(parent)} --out {self.out_dir}/ {url} --force"
                    elif mode == "blast":  # for blast
                        continue  # synteny is not blastable at the moment
#                        cmd = f'set -o pipefail -o errexit -o nounset; curl {url} | gzip -dc'  # retrieve genome and decompress
#                        cmd += f'| makeblastdb -parse_seqids -out {self.out_dir}/{name} -hash_index -dbtype nucl -title "{genus.capitalize()} {species} {infraspecies} {collectionType.capitalize()}"'
    
                # MORE CANONICAL TYPES HERE
                if not cmd:  # continue for null objects
                    continue
                if cmds_only:  # output only cmds
                    print(cmd)
                elif subprocess.check_call(cmd, shell=True, executable='/bin/bash'):  # execute cmd and check exit value = 0
                    logger.error(f"ERROR: {cmd}")

    def populate_jbrowse2(self, out_dir="/var/www/html/jbrowse2_autodeploy", cmds_only=False):
        '''deploy jbrowse2 from collected objects'''
        self.out_dir = out_dir
        pathlib.Path(self.out_dir).mkdir(parents=True, exist_ok=True)
        self.process_collections(cmds_only, "jbrowse")  # process collections for jbrowse-components

    def populate_blast(self, out_dir="/var/www/html/db/Genomic_Sequence_Collection", cmds_only=False):
        '''Populate a BLAST db for genome_main, mrna/mrna_primary and protein/protein_primary'''
        self.out_dir = out_dir
        pathlib.Path(self.out_dir).mkdir(parents=True, exist_ok=True)
        self.process_collections(cmds_only, "blast")  # process collections for BLAST sequenceserver

    def populate_dscensor(self, out_dir="/var/www/html/dscensor/"):
        '''Populate dscensor nodes for loading into a neo4j database'''
        self.out_dir = out_dir
        pathlib.Path(self.out_dir).mkdir(parents=True, exist_ok=True)
        self.process_collections(True, "dscensor")  # process collections for DSCENSOR
        for n in self.file_objects:
            node_out = open(f'{self.out_dir}/{n["filename"]}.json', 'w')  # file to write node to
            node_out.write(json.dumps(n))
            node_out.close()

    def parse_collections(self, target="../_data/taxon_list.yml", species_collections=None):
        '''Retrieve and output collections for jekyll site'''
        #print(target)
        logger = self.logger
        yamlStandard = (open('TEST.yaml', 'w'))
        taxonList = yaml.load(open(target, 'r').read(),
                                     Loader=yaml.FullLoader)  # load taxon list
        for taxon in taxonList:
            if not 'genus' in taxon:
                logger.debug('ERROR GENOME REQUIRED: {taxon}')  # change to log
                sys.exit(1)
            genus = taxon['genus']
            genusDescriptionUrl = f'{self.datastore_url}/{genus}/GENUS/about_this_collection/description_{genus}.yml'
            genusDescriptionResponse = requests.get(genusDescriptionUrl)
            speciesCollectionsFile = None  # yaml file to write for species collections
            genusResourcesFile = None  # yaml file to write for genus resources
            speciesResourcesFile = None  # yaml file to write for species resources
            if genusDescriptionResponse.status_code == 200:  # Genus Description yml SUCCESS
                speciesCollectionsFilename = None
                genusDescription = yaml.load(genusDescriptionResponse.text, Loader=yaml.FullLoader)
                if species_collections:
                    collection_dir = f'{os.path.abspath(species_collections)}/{taxon["genus"]}'
                    pathlib.Path(collection_dir).mkdir(parents=True, exist_ok=True)
                    speciesCollectionsFilename = f'{collection_dir}/species_collections.yml'
                    genusResourcesFilename = f'{collection_dir}/genus_resources.yml'
                    speciesResourcesFilename = f'{collection_dir}/species_resources.yml'
#                if not speciesCollectionsFilename:
#                    speciesCollectionsFilename = "../_data/taxa/"+taxon["genus"]+"/species_collections.yml"  # change this to fstring
                if speciesCollectionsFilename:
                    speciesCollectionsFile = open(speciesCollectionsFilename, 'w')
                    print('---', file=speciesCollectionsFile)
                    print('species:', file=speciesCollectionsFile)
                    genusResourcesFile = open(genusResourcesFilename, 'w')
                    speciesResourcesFile = open(speciesResourcesFilename, 'w')
                    print("---", file=genusResourcesFile)
                    yaml.dump(genusDescription, genusResourcesFile)
                    ## species loop
                    print("---", file=speciesResourcesFile)
                    print("species:", file=speciesResourcesFile)
                speciesDescriptions = []
                for species in genusDescription["species"]:
                    strain_resources = {}
                    logger.info(f"Searching {self.datastore_url} for: "+taxon["genus"]+" "+species)
                    if speciesCollectionsFilename:
                        print('- '+'name: '+species, file=speciesCollectionsFile)
                    speciesUrl = f'{self.datastore_url}/{genus}/{species}'
                    speciesDescriptionUrl = f'{speciesUrl}/about_this_collection/description_{genus}_{species}.yml'
                    logger.debug(speciesDescriptionUrl)  # get species description url
                    speciesDescriptionResponse = requests.get(speciesDescriptionUrl)
#                    if speciesDescriptionResponse.status_code == 200:
#                        speciesDescription = yaml.load(speciesDescriptionResponse.text, Loader=yaml.FullLoader)  # load the yaml from the datastore for species
#                        speciesDescription['resources'].append()
#                        speciesDescriptions.append(speciesDescription)
#                        print(speciesDescription['resources'])
                    for collectionType in self.collection_types:
                        if collectionType not in self.files:  # add new type
                            self.files[collectionType] = {}
                        if speciesCollectionsFilename:
                            print('  '+collectionType+':', file=speciesCollectionsFile)
                        collectionsUrl = speciesUrl+"/"+collectionType+"/"
                        collectionsResponse = requests.get(collectionsUrl)
                        if collectionsResponse.status_code==200:  # Collections SUCCESS
                            self.collections = []
                            self.parse_attributes(collectionsResponse.text)  # Feed response from GET
                            for collectionDir in self.collections:
                                parts = collectionDir.split('/')
                                logger.debug(parts)
                                name = parts[4]
                                url = ''
                                parent = ''
                                parts = self.get_attributes(parts)
                                lookup = f"{parts[0]}.{'.'.join(name.split('.')[:-1])}"  # reference name in datastructure
                                if(collectionType == 'genomes'):  # add parent genomes
                                    url = f'{self.datastore_url}{collectionDir}{parts[0]}.{parts[1]}.genome_main.fna.gz'
                                    linear_session = {
                                        "views": [
                                            {"assembly": lookup,
                                             "loc": "" ,
                                             "type": "LinearGenomeView",
#                                            "tracks": [
#                                                " gff3tabix_genes " ,
#                                                " volvox_filtered_vcf " ,
#                                                " volvox_microarray " ,
#                                                " volvox_cram "
#                                            ]
                                           }
                                        ]
                                    }
                                    strain_lookup = lookup.split('.')[1]  # the strain for the lookup
                                    linear_url = f'{self.jbrowse_url}/?config=config.json&session=spec-{linear_session}'
                                    linear_data = {'name': f'JBrowse2 {lookup}', 'URL': str(linear_url).replace("'", '\\"'), 
                                                   'description': 'JBrowse2 Linear Genome View'}
                                    if strain_lookup not in strain_resources:
                                        strain_resources[strain_lookup] = []  # init list
                                    strain_resources[strain_lookup].append(linear_data)
                                    logger.debug(url)
                                if(collectionType == 'annotations'):
                                    genome_lookup = '.'.join(lookup.split('.')[:-1])  # grab genome
                                    self.files['genomes'][genome_lookup]['url']
                                    parent = genome_lookup
                                    url = f'{self.datastore_url}{collectionDir}{parts[0]}.{parts[1]}.gene_models_main.gff3.gz'
                                    protprimaryUrl = f'{self.datastore_url}{collectionDir}{parts[0]}.{parts[1]}.protein_primary.faa.gz'
                                    protprimaryResponse = requests.get(protprimaryUrl)
                                    if protprimaryResponse.status_code==200:
                                        protprimary_lookup = f'{lookup}.protein_primary'
                                        self.files[collectionType][protprimary_lookup] = {'url': protprimaryUrl, 'name': protprimary_lookup, 'parent': parent,
                                                                                          'genus': genus, 'species': species,
                                                                                          'infraspecies': parts[1], 'taxid': 0}
                                    else:
                                        logger.debug(f'protprimaryUrl(PrimaryProtien):Failed {protprimaryResponse}')

                                    proteinUrl =f'{self.datastore_url}{collectionDir}{parts[0]}.{parts[1]}.protein.faa.gz'
                                    protein_response = requests.get(proteinUrl)
                                    if protein_response.status_code==200:
                                        protein_lookup = f'{lookup}.protein'
                                        self.files[collectionType][protein_lookup] = {'url': proteinUrl, 'name': protein_lookup, 'parent': parent,
                                                                                      'genus': genus, 'species': species,
                                                                                      'infraspecies': parts[1], 'taxid': 0}
                                    else:
                                        logger.debug(f'proteinUrl(Protein):Failed {protein_response}')
#####
                                if(collectionType == 'synteny'):
#                                   checksum reader
                                    checksumUrl = f'{self.datastore_url}{collectionDir}CHECKSUM.{parts[1]}.md5'
                                    checkResponse = requests.get(checksumUrl)
                                    if checkResponse.status_code==200:
                                        continue
#                                        openCheck = open(checksumUrl)
#                                        for line in openCheck:
#                                            sytenyUrl = f'{self.datastore_url}{collectionDir}{parts[0]}.{parts[1]}.{line}'
#                                            yamlStandard.write('{sytenyUrl}')
                                    else:  #CheckSum FAILURE
                                        logger.debug(f'GET Failed for checksum {checkResponse.status_code} {checksumUrl}')
                                elif(collectionType == 'genome_alignments'):
                                    checksumUrl = f'{self.datastore_url}{collectionDir}CHECKSUM.{parts[1]}.md5'
                                    checkResponse = requests.get(checksumUrl)
                                    logger.debug(checkResponse)
                                    if checkResponse.status_code==200:  # file exists at datastore_url
                                        for line in checkResponse.text.split('\n'):
                                            logger.debug(line)
                                            fields = line.split()
                                            if fields:  # process if fields exists
                                                if fields[1].endswith('paf.gz'):  # get paf file
                                                    paf_lookup = fields[1].replace('./', '')  # get paf file to load will start with ./
                                                    logger.debug(paf_lookup)
                                                    pafUrl = f'{self.datastore_url}{collectionDir}{paf_lookup}'  # where the paf file is in the datastore
                                                    paf_parts = paf_lookup.split('.')  # split the paf file name into parts delimited by '.'
                                                    parent1 = '.'.join(paf_parts[:3])  # parent 1 in pair-wise
                                                    parent2 = '.'.join(paf_parts[5:8])  # parent 2 in pair-wise
                                                    self.files[collectionType][paf_lookup] = {'url': pafUrl, 'name': paf_lookup, 
                                                                                              'parent': [parent1, parent2],
                                                                                              'genus': genus, 'species': species,
                                                                                              'infraspecies': parts[1], 'taxid': 0}
                                                    logger.debug(self.files[collectionType][paf_lookup])
#####

                                self.files[collectionType][lookup] = {'url': url, 'name': lookup, 'parent': parent,
                                                                      'genus': genus, 'species': species,
                                                                      'infraspecies': parts[1], 'taxid': 0}  # add type and url
                                readmeUrl = f'{self.datastore_url}/{collectionDir}README.{name}.yml'
                                readmeResponse = requests.get(readmeUrl)
                                if readmeResponse.status_code==200:
                                    readme = yaml.load(readmeResponse.text, Loader=yaml.FullLoader)
                                    synopsis = readme["synopsis"]
                                    taxid = readme["taxid"]
                                    self.files[collectionType][lookup]['taxid'] = taxid  # set taxid if needed for blast
                                    if speciesCollectionsFilename:
                                        print('    - collection: '+name, file=speciesCollectionsFile)
                                        print('      synopsis: "'+synopsis+'"', file=speciesCollectionsFile)
                                else:  # README FAILURE
                                    logger.debug(f'GET Failed for README {readmeResponse.status_code} {readmeUrl}')  # change to log
#                                    sys.exit(1)
                        else:  # Collections FAILUTRE
                            logger.debug(f'GET Failed for collections {collectionsResponse.status_code} {collectionsUrl}')  # change to log
#                            sys.exit(1)
#                    logger.info(f'{}')
                    if speciesDescriptionResponse.status_code == 200:  # add the remainder of the species resources and info and add jbrowse
                        speciesDescription = yaml.load(speciesDescriptionResponse.text, Loader=yaml.FullLoader)  # load the yaml from the datastore for species
                        count = 0
                        for strain in speciesDescription['strains']:
                            if strain['identifier'] in strain_resources:  # add to this strain
                                if speciesDescription['strains'][count].get('resources', None):  # this strain has resources
                                    for resource in strain_resources[strain['identifier']]:  # append all the resources to the existing
                                        speciesDescription['strains'][count]['resources'].append(resource)
                                else:
                                    speciesDescription['strains'][count]['resources'] = strain_resources[strain['identifier']]  # set resources
                            count += 1
                        speciesDescriptions.append(speciesDescription)
                ## dump out species_resources.yml
                yaml.dump(speciesDescriptions, speciesResourcesFile)
            else:  # FAILURE
                logger.warning(f'GET Failed for genus {genusDescriptionResponse.status_code} {genusDescriptionUrl}')  # change to log
#                sys.exit(1)


if __name__ == '__main__':
    parser = ProcessCollections()
    parser.parse_collections()
