from D2VModel import D2VModel, TaggedDocs
from random import randint

def main():
    #Directories of posts

    #directories and model names to test
    test_list = [[train_dir, "model_name"]]

    # ---- Vector Prediction Accuracy ----
    for test in test_list:
        #initialzie objects
        dm_mean = D2VModel("dmM_" + test[1])
        dm_concat = D2VModel("dmC_" + test[1])
        dbow = D2VModel("dbow_" + test[1])

        #create training corpus
        all_models = [dbow, dm_mean, dm_concat]


        #load models if an error during testing - training is slow
        #dm_mean.loadModel("./dmM_" + test[1] + ".model")
        # dm_concat.loadModel("./dmC_" + test[1] + ".model")
        # dbow.loadModel("./dbow_" + test[1] + ".model")
    

        #create training corpus
        for m in all_models:
             m.createCorpus(test[0])

        #create models
        dbow.createModel(dm=0, vector_size=300, negative=10, window=0, min_count=1, epochs=20, dm_concat=0, dm_mean=0)
        dm_mean.createModel(dm=1, vector_size=400, negative=5, window=5, min_count=1, epochs=20, dm_concat=0, dm_mean=1)
        dm_concat.createModel(dm=1, vector_size=300, negative=5, window=5, min_count=1, epochs=20, dm_concat=1, dm_mean=0)
        

        #train models
        for mo in all_models:
            mo.trainModel()
            mo.saveModel()
            

        #send to vector prediction accuracy analysis
        for mod in all_models:
            results = mod.vpa()
            print()
            print(mod.model)
            print("Correct:", results[0], "Out of:", results[1] )
            print("Min:", results[2], "Max:", results[3] )
            print("Mean:", results[4], "Median:", results[5] )
            print("1st Quartile:", results[6], "3rd Quartile:", results[7])
            print()



    # ---- End of Info Retieval ----



if __name__ == "__main__":
    main()