from surprise import Dataset, Reader, SVD

def train_collaborative_filtering_model(ratings_df):
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(ratings_df[['reviewer_user_uuid', 'meeting_id', 'rating']], reader)
    trainset = data.build_full_trainset()
    model = SVD(n_epochs=10)
    model.fit(trainset)
    return model
