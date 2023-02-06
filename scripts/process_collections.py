"""Populate collections and resources for JBrowse2 and BLAST from a remote Datastore."""
#!/usr/bin/env python3

import os
import sys
import json
import pathlib
import subprocess
from html.parser import HTMLParser
import requests
import yaml


class ProcessCollections:
    """Parses Collections from the datastore_url provided. Default: https://data.legumeinfo.org"""

    def __init__(
        self,
        logger=None,
        datastore_url="https://data.legumeinfo.org",
        jbrowse_url="",
        out_dir="./autocontent",
    ):
        self.logger = logger
        if self.logger:
            self.logger.info("logger initialized")
        else:  # logger object required
            print("logger required to initialize process_collections")
            sys.exit(1)
        self.collections = []  # stores all collections from self.parse_attributes
        self.datastore_url = datastore_url  # URL to search for collections
        self.jbrowse_url = jbrowse_url  # URL to append jbrowse2 sessions
        self.out_dir = out_dir  # output directory for objects.  This is set by the runtimes if provided
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
        self.current_taxon = {}
        self.species_descriptions = (
            []
        )  # list of all species descriptions to be written to species collections
        self.infraspecies_resources = {}  # used to track all "strains"
        self.species_collections_handle = (
            None  # yaml file to write for species collections
        )
        self.genus_resources_handle = None  # yaml file to write for genus resources
        self.species_resources_handle = None  # yaml file to write for species resources

    def get_remote(self, url):
        """Uses requests.get to grab remote URL returns response object otherwise returns False"""
        logger = self.logger
        response = requests.get(url, timeout=5)  # get remote object
        if response.status_code == 200:  # SUCCESS
            return response
        logger.debug(f"GET failed with status {response.status_code} for: {url}")
        return False

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
        gensp = f"{parts[1][:3].lower()}{parts[2][:2].lower()}"  # make gensp
        strain = parts[-2]  # get strain and key information
        return (gensp, strain)

    def process_collections(self, cmds_only, mode):
        """General method to create a jbrowse-components config or populate a blast db using mode"""
        logger = self.logger
        pathlib.Path(self.out_dir).mkdir(parents=True, exist_ok=True)
        for collection_type in self.collection_types:  # for all collections
            for dsfile in self.files[
                collection_type
            ]:  # for all files in all collections
                cmd = ""
                url = self.files[collection_type][dsfile]["url"]
                if not url:  # do not take objects with no defined link
                    continue
                name = self.files[collection_type][dsfile]["name"]
                genus = self.files[collection_type][dsfile]["genus"]
                taxid = self.files[collection_type][dsfile].get("taxid", 0)
                parent = self.files[collection_type][dsfile]["parent"]
                species = self.files[collection_type][dsfile]["species"]
                infraspecies = self.files[collection_type][dsfile]["infraspecies"]
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
                ### possibly break out next section into methods: blast, jbrowse, then types
                if collection_type == "genomes":  # add genome
                    if mode == "jbrowse":  # for jbrowse
                        cmd = f"jbrowse add-assembly -a {name} --out {self.out_dir}/ -t bgzipFasta --force"
                        cmd += f' -n "{genus.capitalize()} {species} {infraspecies} {collection_type.capitalize()}" {url}'
                    elif mode == "blast":  # for blast
                        cmd = f"set -o pipefail -o errexit -o nounset; curl {url} | gzip -dc"  # retrieve genome and decompress
                        cmd += f'| makeblastdb -parse_seqids -out {self.out_dir}/{name} -hash_index -dbtype nucl -title "{genus.capitalize()} {species} {infraspecies} {collection_type.capitalize()}"'
                        if taxid:
                            cmd += f" -taxid {taxid}"
                if collection_type == "annotations":  # add annotation
                    if mode == "jbrowse":  # for jbrowse
                        if url.endswith(
                            "faa.gz"
                        ):  # only process non faa annotations in jbrowse
                            continue
                        cmd = f"jbrowse add-track -a {parent} --out {self.out_dir}/ --force"
                        cmd += f' -n "{genus.capitalize()} {species} {infraspecies} {collection_type.capitalize()}" {url}'
                    elif mode == "blast":  # for blast
                        if not url.endswith(
                            "faa.gz"
                        ):  # only process faa annotations in blast
                            continue
                        cmd = f"set -o pipefail -o errexit -o nounset; curl {url} | gzip -dc"  # retrieve genome and decompress
                        cmd += f'| makeblastdb -parse_seqids -out {self.out_dir}/{name} -hash_index -dbtype prot -title "{genus.capitalize()} {species} {infraspecies} {collection_type.capitalize()}"'
                        if taxid:
                            cmd += f" -taxid {taxid}"
                if collection_type == "genome_alignments":  # add pair-wise paf files
                    if mode == "jbrowse":  # for jbrowse
                        cmd = f"jbrowse add-track --assemblyNames {','.join(parent)} --out {self.out_dir}/ {url} --force"
                    elif mode == "blast":  # for blast
                        continue  # Not blastable at the moment
                # MORE CANONICAL TYPES HERE
                if not cmd:  # continue for null or incomplete objects
                    continue
                if cmds_only:  # output only cmds
                    print(cmd)
                elif subprocess.check_call(
                    cmd, shell=True, executable="/bin/bash"
                ):  # execute cmd and check exit value = 0
                    logger.error(f"Non-zero exit value: {cmd}")

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
        for node in self.file_objects:  # write all processed objects to node files
            node_out = open(
                f'{self.out_dir}/{node["filename"]}.json', "w", encoding="utf-8"
            )  # file to write node to
            node_out.write(json.dumps(node))
            node_out.close()

    def add_collections(self, collection_type, genus, species):
        """Adds collection to self.files[collection_type] for later use"""
        logger = self.logger
        species_url = f"{self.datastore_url}/{genus}/{species}"
        if collection_type not in self.files:  # add new type
            self.files[collection_type] = {}
        print(
            f"  {collection_type}:", file=self.species_collections_handle
        )  # print collection type in species collections
        collections_url = f"{species_url}/{collection_type}/"
        collections_response = self.get_remote(collections_url)
        if not collections_response:  # get remote failed
            logger.debug(collections_response)
            return False
        self.collections = []  # Set to empty list for use in self.parse_attributes
        self.parse_attributes(
            collections_response.text
        )  # Feed response from GET to populate collections
        for collection_dir in self.collections:
            parts = collection_dir.split("/")
            logger.debug(parts)
            name = parts[4]
            url = ""
            parent = ""
            parts = self.get_attributes(parts)
            lookup = f"{parts[0]}.{'.'.join(name.split('.')[:-1])}"  # reference name in datastructure
            if collection_type == "genomes":  # add parent genome_main files
                ref = ""
                stop = 0
                url = f"{self.datastore_url}{collection_dir}{parts[0]}.{parts[1]}.genome_main.fna.gz"  # genome_main in datastore_url
                fai_url = f"{url}.fai"  # get fai file for jbrowse session construction
                fai_response = self.get_remote(
                    fai_url
                )  # get fai file to build loc from
                if fai_response:  # fai SUCCESS 200
                    (ref, stop) = fai_response.text.split("\n")[0].split()[
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
                strain_lookup = lookup.split(".")[1]  # the strain for the lookup
                linear_url = f"{self.jbrowse_url}/?config=config.json&session=spec-{linear_session}"  # build the URL for the resource
                linear_data = {
                    "name": f"JBrowse2 {lookup}",
                    "URL": str(linear_url).replace(
                        "'", "%22"
                    ),  # url encode for yml file and Jekyll linking
                    "description": "JBrowse2 Linear Genome View",
                }  # the object that will be written into the yml file
                if strain_lookup not in self.infraspecies_resources:
                    self.infraspecies_resources[
                        strain_lookup
                    ] = []  # initialize infraspecies list within species
                if self.jbrowse_url:  # dont add data if no jbrowse url set
                    self.infraspecies_resources[strain_lookup].append(linear_data)
                logger.debug(url)
                self.files[collection_type][lookup] = {
                    "url": url,
                    "name": lookup,
                    "parent": parent,
                    "genus": genus,
                    "species": species,
                    "infraspecies": parts[1],
                    "taxid": 0,
                }  # add type and url
            ###
            elif (
                collection_type == "annotations"
            ):  # add gff3 annotation files and protein/protein_primary. genome_main parent
                genome_lookup = ".".join(lookup.split(".")[:-1])  # genome parent prefix
                #                self.files["genomes"][genome_lookup]["url"]
                parent = genome_lookup
                url = f"{self.datastore_url}{collection_dir}{parts[0]}.{parts[1]}.gene_models_main.gff3.gz"
                self.files[collection_type][lookup] = {  # gene_models_main
                    "url": url,
                    "name": lookup,
                    "parent": parent,
                    "genus": genus,
                    "species": species,
                    "infraspecies": parts[1],
                    "taxid": 0,
                }  # add type and url
                protprimary_url = f"{self.datastore_url}{collection_dir}{parts[0]}.{parts[1]}.protein_primary.faa.gz"
                protprimary_response = self.get_remote(protprimary_url)
                if protprimary_response:
                    protprimary_lookup = f"{lookup}.protein_primary"
                    self.files[collection_type][
                        protprimary_lookup
                    ] = {  # protein_primary
                        "url": protprimary_url,
                        "name": protprimary_lookup,
                        "parent": parent,
                        "genus": genus,
                        "species": species,
                        "infraspecies": parts[1],
                        "taxid": 0,
                    }
                else:
                    logger.debug(
                        f"protein_primary failed:{protprimary_url}, {protprimary_response}"
                    )

                protein_url = f"{self.datastore_url}{collection_dir}{parts[0]}.{parts[1]}.protein.faa.gz"
                protein_response = self.get_remote(protein_url)
                if protein_response:
                    protein_lookup = f"{lookup}.protein"
                    self.files[collection_type][protein_lookup] = {  # all proteins
                        "url": protein_url,
                        "name": protein_lookup,
                        "parent": parent,
                        "genus": genus,
                        "species": species,
                        "infraspecies": parts[1],
                        "taxid": 0,
                    }
                else:
                    logger.debug(f"protein failed:{protein_url}, {protein_response}")
            ###
            #            elif collection_type == "synteny":  # DEPRICATED?
            #                checksum_url = f"{self.datastore_url}{collection_dir}CHECKSUM.{parts[1]}.md5"
            #                checksum_response = requests.get(checksum_url)
            #                if checksum_response.status_code == 200:
            #                    continue
            #                else:  # CheckSum FAILURE
            #                    logger.debug(
            #                        f"GET Failed for checksum {checksum_response.status_code} {checksum_url}"
            #                    )
            ###
            elif (
                collection_type == "genome_alignments"
            ):  # Synteny after the new changes. Parent is a tuple with both genome_main files
                #                dotplot_view = {  # session object for jbrowse2 dotplot view populate below with parent1 and parent2
                #                    " views ": [
                #                        {
                #                            " type ": " DotplotView ",
                #                            " views ": [
                #                                {" assembly ": " volvox "},
                #                                {" assembly ": " volvox "},
                #                            ],
                #                            " tracks ": [" volvox_fake_synteny "],
                #                        }
                #                    ]
                #                }
                checksum_url = (
                    f"{self.datastore_url}{collection_dir}CHECKSUM.{parts[1]}.md5"
                )
                checksum_response = self.get_remote(checksum_url)
                if checksum_response:  # checksum SUCCESS 200
                    for line in checksum_response.text.split("\n"):
                        logger.debug(line)
                        fields = line.split()
                        if fields:  # process if fields exists
                            if fields[1].endswith("paf.gz"):  # get paf file
                                paf_lookup = fields[1].replace(
                                    "./", ""
                                )  # get paf file to load will start with ./
                                logger.debug(paf_lookup)
                                paf_url = f"{self.datastore_url}{collection_dir}{paf_lookup}"  # where the paf file is in the datastore
                                paf_parts = paf_lookup.split(
                                    "."
                                )  # split the paf file name into parts delimited by '.'
                                parent1 = ".".join(
                                    paf_parts[:3]
                                )  # parent 1 in pair-wise alignment
                                parent2 = ".".join(
                                    paf_parts[5:8]
                                )  # parent 2 in pair-wise alignment
                                self.files[collection_type][paf_lookup] = {
                                    "url": paf_url,
                                    "name": paf_lookup,
                                    "parent": [parent1, parent2],
                                    "genus": genus,
                                    "species": species,
                                    "infraspecies": parts[1],
                                    "taxid": 0,
                                }
                                logger.debug(self.files[collection_type][paf_lookup])
            readme_url = f"{self.datastore_url}/{collection_dir}README.{name}.yml"  # species collection readme
            readme_response = self.get_remote(readme_url)
            if readme_response:  # readme get success
                readme = yaml.load(readme_response.text, Loader=yaml.FullLoader)
                synopsis = readme["synopsis"]
                taxid = readme["taxid"]
                if lookup in self.files[collection_type]:
                    self.files[collection_type][lookup][
                        "taxid"
                    ] = taxid  # set taxid if available for this file object
                else:
                    logger.debug(f"{lookup} not in {self.files[collection_type]}")
                print(
                    f"    - collection: {name}",
                    file=self.species_collections_handle,
                )
                print(
                    f'      synopsis: "{synopsis}"',
                    file=self.species_collections_handle,
                )
            else:  # get failed for
                logger.debug(f"GET Failed for README {readme_url}")
        return True

    def process_species(self, genus, species):
        """Process species and genus from genus_description object"""
        logger = self.logger
        logger.info(f"Searching {self.datastore_url} for: {genus} {species}")
        species_url = f"{self.datastore_url}/{genus}/{species}"
        self.infraspecies_resources = {}
        print(f"- name: {species}", file=self.species_collections_handle)

        for (
            collection_type
        ) in (
            self.collection_types
        ):  # iterate through collections found in the datastore
            self.add_collections(collection_type, genus, species)

        species_description_url = f"{species_url}/about_this_collection/description_{genus}_{species}.yml"  # parse for strain resources
        logger.debug(species_description_url)  # get species description url
        species_description_response = self.get_remote(species_description_url)
        if (
            species_description_response
        ):  # Read species description yml and add jbrowse resources to "strains"
            species_description = yaml.load(
                species_description_response.text, Loader=yaml.FullLoader
            )  # load the yaml from the datastore for species
            count = 0
            for strain in species_description[
                "strains"
            ]:  # iterate through all strains in this species description
                if (
                    strain["identifier"] in self.infraspecies_resources
                ):  # add to this strain
                    if species_description["strains"][count].get(
                        "resources", None
                    ):  # this strain has resources
                        for resource in self.infraspecies_resources[
                            strain["identifier"]
                        ]:  # append all the resources to the existing
                            species_description["strains"][count]["resources"].append(
                                resource
                            )
                    else:
                        species_description["strains"][count][
                            "resources"
                        ] = self.infraspecies_resources[
                            strain["identifier"]
                        ]  # set resources
                count += 1  # keep track of how many "strains" we have seen
            self.species_descriptions.append(species_description)

    def process_taxon(self, taxon):
        """Retrieve and output collections for jekyll site"""
        logger = self.logger
        if not "genus" in taxon:  # genus required for all taxon
            logger.error(f"Genus not found for: {taxon}")
            sys.exit(1)
        genus = taxon["genus"]
        genus_description_url = f"{self.datastore_url}/{genus}/GENUS/about_this_collection/description_{genus}.yml"  # genus desciprion to be read
        genus_description_response = self.get_remote(genus_description_url)
        self.genus_resources_handle = None  # yaml file to write for genus resources
        self.species_resources_handle = None  # yaml file to write for species resources
        self.species_collections_handle = (
            None  # yaml file to write for species collections
        )
        if genus_description_response:  # Genus Description yml 200 SUCCESS
            species_collections_filename = None
            self.species_descriptions = []  # null for current taxon genus
            genus_description = yaml.load(
                genus_description_response.text, Loader=yaml.FullLoader
            )  # load yml into python object
            collection_dir = f"{os.path.abspath(self.out_dir)}/{genus}"
            pathlib.Path(collection_dir).mkdir(
                parents=True, exist_ok=True
            )  # make output dirs if they dont exist
            genus_resources_filename = f"{collection_dir}/genus_resources.yml"  # local file to write genus resources
            species_resources_filename = f"{collection_dir}/species_resources.yml"  # local file to write species resources
            species_collections_filename = f"{collection_dir}/species_collections.yml"  # local file to write collections
            self.species_collections_handle = open(
                species_collections_filename, "w", encoding="utf-8"
            )
            self.genus_resources_handle = open(
                genus_resources_filename, "w", encoding="utf-8"
            )
            self.species_resources_handle = open(
                species_resources_filename, "w", encoding="utf-8"
            )
            collection_string = "---\nspecies:"
            print("---", file=self.genus_resources_handle)  # write genus resources
            yaml.dump(
                genus_description, self.genus_resources_handle
            )  # dump full description of genus
            print(
                collection_string, file=self.species_collections_handle
            )  # write species collection
            print(
                collection_string, file=self.species_resources_handle
            )  # write species resources

            for species in genus_description[
                "species"
            ]:  # iterate through all species in the genus
                self.process_species(
                    genus, species
                )  # process species and genus to populate self.species_descriptions

            yaml.dump(
                self.species_descriptions, self.species_resources_handle
            )  # dump species_resources.yml locally with all self.species_descriptions from genus
        if self.genus_resources_handle:  # close genus resources
            self.genus_resources_handle.close()
        if self.species_resources_handle:  # close species resources
            self.species_resources_handle.close()
        if self.species_collections_handle:  # close species collections
            self.species_collections_handle.close()

    def parse_collections(
        self, target="../_data/taxon_list.yml"
    ):  # refactored from SammyJava
        """Retrieve and output collections for jekyll site"""
        taxon_list = yaml.load(
            open(target, "r", encoding="utf-8").read(), Loader=yaml.FullLoader
        )  # load taxon list
        for taxon in taxon_list:
            self.process_taxon(taxon)  # process taxon object


if __name__ == "__main__":
    parser = ProcessCollections()
    parser.parse_collections()
