import sys
import os
import hashlib
import subprocess
import collections
import glob

import json
import tarfile
import io
import re
import Downloader
import PreProcess
import tokenizeText
from pathlib import Path
import pickle as pkl

paperCount = 0
dm_single_close_quote = '\u2019' # unicode
dm_double_close_quote = '\u201d'
dm__fi_unicode='\ufb01'
dm_ffi_unicode='\ufb03'
# acceptable ways to end a sentence
END_TOKENS = ['.', '!', '?']

#def tokenize_stories(category= 'cat:cs.LG', numPapers = 50):
    #Downloads the papers you want
#    corpusAbstracts = Downloader.main('cat:cs.LG', numPapers)
    #Preprocess,Tokenize,Save them
#    PreProcess.main(corpusAbstracts,r'C:\Users\Al\Documents\ByteSizeArxiv\library')
#    tokenizeText.main()
    #tokenizedPapersDir = "/library/toked" 

def convert_txt_json(fileName):
	# loop over all story files in directory
	#for file in os.listdir(r'/Users/neerajsudhakar/Documents/ByteSizeArxixv-master/library/toToken/0001004v1.txt'):
    #theFile = r'/Users/neerajsudhakar/Desktop/0001004v1.txt'
    theFile = fileName
    # empty lists for each story
    #abstract_lines = list()
    #article_lines = list()
    with open(theFile,'r' , encoding = "utf8") as f:
        thePaper = f.read()
        theAbs , theArt = thePaper.split('\n#####\n')
        abstract_lines= theAbs.split(".")
        article_lines = theArt.split(".")

        """
        for line in 
        hashfound = False
        for line in f.readlines():
            line=line.rstrip('\n').replace(dm_single_close_quote, '\'').replace(dm_double_close_quote, '\"').replace(dm__fi_unicode, 'fi').replace(dm_ffi_unicode, 'ffi')
            if line == '#####':
                hashfound = True
            elif hashfound:
                article_lines.append(line)
            else:
                abstract_lines.append(line)
        """

    fileid=os.path.basename(theFile)
    fileid=fileid.replace('.txt', '')
    newid= fileid + '.json'
    theJson = os.path.join(os.path.dirname(theFile),newid)
		
    # make json data
    js_example = {}
    js_example['id'] = fileid
    js_example['article'] = article_lines
    js_example['abstract'] = abstract_lines

    #with open(theJson , 'w') as outfile:
    #    json.dump(js_example, outfile)
    js_serialized = json.dumps(js_example, indent=4).encode()
    save_file = io.BytesIO(js_serialized)
    return article_lines,abstract_lines,js_serialized,save_file

def makeLibrary(direct):
    library = []
    theFiles = glob.glob((direct+"\*.txt"))
    for fileName in theFiles:
        #Get the names of the files from the paths
        name = fileName.rsplit('\\',1)[1]
        name = re.sub(r'\n','',name)
        library.append(name)
    return library

def write_to_tar(direct, out_file, makevocab=True):
    paperCount =0
    """Reads the tokenized .txt files corresponding to the urls listed in the
       library and writes them to a out_file.
    """
    #get a list of papers in the library
    library = makeLibrary(direct)

    if makevocab:
        vocab_counter = collections.Counter()

    open(out_file, 'a').close()
    with tarfile.open(out_file, 'w') as writer:
        for idx, line in enumerate(library):
            #activeTXT = tokenizedPapersDir + '/' + line + '.txt'
            activeTXT = Path(direct) / line
            # Get the strings to write to .bin file and save the JSON
            article_sents, abstract_sents,js_serialized,save_file = convert_txt_json(activeTXT)
            tar_info = tarfile.TarInfo('{}/{}.json'.format(
                os.path.basename(out_file).replace('.tar', ''), idx))
            tar_info.size = len(js_serialized)
            writer.addfile(tar_info, save_file)

            # Write the vocab to file, if applicable
            if makevocab:
                art_tokens = ' '.join(article_sents).split()
                abs_tokens = ' '.join(abstract_sents).split()
                tokens = art_tokens + abs_tokens
                tokens = [t.strip() for t in tokens] # strip
                tokens = [t for t in tokens if t != ""] # remove empty
                vocab_counter.update(tokens)

    print("Finished writing file {}\n".format(out_file))

    # write vocab to file
    if makevocab:
        print (Path(os.path.basename(out_file)))
        print("Writing vocab file...")
        theVocabPath= (Path(os.path.dirname(out_file)) / "vocab_cnt.pkl")
        with open(theVocabPath,'wb') as vocab_file:
            pkl.dump(vocab_counter, vocab_file)
        print("Finished writing vocab file")



if __name__ == '__main__':
    #papersDir = sys.argv[1]

    # Run stanford tokenizer on both stories dirs,
    # outputting to tokenized stories directories
    #tokenize_stories(cnn_stories_dir, tokenizedPapers)
    #tokenize_stories(dm_stories_dir, dm_tokenized_stories_dir)

    # Read the tokenized stories, do a little postprocessing
    # then write to bin files
    testTokenized = r'C:\Users\Al\Documents\ByteSizeArxiv\library\Finished\test'
    valTokenized = r'C:\Users\Al\Documents\ByteSizeArxiv\library\Finished\val'
    trainTokenized = r'C:\Users\Al\Documents\ByteSizeArxiv\library\Finished\train'
    write_to_tar(testTokenized, r'C:\Users\Al\Documents\ByteSizeArxiv\library\Finished\test\test.tar',makevocab=True)
    write_to_tar(valTokenized, r'C:\Users\Al\Documents\ByteSizeArxiv\library\Finished\val\val.tar',makevocab=True)
    write_to_tar(trainTokenized, r'C:\Users\Al\Documents\ByteSizeArxiv\library\Finished\train\train.tar',makevocab=True)
