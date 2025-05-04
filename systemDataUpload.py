import pickle

data = {
    "version" : {
        "botVersion" : "0.0.4_DeveloperOnly",
        "siteVersion" : "0.1.9_CloseBeta"
    },
}

with open("engine/systemData.db", "wb+") as file:
    pickle.dump(data, file)