#!/usr/bin/env python3

import os
import sys
import yaml
import json
import pathlib
import requests
import subprocess
from html.parser import HTMLParser


class ProcessCollections:
    """Parses Collections from the datastore_url provided. Default: https://data.legumeinfo.org"""

    def __init__(
        self, logger=None, datastore_url="https://data.legumeinfo.org", jbrowse_url=""
    ):
        self.logger = logger
        if self.logger:
            self.logger.info("logger initialized")
        self.collections = []  # stores all collections from self.parse_attributes
        self.datastore_url = datastore_url  # URL to search for collections
        self.jbrowse_url = jbrowse_url  # URL to append jbrowse2 sessions
        self.out_dir = "./autocontent"  # output directory for objects.
        self.files = (
            {}
        )  # stores all files by collection type. This is used to populate output after scanning
        self.file_objects = []  # a list of all file objects to write for DSCensor nodes
        self.collection_types = (
            [  # collection types currently recorded from datastore_url
                "genomes",  # fasta
                "annotations",  # gff3
                "diversity",  # vcf
                "expression",  # bed, wig, bw
                "genetic",  # bed
                "markers",  # bed
                "synteny",  # paf, this may be depricated now for genome_alignments
                "genome_alignments",  # paf
            ]
        )  # types to search the datastore_url for
        #        self.relationships = {'genomes': {'annotations': ...}, 'annotations': {}}  # establish related objects once this is relevant

    def parse_attributes(self, response_text):  # inherited from Sammyjava
        """parses attributes returned from HTMLParser. Credit to SammyJava"""
        collections = (
            []
        )  # Prevents self.collections collision with self in CollectionsParser
        collection_types = self.collection_types

        class CollectionsParser(HTMLParser):
            """HTMLParser for Collections"""

            def handle_starttag(self, tag, attrs):
                """Feed from HTMLParser"""
                for attr in attrs:  # check each attribute passed in attrs
                    if attr[0] == "href":  # attribute is a URL
                        for collection_type in collection_types:
                            if (
                                f"/{collection_type}/" in attr[1]
                            ):  # collection_type iterator is in URL attr[1]
                                collections.append(
                                    attr[1]
                                )  # add attr[1] to collections for later use in process_collections

        CollectionsParser().feed(response_text)  # populate collections
        self.collections = collections  # set self.collections

    def get_attributes(self, parts):
        """parse parts return url components"""
        gensp = f"{parts[1].lower()[:3]}{parts[2][:2]}"  # make gensp
        strain = parts[-2]  # get strain and key information
        return (gensp, strain)

    def process_collections(self, cmds_only, mode):
        """General method to create a jbrowse-components config or populate a blast db using mode"""
        logger = self.logger
        pathlib.Path(self.out_dir).mkdir(parents=True, exist_ok=True)
        for collectionType in self.collection_types:
            for file in self.files[collectionType]:
                cmd = ""
                url = self.files[collectionType][file]["url"]
                if not url:  # do not take objects with no defined link
                    continue
                name = self.files[collectionType][file]["name"]
                genus = self.files[collectionType][file]["genus"]
                parent = self.files[collectionType][file]["parent"]
                species = self.files[collectionType][file]["species"]
                infraspecies = self.files[collectionType][file]["infraspecies"]
                filetype = url.split(".")[
                    -3
                ]  # get file type from datastore file name filetype.X.gz
                self.file_objects.append(
                    {
                        "filename": name,
                        "filetype": filetype,
                        "url": url,
                        "counts": "",
                        "genus": genus,
                        "species": species,
                        "origin": "LIS",
                        "infraspecies": infraspecies,
                        "derived_from": parent,
                    }
                )  # object for DSCensor node
                if collectionType == "genomes":  # add genome
                    if mode == "jbrowse":  # for jbrowse
                        cmd = f"jbrowse add-assembly -a {name} --out {self.out_dir}/ -t bgzipFasta --force"
                        cmd += f' -n "{genus.capitalize()} {species} {infraspecies} {collectionType.capitalize()}" {url}'
                    elif mode == "blast":  # for blast
                        cmd = f"set -o pipefail -o errexit -o nounset; curl {url} | gzip -dc"  # retrieve genome and decompress
                        cmd += f'| makeblastdb -parse_seqids -out {self.out_dir}/{name} -hash_index -dbtype nucl -title "{genus.capitalize()} {species} {infraspecies} {collectionType.capitalize()}"'
                if collectionType == "annotations":  # add annotation
                    if mode == "jbrowse":  # for jbrowse
                        cmd = f"jbrowse add-track -a {parent} --out {self.out_dir}/ --force"
                        cmd += f' -n "{genus.capitalize()} {species} {infraspecies} {collectionType.capitalize()}" {url}'
                    elif mode == "blast":  # for blast
                        if not url.endswith("faa.gz"):
                            continue
                        cmd = f"set -o pipefail -o errexit -o nounset; curl {url} | gzip -dc"  # retrieve genome and decompress
                        cmd += f'| makeblastdb -parse_seqids -out {self.out_dir}/{name} -hash_index -dbtype prot -title "{genus.capitalize()} {species} {infraspecies} {collectionType.capitalize()}"'
                # Quick Note: Change senteny and diversity cmd jbrowse lines later. They are like this for now just to see if it will even work.
                if collectionType == "genome_alignments":  # add pair-wise paf files
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
                elif subprocess.check_call(
                    cmd, shell=True, executable="/bin/bash"
                ):  # execute cmd and check exit value = 0
                    logger.error(f"Non zero exit value: {cmd}")

    def populate_jbrowse2(self, out_dir, cmds_only=False):
        """Populate jbrowse2 config object from collected objects"""
        if out_dir:  # set output directory
            self.out_dir = out_dir
        pathlib.Path(self.out_dir).mkdir(parents=True, exist_ok=True)
        self.process_collections(
            cmds_only, "jbrowse"
        )  # process collections for jbrowse-components

    def populate_blast(self, out_dir, cmds_only=False):
        """Populate a BLAST db for genome_main, mrna/mrna_primary and protein/protein_primary"""
        if out_dir:  # set output directory
            self.out_dir = out_dir
        pathlib.Path(self.out_dir).mkdir(parents=True, exist_ok=True)
        self.process_collections(
            cmds_only, "blast"
        )  # process collections for BLAST sequenceserver

    def populate_dscensor(self, out_dir):
        """Populate dscensor nodes for loading into a neo4j database"""
        if out_dir:  # set output directory
            self.out_dir = out_dir
        pathlib.Path(self.out_dir).mkdir(parents=True, exist_ok=True)
        self.process_collections(True, "dscensor")  # process collections for DSCensor
        for n in self.file_objects:  # write all processed objects to node files
            node_out = open(
                f'{self.out_dir}/{n["filename"]}.json', "w"
            )  # file to write node to
            node_out.write(json.dumps(n))
            node_out.close()

    def parse_collections(
        self, target="../_data/taxon_list.yml", species_collections=None
    ):
        """Retrieve and output collections for jekyll site"""
        logger = self.logger
        taxonList = yaml.load(
            open(target, "r").read(), Loader=yaml.FullLoader
        )  # load taxon list
        for taxon in taxonList:
            if not "genus" in taxon:  # genus required for all taxon
                logger.error(f"Genus not found for: {taxon}")
                sys.exit(1)
            genus = taxon["genus"]
            genusDescriptionUrl = f"{self.datastore_url}/{genus}/GENUS/about_this_collection/description_{genus}.yml"
            genusDescriptionResponse = requests.get(genusDescriptionUrl)
            speciesCollectionsFile = None  # yaml file to write for species collections
            genusResourcesFile = None  # yaml file to write for genus resources
            speciesResourcesFile = None  # yaml file to write for species resources
            if (
                genusDescriptionResponse.status_code == 200
            ):  # Genus Description yml SUCCESS
                speciesCollectionsFilename = None
                genusDescription = yaml.load(
                    genusDescriptionResponse.text, Loader=yaml.FullLoader
                )
                if species_collections:
                    collection_dir = (
                        f'{os.path.abspath(species_collections)}/{taxon["genus"]}'
                    )
                    pathlib.Path(collection_dir).mkdir(parents=True, exist_ok=True)
                    speciesCollectionsFilename = (
                        f"{collection_dir}/species_collections.yml"
                    )
                    genusResourcesFilename = f"{collection_dir}/genus_resources.yml"  # file in the datastore_url to read genus resources
                    speciesResourcesFilename = f"{collection_dir}/species_resources.yml"  # file in the datastore_url to read species resources
                if (
                    speciesCollectionsFilename
                ):  # write info for speciesCollections and open resources files
                    speciesCollectionsFile = open(speciesCollectionsFilename, "w")
                    print("---", file=speciesCollectionsFile)
                    print("species:", file=speciesCollectionsFile)
                    genusResourcesFile = open(genusResourcesFilename, "w")
                    speciesResourcesFile = open(speciesResourcesFilename, "w")
                    print("---", file=genusResourcesFile)
                    yaml.dump(genusDescription, genusResourcesFile)
                    print("---", file=speciesResourcesFile)
                    print("species:", file=speciesResourcesFile)
                speciesDescriptions = []
                for species in genusDescription[
                    "species"
                ]:  # iterate through all species in the genus
                    infraspecies_resources = {}
                    logger.info(
                        f"Searching {self.datastore_url} for: {taxon['genus']} {species}"
                    )
                    if speciesCollectionsFilename:
                        print(f"- name: {species}", file=speciesCollectionsFile)
                    speciesUrl = f"{self.datastore_url}/{genus}/{species}"
                    speciesDescriptionUrl = f"{speciesUrl}/about_this_collection/description_{genus}_{species}.yml"
                    logger.debug(speciesDescriptionUrl)  # get species description url
                    speciesDescriptionResponse = requests.get(speciesDescriptionUrl)
                    #                    if speciesDescriptionResponse.status_code == 200:
                    #                        speciesDescription = yaml.load(speciesDescriptionResponse.text, Loader=yaml.FullLoader)  # load the yaml from the datastore for species
                    #                        speciesDescription['resources'].append()
                    #                        speciesDescriptions.append(speciesDescription)
                    #                        print(speciesDescription['resources'])
                    for (
                        collectionType
                    ) in (
                        self.collection_types
                    ):  # iterate through collections found in the datastore with readme files
                        if collectionType not in self.files:  # add new type
                            self.files[collectionType] = {}
                        if speciesCollectionsFilename:
                            print(f"  {collectionType}:", file=speciesCollectionsFile)
                        collectionsUrl = f"{speciesUrl}/{collectionType}/"
                        collectionsResponse = requests.get(collectionsUrl)
                        if (
                            collectionsResponse.status_code == 200
                        ):  # Collections SUCCESS
                            self.collections = []
                            self.parse_attributes(
                                collectionsResponse.text
                            )  # Feed response from GET
                            for collectionDir in self.collections:
                                parts = collectionDir.split("/")
                                logger.debug(parts)
                                name = parts[4]
                                url = ""
                                parent = ""
                                parts = self.get_attributes(parts)
                                lookup = f"{parts[0]}.{'.'.join(name.split('.')[:-1])}"  # reference name in datastructure
                                if (
                                    collectionType == "genomes"
                                ):  # add parent genome_main files
                                    ref = ""
                                    stop = 0
                                    url = f"{self.datastore_url}{collectionDir}{parts[0]}.{parts[1]}.genome_main.fna.gz"  # genome_main in datastore_url
                                    fai = f"{url}.fai"  # get fai file for jbrowse session construction
                                    faiResponse = requests.get(
                                        fai
                                    )  # get fai file to build loc from
                                    if (
                                        faiResponse.status_code == 200
                                    ):  # fai exists and can be retrieved
                                        (ref, stop) = faiResponse.text.split("\n")[
                                            0
                                        ].split()[
                                            :2
                                        ]  # fai field 1\s+2. field 1 is sequence_id field 2 is length
                                        logger.debug(f"{ref},{stop}")
                                    else:  # fai file could not be accessed
                                        logger.error(f"No fai file for: {url}")
                                        sys.exit(1)
                                    linear_session = {  # LinearGenomeView object for JBrowse2
                                        "views": [
                                            {
                                                "assembly": lookup,
                                                "loc": f"{ref}:1-{stop}",  # JBrowse2 does not allow null loc
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
                                    strain_lookup = lookup.split(".")[
                                        1
                                    ]  # the strain for the lookup
                                    linear_url = f"{self.jbrowse_url}/?config=config.json&session=spec-{linear_session}"  # build the URL for the resource
                                    linear_data = {
                                        "name": f"JBrowse2 {lookup}",
                                        "URL": str(linear_url).replace(
                                            "'", "%22"
                                        ),  # url encode for yml file and Jekyll linking
                                        "description": "JBrowse2 Linear Genome View",
                                    }  # the object that will be written into the yml file
                                    if strain_lookup not in infraspecies_resources:
                                        infraspecies_resources[
                                            strain_lookup
                                        ] = (
                                            []
                                        )  # initialize infraspecies list within species
                                    infraspecies_resources[strain_lookup].append(
                                        linear_data
                                    )
                                    logger.debug(url)
                                    self.files[collectionType][lookup] = {
                                        "url": url,
                                        "name": lookup,
                                        "parent": parent,
                                        "genus": genus,
                                        "species": species,
                                        "infraspecies": parts[1],
                                        "taxid": 0,
                                    }  # add type and url

                                elif (
                                    collectionType == "annotations"
                                ):  # add gff3 annotation files. genome_main parent
                                    genome_lookup = ".".join(
                                        lookup.split(".")[:-1]
                                    )  # grab genome
                                    self.files["genomes"][genome_lookup]["url"]
                                    parent = genome_lookup
                                    url = f"{self.datastore_url}{collectionDir}{parts[0]}.{parts[1]}.gene_models_main.gff3.gz"
                                    self.files[collectionType][lookup] = {
                                        "url": url,
                                        "name": lookup,
                                        "parent": parent,
                                        "genus": genus,
                                        "species": species,
                                        "infraspecies": parts[1],
                                        "taxid": 0,
                                    }  # add type and url
                                    protprimaryUrl = f"{self.datastore_url}{collectionDir}{parts[0]}.{parts[1]}.protein_primary.faa.gz"
                                    protprimaryResponse = requests.get(protprimaryUrl)
                                    if protprimaryResponse.status_code == 200:
                                        protprimary_lookup = f"{lookup}.protein_primary"
                                        self.files[collectionType][
                                            protprimary_lookup
                                        ] = {
                                            "url": protprimaryUrl,
                                            "name": protprimary_lookup,
                                            "parent": parent,
                                            "genus": genus,
                                            "species": species,
                                            "infraspecies": parts[1],
                                            "taxid": 0,
                                        }
                                    else:
                                        logger.debug(
                                            f"protprimaryUrl(PrimaryProtien):Failed {protprimaryResponse}"
                                        )

                                    proteinUrl = f"{self.datastore_url}{collectionDir}{parts[0]}.{parts[1]}.protein.faa.gz"
                                    protein_response = requests.get(proteinUrl)
                                    if protein_response.status_code == 200:
                                        protein_lookup = f"{lookup}.protein"
                                        self.files[collectionType][protein_lookup] = {
                                            "url": proteinUrl,
                                            "name": protein_lookup,
                                            "parent": parent,
                                            "genus": genus,
                                            "species": species,
                                            "infraspecies": parts[1],
                                            "taxid": 0,
                                        }
                                    else:
                                        logger.debug(
                                            f"proteinUrl(Protein):Failed {protein_response}"
                                        )
                                elif collectionType == "synteny":  # DEPRICATED?
                                    checksumUrl = f"{self.datastore_url}{collectionDir}CHECKSUM.{parts[1]}.md5"
                                    checkResponse = requests.get(checksumUrl)
                                    if checkResponse.status_code == 200:
                                        continue
                                    else:  # CheckSum FAILURE
                                        logger.debug(
                                            f"GET Failed for checksum {checkResponse.status_code} {checksumUrl}"
                                        )
                                elif (
                                    collectionType == "genome_alignments"
                                ):  # Synteny after the new changes. Parent is a tuple with both genome_main files
                                    dotplot_view = {  # session object for jbrowse2 dotplot view populate below with parent1 and parent2
                                        " views ": [
                                            {
                                                " type ": " DotplotView ",
                                                " views ": [
                                                    {" assembly ": " volvox "},
                                                    {" assembly ": " volvox "},
                                                ],
                                                " tracks ": [" volvox_fake_synteny "],
                                            }
                                        ]
                                    }
                                    checksumUrl = f"{self.datastore_url}{collectionDir}CHECKSUM.{parts[1]}.md5"
                                    checkResponse = requests.get(checksumUrl)
                                    logger.debug(checkResponse)
                                    if (
                                        checkResponse.status_code == 200
                                    ):  # file exists at datastore_url
                                        for line in checkResponse.text.split("\n"):
                                            logger.debug(line)
                                            fields = line.split()
                                            if fields:  # process if fields exists
                                                if fields[1].endswith(
                                                    "paf.gz"
                                                ):  # get paf file
                                                    paf_lookup = fields[1].replace(
                                                        "./", ""
                                                    )  # get paf file to load will start with ./
                                                    logger.debug(paf_lookup)
                                                    pafUrl = f"{self.datastore_url}{collectionDir}{paf_lookup}"  # where the paf file is in the datastore
                                                    paf_parts = paf_lookup.split(
                                                        "."
                                                    )  # split the paf file name into parts delimited by '.'
                                                    parent1 = ".".join(
                                                        paf_parts[:3]
                                                    )  # parent 1 in pair-wise alignment
                                                    parent2 = ".".join(
                                                        paf_parts[5:8]
                                                    )  # parent 2 in pair-wise alignment
                                                    self.files[collectionType][
                                                        paf_lookup
                                                    ] = {
                                                        "url": pafUrl,
                                                        "name": paf_lookup,
                                                        "parent": [parent1, parent2],
                                                        "genus": genus,
                                                        "species": species,
                                                        "infraspecies": parts[1],
                                                        "taxid": 0,
                                                    }
                                                    logger.debug(
                                                        self.files[collectionType][
                                                            paf_lookup
                                                        ]
                                                    )
                                readmeUrl = f"{self.datastore_url}/{collectionDir}README.{name}.yml"  # species collection file
                                readmeResponse = requests.get(readmeUrl)
                                if readmeResponse.status_code == 200:
                                    readme = yaml.load(
                                        readmeResponse.text, Loader=yaml.FullLoader
                                    )
                                    synopsis = readme["synopsis"]
                                    taxid = readme["taxid"]
                                    if lookup in self.files[collectionType]:
                                        self.files[collectionType][lookup][
                                            "taxid"
                                        ] = taxid  # set taxid if available for this file object
                                    else:
                                        logger.debug(
                                            f"{lookup} not in {self.files[collectionType]}"
                                        )
                                    if speciesCollectionsFilename:
                                        print(
                                            f"    - collection: {name}",
                                            file=speciesCollectionsFile,
                                        )
                                        print(
                                            f'      synopsis: "{synopsis}"',
                                            file=speciesCollectionsFile,
                                        )
                                else:  # README FAILURE
                                    logger.debug(
                                        f"GET Failed for README {readmeResponse.status_code} {readmeUrl}"
                                    )  # change to log
                        #                                    sys.exit(1)
                        else:  # Collections FAILUTRE
                            logger.debug(
                                f"GET Failed for collections {collectionsResponse.status_code} {collectionsUrl}"
                            )  # change to log
                    #                            sys.exit(1)
                    #                    logger.info(f'{}')
                    if (
                        speciesDescriptionResponse.status_code == 200
                    ):  # add the remainder of the species resources and info and add jbrowse
                        speciesDescription = yaml.load(
                            speciesDescriptionResponse.text, Loader=yaml.FullLoader
                        )  # load the yaml from the datastore for species
                        count = 0
                        for strain in speciesDescription[
                            "strains"
                        ]:  # iterate through all infraspecies in this species
                            if (
                                strain["identifier"] in infraspecies_resources
                            ):  # add to this strain
                                if speciesDescription["strains"][count].get(
                                    "resources", None
                                ):  # this strain has resources
                                    for resource in infraspecies_resources[
                                        strain["identifier"]
                                    ]:  # append all the resources to the existing
                                        speciesDescription["strains"][count][
                                            "resources"
                                        ].append(resource)
                                else:
                                    speciesDescription["strains"][count][
                                        "resources"
                                    ] = infraspecies_resources[
                                        strain["identifier"]
                                    ]  # set resources
                            count += 1  # keep track of how many "strains" we have seen
                        speciesDescriptions.append(speciesDescription)
                yaml.dump(
                    speciesDescriptions, speciesResourcesFile
                )  # dump species_resources.yml locally with jbrowse links
            else:  # Genus Description file could not be found.
                logger.warning(
                    f"GET Failed for genus {genusDescriptionResponse.status_code} {genusDescriptionUrl}"
                )
            #                sys.exit(1)
            if speciesCollectionsFile:
                speciesCollectionsFile.close()
            if genusResourcesFile:
                genusResourcesFile.close()
            if speciesResourcesFile:
                speciesResourcesFile.close()


if __name__ == "__main__":
    parser = ProcessCollections()
    parser.parse_collections()
