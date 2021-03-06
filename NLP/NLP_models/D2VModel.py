import gensim
from os import listdir
from random import randint
from shutil import copyfile
from multiprocessing import cpu_count
from smart_open import smart_open
import numpy as np
from scipy import spatial

"""
Gensim Doc2Vec needs model training data in an iterator object
- modified to iterate through documents instead of a list
"""
class TaggedDocs():
    def __init__(self, data_dir, tokens_only=False):
        """
        docData = the raw contents string of the documents 
        """
        self.data_dir = data_dir
        self.filenames = [file for file in listdir(data_dir) if file.endswith('.txt')]
        self.tokens_only = tokens_only

    def __iter__(self):

        #read the corpus - the collection or set of documents
        #Documents are in body/ directory of stackoverflow input
        #gives it new integer tag/label to save space in case of large filenames

        for i, filename in enumerate(self.filenames):
            file = smart_open(self.data_dir + filename, 'rb')
            doc = file.read().decode("utf-8") #get past unicode
            file.close()

                       
            #gensim has built in tokenizer - remove punctuation, set to lowercase, split into list of words...
            if self.tokens_only:
                yield gensim.utils.simple_preprocess(doc)

            else:
                yield gensim.models.doc2vec.TaggedDocument(words=gensim.utils.simple_preprocess(doc),tags=[i])


    ## With the current gensim implementation, all label vectors are stored separately in RAM.
    ## they report being able to run 2 million different sentences no problem, however


class D2VModel():
    def __init__(self, model_name):
        self.model_name = model_name
        self.cores = cpu_count()
        assert gensim.models.doc2vec.FAST_VERSION > -1


        """
        Instructions:
        create the corpus
        build the model
        train model
        save model
        """

    def createCorpus(self, directory, tokens_only=False):
        #TaggedDocs acts as a iterator
        print()
        print("Creating", self.model_name, "Corpus...")
        if tokens_only: #testing, not training. Doesn't use tags.
            corpus = TaggedDocs(directory, True)
        else:
            corpus = TaggedDocs(directory) 

        self.corpus = corpus
        print("Corpus Created")
        print()

    def createModel(self, dm=1, vector_size=300, negative=5, window=5, min_count=2, epochs=20, dm_concat=1, dm_mean=0):
        print()
        print("Creating", self.model_name, "Model...")
        #create doc2vec model
        model = gensim.models.doc2vec.Doc2Vec(dm=dm, vector_size=vector_size, negative=negative, window=window, min_count=min_count, epochs=epochs, dm_concat=dm_concat, dm_mean=dm_mean, workers=self.cores)
        self.model = model
        print("Model", str(model), "Created")
        print()

    def trainModel(self):
        model = self.model
        print()
        print("Training Model ", self.model_name, str(model), "...")

        #build vocabulary (dictionary accessible via mode.wv.vocab of all unique words extracted 
        #from the training corpus) with the frequency counts (model.wv.vocan['word'].count)
        model.build_vocab(self.corpus)

        #Train
        model.train(self.corpus, total_examples=model.corpus_count, epochs=model.epochs)

        self.model = model
        print("Model Trained")
        print()

    def saveModel(self, doneTraining=True):
        #save model. Set doneTraining = False if you want to keep training
        print()
        print("Saving Model ", self.model_name, "...")
        self.model.save(self.model_name + ".model")

        if doneTraining: #save space, RAM
            self.model.delete_temporary_training_data(keep_doctags_vectors=True, keep_inference=True)
            print("Model Saved. Cannot be trained further.")
        else:
            print("Model Saved. Can still be trained.")
        
        print()

    def loadModel(self, filename):
        # LOAD
        print()
        print("Loading Model ", filename, "...")
        model_loaded = gensim.models.Doc2Vec.load(filename)
        print("Model Loaded")
        print()

        self.model = model_loaded


    def infoRet(self, test_corpus1, test_corpus2):
        """
        Information Retrieval Test. Can the model accuratly predict 
        whether two documents are similar or not in comparison to another?
        @params - test_corpus2 is the corpus that needs twice as many documents
        @return - number of correct times Eudcildean and cosine distance found the
                  two documents from the same topic were the most similar
                - total times tested
        """
        print()
        print("Starting Information Retrieval on", self.model_name, str(self.model))

        model = self.model
        used1 = []
        used2 = []
        correct1 = 0
        correct2 = 0
        count = 0
        n1 = len(test_corpus1.filenames)
        n2 = len(test_corpus2.filenames)

        x = randint(0, n1-1) #randint is inclusive
        y1 = randint(0, n2-1)
        y2 = randint(0, n2-1)
        
        #cant use indexing on an iterator, have to add TaggedDocs to a list
        print("Creating first test corpus list")
        tc1 = list(test_corpus1)
        print("Creating second test corpus list")
        tc2 = list(test_corpus2)

        #find minimum number of times to run test
        min_ = min(n1, (n2)//2)

        #INFER A VECTOR without having to retrain
        #use random documents from the corpuses
        print("Calculating inferred_vectors...")
        for i in range(min_):
            while x in used1:
                x = randint(0, n1-1)

            used1.append(x)

            while y1 in used2:
                y1 = randint(0, n2-1)

            used2.append(y1)

            while y2 in used2:
                y2 = randint(0, n2-1)

            used2.append(y2)

            x_vector = model.infer_vector(tc1[x]) #only tokens (no tags) don't have to call .words
            y1_vector = model.infer_vector(tc2[y1])
            y2_vector = model.infer_vector(tc2[y2])

            #Eucildean Distance:y1 and y2 vectors should be closer in distance to each other than x
            xy1 = np.linalg.norm(x_vector - y1_vector)
            xy2 = np.linalg.norm(x_vector - y2_vector)
            y1y2 = np.linalg.norm(y1_vector - y2_vector)

            if min(xy1, xy2, y1y2) == y1y2:
                correct1 += 1

            #cosine similarity - may be better for vectors with different directions/magnitudes
            xy1 = spatial.distance.cosine(x_vector, y1_vector)
            xy2 = spatial.distance.cosine(x_vector, y2_vector)
            y1y2 = spatial.distance.cosine(y1_vector, y2_vector)

            if max(xy1, xy2, y1y2) == y1y2: #values -1 to 1, 1 = the same
                correct2 += 1

            count += 1

        return (correct1, correct2, count)


    def vpa(self):
        """
        Vector Prediction Accuracy
        Is the model able to infer a trained document's vector as 
        the most similar to its trained vector self?
        Checks every document in the corpus that was trained --> smaller corpus
        @return - number of correct tiems the cosine similarity found the inferred
                  vector from same document was the most similar to the trained
                  vector corresponding to that document within the model
                - total times tested
                - min, max, mean, median, first and third quartiles
        """
        print()
        print("Starting Vector Prediction Accuracy on", self.model_name, str(self.model))

        model = self.model
        corpus = list(self.corpus) #gets every TaggedDocument out of the iterator.
        results = []
        correct = 0
        ap = results.append
        for doc in corpus:
            inferred_vector = model.infer_vector(doc.words) #have to call .words on TaggedDoc with words (tokens) and tags(labels)
            similar_vector = model.docvecs.most_similar([inferred_vector], topn=1)
            ap(similar_vector[0][1]) 

            if similar_vector[0][0] == doc.tags[0]: #tag of most similar vector should match tag of the document in the corpus
                correct += 1

        npArray = np.array(results)
        min_ = min(results) #smallest cosine simularity
        max_ = max(results) #largest = the most similar
        mean_ = np.mean(npArray, dtype=np.float64) #float64 more accurate
        median_ = np.percentile(npArray, 50)
        firstQ = np.percentile(npArray, 25)
        thirdQ = np.percentile(npArray, 75)



        return (correct, len(results), min_, max_, mean_, median_, firstQ, thirdQ)