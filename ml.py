import os
from surprise import KNNBaseline
from surprise import Dataset
from surprise import Reader
from surprise import get_dataset_dir


def get_nearest_neighbors(user_id):
    #path to dataset file
    file_path = os.path.expanduser('~/src/project/outward.csv')

    # define a reader object for our dataset
    reader = Reader(sep=',')

    #load data from dataset
    data = Dataset.load_from_file(file_path, reader=reader)

    #Train algorithm on dataset
    trainset = data.build_full_trainset()
    sim_options = {'name': 'pearson_baseline', 'user_based': True}
    algo = KNNBaseline(sim_options=sim_options)
    algo.fit(trainset)

    #Retrieve inner id of the user in question
    user_inner_id = algo.trainset.to_inner_uid(str(user_id))

    #Retrieve inner ids of the nearest neighbors of user
    user_neighbors = algo.get_neighbors(user_inner_id, k=10)

    #Convert inner ids of the neighbors into raw user ids
    user_neighbors = (algo.trainset.to_raw_uid(inner_id)
                      for inner_id in user_neighbors)

    neighbors_lst = []
    print()
    print(f'The 10 nearest neighbors of {user_id} are:')
    for user in user_neighbors:
        print(user)
        neighbors_lst.append(user)

    return neighbors_lst










# pred = algo.predict(uid, bid, verbose=True)
# pred is <class 'surprise.prediction_algorithms.predictions.Prediction'>