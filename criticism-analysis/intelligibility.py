import enchant
from enchant.checker import SpellChecker
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import plotly.express as px
import textwrap
import spacy
import langdetect
from collections import Counter
import re
nlp = spacy.load('en_core_web_lg')

class Text():
    def __init__(self, filename, textType='plain'):
        self.filename = filename
        with open(filename) as f:
            self.rawText = f.read()
        if filename[-4:] == '.xml':
            print('Assuming XML')
            soup = BeautifulSoup(self.rawText, features='lxml')
            self.rawText = soup.get_text()
        self.segments = self.getSegments(self.rawText)
        print(f'Got {len(self.segments)} segments.')
        self.misspelledDf = self.getMisspelledDf()
        self.df = self.getMisspelledDf()
        print('Got misspelled words.')
        self.langProps = [self.languageProportions(seg) for seg in self.segments]
        print('Got language guesses.')
        self.colemanLiaus = [self.colemanLiau(seg) for seg in self.segments]
        print('Got Coleman-Liau indices.')
        self.df['spelledCorrectly'] = 1 - self.df['nMisspelled']
        self.df['percEng'] = [seg['en'] for seg in self.langProps]
        self.df['coleman'] = self.colemanLiaus

    def getSegments(self, text, n=50):
        binA = list(range(0, len(text), round(len(text)/n)))
        ranges = list((zip(binA, binA[1:])))
        segments = []
        for i, j in ranges:
            segments.append(text[i:j])
        return segments

    def removeEnts(self, text):
        textDoc = nlp(text)
        noEnts = [w for w in textDoc if w.ent_type_ == '']
        noEntsTexts = [str(w) for w in noEnts]
        return ' '.join(noEntsTexts)

    def getMisspelled(self, text):
        checker = SpellChecker('en_GB')
        noEnts = self.removeEnts(text)
        checker.set_text(noEnts)
        misspelledWords = []
        for w in checker:
            misspelledWords.append(w.word)
        return misspelledWords

    def getNumMisspelled(self, text):
        return len(self.getMisspelled(text))

    def getMisspelledDf(self):
        segments = self.segments
        misspelledN = [self.getNumMisspelled(seg) / len(seg.split()) for seg in segments]
        s = pd.Series(misspelledN) #.plot(kind='bar')
        df = pd.DataFrame(s, index=s.index, columns=['nMisspelled'])
        df['segment'] = df.index
        df['previews'] = [textwrap.wrap(seg[:150], 40) for seg in segments]
        df['misspelled'] = [' '.join(self.getMisspelled(seg))[:150] for seg in segments]
        return df

    def plotMisspelled(self):
        df = self.misspelledDf()
        fig = px.bar(df, x='segment', y='nMisspelled', hover_data=['previews', 'misspelled'])
        fig.write_html('misspelled-plot.html')

    def languageProportions(self, text):
        """ Second method: get the highest-scoring language for each sentence, and tally
        them according to number of sentences.
        """
        allProps = {}
        doc = nlp(text)
        for sent in doc.sents:
            sent = sent.text
            try:
                lang = langdetect.detect(sent)
            except:
                continue
            if lang in allProps:
                allProps[lang] += 1
            else:
                allProps[lang] = 1
        langsDf = pd.Series(allProps)
        return langsDf / len(list(doc.sents)) # return proportions

    def plotLanguageProportions(self, langs=['en']):
        props = [self.languageProportions(seg) for seg in self.segments]
        df = pd.DataFrame(props)[langs]
        fig = px.bar(df)
        fig.write_html('language-guesses.html')

    def colemanLiau(self, text):
        """ Computes the Coleman-Liau readability index for a text."""
        doc = nlp(text)
        numLetters = len(text)
        numWords = len(doc)
        numSents = len(list(doc.sents))
        l = (numLetters/numWords)*100
        s = (numSents/numWords)*100
        return 0.0588*l - 0.296*s - 15.8

    def plotColeman(self):
        colemanLiau = [self.colemanLiau(seg) for seg in self.segments]
        df = pd.DataFrame(colemanLiau)
        fig = px.line(df)
        fig.write_html('coleman-liau.html')

    def plotAll(self):
        df = self.df
        dataCols = ['spelledCorrectly', 'percEng', 'coleman']
        df['avg'] = df[dataCols].mean()
        for col in dataCols:
            df[col] = df[col] / df[col].max()
        fig = px.line(df, x='segment', y= ['spelledCorrectly', 'percEng', 'coleman', 'avg'],
                      hover_data=['previews', 'misspelled'])
        fig.write_html('intelligibility.html')
        print('Wrote plot to intelligibility.html')

t = Text('../finnegans-wake-tei/finnegans-wake.xml')
t.plotAll()
