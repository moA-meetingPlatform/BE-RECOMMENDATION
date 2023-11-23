from datetime import datetime, timedelta


def determine_meeting_status(meeting_id, meeting_df, now):
    """
    주어진 모임 ID에 해당하는 모임의 상태를 결정합니다.
    :param meeting_id: 모임 ID
    :param meeting_df: 모임 데이터 프레임
    :param now: 현재 시간 (datetime 객체)
    :return: 모임의 상태를 나타내는 문자열
    """
    meeting = meeting_df[meeting_df['id'] == meeting_id].iloc[0]
    meeting_datetime = meeting['meeting_datetime']
    current_participants = meeting['current_participants']
    max_participants = meeting['max_participants']

    if meeting_datetime > now and 3 <= current_participants < max_participants:
        return "모집중"
    elif meeting_datetime - timedelta(hours=3) < now and current_participants <= 2:
        return "모임취소"
    elif meeting_datetime > now and current_participants == max_participants:
        return "모집완료"
    elif meeting_datetime == now:
        return "모임시작"
    elif meeting_datetime + timedelta(hours=3) < now:
        return "모임종료"

    return ""
