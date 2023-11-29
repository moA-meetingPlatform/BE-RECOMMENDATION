from database import convert_bytearray_to_string  # 데이터베이스 모듈에서 문자열 변환 함수 임포트
from utils import determine_meeting_status  # 유틸리티 모듈에서 미팅 상태 결정 함수 임포트
import logging  # 로깅 모듈 임포트


def hybrid_recommendation(user_uuid, model, meeting_category_list_df, user_profiles, now, meeting_df):
    try:
        # 로깅 시작 메시지
        logging.info("Start Hybrid Recommendation")

        # 사용자 프로필에서 UUID를 문자열로 변환 (바이트 배열인 경우)
        user_profiles['user_uuid'] = user_profiles['user_uuid'].apply(
            lambda x: convert_bytearray_to_string(x) if isinstance(x, bytearray) else x
        )

        # 사용자별 관심 카테고리 목록을 그룹화
        user_profiles_grouped = user_profiles.groupby('user_uuid')['user_category_id'].apply(list).reset_index()

        # 활성화된(=enable 컬럼이 1인) 미팅 필터링
        enabled_meetings = meeting_category_list_df[meeting_category_list_df['enable'] == 1]

        scores = []  # 각 미팅의 점수를 저장할 리스트

        # 활성화된 미팅에 대해 점수 계산
        for _, meeting in enabled_meetings.iterrows():
            meeting_id = meeting['meeting_id']
            category_id = meeting['sub_category_id']
            meeting_status = determine_meeting_status(meeting_id, meeting_df, now)

            # 미팅 상태가 '모집중'이나 '모집완료'인 경우에만 계산
            if meeting_status in ["모집중", "모집완료"]:
                user_categories = \
                    user_profiles_grouped[user_profiles_grouped['user_uuid'] == user_uuid]['user_category_id'].iloc[0]

                # 콘텐츠 기반 필터링 점수 계산
                cbf_score = 1.0 if category_id in user_categories else 0.0

                # 협업 필터링 점수 계산
                cf_score = model.predict(user_uuid, meeting_id).est

                # 하이브리드 점수 계산 (CBF와 CF의 평균)
                hybrid_score = (cbf_score + cf_score) / 2
                scores.append((meeting_id, hybrid_score))

        # 점수가 가장 높은 상위 3개 미팅 추출
        top_3_meetings = sorted(scores, key=lambda x: x[1], reverse=True)[:3]

        # 로깅 완료 메시지
        logging.info("Hybrid recommendation complete")

        # 상위 3개 미팅의 ID 반환
        return [meeting_id for meeting_id, _ in top_3_meetings]

    except (KeyError, ValueError) as e:
        # 오류 발생 시 로깅 후 ValueError 발생
        logging.error(f"Error during recommendation: {str(e)}")
        raise ValueError(f"This user does not exist.")
