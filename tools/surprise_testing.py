import os
from surprise import NMF
from surprise import Dataset
from surprise import Reader
from surprise import get_dataset_dir
from surprise.model_selection import cross_validate

#path to dataset file
file_path = os.path.expanduser('~/src/project/outward.csv')

# define a reader object for our dataset
reader = Reader(sep=',')

#load data from dataset
data = Dataset.load_from_file(file_path, reader=reader)

# Use the famous SVD algorithm.
# sim_options = {'name': 'pearson_baseline', 'user_based': True}
algo = NMF()


# Run 5-fold cross-validation and print results.
cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)

# Evaluating RMSE, MAE of algorithm SVD on 5 split(s).

#                   Fold 1  Fold 2  Fold 3  Fold 4  Fold 5  Mean    Std
# RMSE (testset)    0.8860  0.8866  0.8824  0.8817  0.8847  0.8843  0.0019
# MAE (testset)     0.6981  0.7013  0.6970  0.6977  0.6999  0.6988  0.0016
# Fit time          14.28   14.15   16.29   14.59   14.52   14.77   0.78
# Test time         0.51    0.49    0.52    0.54    0.54    0.52    0.02

# Evaluating RMSE, MAE of algorithm SVDpp on 5 split(s).

#                   Fold 1  Fold 2  Fold 3  Fold 4  Fold 5  Mean    Std
# RMSE (testset)    0.8739  0.8776  0.8701  0.8737  0.8771  0.8745  0.0027
# MAE (testset)     0.6874  0.6916  0.6862  0.6859  0.6902  0.6883  0.0023
# Fit time          273.49  420.90  327.88  395.41  295.99  342.73  56.72
# Test time         5.73    18.88   8.13    5.16    5.26    8.63    5.24

# Evaluating RMSE, MAE of algorithm KNNBaseline on 5 split(s).

#                   Fold 1  Fold 2  Fold 3  Fold 4  Fold 5  Mean    Std
# RMSE (testset)    0.8782  0.8706  0.8766  0.8788  0.8813  0.8771  0.0036
# MAE (testset)     0.6894  0.6870  0.6880  0.6930  0.6937  0.6902  0.0027
# Fit time          3.42    3.61    3.55    3.61    3.56    3.55    0.07
# Test time         15.95   15.13   14.08   14.51   13.79   14.69   0.77

# Evaluating RMSE, MAE of algorithm KNNBaseline on 5 split(s), with sim_options = pearson_baseline and user_based = True

#                   Fold 1  Fold 2  Fold 3  Fold 4  Fold 5  Mean    Std
# RMSE (testset)    0.8789  0.8759  0.8757  0.8777  0.8798  0.8776  0.0016
# MAE (testset)     0.6883  0.6845  0.6847  0.6852  0.6849  0.6855  0.0014
# Fit time          9.33    9.94    10.56   10.56   10.01   10.08   0.46
# Test time         16.60   18.34   16.79   14.47   15.34   16.31   1.32

# Evaluating RMSE, MAE of algorithm KNNWithMeans on 5 split(s).

#                   Fold 1  Fold 2  Fold 3  Fold 4  Fold 5  Mean    Std
# RMSE (testset)    0.8786  0.8879  0.8850  0.8835  0.8868  0.8844  0.0032
# MAE (testset)     0.6853  0.6896  0.6879  0.6867  0.6898  0.6879  0.0017
# Fit time          10.61   13.43   10.87   22.45   13.79   14.23   4.31
# Test time         13.22   23.84   14.46   25.41   17.17   18.82   4.93

# Evaluating RMSE, MAE of algorithm NMF on 5 split(s).

#                   Fold 1  Fold 2  Fold 3  Fold 4  Fold 5  Mean    Std
# RMSE (testset)    0.9155  0.9173  0.9238  0.9248  0.9218  0.9206  0.0036
# MAE (testset)     0.7236  0.7237  0.7291  0.7299  0.7290  0.7271  0.0028
# Fit time          15.45   22.73   17.26   16.26   26.00   19.54   4.11
# Test time         0.64    0.56    0.42    0.42    1.14    0.64    0.27
