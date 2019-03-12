import sys, nltk, os
import io
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.parse.stanford import StanfordDependencyParser
from nltk.tokenize import sent_tokenize, word_tokenize

os.environ['JAVAHOME'] = "/Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home"
stan_dep_parser = StanfordDependencyParser("jars/stanford-parser.jar", "jars/stanford-parser-3.4.1-models.jar")

hypernyms = []
hyponyms = []
meronyms = []
holonyms = []

to_do = ["word_tokens", "sentence_tokens", "Lemmas", "POS_TAGS", "Dependency_Parse", "hypernym_list", "hyponym_list"
    , "meronym_list", "holonym_list"]


def get_feature_vector(sentence):
    return_list = []

    # wordtokenize
    tokens = nltk.word_tokenize(sentence)
    return_list.append(tokens)

    # sentencetokenize
    sent_tokens = sent_tokenize(sentence)
    return_list.append(sent_tokens)

    # lemmatize
    lmtzr = WordNetLemmatizer()
    # " ".join([lmtzr.lemmatize(i) for i in tokens])
    lemma_list = [lmtzr.lemmatize(i) for i in tokens]
    return_list.append(lemma_list)

    # pos tagger
    pos_tag_list = [i[1] for i in nltk.pos_tag(tokens)]
    return_list.append(pos_tag_list)

    # dependency_parsing:
    dependency_list = []
    for sentence in sent_tokens:
        dependency_parser = stan_dep_parser.raw_parse(sentence)
        dep = dependency_parser.next()
        for triple in dep.triples():
            dependency_list.append(triple)
    return_list.append(dependency_list)

    # hypernym,hyponym,meronym,holonym:

    for t in tokens:
        hyper_list = []
        hypo_list = []
        mero_list = []
        holo_list = []
        for syn in wordnet.synsets(t):
            if (syn.hypernyms()):
                for h in syn.hypernyms():
                    for hl in h.lemmas():
                        hyper_list.append(hl.name())
            if (syn.hyponyms()):
                for h in syn.hyponyms():
                    for hl in h.lemmas():
                        hypo_list.append(hl.name())
            if (syn.part_meronyms()):
                for h in syn.part_meronyms():
                    for hl in h.lemmas():
                        mero_list.append(hl.name())
            if (syn.part_holonyms()):
                for h in syn.part_holonyms():
                    for hl in h.lemmas():
                        holo_list.append(hl.name())
        if hyper_list:
            hypernyms.append(set(hyper_list))
        if hypo_list:
            hyponyms.append(set(hypo_list))
        if mero_list:
            meronyms.append(set(mero_list))
        if holo_list:
            holonyms.append(set(holo_list))
    return_list.append(hypernyms)
    return_list.append(hyponyms)
    return_list.append(meronyms)
    return_list.append(holonyms)

    return return_list


def print_feature_vector_corpus():
    with io.open("corpus.txt", "r", encoding="utf-8") as f:
        read_data = f.read()
    f.close()
    sent_tokens = sent_tokenize(read_data)

    f1 = open("test.txt", "wb")
    sentence_count = 0
    for sentence in sent_tokens:
        # cleaning sentences in the corpus
        if sentence == "":
            continue
        sentence = sentence.replace("</br></br>", " ")

        sentence_count += 1
        if sentence_count == 2:
            break
        result_list = []
        result_list = get_feature_vector(sentence)
        for name, result in zip(to_do, result_list):
            f1.write(name + "\n" + str(result) + "\n")


def print_feature_vector(sentence):
    result_list = get_feature_vector(sentence)
    for name, result in zip(to_do, result_list):
        print name, "\n", result, "\n"


def main():
    choice = raw_input("Enter 0 to run on a corpus, 1 to run on single sentence  ")
    if choice == "1":
        sentence = raw_input("Enter a sentence  ")
        sentence = unicode(sentence, 'utf-8')
        print_feature_vector(sentence)
    else:
        print_feature_vector_corpus()


if __name__ == '__main__':
    main()
