from __future__ import unicode_literals, print_function
from itertools import chain
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
synonym_list = ["post", "report", "announce", "publish", "record", "account", "note", "reveal"]
synonym_set = set(synonym_list)
for synonym in synonym_list:
    lem = wn.lemmas(synonym)
    if (not lem):
        continue
    related_forms = lem[0].derivationally_related_forms()
    for form in related_forms:
        synonym_set.add(form.name())
print("Similar words to the word - Post : ", synonym_set)

loss_synonyms = ["loss", "deprive", "deficit", "debt", "deplete", "decline", "fall", "diminish", "shrink", "reduce", "crash", "drop"]
gain_synonyms = ["gain", "earn", "profit", "income", "revenue", "benefit", "grow", "rise", "boost"]


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
    # extract money information
    relations = extract_currency_relations(doc)
    type = [r1 for r1, r2 in relations]
    price = [ent for ent in doc if (ent.ent_type_ == "PERCENT" or ent.ent_type_ == "MONEY")]
    print("Price/Percent:", price)
    print("Type:", type)

    # check if passive phrase exists in sentence

    if sub_tokens and direct_obj_tokens:
        posters = [tok for tok in sub_tokens if
                   (tok not in price and tok not in date)]
    else:
        posters = [tok for tok in passive_obj_tokens if
                   (tok not in price and tok not in date)]

    print("Date:", date)
    print("Poster:", posters)


def extract_currency_relations(doc):
    relations = []
    for money in filter(lambda w: w.ent_type_ == 'MONEY' or w.ent_type_ == 'PERCENT', doc):
        if money.dep_ in ('attr', 'dobj'):
            subject = [w for w in money.head.lefts if w.dep_ == 'nsubj']
            if subject:
                subject = subject[0]
                relations.append((subject, money))
        elif money.dep_ == 'pobj' and money.head.dep_ == 'prep':
            relations.append((money.head.head, money))
    return relations


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
    posters = [npstr for npstr in extract_np(sub_parsed_sent)]

    # perform NER now so as to compare with the existing entities
    ner_posters_result = merge_with_poster_entities(sub_sentence, posters)
    if (ner_posters_result):
        posters = ner_posters_result
    else:
        if (passive == False):
            posters.reverse()
        if (len(posters) > 2):
            posters = posters[0:2]

    posters = ' '.join(posters)

    # do the same as above for the sentence after the verb
    obj_tagged_sent = nltk.pos_tag(obj_sentence.split())
    obj_parsed_sent = cp.parse(obj_tagged_sent)
    types = [npstr for npstr in extract_np(obj_parsed_sent)]

    # perform NER now
    ner_items_result = find_type(lemmas)
    if (ner_items_result):
        types = ner_items_result
    else:
        if (passive == True):
            types.reverse()
        if (len(types) > 2):
            types = types[0:2]
    types = ' '.join(str(elem) for elem in types)

    doc = nlp(sentence)
    # merge entities and noun chunks into one token
    spans = list(doc.ents) + list(doc.noun_chunks)
    for span in spans:
        span.merge()

    # extract named entities information templates
    amount = [ent for ent in doc if (ent.ent_type_ == "MONEY" or ent.ent_type_ == "PERCENT")]
    amount = ' '.join(str(elem) for elem in amount)
    date = [ent for ent in doc if (ent.ent_type_ == "DATE" or ent.ent_type_ == "TIME")]
    date = ' '.join(str(elem) for elem in date)

    print("----------Extracted Templates----------")
    print("Poster:", posters)
    print("Amount/Percent:", amount)
    print("Date:", date)
    print("Type:", types)


def merge_with_poster_entities(sentence, existing_list):
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


def find_type(lemma_list):
    lmtzr = nltk.WordNetLemmatizer()
    lemmas = [lmtzr.lemmatize(token) for token in lemma_list]
    type = []
    for ent in loss_synonyms:
        for lemma in lemmas:
            if (ent in lemma):
                type.append(ent)
    for ent in gain_synonyms:
        for lemma in lemmas:
            if (ent in lemma):
                type.append(ent)
    return type


def extract_np(psent):
    for subtree in psent.subtrees():
        if subtree.label() == 'NP':
            yield ' '.join(word for word, tag in subtree.leaves())


def main():
    sentence = "Ford Motor Co. posted a 2.6% decline in March sales on Monday"
    sentence = "Children's Place Retail Stores Inc.'s announced that it's 2018 fiscal first-quarter earnings rose 19%, handily beating its own forecasts."
    sentence = sys.argv[1]
    matching_template = sys.argv[2]
    sentence = unicode(sentence, 'utf-8')
    extract_filled_templates_2(sentence, matching_template)


if __name__ == '__main__':
    main()
