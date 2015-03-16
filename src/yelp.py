import json
import time
import re
import pickle
import numpy as np
from stemming.porter2 import stem

def read_yelp(idxer):
    fp = open("../data/yelp_dataset_challenge_academic_dataset/yelp_academic_dataset_review.json")
    line = fp.readline()
    i = 0
    while line and i < 1000:
        line = fp.readline()
        #try:
        review = json.loads(line)
        idxer.addDoc(review['text'])
        #except:
        #    print "parse", i, "failed"
        i += 1
        if i % 1000 == 0:
            print i

class Idxer:
    def __init__(self):
        self.docId = 0
        self.rgx = re.compile("[\.\?\n\!]")
        self.invertedIdx = {}
        self.docLs = []
        self.sentenceNum = 0
    def addDoc(self, doc):
        ri = self.docId
        self.docId += 1
        sentenceLs = self.rgx.split(doc)
        self.docLs.append([])
        self.sentenceNum += len(sentenceLs)
        for si, sentence in enumerate(sentenceLs):
            wordLs = sentence.strip().lower().split()
            wordLs = [stem(word) for word in wordLs]
            for word in wordLs:
                if word not in self.invertedIdx:
                    self.invertedIdx[word] = []
                # the si-th sentence in ri-th review is idexed by ri*1000+si
                self.invertedIdx[word].append(ri*1000 + si) 
            self.docLs[ri].append(wordLs)

#improve this by the property that ls0 and ls1 are increasing integer list.
def intersection(ls0, ls1):
    return filter(lambda x: x in ls0, ls1)


if __name__ == "__main__":
    start_time = time.time()
    idxer = Idxer()
    read_yelp(idxer)
    #print len(idxer.invertedIdx)
    while True:
        word = raw_input('Search?')
        word = stem(word.strip().lower())
        print word
        relWordDic = {}
        if word in idxer.invertedIdx:
            docLs = idxer.invertedIdx[word]
            for doc in docLs:
                ri = doc/1000
                si = doc%1000
                print " ".join(idxer.docLs[ri][si])
                wordLs = idxer.docLs[ri][si]
                for term in wordLs:
                    if term not in relWordDic:
                        sentenceNum = idxer.sentenceNum
                        docLs2 = idxer.invertedIdx[term]
                        interDocLs= intersection(docLs , docLs2)
                        pxy = float(len(interDocLs))/sentenceNum
                        px  = float(len(docLs))/sentenceNum
                        py  = float(len(docLs2))/sentenceNum
                        px_ = px - pxy
                        p__ = 1 - px - py + pxy
                        p_y = py - pxy
                        v0 = pxy * np.log(pxy/(px*py+1e-5))
                        v1 = px_ * np.log(px_/(px*(1-py)+1e-5))
                        v2 = p_y * np.log(p_y/((1-px)*py)+1e-5)
                        v3 = p__ * np.log(p__/((1-px)*(1-py)+1e-5))
                        relWordDic[term] = v0 + v1 + v2 + v3
                        

            relWordLs = sorted(relWordDic.items(), key=lambda x: x[1], reverse = True)
            for i in xrange(min(100, len(relWordLs))):
                print relWordLs[i]



