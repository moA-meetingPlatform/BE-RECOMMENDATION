import threading  # Threading 모듈을 임포트
import api_response
from flask import Flask, request
from datetime import datetime
import uuid
from apscheduler.schedulers.background import BackgroundScheduler
import recommendation as rec
import database as db
import model
import logging

app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 데이터베이스 엔진과 훈련된 모델을 전역 변수로 저장
engine_participate, engine_category, engine_meeting = db.get_database_engines()
trained_model = None


# 모델을 비동기적으로 업데이트하는 함수
def update_model_async():
    global trained_model
    logging.info("모델 업데이트 시작")
    trained_model = model.train_collaborative_filtering_model(db.load_ratings_data(engine_participate))
    logging.info("모델 업데이트 완료")


def update_model():
    threading.Thread(target=update_model_async).start()


# # 스케줄러 설정 및 작업 추가
# scheduler = BackgroundScheduler()
# scheduler.add_job(func=update_model, trigger="interval", hours=24)
# scheduler.start()


# 추천 API 엔드포인트
@app.route('/recommend', methods=['POST'])
def recommend():
    logging.info("추천 API 호출 시작")
    data = request.get_json()
    user_uuid = data.get('user_uuid')
    if not user_uuid:
        return api_response.error_response("잘못된 요청: 'user_uuid'가 요청 JSON에 필요합니다.", 400)
    try:
        # UUID 형식으로 변환을 시도하여 유효성 확인
        uuid.UUID(user_uuid)
    except ValueError:
        # UUID 형식이 아닌 경우 오류 응답
        return api_response.error_response("존재하지 않는 회원입니다.", 400)

    now = datetime.now()

    try:
        # 데이터 로드
        user_category_data = db.load_user_category_data(engine_category)
        meeting_data = db.load_meeting_data(engine_meeting)
        meeting_category_list_data = db.load_meeting_category_list_data(engine_category)

        # 하이브리드 추천 실행
        top_3_recommendations = rec.hybrid_recommendation(
            user_uuid, trained_model, meeting_category_list_data,
            user_category_data, now, meeting_data
        )[:3]  # 상위 3개 추천 아이템 선택

        logging.info("추천 API 호출 완료")
        return api_response.success_response(top_3_recommendations, "성공")
    except ValueError as ve:
        logging.error(f"ValueError 발생: {str(ve)}")
        return api_response.error_response(str(ve), 400)
    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")
        return api_response.error_response("추천 중 오류 발생.", 500)

if __name__ == '__main__':
    # 모델 초기 업데이트
    update_model()
    app.run(debug=True, port=8751)
