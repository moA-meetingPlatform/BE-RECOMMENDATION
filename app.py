import threading  # Threading 모듈 임포트, 멀티 스레딩을 위해 사용
import api_response  # 사용자 정의 api_response 모듈 임포트
from flask import Flask, request  # Flask 웹 프레임워크와 요청 객체 임포트
from datetime import datetime  # 날짜 및 시간 관련 기능 제공
import uuid  # UUID 관련 기능 제공
# from apscheduler.schedulers.background import BackgroundScheduler  # 배경 작업 스케줄러, 현재는 사용하지 않음
import recommendation as rec  # 추천 로직이 담긴 사용자 정의 모듈 임포트
import database as db  # 데이터베이스 관련 기능이 담긴 사용자 정의 모듈 임포트
import model  # ML 모델 관련 기능이 담긴 사용자 정의 모듈 임포트
import logging  # 로깅 기능 제공

app = Flask(__name__)  # Flask 애플리케이션 인스턴스 생성

# 로깅 기본 설정 (INFO 수준의 로그 출력)
logging.basicConfig(level=logging.INFO)

# 데이터베이스 연결 엔진과 모델을 전역 변수로 초기화
engine_participate, engine_category, engine_meeting = db.get_database_engines()
trained_model = None

# 모델을 비동기 방식으로 업데이트하는 함수 정의
def update_model_async():
    global trained_model
    logging.info("모델 업데이트 시작")
    trained_model = model.train_collaborative_filtering_model(db.load_ratings_data(engine_participate))
    logging.info("모델 업데이트 완료")

def update_model():
    threading.Thread(target=update_model_async).start()  # 별도의 스레드에서 모델 업데이트 함수 실행

# 추천 API 엔드포인트 설정
@app.route('/api/v1/recommendation', methods=['POST'])
def recommend():
    logging.info("추천 API 호출 시작")
    data = request.get_json()  # 요청 데이터를 JSON 형태로 파싱
    user_uuid = data.get('user_uuid')  # user_uuid 획득
    if not user_uuid:
        return api_response.error_response("잘못된 요청: 'user_uuid'가 요청 JSON에 필요합니다.", 400)
    try:
        uuid.UUID(user_uuid)  # UUID 유효성 검사
    except ValueError:
        return api_response.error_response("존재하지 않는 회원입니다.", 400)

    now = datetime.now()

    try:
        user_category_data = db.load_user_category_data(engine_category)
        meeting_data = db.load_meeting_data(engine_meeting)
        meeting_category_list_data = db.load_meeting_category_list_data(engine_category)

        top_3_recommendations = rec.hybrid_recommendation(
            user_uuid, trained_model, meeting_category_list_data,
            user_category_data, now, meeting_data
        )

        logging.info("추천 API 호출 완료")
        return api_response.success_response(top_3_recommendations, "성공")
    except ValueError as ve:
        logging.error(f"ValueError 발생: {str(ve)}")
        return api_response.error_response(str(ve), 400)
    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")
        return api_response.error_response("추천 중 오류 발생.", 500)

@app.route('/api/v1/recommendation/test', methods=['GET'])
def recommendation_test():
    print("test")  # 테스트 메시지 출력
    return "Success"  # 성공 메시지 반환

if __name__ == '__main__':
    update_model()  # 애플리케이션 시작 시 모델 업데이트
    app.run(debug=True, host="0.0.0.0", port=8751)  # 애플리케이션을 지정
