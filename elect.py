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
    word_tokens = []
    for token in doc:
        word_tokens.append(token.text)
    # print(word_tokens)

    parsetree = get_parse_tree(sentence)

    # print(sub_tokens)
    # print(sub_pass_tokens)
    # print(indirect_obj_tokens)
    # print(direct_obj_tokens)
    # print(passive_obj_tokens)

    # extract easy information templates first
    org = [ent for ent in doc if (ent.ent_type_ == "ORG")]
    ordinal = [ent for ent in doc if (ent.ent_type_ == "ORDINAL")]
    if not org:
        org = [ent for ent in doc if (ent.ent_type_ == "GPE")]

    # check if passive phrase exists in sentence

    if sub_tokens and direct_obj_tokens:
        Elector = [tok for tok in sub_tokens]
        Person = [tok for tok in direct_obj_tokens]
        
    else:
        Person = [tok for tok in sub_pass_tokens]
        Elector = [ent for ent in doc if ((ent.dep_ == "pobj" or ent.dep_ == "dobj") and ent.head.text == "by")]
    position = "Member"

    with io.open("position.txt", "r", encoding="utf-8") as f:
        read_data = f.read()
        positions = read_data.split(",")
        for p in positions:
            # print(p,"*")
            for w in word_tokens:
                if p in w:
                    position = p
                    break

    f.close()

    print("Organization:", org)
    print("Person:", Person)
    print("Position:", position)
    print("ORDINAL:", ordinal)
    print("Elector:", Elector)


def main():
    sentence = unicode(sys.argv[1],'utf-8')
    # sentence = u"Allott was first elected to the Senate by means of a nasty bit of red-baiting in 1954."
    # print(sentence
    extract_filled_templates(sentence)


if __name__ == '__main__':
    main()

# (ent.ent_type_ == "PERSON" or ent.ent_type_ == "NORP" or ent.ent_type_ == "ORG"))]
