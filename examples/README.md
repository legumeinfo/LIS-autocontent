# Examples

Below are examples that use the various cli entry points to populate backend objects for a genus centric LIS site.

If you want to batch the commands for JBrowse2 and BLAST DB creation you can add the "--cmds_only" flag and capture STDOUT.

## Build Collections and Resources

```
(lis_autocontent_env) $ lis-autocontent populate-jekyll --taxa_list ./examples/cicer.yml --collections_out ./test_jekyll

(lis_autocontent_env) $ ls -1 test_jekyll/
Cicer
(lis_autocontent_env) $ ls -1 test_jekyll/Cicer/
genus_resources.yml
species_collections.yml
species_resources.yml
```

## Build BLAST DBs

```
(lis_autocontent_env) $ lis-autocontent populate-blast --taxa_list ./examples/cicer.yml --blast_out ./test_blast

(lis_autocontent_env) $ ls -1 test_blast/ | egrep "pdb|ndb"
cicar.CDCFrontier.gnm1.ndb
cicar.CDCFrontier.gnm2.ndb
cicar.CDCFrontier.gnm3.ndb
cicar.ICC4958.gnm2.ndb
cicec.S2Drd065.gnm1.ndb
cicre.Besev079.gnm1.ndb
cicar.CDCFrontier.gnm1.ann1.protein.pdb
cicar.CDCFrontier.gnm2.ann1.protein_primary.pdb
cicar.CDCFrontier.gnm2.ann1.protein.pdb
cicar.CDCFrontier.gnm3.ann1.protein.pdb
cicar.ICC4958.gnm2.ann1.protein_primary.pdb
cicar.ICC4958.gnm2.ann1.protein.pdb
cicec.S2Drd065.gnm1.ann1.protein.pdb
cicre.Besev079.gnm1.ann1.protein.pdb
```

## Generate JBrowse2 Config

```
(lis_autocontent_env) $ lis-autocontent populate-jbrowse2 --jbrowse_url "https://my_genus.legumeinfo.org/tools/jbrowse2" --taxa_list ./examples/cicer.yml --jbrowse_out ./test_jbrowse

(lis_autocontent_env) $ ls -1 ./test_jbrowse
config.json
```

## Generate DSCensor Nodes

```
(lis_autocontent_env) $ lis-autocontent populate-dscensor --taxa_list ./examples/cicer.yml --nodes_out ./test_nodes

(lis_autocontent_env) $ ls -1 test_nodes/
cicar.CDCFrontier.gnm1.ann1.json
cicar.CDCFrontier.gnm1.ann1.protein.json
cicar.CDCFrontier.gnm1.json
cicar.CDCFrontier.gnm2.ann1.json
cicar.CDCFrontier.gnm2.ann1.protein.json
cicar.CDCFrontier.gnm2.ann1.protein_primary.json
cicar.CDCFrontier.gnm2.json
cicar.CDCFrontier.gnm3.ann1.json
cicar.CDCFrontier.gnm3.ann1.protein.json
cicar.CDCFrontier.gnm3.json
cicar.CDCFrontier.gnm3.x.cicec.S2Drd065.gnm1.PXV3.minimap2.paf.gz.json
cicar.CDCFrontier.gnm3.x.cicre.Besev079.gnm1.PXV3.minimap2.paf.gz.json
cicar.ICC4958.gnm2.ann1.json
cicar.ICC4958.gnm2.ann1.protein.json
cicar.ICC4958.gnm2.ann1.protein_primary.json
cicar.ICC4958.gnm2.json
cicec.S2Drd065.gnm1.ann1.json
cicec.S2Drd065.gnm1.ann1.protein.json
cicec.S2Drd065.gnm1.json
cicre.Besev079.gnm1.ann1.json
cicre.Besev079.gnm1.ann1.protein.json
cicre.Besev079.gnm1.json
```
