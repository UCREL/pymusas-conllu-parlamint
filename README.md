# pymusas-conllu-parlamint
This repo contains the wrapper script and Dockerfile for running the PyMUSAS tagging of the CoNLL-U format of the [ParlaMint](https://www.clarin.eu/parlamint) project corpora translated to English

# Download corpora
The latest versions will be at https://nl.ijs.si/et/tmp/ParlaMint/MT/CoNLL-U-en/ and some parliaments data may be updated

# Format considerations
Previous discussions with Tomaž and Matyáš about the output format are at https://github.com/clarin-eric/ParlaMint/issues/204 

# Set up
First, create the docker image from the Dockerfile and other files in the `DockerBuild` folder, naming it as follows:
```
docker build -t pymusas_conllu .
```

# Tagging process per parliament zip file
Something like the following ...
1. Unzip the file
2. cd into directory showing all the year folders
3. run `pymusas_parlamint_wrapper.sh` script
4. monitor timestamps and output files until complete (speed is approx. 3 million words/hour on the UCREL VM)
5. create a tar.gz of the output files
6. copy the tarball to https://ucrel.lancs.ac.uk/paul/parlamint/PyMUSASTagged/ or some other wget-able location
