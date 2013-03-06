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
    delimiters = "[ \",;:\.\!']"
    for sentence in sentences:
        englishSentence = ""
        for word in re.split(delimiters, sentence):
            wordUnicode = word.decode('utf-8').lower()
            if wordUnicode in dict:
                englishSentence += dict[wordUnicode] + " "
            else:
                englishSentence += word + " "
        result.append(englishSentence)
    return result

def main():
#    dict = readDict("dict.txt")
#    sentences = readSentences("sentences1.txt")
#    translated = translate(sentences, dict)

    dict2 = readDict("dict2.txt")
    sentences2 = readSentences("sentences2.txt")
    translated2 = translate(sentences2, dict2)
    for sentence in translated2:
        print sentence


    st = POSTagger('stanford-postagger/models/english-left3words-distsim.tagger','stanford-postagger/stanford-postagger.jar')
    POS = []
    for sentence in translated2:
        tagged = st.tag(sentence.split())
        if (len(tagged)>0):
            print(tagged)
            POS.append(tagged)


if __name__ == "__main__":
    main()
