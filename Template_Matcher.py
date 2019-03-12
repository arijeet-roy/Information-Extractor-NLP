import sys, nltk, os
import io
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.parse.stanford import StanfordDependencyParser
from nltk.tokenize import sent_tokenize, word_tokenize

template_list = ['invest', 'elect', 'predict', 'decline', 'launch', 'purchase', 'borrow', 'post', 'pass', 'resign']
port_stemmer = PorterStemmer()

purchase_synonyms = ["purchase", "acquire", "buy", "leverage", "obtain", "procure", "bought"]
purchase_synonyms_set = set(purchase_synonyms)
for syn in purchase_synonyms:
    stem = port_stemmer.stem(syn)
    purchase_synonyms_set.add(stem)
purchase_synonyms_list = list(purchase_synonyms_set)

predict_synonyms = ["predict", "forecast", "anticipate", "expect","estimate","foresee","prophesy","envision","envisioned","foretell","previse","guess"]
predict_synonyms_set = set(predict_synonyms)
for syn in predict_synonyms:
    stem = port_stemmer.stem(syn)
    predict_synonyms_set.add(stem)
predict_synonyms_list = list(predict_synonyms_set)

post_synonyms = ["post", "report", "announce", "publish", "record", "account", "note", "reveal"]
post_synonyms_set = set(post_synonyms)
for syn in post_synonyms:
    stem = port_stemmer.stem(syn)
    post_synonyms_set.add(stem)
post_synonyms_list = list(post_synonyms_set)

borrow_synonyms = ["borrow", "take", "borrowed"]
borrow_synonyms_set = set(borrow_synonyms)
for syn in borrow_synonyms:
    stem = port_stemmer.stem(syn)
    borrow_synonyms_set.add(stem)
borrow_synonyms_list = list(borrow_synonyms_set)

pass_synonyms = ["pass", "legislate", "authorize", "issue", "print", "circulate", "distribute", "decree",
                "enact", "formulate", "ordain", "regulate"]
pass_synonyms_set = set(pass_synonyms)
for syn in pass_synonyms:
    stem = port_stemmer.stem(syn)
    pass_synonyms_set.add(stem)
pass_synonyms_list = list(pass_synonyms_set)

resign_synonyms = ["resign", "quit", "leave", "relinquish", "surrender", "abandon", "renounce", "abdicate", "yield",
                "vacate", "forsake", "forgo", "retire", "step down", "terminate"]
resign_synonyms_set = set(resign_synonyms)
for syn in resign_synonyms:
    stem = port_stemmer.stem(syn)
    resign_synonyms_set.add(stem)
resign_synonyms_list = list(resign_synonyms_set)

launch_synonyms = ["launch", "introduce", "commence", "inaugurate","begin","start","initiate","organize"]
launch_synonyms_set = set(launch_synonyms)
for syn in launch_synonyms:
    stem = port_stemmer.stem(syn)
    launch_synonyms_set.add(stem)
launch_synonyms_list = list(launch_synonyms_set)

invest_synonyms = ["invest", "fund", "finance", "bankroll","subsidize","underwrite"]
invest_synonyms_set = set(invest_synonyms)
for syn in invest_synonyms:
    stem = port_stemmer.stem(syn)
    invest_synonyms_set.add(stem)
invest_synonyms_list = list(invest_synonyms_set)

decline_synonyms = ["decline", "fell", "decrease", "lessen","diminish","shrink","reduce","crash","fall","drop"]
decline_synonyms_set = set(decline_synonyms)
for syn in decline_synonyms:
    stem = port_stemmer.stem(syn)
    decline_synonyms_set.add(stem)
decline_synonyms_list = list(decline_synonyms_set)

elect_synonyms = ["elect", "choose", "pick", "select","appoint","nominate"]
elect_synonyms_set = set(elect_synonyms)
for syn in elect_synonyms:
    stem = port_stemmer.stem(syn)
    elect_synonyms_set.add(stem)
elect_synonyms_list = list(elect_synonyms_set)


def get_related_list(token):
    # print("token received is:",token)
    related_list = []
    for syn in wordnet.synsets(token):
        for sl in syn.lemmas():
            related_list.append(sl.name())

        if (syn.hypernyms()):
            for h in syn.hypernyms():
                for hl in h.lemmas():
                    if (hl.name() == 'take'):
                        print("found in hypernyms----------------------------------")
                    related_list.append(hl.name())
        if (syn.hyponyms()):
            for h in syn.hyponyms():
                for hl in h.lemmas():
                    if (hl.name() == 'take'):
                        print("found in hyponyms-----------------------------------")
                    related_list.append(hl.name())
        if (syn.part_meronyms()):
            for h in syn.part_meronyms():
                for hl in h.lemmas():
                    if (hl.name() == 'take'):
                        print("found in meronyms-----------------------------------")
                    related_list.append(hl.name())
        if (syn.part_holonyms()):
            for h in syn.part_holonyms():
                for hl in h.lemmas():
                    if (hl.name() == 'take'):
                        print("found in holonyms----------------------------------")
                    related_list.append(hl.name())

    related_list = set(related_list)
    return related_list


def check_list(stem, sentence, true_token):
    # print("stem is ", stem)
    if stem in template_list:
        command = 'python ' + stem + '.py ' + '\"' + sentence + '\"' + ' ' + '\"' + true_token + '\"'
        os.system(command)
        exit()

    if stem in predict_synonyms_list:
        command = 'python predict.py ' + '\"' + sentence + '\"' + ' ' + '\"' + true_token + '\"'
        os.system(command)
        exit()

    if stem in launch_synonyms_list:
        command = 'python launch.py ' + '\"' + sentence + '\"' + ' ' + '\"' + true_token + '\"'
        os.system(command)
        exit()

    if stem in post_synonyms_list:
        command = 'python post.py ' + '\"' + sentence + '\"' + ' ' + '\"' + true_token + '\"'
        os.system(command)
        exit()

    if stem in invest_synonyms_list:
        command = 'python invest.py ' + '\"' + sentence + '\"' + ' ' + '\"' + true_token + '\"'
        os.system(command)
        exit()

    if stem in purchase_synonyms_list:
        command = 'python purchase.py ' + '\"' + sentence + '\"' + ' ' + '\"' + true_token + '\"'
        os.system(command)
        exit()

    if stem in borrow_synonyms_list:
        command = 'python borrow.py ' + '\"' + sentence + '\"' + ' ' + '\"' + true_token + '\"'
        os.system(command)
        exit()

    if stem in elect_synonyms_list:
        command = 'python elect.py ' + '\"' + sentence + '\"' + ' ' + '\"' + true_token + '\"'
        os.system(command)
        exit()

    if stem in pass_synonyms_list:
        command = 'python pass.py ' + '\"' + sentence + '\"' + ' ' + '\"' + true_token + '\"'
        os.system(command)
        exit()

    if stem in resign_synonyms_list:
        command = 'python resign.py ' + '\"' + sentence + '\"' + ' ' + '\"' + true_token + '\"'
        os.system(command)
        exit()

    if stem in decline_synonyms_list:
        command = 'python decline.py ' + '\"' + sentence + '\"' + ' ' + '\"' + true_token + '\"'
        os.system(command)
        exit()


def get_matched_template(sentence):
    tokens = word_tokenize(sentence)
    clean_tokens = []
    check_tokens = []
    for i in nltk.pos_tag(tokens):
        if i[1] in ['NN', 'NNS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
            clean_tokens.append(i[0])

    check_tokens = [i.lower() for i in clean_tokens]

    for item in check_tokens:
        stem = port_stemmer.stem(item)
        true_token = item
        # print("went to check_list")
        check_list(stem, sentence, true_token)

    for t in check_tokens:
        true_token = t
        stem = port_stemmer.stem(t)
        # print("stem is :",stem)
        check_list(stem, sentence, true_token)

        related_list = get_related_list(stem)
        # print("starting token :", t)
        # for i in related_list:
        #     if i == 'take':
        #         print("yay **********************************")
        # print(related_list)
        for item in related_list:
            check_list(item, sentence, true_token)

        lem = wordnet.lemmas(t)
        if len(lem) == 0:
            continue
        # print(t)
        # print(lem)
        forms = lem[0].derivationally_related_forms()
        if len(forms) == 0:
            continue
        if len(forms) > 1:
            for i in forms:
                related_forms = set(i.name())
            print(related_forms)
            for j in related_forms:
                check_list(j, sentence, true_token)
                new_list = get_related_list(j)
                for k in new_list:
                    check_list(k, sentence, true_token)
        else:
            # print("k is", forms[0].name())
            k = forms[0].name()
            check_list(k, sentence, true_token)
            new_list = get_related_list(forms[0].name())
            for k in new_list:
                check_list(k, sentence, true_token)

    print("No Matching template present.")


def main():
    sentence = raw_input("Enter a sentence::\n")
    sentence = unicode(sentence, 'utf-8')
    # sentence = u"Thomas was elected as chief executive officer of Continental Illinois Corp., by John E. Swearingen."
    get_matched_template(sentence)


if __name__ == '__main__':
    main()
