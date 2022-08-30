# lis-autocontent
Scrapes the LIS datastore (https://data.legumeinfo.org) and populates various configs and databases for deployment

## Reqiurements

1. JBrowse2 (https://jbrowse.org/jb2/docs/combined/)
2. NCBI-BLAST+ (https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/)
3. Python3

## Install

1. Clone repository. `git clone https://github.com/legumeinfo/LIS-autocontent.git`
2. Create a virtual environment for python3 `/path/to/python3/bin/virtualenv autocontent_env`
3. Source virtual environment `. ./autocontent_env/bin/activate`
4. Install requirements. `pip install -r ./LIS-autocontent/requirements.txt`

## Run

The pipeline will run with no options if run from the _scripts directory. `python3 ./lis-autocontent/populate-jekyll.py collections`

```
(lis-autocontent_env) [legumista@ctc-apollo LIS-autocontent]$ ./lis-autocontent.py --help
Usage: lis-autocontent.py [OPTIONS] COMMAND [ARGS]...

  CLI entry for populate-jekyll

Options:
  --help  Show this message and exit.

Commands:
  populate-blast     CLI entry for populate-blast
  populate-jbrowse2  CLI entry for deploy-jbrowse2
  populate-jekyll    CLI entry for populate-jekyll
```

## populate-blast

```
(lis-autocontent_env) [legumista@ctc-apollo LIS-autocontent]$ ./lis-autocontent.py populate-blast --help
Usage: lis-autocontent.py populate-blast [OPTIONS]

  CLI entry for populate-blast

Options:
  --taxa_list TEXT  Taxa.yml file. (Default: ../_data/taxon_list.yml)
  --blast_out TEXT  Output directory for Jbrowse2. (Default:
                    /var/www/html/db/Genomic_Sequence_Collection)
  --cmds_only       Output commands only. Do not run makeblastdb just output
                    the commands that would be run.
  --help            Show this message and exit.
```

## populate-jbrowse2

```
(lis-autocontent_env) [legumista@ctc-apollo LIS-autocontent]$ ./lis-autocontent.py populate-jbrowse2 --help
Usage: lis-autocontent.py populate-jbrowse2 [OPTIONS]

  CLI entry for deploy-jbrowse2

Options:
  --taxa_list TEXT    Taxa.yml file. (Default: ../_data/taxon_list.yml)
  --jbrowse_out TEXT  Output directory for Jbrowse2. (Default:
                      /var/www/html/jbrowse2_autodeploy)
  --cmds_only         Output commands only. Do not run Jbrowse2 just output
                      the commands that would be run.
  --help              Show this message and exit.
```

## populate-jekyll

```
(lis-autocontent_env) [legumista@ctc-apollo LIS-autocontent]$ ./lis-autocontent.py populate-jekyll --help
Usage: lis-autocontent.py populate-jekyll [OPTIONS]

  CLI entry for populate-jekyll

Options:
  --taxa_list TEXT        Taxa.yml file. (Default: ../_data/taxon_list.yml)
  --collections_out TEXT  Output for collections.
  --help                  Show this message and exit.
```

DOCKER COMING
