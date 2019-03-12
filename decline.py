import spacy
import io
import sys, nltk, os
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet
from collections import Counter
from pprint import pprint
from nltk.parse.stanford import StanfordDependencyParser



nlp = spacy.load('en')

os.environ['JAVAHOME']="/Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home"
stan_dep_parser = StanfordDependencyParser("jars/stanford-parser.jar", "jars/stanford-parser-3.4.1-models.jar")

def get_noun_phrases(word,sentence):
    doc = nlp(sentence)
    index = 0
    nounIndice = 0
    for token in doc:
        if token.text == word and token.pos_ == 'NOUN':
            nounIndice = index
        index = index + 1
    span = doc[doc[nounIndice].left_edge.i : doc[nounIndice].right_edge.i+1]
    span.merge()

    result = word
    for token in doc:
        if word in token.text:
            result = token.text
    for t in doc.noun_chunks:
        if result in t.text:
            result = t.text
    return result

def get_parse_tree(sentence):

    dependency_parser = stan_dep_parser.raw_parse(sentence)
    doc = nlp(sentence)
    parsetree = []
    dep = dependency_parser.next()
    for triple in dep.triples():
        parsetree.append(triple)
        # print(triple)
    return parsetree


def extract_filled_templates(sentence):
    sub_tokens = ""
    Commodity = ""
    dir_obj = ""
    to_point = ""
    location = ""
    doc = nlp(sentence)
    # merge entities and noun chunks into one token
    spans = list(doc.ents) + list(doc.noun_chunks)
    for span in spans:
        span.merge()

    parsetree = get_parse_tree(sentence)

    # extract easy information templates first
    location = [ent for ent in doc if (ent.ent_type_ == "GPE" or ent.ent_type_ == "LOC")]

    # check if passive phrase exists in sentence
    sub_tokens = [tok for tok in doc if (tok.dep_ == "nsubj")]
    for triple in parsetree:

        if triple[0][1] in ['VBD','VBN'] and triple[1] in ['nsubj','nsubjpass']:
            Commodity = get_noun_phrases(triple[2][0],sentence)

        if triple[0][0] in ['to','at']:
            to_point = get_noun_phrases(triple[2][0],sentence)

        elif triple[0][1] in ['VBD','VBN'] and triple[1] == 'dobj':
            dir_obj = get_noun_phrases(triple[2][0],sentence)

    print("Commodity:", sub_tokens)
    print("Commodity1:",Commodity)
    print("from_point:", dir_obj)
    print("to_point:",to_point)
    print("Location:",location)



def main():
    sentence = unicode(sys.argv[1],'utf-8')
    # sentence = u"The bond's yield, which moves in the opposite direction of its price, fell to 5.956% from 5.967%."
    # print(sentence)
    extract_filled_templates(sentence)
    doc = nlp(sentence)

if __name__ == '__main__':
    main()

