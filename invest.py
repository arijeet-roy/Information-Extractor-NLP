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
    impact = ""
    impact_word = ""
    cause_object = ""
    doc = nlp(sentence)
    # merge entities and noun chunks into one token
    spans = list(doc.ents) + list(doc.noun_chunks)
    for span in spans:
        span.merge()

    parsetree = get_parse_tree(sentence)

    # extract easy information templates first
    org = [ent for ent in doc if (ent.ent_type_ == "ORG")]
    capital = [ent for ent in doc if (ent.ent_type_ == "MONEY")]
    date = [ent for ent in doc if (ent.ent_type_ == "DATE" or ent.ent_type_ == "TIME")]
    if not org:
        org = [ent for ent in doc if (ent.ent_type_ == "GPE")]

    # check if passive phrase exists in sentence
    Investor = []
    Endeavor = []
    for ent in doc:
        if (ent.dep_ == "nsubj"):
            Investor.append(get_noun_phrases(ent.text,sentence))

        elif ((ent.dep_ == "pobj" or ent.dep_ == "dobj") and ent.head.text == "by"):
            Investor.append(get_noun_phrases(ent.text,sentence))

        if ((ent.dep_ == "pobj" or ent.dep_ == "dobj") and ent.head.text == "in"):
            Endeavor.append(get_noun_phrases(ent.text,sentence))

    for triple in parsetree:

        if 'VB' in triple[0][1] and triple[1] in ['ccomp','rcmod','vmod','xcomp']:
            if(triple[2][1] == 'VBN'):
                return passive(parsetree)
                
            impact_word = triple[2][0]
            impact = get_noun_phrases(triple[2][0],sentence)

        elif triple[0][0] == impact_word and triple[1] == 'dobj':
            cause_object = get_noun_phrases(triple[2][0],sentence)
            break

    Purpose = ""
    print("Investor:", Investor)
    print("Capital:", capital)
    print("Endeavor:",Endeavor)
    print("Purpose:", impact)
    print("Purpose_object:",cause_object)
    print("Date:", date)



def main():
    sentence = unicode(sys.argv[1],'utf-8')
    # sentence = u"Treasury Department has invested close to $100 billion in the housing-finance giants."
    # print(sentence)
    extract_filled_templates(sentence)
    doc = nlp(sentence)
    # for token in doc:
    #     print("{0}/{1} <--{2}-- {3}/{4}".format(
    #     token.text, token.tag_, token.dep_, token.head.text, token.head.tag_))


if __name__ == '__main__':
    main()

