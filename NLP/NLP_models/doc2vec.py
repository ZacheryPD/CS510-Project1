import gensim
from os import listdir
import random
from docToExcel import docToExcel

"""
Gensim Doc2Vec needs model training data in an iterator object
- modified to iterate through documents instead of a list
"""
class TaggedDocs(object):
    def __init__(self, data_dir):
        """
        docData = the raw contents string of the documents 
        """
        self.data_dir = data_dir
        self.filenames = [file for file in listdir(data_dir + 'body/') if file.endswith('.txt')]
        
    def __iter__(self):

        #read the corpus - the collection or set of documents
        #Documents are in body/ directory of stackoverflow input
        #gives it new integer tag/label to save space in case of large filenames

        for i, filename in enumerate(self.filenames):
            file = open(self.data_dir + 'body/' + filename, 'r')
            doc = file.read()  #get string of entire document
            file.close()
                       
            #gensim has built in tokenizer - remove punctuation, set to lowercase, split into list of words...
            yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(doc),tags=[i])


    ## With the current gensim implementation, all label vectors are stored separately in RAM.
    ## they report being able to run 2 million different sentences no problem, however


def main():
    test_dir = ''
    train_dir = ''
    model_name = ''

    
    #First, get corpus iterator
    train_corpus = TaggedDocs(train_dir)

    #create do2vec model. dm=1 is for DM model
    model = gensim.models.doc2vec.Doc2Vec(dm=1, vector_size=300, window=10, min_count=2, epochs=20)

    #build vocabulary (dictionary accessible via mode.wv.vocab of all unique words extracted 
    #from the training corpus) with the frequency counts (model.wv.vocan['word'].count)
    model.build_vocab(train_corpus)

    #Train
    model.train(train_corpus, total_examples=model.corpus_count, epochs=model.epochs)

    #save model 
    print()
    print("Saving Model..")
    model.save(model_name)
    print("Model Saved")
    print()

     # LOAD
    #model_loaded = doc2vec.Doc2Vec.load('model.doc2vec')


    #to compare:

    #INFER A VECTOR without having to retrain via cosine similarity
    #vector = model.infer_vector(['words', 'in', 'a', 'list'])

    #you can do this with already trained data:
    #vector = model.infer_vector(train_corpus[id].words) where id is the given tag

    #MOST SIMILAR - find the most similar vector in the trained corpus to the given one
    # similar = model.docvecs.most_similar([vector], topn=1)  change topn for number wanted to be returned
    #similar[index] will return data about the vector


    ## TEST RANDOM NEW DOC ##
    """
    doc_id = random.randint(0, len(test_corpus)-1)
    inferred_vector = model.infer_vector(test_corpus[doc_id])
    similar = model.docvecs.most_similar([inferred_vector], topn=1)
    similar[index]
    """

    ## TEST RANDOM TRAINED DOC ##
    """
    doc_id = random.randint(0, len(train_corpus)-1)
    inferred_vector = model.infer_vector(train_corpus[doc_id])
    similar = model.docvecs.most_similar([inferred_vector], topn=1)
    similar[index]
    """

    docToExcel(inferred_vectors, similar_vectors, title)



if __name__ == "__main__":
	main()