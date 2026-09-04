"""Populate collections and resources for JBrowse2 and BLAST from a remote Datastore."""

import json
import os
import pathlib
import subprocess
import sys
from html.parser import HTMLParser

import requests
import yaml
from dataclasses import dataclass, field


class ProcessCollections:
    """Parses Collections from the datastore_url provided.

    Default datastore: https://data.legumeinfo.org
    """

    DEFAULT_DATASTORE_URL = "https://data.legumeinfo.org"
    DEFAULT_OUT_DIR = "./autocontent"
    DEFAULT_GITHUB_CLONE = "./datastore-metadata"

    COLLECTION_TYPES = (
        "genomes",
        "annotations",
        "diversity",
        "expression",
        "genetic",
        "markers",
        "synteny",
        "genome_alignments",
    )

    GENUS_DESCRIPTION = "{genus}/GENUS/about_this_collection/description_{genus}.yml"
    SPECIES_DESCRIPTION = (
        "{genus}/{species}/about_this_collection/description_{genus}_{species}.yml"
    )

    GENUS_OUTPUTS = {
        "genus_resources_handle": "genus_resources.yml",
        "species_resources_handle": "species_resources.yml",
        "species_collections_handle": "species_collections.yml",
    }

    def __init__(
        self,
        logger=None,
        datastore_url=DEFAULT_DATASTORE_URL,
        jbrowse_url="",
        out_dir=DEFAULT_OUT_DIR,
    ):
        if not logger:
            print("logger required to initialize process_collections")
            sys.exit(1)
        self.logger = logger
        self.logger.info("logger initialized")

        self.datastore_url = datastore_url
        self.jbrowse_url = jbrowse_url
        self.out_dir = out_dir
        self.from_github = None
        self.collection_types = list(self.COLLECTION_TYPES)
        self.index = None

        self.collections = []
        self.files = {}
        self.file_objects = []
        self.current_taxon = {}
        self.species_descriptions = []
        self.infraspecies_resources = {}

        self.genus_resources_handle = None
        self.species_resources_handle = None
        self.species_collections_handle = None

    def discover_genera(self):
        """Return every genus in the datastore clone, sorted.

        A directory counts as a genus only when it holds a GENUS description
        file, which excludes non-taxonomic tops such as LEGUMES and .github.
        """
        root = pathlib.Path(self.from_github)
        candidates = sorted(
            entry.name
            for entry in root.iterdir()
            if entry.is_dir() and not entry.name.startswith(".")
        )
        genera = [
            genus
            for genus in candidates
            if (root / self.GENUS_DESCRIPTION.format(genus=genus)).is_file()
        ]
        skipped = sorted(set(candidates) - set(genera))
        if skipped:
            self.logger.debug(f"Not genus directories, skipped: {skipped}")
        self.logger.info(f"Discovered {len(genera)} genera: {genera}")
        return genera

    def load_taxa(self, target=None):
        """Return the taxa to process, from a taxon list file or by discovery."""
        if target and os.path.isdir(target):
            self.logger.warning(
                f"Taxon list {target} is a directory, discovering genera instead"
            )
            target = None
        if target:
            self.logger.info(f"Reading taxon list: {target}")
            with open(target, "r", encoding="utf-8") as handle:
                return yaml.load(handle.read(), Loader=yaml.FullLoader)
        self.logger.info("No taxon list given, discovering all genera")
        return [{"genus": genus} for genus in self.discover_genera()]

    def build_index(self):
        """Index every file in the datastore clone from its CHECKSUM manifests."""
        if not self.from_github:
            self.logger.warning("No datastore clone set, skipping index")
            return None
        self.index = DatastoreIndex(self.from_github, self.logger).build()
        return self.index

    def parse_collections(self, from_github=DEFAULT_GITHUB_CLONE, target=None):
        """Retrieve and output collections for jekyll site.

        from_github is the datastore-metadata clone to read. With no target,
        every genus found there is processed; pass a taxon list yml to restrict
        the run to a subset.
        """
        if from_github:
            self.from_github = os.path.abspath(from_github)
        self.logger.debug(f"THIS IS GITHUB: {self.from_github}")
        self.build_index()
        for taxon in self.load_taxa(target):
            self.process_taxon(taxon)


if __name__ == "__main__":
    parser = ProcessCollections()
    parser.parse_collections()
