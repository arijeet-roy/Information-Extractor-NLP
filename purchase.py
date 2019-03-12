from __future__ import unicode_literals, print_function
from itertools import chain
import spacy
import io
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet
from collections import Counter
from pprint import pprint
import re
from nltk.corpus import wordnet as wn
import sys

nlp = spacy.load('en')

# extract synonyms of the verb
synonym_list = ["purchase", "acquire", "buy", "leverage", "obtain", "procure"]
synonym_set = set(synonym_list)

for synonym in synonym_list:
    lem = wn.lemmas(synonym)
    if (not lem):
        continue
    related_forms = lem[0].derivationally_related_forms()
    for form in related_forms:
        synonym_set.add(form.name())

print("Similar words to the word - Purchase : ", synonym_set)

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

    print(sub_tokens)
    print(sub_pass_tokens)
    print(indirect_obj_tokens)
    print(direct_obj_tokens)
    print(passive_obj_tokens)

    # extract easy information templates first
    price = [ent for ent in doc if (ent.ent_type_ == "MONEY")]
    date = [ent for ent in doc if (ent.ent_type_ == "DATE" or ent.ent_type_ == "TIME")]

    # check if passive phrase exists in sentence

    if sub_tokens and direct_obj_tokens:
        purchasers = [tok for tok in sub_tokens if
                      (tok not in price and tok not in date)]
        items = [tok for tok in direct_obj_tokens if
                 (tok not in price and tok not in date)]
    else:
        purchasers = [tok for tok in passive_obj_tokens if
                      (tok not in price and tok not in date)]
        items = [tok for tok in sub_pass_tokens if
                 (tok not in price and tok not in date)]

        print("Price:", price)
        print("Date:", date)
        print("Purchaser:", purchasers)
        print("Items:", items)


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
    purchasers = [npstr for npstr in extract_np(sub_parsed_sent)]

    # perform NER now so as to compare with the existing entities
    ner_purchasers_result = merge_with_entities(sub_sentence, purchasers)
    if (ner_purchasers_result):
        if (passive == False):
            purchasers.reverse()
        purchasers = ner_purchasers_result
    else:
        if (len(purchasers) > 2):
            purchasers = purchasers[0:2]

    purchasers = ' '.join(purchasers)

    # do the same as above for the sentence after the verb
    obj_tagged_sent = nltk.pos_tag(obj_sentence.split())
    obj_parsed_sent = cp.parse(obj_tagged_sent)
    items = [npstr for npstr in extract_np(obj_parsed_sent)]

    # perform NER now
    ner_items_result = merge_with_items_entities(obj_sentence, items)
    if (ner_items_result):
        items = ner_items_result
    else:
        if (passive == True):
            items.reverse()
        if (len(items) > 2):
            items = items[0:2]
    items = ' '.join(items)

    doc = nlp(sentence)
    # merge entities and noun chunks into one token
    # spans = list(doc.ents) + list(doc.noun_chunks)
    # for span in spans:
    #     span.merge()

    # extract named entities information templates
    price = [ent for ent in doc if (ent.ent_type_ == "MONEY" or ent.ent_type_ == "CARDINAL")]
    price = ' '.join(str(elem) for elem in price)
    date = [ent for ent in doc if (ent.ent_type_ == "DATE" or ent.ent_type_ == "TIME")]
    date = ' '.join(str(elem) for elem in date)

    print("----------Extracted Templates----------")
    print("Price:", price)
    print("Date:", date)
    print("Purchaser:", purchasers)
    print("Items:", items)


def merge_with_entities(sentence, existing_list):
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

def merge_with_items_entities(sentence, existing_list):
    doc = nlp(sentence)
    # merge entities and noun chunks into one token
    spans = list(doc.ents) + list(doc.noun_chunks)
    for span in spans:
        span.merge()

    entities = [ent.text for ent in doc if
                (ent.ent_type_ == "PRODUCT" or ent.ent_type_ == "ORG" or ent.ent_type_ == "WORK_OF_ART")]

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
    sentence = "On Friday GT Interactive Software Corp. purchased Humongous Entertainment Inc., for stock valued at 76 million dollars."
    # sentence = "When private-equity firm Ares Management was bought by New York real-estate investor AREA Property Partners earlier this year, two of AREA's co-founders decided to go their separate ways."
    # sentence = "Amazon.com Inc.'s acquisition of Whole Foods Market Inc. for $13.7 billion was made in 2017"
    # sentence = "A novel was bought by John for 10 dollars yesterday"
    sentence = sys.argv[1]
    matching_template = sys.argv[2]
    sentence = unicode(sentence, 'utf-8')
    extract_filled_templates_2(sentence, matching_template)

if __name__ == '__main__':
    main()
