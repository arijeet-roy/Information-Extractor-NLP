import spacy
import io
import sys, nltk, os
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet
from collections import Counter
from pprint import pprint
from nltk.stem import PorterStemmer
from nltk.parse.stanford import StanfordDependencyParser



nlp = spacy.load('en')

os.environ['JAVAHOME']="/Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home"
stan_dep_parser = StanfordDependencyParser("jars/stanford-parser.jar", "jars/stanford-parser-3.4.1-models.jar")

port_stemmer = PorterStemmer()
phrase_list = ['nn','det','num','number','amod','advmod','poss','dep','conj','cc']
# extract easy information templates first
# amount = [ent for ent in doc if (ent.ent_type_ == "MONEY")]
# date = [ent for ent in doc if (ent.ent_type_ == "DATE" or ent.ent_type_ == "TIME")]

def get_noun_phrases(word,sentence):
    # print("reached word is ",word)
    doc = nlp(sentence)
    index = 0
    nounIndice = 0
    for token in doc:
        if token.text == word and token.pos_ == 'NOUN':
            nounIndice = index
        index = index + 1
    # for node in [doc[nounIndice].left_edge : doc[nounIndice].right_edge]:
    if doc[nounIndice].left_edge.tag_ in ['IN','TO']:
        left_index = doc[nounIndice].left_edge.i+1
    else:
        left_index = doc[nounIndice].left_edge.i
    span = doc[left_index : doc[nounIndice].right_edge.i+1]
    span.merge()

    result = word
    for token in doc:
        if word in token.text:
            # print(token.text,"-----------------------------")
            result = token.text
    for t in doc.noun_chunks:
        # print(t,"+++++++++++++++++++++++++++++++++++")
        if result in t.text:
            result = t.text

    # print("result is *******",result)
    # check_tokens = word_tokenize(result)
    return result

def get_full_word(word,parsetree):
    full_word = ""
    for triple in parsetree:
        # print("triple in full_word is ",triple)
        if(triple[0][0] == word and (triple[1] in phrase_list)):
            full_word = full_word + " " + get_full_word(triple[2][0],parsetree)

    full_word = full_word + " " + word
    return full_word

def extract_np(psent):
    for subtree in psent.subtrees():
        if subtree.label() == 'NP':
            yield ' '.join(word for word, tag in subtree.leaves())

def get_parse_tree(sentence):

    dependency_parser = stan_dep_parser.raw_parse(sentence)
    doc = nlp(sentence)
    parsetree = []
    dep = dependency_parser.next()
    for triple in dep.triples():
        parsetree.append(triple)
        # print(triple)
    return parsetree

def get_sub_parse_tree(sentence,parsetree,stem):
    parsetree_sub = []
    word_tokens_sub = word_tokenize(sentence)
    for triple in parsetree:
        if ((triple[0][0] in word_tokens_sub or triple[2][0] in word_tokens_sub) and (triple[0][0] != stem and triple[2][0] != stem)):
            parsetree_sub.append(triple)
            # print(triple)
    return parsetree_sub


def passive(parsetree):
    doc = nlp(sentence)

    impact = ""
    impact_word = ""
    cause_subject = ""
    cause_object = ""

    for ent in doc:
        if ((ent.dep_ == "pobj" or ent.dep_ == "dobj") and ent.head.text == "by"):
            Predictor = get_noun_phrases(ent.text,sentence)
    
    should_restart = True
    restarted = False
    while should_restart == True:
        should_restart = False
        for triple in parsetree:

            if restarted == False and triple[0][1] in ['VBD'] and triple[1] in ['ccomp','rcmod','vmod','xcomp']:

                impact_word = triple[0][0]
                impact = get_noun_phrases(triple[0][0],sentence)
                should_restart = True
                restarted = True
                break

            elif triple[0][0] == impact_word and triple[1] == 'nsubj':
                cause_subject = get_noun_phrases(triple[2][0],sentence)

            elif triple[0][1] == 'VBN' and triple[1] == 'nsubjpass':
                cause_object = get_noun_phrases(triple[2][0],sentence)

    print("predictors:",predictors)
    print("Predictor:", Predictor)
    print("Impact:", impact)
    print("cause_subject:",cause_subject)
    print("cause_object:",cause_object)
    # print("Date:", date)


def extract_filled_templates(sentence,stem):
    doc = nlp(sentence)
    # merge entities and noun chunks into one token
    spans = list(doc.ents) + list(doc.noun_chunks)
    for span in spans:
        span.merge()

    parsetree = get_parse_tree(sentence)

    

    Predictor = ""
    impact = ""
    impact_word = ""
    cause_subject = ""
    cause_object = ""
    

    for triple in parsetree:

        if triple[0][1] in ['VBD','VBN'] and triple[1] in ['nsubj','nsubjpass']:
            Predictor = get_noun_phrases(triple[2][0],sentence)

        elif triple[0][1] in ['VBD'] and triple[1] in ['ccomp','rcmod','vmod','xcomp']:
            if(triple[2][1] == 'VBN'):
                return passive(parsetree)
                
            impact_word = triple[2][0]
            impact = get_noun_phrases(triple[2][0],sentence)

        elif triple[0][0] == impact_word and triple[1] == 'nsubj':
            cause_subject = get_noun_phrases(triple[2][0],sentence)

        elif triple[0][0] == impact_word and triple[1] == 'dobj':
            cause_object = get_noun_phrases(triple[2][0],sentence)


    
    print("Predictor:", Predictor)
    print("Impact:", impact)
    print("cause_subject:",cause_subject)
    print("cause_object:",cause_object)
    # print("Date:", date)

def get_subject_object(word_index,lemmas):
    if (word_index + 1 < len(lemmas) - 1 and lemmas[word_index + 1] == 'by'):
        # passive voice
        passive = True
        sub_sentence = ' '.join(lemmas[word_index + 2:])
        obj_sentence = ' '.join(lemmas[:word_index])
    else:
        # active voice
        sub_sentence = ' '.join(lemmas[:word_index])
        obj_sentence = ' '.join(lemmas[word_index + 1:])

    return sub_sentence,obj_sentence


def extract_filled_templates2(sentence,stem):
    impact_word = ""
    cause_subject = ""
    cause_object = ""
    Predictor = ""
    imp_sub_sentence = ""
    impact_subjects = []
    cause_object_word = ""
    imp_sub_sentence = ""
    imp_obj_sentence = ""
    sub_sentence = ""
    obj_sentence = ""

    lmtzr = nltk.WordNetLemmatizer()
    word_tokens = word_tokenize(sentence)
    # lemmas = [lmtzr.lemmatize(token, 'v') for token in word_tokens]
    # lemma_set = set(lemmas)

    # for item in lemma_set:
    #     print("stem is ",stem,"item is ",item)
    #     if stem in item:
    #         matching_template = item

    matching_template = stem
    word_index = word_tokens.index(matching_template)
    # divide the sentence before the template verb and after the template verb by considering 'by' to be active or passive voice determiner
    
    sub_sentence,obj_sentence = get_subject_object(word_index,word_tokens)
    # print(sub_sentence)
    # print(obj_sentence)

    # include grammar for extracting head level noun phrases in the template
    grammar = r"""
         NP: {<DT|PP\$>?<JJ>*<NN>}   # chunk determiner/possessive, adjectives and noun
         {<NNP>+}                # chunk sequences of proper nouns
         {<NN>+}                 # chunk consecutive nouns
         """
    cp = nltk.RegexpParser(grammar)  # Define Parser for extracting noun phrases

    sub_tagged_sent = nltk.pos_tag(sub_sentence.split())
    sub_tokens = word_tokenize(sub_sentence)
    sub_parsed_sent = cp.parse(sub_tagged_sent)
    predictors = set([get_noun_phrases(npstr,sentence) for npstr in extract_np(sub_parsed_sent)])
    # predictors = [get_noun_phrases(entry,sub_sentence) for entry in sub_tagged_sent]

    parsetree = get_parse_tree(sentence)
    for triple in parsetree:
        # if 'VB' in triple[0][1] and triple[1] in ['nsubj']:
        if stem in triple[0][0]:
            predictor_word = triple[2][0]
            # print("Predictor word is ",predictor_word)
            break
    # for entry in predictors:
    #     if predictor_word in entry:
    #         Predictor = entry
    Predictor = get_noun_phrases(predictor_word,sub_sentence)



    # 
    

    parsetree_sub = get_sub_parse_tree(obj_sentence,parsetree,stem)
    impact_word = ""
    for triple in parsetree_sub:
        # print("triple in sub sentence is ",triple)
        if 'VB' in triple[0][1]:
            if(triple[0][0] in ['was','is']):
                continue
            impact_word = triple[0][0]
            # print("impact_word found is ************",impact_word)
            word_tokens = word_tokenize(obj_sentence)
            # lemmas = [lmtzr.lemmatize(token, 'v') for token in word_tokens]
            word_index_imp = word_tokens.index(impact_word)
            imp_sub_sentence,imp_obj_sentence = get_subject_object(word_index_imp,word_tokens)
            # print(imp_sub_sentence)
            # print(imp_obj_sentence)
            
        if triple[0][0] == impact_word and triple[1] == 'nsubj':
            cause_subject = get_noun_phrases(triple[2][0],imp_sub_sentence)

        elif triple[0][0] == impact_word and triple[1] == 'dobj':
            cause_object = get_full_word(triple[2][0],parsetree_sub)
            break
 
        # elif impact_word != "" and triple[2][1] == 'NN':
        #     cause_object = get_full_word(triple[2][0],parsetree_sub)
        #     break
    
    if cause_subject == "":
        obj_tagged_sent = nltk.pos_tag(imp_sub_sentence.split())
        obj_parsed_sent = cp.parse(obj_tagged_sent)
        impact_subjects = set([get_noun_phrases(npstr,imp_sub_sentence) for npstr in extract_np(obj_parsed_sent)])

    if len(impact_subjects)==0:
        sub_tokens = word_tokenize(imp_sub_sentence)
        impact_subjects = set([get_noun_phrases(entry,imp_sub_sentence) for entry in sub_tokens]) 
        


    

    if impact_word == "" or cause_object == "":
        if imp_obj_sentence != "":
            # print("entered imp_obj_sentence")
            doc_obj = nlp(imp_obj_sentence)
            for triple in parsetree_sub:
                if triple[1] in ['pobj','dobj']:
                    cause_object_word = triple[2][0]
                    # print("cause_object word is **",cause_object_word)
                    break
        # doc_sub = nlp(obj_sentence)
        
                
            for entry in doc_obj.noun_chunks:
                if cause_object_word in entry.text:
                    cause_object = get_full_word(entry.text,parsetree_sub)
            # else:
            #     impact_subjects.append(entry.text)


    print("Launchers:",predictors)
    print("Launcher:", Predictor)
    print("Effect:", impact_word)
    print("commodity/plan",impact_subjects)
    print("commodity/plan:",cause_subject)
    print("Effected person/org:",cause_object)


def main():
    sentence = unicode(sys.argv[1],'utf-8')
    # print(sentence)
    stem = unicode(sys.argv[2],'utf-8')
    # print("stem is ",stem)
    # stem = u"launched"
    # sentence = u"Hewlett-Packard launched a bidding war to wrest data-storage company 3Par from Dell."
    extract_filled_templates2(sentence,stem)
    

if __name__ == '__main__':
    main()

