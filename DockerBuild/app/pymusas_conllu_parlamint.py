# pymusas_conllu_parlamint

# This is a script to take ParlaMint CoNLL-U format files and extra annotation as semantic tags using PyMUSAS
# Created by Daisy Lal and Paul Rayson @ UCREL, Lancaster University
# PyMUSAS was created by Andrew Moore and Paul Rayson @ UCREL, Lancaster University

# Licence: Apache License 2.0: https://github.com/UCREL/pymusas/blob/main/LICENSE

# We're assuming CONLL-U as input format: https://universaldependencies.org/format.html
# Output format is the same plus an extra list of semantic tags appended to the MISC field
# This version also preserves spaCy's lemma, upos and xpos as elements in the MISC field
# See further details and format discussions at: https://github.com/clarin-eric/ParlaMint/issues/204

# Before running, you need to install the PyMUSAS model, spaCy English model and conllu, as follows ...
# pip install https://github.com/UCREL/pymusas-models/releases/download/en_dual_none_contextual-0.3.3/en_dual_none_contextual-0.3.3-py3-none-any.whl
# python3 -m spacy download en_core_web_sm
# pip install conllu==4.4.2

# we can source ParlaMint corpora from https://nl.ijs.si/et/tmp/ParlaMint/MT/CoNLL-U-en/
# e.g. curl -o english_ParlaMint_MT.conllu https://nl.ijs.si/et/tmp/ParlaMint/MT/

# import spacy and create the pipeline
import spacy

# We exclude the following components as we do not need them. 
nlp = spacy.load('en_core_web_sm', exclude=['parser', 'ner'])
# Load the English PyMUSAS rule based tagger in a separate spaCy pipeline
english_tagger_pipeline = spacy.load('en_dual_none_contextual')
# Adds the English PyMUSAS rule based tagger to the main spaCy pipeline
nlp.add_pipe('pymusas_rule_based_tagger', source=english_tagger_pipeline)

# other required imports
import csv
from pathlib import Path
from typing import List
import conllu
from conllu import parse_incr

# Input file to be tagged
input_file = Path('/mnt/host/input.conllu').resolve()
# Extract the sentences 
data = open(input_file, mode = 'r', encoding='utf-8')
annotations = data.read()
sentence_list = conllu.parse(annotations)

# Create output file - tsv format
output_file = Path('/mnt/host/output.conllu').resolve()

# ADDING DATA TO TSV
with output_file.open('w', encoding='utf-8') as output_fp:
  for sent in sentence_list:
    sent_id = []
    source = []
    text = []
    # pre_id = ['# sent_id =']
    # pre_src = ['# source =']
    # pre_txt = ['# text =']
    pre_id = ['#', 'sent_id', '=']
    pre_src = ['#', 'source', '=']
    pre_txt = ['#', 'text', '=']

    # Attempt to fix-up untranslated sources (EN -> EN) with no source texts
    # In these cases we just use the original 'text' attribute instead
    if 'source' not in sent.metadata:
      sent.metadata['source'] = sent.metadata['text']

    sent_id.append(sent.metadata['sent_id'])
    source.append(sent.metadata['source'])
    text.append(sent.metadata['text'])

    tsv_writer = csv.writer(output_fp, delimiter= '\n', lineterminator= '\n', quoting=csv.QUOTE_NONE, quotechar="")
    tsv_writer_pre = csv.writer(output_fp, delimiter= ' ', lineterminator= ' ', quoting=csv.QUOTE_NONE)

    tsv_writer_pre.writerow(pre_id)
    tsv_writer.writerow(sent_id)
    tsv_writer_pre.writerow(pre_src)
    tsv_writer.writerow(source)
    tsv_writer_pre.writerow(pre_txt)
    tsv_writer.writerow(text)

    sentence = sent.filter(id=lambda x: type(x) is int)

    # Input needed for spacy pipeline
    spaces: List[bool] = []
    token_text: List[str] = []
    lemmas: List[str] = []
    upos_tags: List[str] = []

    miscs: List[str] = []   
    feats: List[str] = []

    temp_lemma: List[str] = []
    temp_upos: List[str] = []
    temp_xpos: List[str] = []

    for token_data in sentence:
      token_text.append(token_data['form'])
      lemmas.append(token_data['lemma'])
      upos_tags.append(token_data['upos'])
      miscs.append(token_data['misc'])
      feats.append(token_data['feats'])
      space = True
      if isinstance(token_data['misc'], dict):
        if token_data['misc'].get('SpaceAfter', 'yes').lower() == 'no':
          space = False
        spaces.append(space)

      temp_miscs = []
      temp_feats = []

      # populate temporary copies of lemma, UPOS, XPOS, MISC and Features fields to preserve them for the output
      temp_lemma.append(token_data['lemma'])
      temp_upos.append(token_data['upos'])
      temp_xpos.append(token_data['xpos'])

      try:
        for features in miscs:
          str_misc = ''
          for keys, values in features.items():   # metadata related to the sentence, i.e., sent_id, source, and text
            str_misc = str_misc + keys + '=' + values + '|'
          temp_miscs.append(str_misc[:-1])
      except Exception as e:
        print("Failed to reassemble miscs, list was:")
        print( features.items() )
        print( source )
        print( text )
        raise e
      
      for features in feats:
        str_feats = ''
        if features is not None:
          for keys, values in features.items():   # features related to the sentence, i.e., mood, number, etc.
            str_feats = str_feats + keys + '=' + values + '|'
          temp_feats.append(str_feats[:-1])
        else:
          temp_feats.append('_')

    doc = spacy.tokens.Doc(nlp.vocab, words=token_text, pos=upos_tags, lemmas=lemmas, spaces=spaces)
    output_doc = nlp(doc)

#    field_names = ['ID', 'Token', 'Lemma', 'UPOS', 'XPos', 'Feats', 'Head', 'Deprel', 'Deps', 'MISC', 'USAS Tags']
    field_names = ['ID', 'Token', 'Lemma', 'UPOS', 'XPos', 'Feats', 'Head', 'Deprel', 'Deps', 'MISC']
    tsv_writer = csv.DictWriter(output_fp, fieldnames=field_names, delimiter='\t')

    index = 0
    token_num = 1
    str_pymusas_tags = ''
    # str_pymusas_mwe = ''
    str_pymusas_bio = ''
    for token in output_doc:
      # append pymusas MWE information to MISC field and preserve spaCy tags and lemmas in case they are different to the input
      start, end = token._.pymusas_mwe_indexes[0]
      # debug code for tracing start and end 
      # str_pymusas_mwe = str(index) + ',' + str(start) + ',' + str(end)
      if (end - start) <= 1:
        str_pymusas_bio = 'O'
      elif index == start:
        str_pymusas_bio = 'B'
      else:
        str_pymusas_bio = 'I'
      # append pymusas tags to MISC field
      str_pymusas_tags = ','.join(token._.pymusas_tags)
      # change punctuation tag to Z9
      if str_pymusas_tags == 'PUNCT':
        str_pymusas_tags = 'Z9'
#       temp_miscs[index] = temp_miscs[index] + '|SEMNUM=' + str_pymusas_mwe + '|SEMMWE=' + str_pymusas_bio + '|SEM=' + str_pymusas_tags
      temp_miscs[index] = temp_miscs[index] + '|SpacyLemma=' + token.lemma_ + '|SpacyUPoS=' + token.pos_ + '|SpacyXPoS=' + token.tag_ + '|SEMMWE=' + str_pymusas_bio + '|SEM=' + str_pymusas_tags
      # print row
      tsv_writer = csv.DictWriter(output_fp, fieldnames=field_names, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar="")
      tsv_writer.writerow({'ID': token_num,
                                     'Token': token.text,
                                     # this version shows output from spacy pipeline
                                     # 'Lemma': token.lemma_,
                                     # 'UPOS': token.pos_,
                                     # 'XPos': token.tag_,
                                     # this version shows original input (from stanza?)
                                     'Lemma': temp_lemma[index],
                                     'UPOS': temp_upos[index],
                                     'XPos': temp_xpos[index],
                                     'Feats': temp_feats[index],
                                     'Head': token.i,
                                     'Deprel': '_',
                                     'Deps': '_',
                                     'MISC': temp_miscs[index]})
#                                     'USAS Tags': token._.pymusas_tags})
      index += 1
      token_num += 1
      
    tsv_writer = csv.writer(output_fp, delimiter= '\n', lineterminator= '\n')
    tsv_writer.writerow('')

