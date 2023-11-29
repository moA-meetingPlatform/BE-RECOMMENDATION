from surprise import Dataset, Reader, SVD  # Surprise 라이브러리의 필요한 클래스 임포트


def train_collaborative_filtering_model(ratings_df):
    # SVD(Singular Value Decomposition) 기반의 협업 필터링 모델을 훈련하는 함수

    reader = Reader(rating_scale=(1, 5))  # 평점 스케일을 설정하여 Reader 객체 생성
    # 데이터프레임에서 협업 필터링 데이터셋 생성
    # 'reviewer_user_uuid', 'meeting_id', 'rating' 컬럼을 사용
    data = Dataset.load_from_df(ratings_df[['reviewer_user_uuid', 'meeting_id', 'rating']], reader)

    trainset = data.build_full_trainset()  # 전체 데이터를 훈련 세트로 변환
    model = SVD(n_epochs=10)  # SVD 모델 인스턴스 생성, 에포크 수를 10으로 설정
    model.fit(trainset)  # 모델을 훈련 세트에 피팅

    return model  # 훈련된 모델 반환
