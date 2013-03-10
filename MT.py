from nltk.tag.stanford import POSTagger
import sys
import re

VOWELS = ['a','e','o','i','u']

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
        'dangling':'','step':'','there':'it'}
    specialFixes = {'step':'','that':'while'}
    word, tag = taggedWord # ack use a map!!
    if word in fixes:
        return (fixes[word],tag)
    if (dangleFlag or notFlag) and taggedWord in specialFixes:
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

def ruleTwoNine(POS):
    modifiedPOS = []
    for taggedSentence in POS:
        modifiedSentence = []
        prevWord2, prevTag2 = taggedSentence[0]
        modifiedSentence.append((prevWord2, prevTag2))
        prevWord, prevTag = taggedSentence[1]
        modifiedSentence.append((prevWord, prevTag))
        switchedPos = sys.maxint
        for taggedWord in taggedSentence[2:]:
            word, tag = taggedWord
            switchedPos = switchedPos + 1
            # Rule 9
            if switchedPos>2  and prevWord == "of" and tag in ["NN", "NNP"] and prevTag2 in ["NN", "NNP"]:
                # print prevWord2, word
                modifiedSentence[len(modifiedSentence)-2] = (word + " " + prevWord2, tag)
                modifiedSentence.pop()
#                modifiedSentence[len(modifiedSentence)-1] = (prevWord2, prevTag2)
                switchedPos = 0
            # Rule 2
            elif tag == "CD" and prevTag2 == "CD":
                modifiedSentence[len(modifiedSentence)-1] = (prevWord2+"."+word, tag)
            elif prevTag == "CD" and tag == ",":
                word = "." # actually not added
            else:
                modifiedSentence.append(taggedWord)

            prevWord2, prevTag2 = prevWord, prevTag
            prevWord, prevTag = word, tag
        modifiedPOS.append(modifiedSentence)
    return modifiedPOS

def ruleSixEight(POS):
    modifiedPOS = []
    for taggedSentence in POS:
        modifiedSentence = []
        prevWord3, prevTag3 = taggedSentence[0]
        modifiedSentence.append((prevWord3, prevTag3))
        prevWord2, prevTag2 = taggedSentence[1]
        modifiedSentence.append((prevWord2, prevTag2))
        prevWord, prevTag = taggedSentence[2]
        modifiedSentence.append((prevWord, prevTag))
        for taggedWord in taggedSentence[3:]:
            word, tag = taggedWord
            if prevTag == 'DT' and prevWord[0] in VOWELS and tag in ['NN','JJ'] and word[0] in VOWELS:
                modifiedSentence[len(modifiedSentence)-1] = ('an','DT')
            # Rule 6 do not ... always => still do not
            if prevTag == "VB" and prevTag3 == "RB" and prevWord2 == "not" and tag == "RB":
                modifiedSentence.insert(len(modifiedSentence)-3,("still", tag))
            else:
                modifiedSentence.append(taggedWord)
            prevWord3, prevTag3 = prevWord2, prevTag2
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

    POS = ruleTwoNine(POS)
    POS = ruleTwoNine(POS) # apply twice
    print "=====================================RULE2+9 TRANSLATION========================================"
    for sentence in POS:
        print ' '.join(map(getWord, sentence))

    POS = ruleSixEight(POS)
    print "=====================================RULE6+8 TRANSLATION========================================"
    for sentence in POS:
        print ' '.join(map(getWord, sentence))



if __name__ == "__main__":
    main()
