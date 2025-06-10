import pickle

data = {
    "version" : {
        "botVersion" : "1.0.0_preRelease0 (1001)",
        "siteVersion" : "1.0.0_preRelease0 (1001)"
    },
}

with open("engine/data/systemData.db", "wb+") as file:
    pickle.dump(data, file)