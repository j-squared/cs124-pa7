from nltk.tag.stanford import POSTagger
import re

def readDict(file):
    dict = {}
    with open(file) as f:
        for line in f:
            (key, val) = line.split(':')
            dict[unicode(key, 'utf-8')] = val.rstrip()
    return dict

def readSentences(file):
    result = []
    with open(file) as f:
        for line in f:
            result.append(line.strip())
    return result

def translate(sentences, dict):
    result = []
    delimiters = "([ \",;:\.\!])"
    for sentence in sentences:
        englishSentence = ""
        for word in re.split(delimiters, sentence):
            wordUnicode = word.decode('utf-8')
            if wordUnicode == ' ': continue
            if wordUnicode.find("'") != -1:
                ind = wordUnicode.find("'")
                firstWord = wordUnicode[0:ind] + "'"
                secondWord = wordUnicode[ind+1:len(wordUnicode)]
                englishSentence += translateWord(firstWord, dict)
                englishSentence += translateWord(secondWord, dict)
            else:
                englishSentence += translateWord(wordUnicode, dict)
        result.append(englishSentence)
    return result

def translateWord(word, dict):
    if word.lower() in dict:
        return dict[word.lower()] + " "
    else:
        return word + " "

# Realized rules need to be related to POS somehow, will change that later
def stupidFixes(POS):
    modifiedPOS = []
    for taggedSentence in POS:
        modifiedSentence = []
        notFlag, dangleFlag = False, False
        for taggedWord in taggedSentence:
            word, tag = taggedWord
            if word == 'not':
                notFlag = True
            elif word == 'dangling':
                dangleFlag = True
            taggedWord = simpleTranslationRules(taggedWord,notFlag,dangleFlag)
            if len(taggedWord[0]) > 0:
                modifiedSentence.append(taggedWord)
        modifiedPOS.append(modifiedSentence)
    return modifiedPOS

def simpleTranslationRules(taggedWord, notFlag, dangleFlag):
    fixes = {'set':'play','founding':'mother','avenues':'e-mails','commanded':'purchased',
        'dangling':'','that':'while','step':'','there':'it'}
    word, tag = taggedWord # ack use a map!!
    if word in fixes:
        return (fixes[word],tag)
    return (word,tag)

# 1: NN - JJ / VBG => JJ / VBG - NN
# 3: EX / PRP / PRP$ / DT - V* but not VBD => switch
def rulesOneThree(POS):
    modifiedPOS = []
    for taggedSentence in POS:
        modifiedSentence = []
        prevWord, prevTag = taggedSentence[0]
        modifiedSentence.append((prevWord, prevTag))
        for taggedWord in taggedSentence[1:]:
            word, tag = taggedWord
            if prevTag == "NN" and tag in ["JJ", "VBG"]:
                modifiedSentence[len(modifiedSentence)-1] = (word, tag) # switch words
                modifiedSentence.append((prevWord, prevTag))
            elif prevTag in ["EX", "PRP", "PRP$", "DT"] and (tag[0] == 'V' and tag != "VBD"):
                modifiedSentence[len(modifiedSentence)-1] = (word, tag)
                modifiedSentence.append((prevWord, prevTag))
            else:
                modifiedSentence.append(taggedWord)

            prevWord, prevTag = word, tag
        modifiedPOS.append(modifiedSentence)
    return modifiedPOS

# PRP / NN - PRP => remove second PRP
def rulesFourFiveSeven(POS):
    modifiedPOS = []
    for taggedSentence in POS:
        modifiedSentence = []
        prevWord, prevTag = taggedSentence[0]
        modifiedSentence.append((prevWord, prevTag))
        for taggedWord in taggedSentence[1:]:
            word, tag = taggedWord
            if prevTag in ["PRP", "NN"] and tag == "PRP":
                continue
            if tag == "RB" and word == "not": # don't need the tag condition but trying involve POS :p
                modifiedSentence.append(("do "+word, tag))
            if prevTag == "IN" and prevWord == "of" and tag[0] == 'V':
                modifiedSentence[len(modifiedSentence)-1] = ("to", prevTag)
                modifiedSentence.append(taggedWord)
            else:
                modifiedSentence.append(taggedWord)

            prevWord, prevTag = word, tag
        modifiedPOS.append(modifiedSentence)
    return modifiedPOS


def ruleNine(POS):
    modifiedPOS = []
    for taggedSentence in POS:
        modifiedSentence = []
        prevWord2, prevTag2 = taggedSentence[0]
        modifiedSentence.append((prevWord2, prevTag2))
        prevWord, prevTag = taggedSentence[1]
        modifiedSentence.append((prevWord, prevTag))
        for taggedWord in taggedSentence[2:]:
            word, tag = taggedWord
            if prevWord == "of" and tag == "NN" and prevTag2 == "NN":
#                print prevWord2, word
                modifiedSentence[len(modifiedSentence)-2] = (word, tag)
                modifiedSentence[len(modifiedSentence)-1] = (prevWord2, prevTag2)
            else:
                modifiedSentence.append(taggedWord)

            prevWord2, prevTag2 = prevWord, prevTag
            prevWord, prevTag = word, tag
        modifiedPOS.append(modifiedSentence)
    return modifiedPOS

def getWord(tuple):
    return tuple[0]

def main():
    dict2 = readDict("dict2.txt")
    sentences2 = readSentences("sentences2.txt")
    translated2 = translate(sentences2, dict2)
    print "======================================BASE TRANSLATION=========================================="
    for sentence in translated2:
        print sentence

    print "================================================================================================"

    st = POSTagger('stanford-postagger/models/english-left3words-distsim.tagger',
        'stanford-postagger/stanford-postagger.jar')
    POS = []
    for sentence in translated2:
        tagged = st.tag(sentence.split())
        if (len(tagged)>0):
            POS.append(tagged)

    POS = stupidFixes(POS)
    print "==================================STUPID FIXES TRANSLATION======================================"
    for sentence in POS:
#        print sentence # '[%s]' % ', '.join(map(str, sentence))
        print ' '.join(map(getWord, sentence))


    POS = rulesOneThree(POS)
    print "=====================================RULE1+3 TRANSLATION========================================"
    for sentence in POS:
        print ' '.join(map(getWord, sentence))

    POS = rulesFourFiveSeven(POS)
    print "=====================================RULE4+5+7 TRANSLATION========================================"
    for sentence in POS:
        print ' '.join(map(getWord, sentence))

    POS = ruleNine(POS)
    print "=====================================RULE9 TRANSLATION========================================"
    for sentence in POS:
        print ' '.join(map(getWord, sentence))


if __name__ == "__main__":
    main()
