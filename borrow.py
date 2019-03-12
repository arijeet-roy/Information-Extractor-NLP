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
synonym_list = ["borrow", "take"]
synonym_set = set(synonym_list)
for synonym in synonym_list:
    lem = wn.lemmas(synonym)
    if (not lem):
        continue
    related_forms = lem[0].derivationally_related_forms()
    for form in related_forms:
        synonym_set.add(form.name())
print("Similar words to the word - Borrow : ", synonym_set)


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
    price = [ent for ent in doc if (ent.ent_type_ == "MONEY")]
    if price:
        commodity = ["MONEY"]
        amount = price
    else:
        commodity = [ent for ent in doc if (ent.ent_type_ == "PRODUCT")]
        amount = [ent for ent in doc if
                  (ent.ent_type_ == "QUANTITY" or ent.ent_type_ == "ORDINAL" or ent.ent_type_ == "CARDINAL")]
    date = [ent for ent in doc if (ent.ent_type_ == "DATE" or ent.ent_type_ == "TIME")]

    # check if passive phrase exists in sentence

    if sub_tokens and direct_obj_tokens:
        borrowers = [tok for tok in sub_tokens if
                     (tok not in price and tok not in date)]
        if not commodity:
            commodity = [tok for tok in direct_obj_tokens if
                         (tok not in price and tok not in date)]
    else:
        borrowers = [tok for tok in passive_obj_tokens if
                     (tok not in price and tok not in date)]
        if not commodity:
            commodity = [tok for tok in sub_pass_tokens if
                         (tok not in price and tok not in date)]

    amount = ' '.join(str(elem) for elem in amount)
    date = ' '.join(str(elem) for elem in date)
    borrowers = ' '.join(str(elem) for elem in borrowers)
    commodity = ' '.join(str(elem) for elem in commodity)

    print("Amount:", amount)
    print("Date:", date)
    print("Borrower/Lender:", borrowers)
    print("Commodity:", commodity)


def extract_filled_templates_2(sentence, matching_template):
    # first extract the synonyms of purchase
    word_tokens = word_tokenize(sentence)
    lemmas = word_tokens
    # search for the matching template in list of lemmas and get the index
    word_index = lemmas.index(matching_template)
    if('from' in lemmas):
        from_index = lemmas.index('from')
    else:
        from_index = -1
    # divide the sentence before the template verb and after the template verb by considering 'by' to be active or passive voice determiner
    passive = False
    from_sentence = ''

    if (word_index + 1 < len(lemmas) - 1 and lemmas[word_index + 1] == 'by'):
        # passive voice
        passive = True
        obj_sentence = ' '.join(lemmas[:word_index])
        if (from_index > word_index):
            sub_sentence = ' '.join(lemmas[word_index + 2:from_index])
            from_sentence = ' '.join(lemmas[from_index + 1:])
        else:
            sub_sentence = ' '.join(lemmas[word_index + 2:])


    else:
        # active voice
        sub_sentence = ' '.join(lemmas[:word_index])
        if (from_index > word_index):
            obj_sentence = ' '.join(lemmas[word_index + 1:from_index])
            from_sentence = ' '.join(lemmas[from_index + 1:])
        else:
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
    borrowers = [npstr for npstr in extract_np(sub_parsed_sent)]

    # perform NER now so as to compare with the existing entities
    ner_borrowers_result = find_entities(sub_sentence, borrowers)
    if (ner_borrowers_result):
        borrowers = ner_borrowers_result
    else:
        if (passive == False):
            borrowers.reverse()
        if (len(borrowers) > 2):
            borrowers = borrowers[0:2]

    borrowers = ' '.join(borrowers)

    # do the same as above for the sentence after the verb
    obj_tagged_sent = nltk.pos_tag(obj_sentence.split())
    obj_parsed_sent = cp.parse(obj_tagged_sent)
    items = [npstr for npstr in extract_np(obj_parsed_sent)]

    if (passive == True):
        items.reverse()
    if (len(items) > 3):
        items = items[0:3]

    items = ' '.join(str(elem) for elem in items)

    # do the same as above for the sentence after from
    from_tagged_sent = nltk.pos_tag(from_sentence.split())
    from_parsed_sent = cp.parse(from_tagged_sent)
    lenders = [npstr for npstr in extract_np(from_parsed_sent)]

    # perform NER now so as to compare with the existing entities
    ner_lenders_result = find_entities(from_sentence, lenders)
    if (ner_lenders_result):
        lenders = ner_lenders_result
    else:
        if (passive == False):
            lenders.reverse()
        if (len(lenders) > 2):
            lenders = lenders[0:2]

    lenders = ' '.join(lenders)

    doc = nlp(sentence)
    # merge entities and noun chunks into one token
    # spans = list(doc.ents) + list(doc.noun_chunks)
    # for span in spans:
    #     span.merge()

    # extract named entities information templates
    amount = [ent for ent in doc if (
    ent.ent_type_ == "MONEY" or ent.ent_type_ == "PERCENT" or ent.ent_type_ == "QUANTITY" or ent.ent_type_ == "ORDINAL" or ent.ent_type_ == "CARDINAL")]
    amount = ' '.join(str(elem) for elem in amount)
    print("----------Extracted Templates----------")
    print("Borrower:", borrowers)
    print("Lender:", lenders)
    print("Amount:", amount)
    print("Commodity:", items)


def find_entities(sentence, borrowers):
    doc = nlp(sentence)
    # merge entities and noun chunks into one token
    spans = list(doc.ents) + list(doc.noun_chunks)
    for span in spans:
        span.merge()

    entities = [ent.text for ent in doc if
                (ent.ent_type_ == "NORP" or ent.ent_type_ == "ORG" or ent.ent_type_ == "PERSON" or ent.ent_type_ == "GPE")]

    result = []
    for ent in entities:
        for existing in borrowers:
            if (existing in ent):
                result.append(ent)
                break
    return result


def extract_np(psent):
    for subtree in psent.subtrees():
        if subtree.label() == 'NP':
            yield ' '.join(word for word, tag in subtree.leaves())


def main():
    sentence = "An amount of 4.17 billion euros was borrowed by Germany for two years at an average yield of minus 0.06%."
    sentence = "John borrowed two books from Jack last Monday."
    sentence = sys.argv[1]
    matching_template = sys.argv[2]
    sentence = unicode(sentence, 'utf-8')
    extract_filled_templates_2(sentence, matching_template)


if __name__ == '__main__':
    main()
