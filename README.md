# lis-autocontent
Scrapes the LIS datastore (https://data.legumeinfo.org) and populates various configs and databases for deployment

## Reqiurements

1. JBrowse2 (https://jbrowse.org/jb2/docs/combined/)
2. NCBI-BLAST+ (https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/)
3. Python3.7+

## Quick Install With pip (register as python package soon.)

`pip install 'lis_autocontent @ git+https://github.com/legumeinfo/LIS-autocontent.git'`

## Developer Install

1. Clone repository. `git clone https://github.com/legumeinfo/LIS-autocontent.git`
2. Create a virtual environment for python3 `/path/to/python3/bin/virtualenv autocontent_env`  (optional)
3. Source virtual environment `. ./autocontent_env/bin/activate`  (optional)
4. CD into repo and install requirements. `cd ./LIS-autocontent;pip install -r ./requirements.txt`  (optional)
5. Install Black and pre-commit for git hooks. `pip install black pre-commit`
6. Initialize pre-commit. `pre-commit install`
7. Build package locally. `python setup.py build` (optional)
8. Install package into env and add to PATH. `python setup.py install` (optional)

## Run

```
(lisautocontent_env) [ctc@haldane LIS-autocontent]$ lis-autocontent.py
Usage: lis-autocontent.py [OPTIONS] COMMAND [ARGS]...

  CLI entry for LIS-autocontent

Options:
  --help  Show this message and exit.

Commands:
  populate-blast     CLI entry for populate-blast
  populate-dscensor  CLI entry for populate-dscensor
  populate-jbrowse2  CLI entry for populate-jbrowse2
  populate-jekyll    CLI entry for populate-jekyll
```

## populate-blast

```
(lisautocontent_env) [ctc@haldane LIS-autocontent]$ lis-autocontent.py populate-blast --help
Usage: lis-autocontent.py populate-blast [OPTIONS]

  CLI entry for populate-blast

Options:
  --taxa_list TEXT  Taxa.yml file. (Default: ../_data/taxon_list.yml)
  --blast_out TEXT  Output directory for BLAST DBs. (Default: ./autocontent)
  --cmds_only       Output commands only. Do not run makeblastdb just output
                    the commands that would be run.
  --log_file TEXT   Log file to output messages. (default: ./populate-
                    blast.log)
  --log_level TEXT  Log Level to output messages. (default: INFO)
  --help            Show this message and exit.
```

## populate-jbrowse2

```
(lisautocontent_env) [ctc@haldane LIS-autocontent]$ lis-autocontent.py populate-jbrowse2 --help
Usage: lis-autocontent.py populate-jbrowse2 [OPTIONS]

  CLI entry for populate-jbrowse2

Options:
  --jbrowse_url TEXT  URL hosting JBrowse2
  --taxa_list TEXT    Taxa.yml file. (Default: ../_data/taxon_list.yml)
  --jbrowse_out TEXT  Output directory for Jbrowse2. (Default: ./autocontent)
  --cmds_only         Output commands only. Do not run Jbrowse2 just output
                      the commands that would be run.
  --log_file TEXT     Log file to output messages. (default: ./populate-
                      jbrowse2.log)
  --log_level TEXT    Log Level to output messages. (default: INFO)
  --help              Show this message and exit.
```

## populate-jekyll

```
(lisautocontent_env) [ctc@haldane LIS-autocontent]$ lis-autocontent.py populate-jekyll --help
Usage: lis-autocontent.py populate-jekyll [OPTIONS]

  CLI entry for populate-jekyll

Options:
  --taxa_list TEXT        Taxa.yml file. (Default: ../_data/taxon_list.yml)
  --collections_out TEXT  Output for collections.
  --help                  Show this message and exit.
```

## populate-dscensor

```
(lisautocontent_env) [ctc@haldane LIS-autocontent]$ lis-autocontent.py populate-dscensor --help
Usage: lis-autocontent.py populate-dscensor [OPTIONS]

  CLI entry for populate-dscensor

Options:
  --taxa_list TEXT  Taxa.yml file. (Default: ../_data/taxon_list.yml)
  --nodes_out TEXT  Output for dscensor nodes.
  --log_file TEXT   Log file to output messages. (default: ./populate-
                    dscensor.log)
  --log_level TEXT  Log Level to output messages. (default: INFO)
  --help            Show this message and exit.
```
