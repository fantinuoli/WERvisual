import os
import re
import jiwer
import math
import statistics
from decimal import *
import numpy as np

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-r','--ref', help="path to reference", required=True)
parser.add_argument('-y','--hyp', help="path to hyothesis", required=True)
args = vars(parser.parse_args())


full_path_reference    = args['ref']
full_path_hypothesis   = args['hyp']

#hardcoded preprocessing of input if text is separated by newlines
input_type = 'segmented'
print("Input is: " + input_type)

with open(full_path_reference, 'r', encoding='utf8') as file:
    if input_type == 'segmented' :
        reference = file.read().replace('\n', ' ')
    else :
        reference = file.read().splitlines()
        
with open(full_path_hypothesis, 'r', encoding='utf8') as file:
    if input_type == 'segmented' :
        hypothesis = file.read().replace('\n', ' ')
    else :
        hypothesis = file.read().splitlines()

WORD = re.compile(r'\w+')
       
def wer(reference, hypothesis):

    transformation = jiwer.Compose([
        jiwer.ToLowerCase(),
        jiwer.RemovePunctuation(),
        jiwer.Strip(),
        jiwer.RemoveMultipleSpaces(),
        jiwer.ReduceToListOfListOfWords(),
    ]) 

    wer = jiwer.wer(
        reference, 
        hypothesis, 
        reference_transform=transformation, 
        hypothesis_transform=transformation
    )
    wer_rounded = Decimal(str(wer*100)).quantize(Decimal('.01'), rounding=ROUND_UP)
    return (wer_rounded)

def visualize_wer(r, h):
    r = regTokenize(r.lower())
    h = regTokenize(h.lower())
    
    d = np.zeros((len(r) + 1) * (len(h) + 1), dtype=np.uint16)
    d = d.reshape((len(r) + 1, len(h) + 1))
    for i in range(len(r) + 1):
        for j in range(len(h) + 1):
            if i == 0:
                d[0][j] = j
            elif j == 0:
                d[i][0] = i

    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                substitution = d[i - 1][j - 1] + 1
                insertion = d[i][j - 1] + 1
                deletion = d[i - 1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)
    result = float(d[len(r)][len(h)]) / len(r) * 100
    
    print_to_html(r, h, d)
    return result

def print_to_html(r, h, d):

    filename = "RESULT_diff.html"
    x = len(r)
    y = len(h)

    html_pre = '<html><body><head><meta charset="utf-8"></head>' \
           '<style>.g{background-color:#0080004d}.r{background-color:#ff00004d}.y{background-color:#ffa50099}</style><span class="y">Substitution</span> - <span class="r">Deletion</span> - <span class="g">Insertion</span><br><br>'
    with open(filename, "a+", encoding='utf-8') as f:
        f.write(html_pre)
    f.close()

    html = ''
    while True:
        if x == 0 or y == 0:
            break

        if r[x - 1] == h[y - 1]:
            x = x - 1
            y = y - 1
            html = '%s ' % h[y] + html
        elif d[x][y] == d[x - 1][y - 1] + 1:    # substitution
            x = x - 1
            y = y - 1
            html = '<span class="y">%s(%s)</span> ' % (h[y], r[x]) + html
        elif d[x][y] == d[x - 1][y] + 1:        # deletion
            x = x - 1
            html = '<span class="r">%s</span> ' % r[x] + html
        elif d[x][y] == d[x][y - 1] + 1:        # insertion
            y = y - 1
            html = '<span class="g">%s</span> ' % h[y] + html
        else:
            print('\nWe got an error.')
            break

    html += '</body></html>'

    with open(filename, 'a+', encoding='utf-8') as f:
        f.write(html)
    f.close()
    print("Printed comparison to: {0}".format(filename))

def regTokenize(text):
    words = WORD.findall(text)
    return words

#create visualisator
visualize_wer(reference, hypothesis)

#compute wer
wer_rounded = wer(reference, hypothesis)

print(wer_rounded)





