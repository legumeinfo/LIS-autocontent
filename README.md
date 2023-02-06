# lis-autocontent
Scrapes the LIS datastore (https://data.legumeinfo.org) and populates various configs and databases for deployment

## Reqiurements

1. JBrowse2 (https://jbrowse.org/jb2/docs/combined/)
2. NCBI-BLAST+ (https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/)
3. Python3.7+

## Quick Install With pip (register as python package soon.)

1. Create a virtual environment for python3. `python3 -m venv lis_autocontent_env` (optional)
2. Source environment. `. ./lis_autocontent_env/bin/activate` (optional)
3. pip install from github. `pip install 'lis_autocontent @ git+https://github.com/legumeinfo/LIS-autocontent.git'`

## Developer Install

1. Clone repository. `git clone https://github.com/legumeinfo/LIS-autocontent.git`
2. Create a virtual environment for python3 `python3 -m venv lis_autocontent_env`  (optional)
3. Source virtual environment `. ./lis_autocontent_env/bin/activate`  (optional)
4. CD into repo and install requirements. `(lis_autocontent_env) [ctc@haldane lisautocontent]$ cd LIS-autocontent/;pip install -r requirements.txt`  (optional)
5. Install Black and pre-commit for git hooks. `pip install black pre-commit`
6. Initialize pre-commit. `pre-commit install`
7. Build package locally. `python setup.py build` (optional)
8. Install package into env and add to PATH. `python setup.py install` (optional)

## Run

```
(lisautocontent_env) [ctc@haldane LIS-autocontent]$ lis-autocontent --help
Usage: lis-autocontent [OPTIONS] COMMAND [ARGS]...

  Click Group Object to Attach Commands.

Options:
  --help  Show this message and exit.

Commands:
  populate-blast     CLI entry for populate-blast
  populate-dscensor  CLI entry for populate-dscensor
  populate-jbrowse2  CLI entry for populate-jbrowse2
  populate-jekyll    CLI entry for populate-jekyll
```
