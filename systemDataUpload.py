import pickle

data = {
    "version" : {
        "botVersion" : "0.1.0.1_CloseBeta",
        "siteVersion" : "0.1.10_CloseBeta"
    },
}

with open("engine/data/systemData.db", "wb+") as file:
    pickle.dump(data, file)