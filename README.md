# lis-autocontent
Populates various configs and databases for deployment from the datastore-meta data github.

## Reqiurements

1. JBrowse2 (https://jbrowse.org/jb2/docs/combined/)
2. NCBI-BLAST+ (https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/)
3. Python3.10+

## Quick Install With pip

1. Create a virtual environment for python3. `python3 -m venv lis_autocontent_env` (optional)
2. Source environment. `. ./lis_autocontent_env/bin/activate` (optional)
3. pip install from the repo. `cd LIS-autocontent;pip install .`

## Developer Install

1. Clone repository. `git clone https://github.com/legumeinfo/LIS-autocontent.git`
2. Create a virtual environment for python3 `python3 -m venv lis_autocontent_env`  (optional)
3. Source virtual environment `. ./lis_autocontent_env/bin/activate`  (optional)
4. Install Black and pre-commit for git hooks. `pip install black pre-commit`
5. Initialize pre-commit (if you haven't already). `pip install pre-commit;pre-commit install`
6. Build package locally. `python setup.py build` (optional)

## Run

```
(lis_autocontent_env) $ lis-autocontent --help
Usage: lis-autocontent [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  populate-blast     CLI entry for populate-blast
  populate-dscensor  CLI entry for populate-dscensor
  populate-jbrowse2  CLI entry for populate-jbrowse2
  populate-jekyll    CLI entry for populate-jekyll
```
