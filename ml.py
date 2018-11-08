import os
# from collections import defaultdict
from surprise import KNNBaseline
from surprise import Dataset
# from surprise import accuracy
from surprise import Reader
from surprise import get_dataset_dir
# from surprise.model_selection import train_test_split


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

user_id = 2
#Retrieve inner id of the user in question
user_inner_id = algo.trainset.to_inner_uid(str(user_id))

#Retrieve inner ids of the nearest neighbors of user
user_neighbors = algo.get_neighbors(user_inner_id, k=10)

#Convert inner ids of the neighbors into names
user_neighbors = (algo.trainset.to_raw_uid(inner_id)
                  for inner_id in user_neighbors)

print()
print(f'The 10 nearest neighbors of {user_id} are:')
for user in user_neighbors:
    print(user)

""" 
Pre this calculation:
take in ISBNs for five books
query database for matching book_ids
create user_id, 5 rating_ids that have new user_id and each book_id and scores of 5
generate ratings csv file that has new user's ratings! (was using static data file previously)
pass new ratings file to Surprise !!!Memory limitations!!! It will not currently process the 6M ratings file:
    how to split on the fly OR how to generate partial set that still contains new user's ratings?

Get neighbors: ////The process above ////

After this process:
user_neighbors each have books they have reviewed positively (let's assume 5/5)
create one dictionary of book_ids from user_neighbors, (hopefully some books recommended by multiple neighbors),
get the five most popular book_ids
query database for title, author, isbn associated with those book_ids
display list (eventually rich content based on API call with ISBN); 
but for now list pf 5 books with title, author ISBN from database

"""








# uid = str(1)
# bid = str(5556)

# pred = algo.predict(uid, bid, verbose=True)
# pred is <class 'surprise.prediction_algorithms.predictions.Prediction'>