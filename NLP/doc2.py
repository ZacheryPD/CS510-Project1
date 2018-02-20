from gensim.models import doc2vec
from TaggedDocs import TaggedDocs

##get txt documents from folder 'input'
from os import listdir
from os.path import isfile, join


def main():

    path_to_input = "input/"
    # the file names of the txt documents kept in a list
    docLabels = []
    docLabels = [file for file in listdir(path_to_input) if file.endswith('.txt')]


    # load text out of .txt documents to list - may have to change if content is too large
    data = []
    for doc in docLabels:
        file = open(path_to_input + doc, 'r')
        data.append(file.read())

        file.close()


    # TRAINING

    #the iterator object produced from the TaggedDocs object
    #based on an older version. Can maybe fixed to read data from disk
    it = TaggedDocs(data, docLabels)

    #model using a fixed model rate given by gensim
    #model = doc2vec.Doc2Vec(size=300, window=10, min_count=5, workers=11, alpha=0.025, min_alpha=0.025)
    # NEW VERSION

    #it = tagged documents iterable
    model = doc2vec.Doc2Vec(it, size=300, window=10, min_count=5, workers=11,  alpha=0.025, min_alpha=0.025)
    

    #before training, needs to build vocab
    #model.build_vocab(it)

    #Gensim found that training over the data several times works better
    for epoch in range(10):
        model.train(it)
        model.alpha -= 0.002 # decrease the learning rate over time
        model.min_alpha = model.alpha # fix the learning rate, no decay
        model.train(it)


    # SAVE
    model.save('model.doc2vec')

    # LOAD
    model_loaded = doc2vec.Doc2Vec.load('model.doc2vec')




if __name__ == "__main__":
    main()