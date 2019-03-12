from __future__ import unicode_literals, print_function
import spacy
import io
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet
from collections import Counter
from pprint import pprint
from nltk.corpus import wordnet as wn
import sys

nlp = spacy.load('en')

# extract synonyms of the verb
synonym_list = ["pass", "legislate", "authorize", "issue", "print", "circulate", "distribute", "decree",
                "enact", "formulate", "ordain", "regulate"]
synonym_set = set(synonym_list)
for synonym in synonym_list:
    lem = wn.lemmas(synonym)
    if (not lem):
        continue
    related_forms = lem[0].derivationally_related_forms()
    for form in related_forms:
        synonym_set.add(form.name())

print("Similar words to the word - Pass : ", synonym_set)


def extract_filled_templates(sentence):
    doc = nlp(sentence)
    # merge entities and noun chunks into one token
    spans = list(doc.ents) + list(doc.noun_chunks)
    for span in spans:
        span.merge()

    # get token dependencies
    sub_tokens = [tok for tok in doc if (tok.dep_ == "nsubj")]
    sub_pass_tokens = [tok for tok in doc if (tok.dep_ == "nsubjpass")]
    indirect_obj_tokens = [tok for tok in doc if (tok.dep_ == "iobj")]
    direct_obj_tokens = [tok for tok in doc if (tok.dep_ == "dobj")]
    passive_obj_tokens = [tok for tok in doc if (tok.dep_ == "pobj")]

    # print(sub_tokens)
    # print(sub_pass_tokens)
    # print(indirect_obj_tokens)
    # print(direct_obj_tokens)
    # print(passive_obj_tokens)

    # extract easy information templates first
    date = [ent for ent in doc if (ent.ent_type_ == "DATE" or ent.ent_type_ == "TIME")]
    locations = [ent for ent in doc if (ent.ent_type_ == "GPE" or ent.ent_type_ == "LOC")]
    if sub_tokens and direct_obj_tokens:
        passer = [tok for tok in sub_tokens if
                  (tok not in locations and tok not in date)]
        law = [tok for tok in direct_obj_tokens if
               (tok not in locations and tok not in date)]
    else:
        passer = [tok for tok in passive_obj_tokens if
                  (tok not in locations and tok not in date)]
        law = [tok for tok in sub_pass_tokens if
               (tok not in locations and tok not in date)]

    print("Passer:", passer)
    print("Date:", date)
    print("Law/Bill:", law)
    print("Location:", locations)


def extract_filled_templates_2(sentence, matching_template):
    # first extract the synonyms of purchase
    word_tokens = word_tokenize(sentence)
    lemmas = word_tokens
    # search for the matching template in list of lemmas and get the index
    word_index = lemmas.index(matching_template)
    # divide the sentence before the template verb and after the template verb by considering 'by' to be active or passive voice determiner
    passive = False
    if (word_index + 1 < len(lemmas) - 1 and lemmas[word_index + 1] == 'by'):
        # passive voice
        passive = True
        sub_sentence = ' '.join(lemmas[word_index + 2:])
        obj_sentence = ' '.join(lemmas[:word_index])
    else:
        # active voice
        sub_sentence = ' '.join(lemmas[:word_index])
        obj_sentence = ' '.join(lemmas[word_index + 1:])

    # include grammar for extracting head level noun phrases in the template
    grammar = r"""
             NP: {<DT|PP\$>?<JJ>*<NN>}   # chunk determiner/possessive, adjectives and noun
             {<NNP>+}                # chunk sequences of proper nouns
             {<NN>+}                 # chunk consecutive nouns
             {<NNS>+}                 # chunk consecutive nouns
             {<NNPS>+}                 # chunk consecutive nouns
             """
    cp = nltk.RegexpParser(grammar)  # Define Parser for extracting noun phrases

    sub_tagged_sent = nltk.pos_tag(sub_sentence.split())
    sub_parsed_sent = cp.parse(sub_tagged_sent)
    issuers = [npstr for npstr in extract_np(sub_parsed_sent)]

    # perform NER now so as to compare with the existing entities
    ner_issuers_result = merge_with_issuer_entities(sub_sentence, issuers)
    if (ner_issuers_result):
        issuers = ner_issuers_result
    else:
        if (passive == False):
            issuers.reverse()
        if (len(issuers) > 2):
            issuers = issuers[0:2]

    issuers = ' '.join(issuers)

    # do the same as above for the sentence after the verb
    obj_tagged_sent = nltk.pos_tag(obj_sentence.split())
    obj_parsed_sent = cp.parse(obj_tagged_sent)
    types = [npstr for npstr in extract_np(obj_parsed_sent)]

    # perform NER now
    ner_items_result = merge_with_bill_entities(obj_sentence, types)
    if (ner_items_result):
        types = ner_items_result
    else:
        if (passive == True):
            types.reverse()
        if (len(types) > 3):
            types = types[0:3]
    types = ' '.join(str(elem) for elem in types)

    doc = nlp(sentence)
    # merge entities and noun chunks into one token
    spans = list(doc.ents) + list(doc.noun_chunks)
    for span in spans:
        span.merge()

    # extract named entities information templates
    location = [ent for ent in doc if (ent.ent_type_ == "LOC" or ent.ent_type_ == "GPE" or ent.ent_type_ == "FAC")]
    location = ' '.join(str(elem) for elem in location)
    date = [ent for ent in doc if (ent.ent_type_ == "DATE" or ent.ent_type_ == "TIME")]
    date = ' '.join(str(elem) for elem in date)

    print("----------Extracted Templates----------")
    print("Issuer:", issuers)
    print("Bill/Law:", types)
    print("Date:", date)
    print("Location:", location)


def merge_with_issuer_entities(sentence, existing_list):
    doc = nlp(sentence)
    # merge entities and noun chunks into one token
    spans = list(doc.ents) + list(doc.noun_chunks)
    for span in spans:
        span.merge()

    entities = [ent.text for ent in doc if
                (ent.ent_type_ == "NORP" or ent.ent_type_ == "ORG" or ent.ent_type_ == "PERSON")]

    result = []
    for ent in entities:
        for existing in existing_list:
            if (existing in ent):
                result.append(ent)
                break
    return result


def merge_with_bill_entities(sentence, existing_list):
    doc = nlp(sentence)
    # merge entities and noun chunks into one token
    spans = list(doc.ents) + list(doc.noun_chunks)
    for span in spans:
        span.merge()

    entities = [ent.text for ent in doc if
                (ent.ent_type_ == "WORK_OF_ART" or ent.ent_type_ == "LAW")]

    result = []
    for ent in entities:
        for existing in existing_list:
            if (existing in ent):
                result.append(ent)
                break
    return result


def extract_np(psent):
    for subtree in psent.subtrees():
        if subtree.label() == 'NP':
            yield ' '.join(word for word, tag in subtree.leaves())


def main():
    sentence = "Earlier this year at the Capitol Hill, over the objections of securities firms, the Senate passed a bill expanding banks' securities powers."
    sentence = "The President has threatened to veto the Employment bill passed by the House and the Senate on Monday, December 10th at Washington D.C."
    sentence = "A high official in London said last night, the deficit could run to $24.2 billion, unless the Government passes the 10 percent surtax bill on April 1."
    sentence = sys.argv[1]
    matching_template = sys.argv[2]
    sentence = unicode(sentence, 'utf-8')
    extract_filled_templates_2(sentence, matching_template)


if __name__ == '__main__':
    main()
