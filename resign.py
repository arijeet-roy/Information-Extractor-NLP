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
synonym_list = ["resign", "quit", "leave", "relinquish", "surrender", "abandon", "renounce", "abdicate", "yield",
                "vacate", "forsake", "forgo", "retire", "step down", "terminate"]
synonym_set = set(synonym_list)
for synonym in synonym_list:
    lem = wn.lemmas(synonym)
    if(not lem):
        continue
    related_forms = lem[0].derivationally_related_forms()
    for form in related_forms:
        synonym_set.add(form.name())
print("Similar words to the word - resign : ", synonym_set)

def extract_filled_templates(sentence):
    doc = nlp(sentence)
    # merge entities and noun chunks into one token
    spans = list(doc.ents) + list(doc.noun_chunks)
    for span in spans:
        span.merge()

    # extract easy information templates first
    orgs = [ent for ent in doc if (ent.ent_type_ == "NORP" or ent.ent_type_ == "ORG")]
    entities = [ent for ent in doc if (ent.ent_type_ == "PERSON")]
    locations = [ent for ent in doc if (ent.ent_type_ == "GPE" or ent.ent_type_ == "LOC")]

    word_tokens = []
    for token in doc:
        word_tokens.append(token.text)
    word_tokens = [i.lower() for i in word_tokens]

    with io.open("position.txt", "r", encoding="utf-8") as f:
        read_data = f.read()
        positions = read_data.split(",")
        positions = [i.lower() for i in positions]
        for p in positions:
            for w in word_tokens:
                if p in w:
                    position = p
                    break
    print("----------Extracted Templates----------")
    print("Organization:", orgs)
    print("Role:", position)
    print("Entities:", entities)
    print("Location:", locations)


def main():
    sentence = "J. William Middleton has resigned as president of Equitable Bank N.A. and as a director of its holding company, Equitable Bancorp, the bank announced yesterday in California."
    sentence = sys.argv[1]
    matching_template = sys.argv[2]
    sentence = unicode(sentence, 'utf-8')
    extract_filled_templates(sentence)

if __name__ == '__main__':
    main()
