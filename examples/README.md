# Examples

## Build Collections and Resources

```
(lisautocontent_env) [ctc@haldane LIS-autocontent]$ ./lis-autocontent.py populate-jekyll --taxa_list ./examples/cicer.yml --collections_out ./test_jekyll

(lisautocontent_env) [ctc@haldane LIS-autocontent]$ ls -ltr test_jekyll/
total 0
drwxrwxr-x. 2 ctc ctc 106 Feb  1 12:54 Cicer
(lisautocontent_env) [ctc@haldane LIS-autocontent]$ ls -ltr test_jekyll/Cicer/
total 16
-rw-rw-r--. 1 ctc ctc 1724 Feb  1 12:54 genus_resources.yml
-rw-rw-r--. 1 ctc ctc 3335 Feb  1 12:55 species_collections.yml
-rw-rw-r--. 1 ctc ctc 6038 Feb  1 12:55 species_resources.yml
```

## Build BLAST DBs

```
(lisautocontent_env) [ctc@haldane LIS-autocontent]$ ./lis-autocontent.py populate-blast --taxa_list ./examples/cicer.yml --blast_out ./test_blast/

(lisautocontent_env) [ctc@haldane LIS-autocontent]$ ls -ltr test_blast/ | egrep "pdb|ndb" | less
-rw-rw-r--. 1 ctc ctc    765952 Feb  1 13:07 cicar.CDCFrontier.gnm1.ndb
-rw-rw-r--. 1 ctc ctc    704512 Feb  1 13:07 cicar.CDCFrontier.gnm2.ndb
-rw-rw-r--. 1 ctc ctc    237568 Feb  1 13:08 cicar.CDCFrontier.gnm3.ndb
-rw-rw-r--. 1 ctc ctc   3653632 Feb  1 13:08 cicar.ICC4958.gnm2.ndb
-rw-rw-r--. 1 ctc ctc   1454080 Feb  1 13:09 cicec.S2Drd065.gnm1.ndb
-rw-rw-r--. 1 ctc ctc    249856 Feb  1 13:09 cicre.Besev079.gnm1.ndb
-rw-rw-r--. 1 ctc ctc   3100672 Feb  1 13:10 cicar.CDCFrontier.gnm1.ann1.protein.pdb
-rw-rw-r--. 1 ctc ctc   2760704 Feb  1 13:10 cicar.CDCFrontier.gnm2.ann1.protein_primary.pdb
-rw-rw-r--. 1 ctc ctc   3444736 Feb  1 13:10 cicar.CDCFrontier.gnm2.ann1.protein.pdb
-rw-rw-r--. 1 ctc ctc   3518464 Feb  1 13:10 cicar.CDCFrontier.gnm3.ann1.protein.pdb
-rw-rw-r--. 1 ctc ctc   3039232 Feb  1 13:10 cicar.ICC4958.gnm2.ann1.protein_primary.pdb
-rw-rw-r--. 1 ctc ctc   3080192 Feb  1 13:10 cicar.ICC4958.gnm2.ann1.protein.pdb
-rw-rw-r--. 1 ctc ctc   3792896 Feb  1 13:10 cicec.S2Drd065.gnm1.ann1.protein.pdb
-rw-rw-r--. 1 ctc ctc   4005888 Feb  1 13:10 cicre.Besev079.gnm1.ann1.protein.pdb
```

## Generate JBrowse2 Config

```
```

## Generate DSCensor Nodes

```
```

