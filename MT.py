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

def main():
    dict2 = readDict("dict2.txt")
    sentences2 = readSentences("sentences2.txt")
    translated2 = translate(sentences2, dict2)
    print "========TRANSLATION 0========="
    for sentence in translated2:
        print sentence


    st = POSTagger('stanford-postagger/models/english-left3words-distsim.tagger',
        'stanford-postagger/stanford-postagger.jar')
    POS = []
    for sentence in translated2:
        tagged = st.tag(sentence.split())
        if (len(tagged)>0):
            #print(tagged)
            POS.append(tagged)
    POS = stupidFixes(POS)
    for sentence in POS:
        print sentence # '[%s]' % ', '.join(map(str, sentence))

if __name__ == "__main__":
    main()
