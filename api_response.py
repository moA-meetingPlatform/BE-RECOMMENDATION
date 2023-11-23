# api_response.py

from flask import jsonify

def success_response(result, message="success"):
    """
    성공적인 API 호출에 대한 JSON 응답을 생성합니다.
    Args:
        result: API 호출의 결과 데이터.
        message (str): 성공 메시지.
    Returns:
        Flask 응답 객체로 결과 데이터와 성공 메시지를 포함합니다.
    """
    return jsonify({
        "result": result,
        "isSuccess": True,
        "message": message
    }), 200

def error_response(message, status_code):
    """
    오류 발생 시 JSON 응답을 생성합니다.
    Args:
        message (str): 표시할 오류 메시지.
        status_code (int): HTTP 상태 코드.
    Returns:
        Flask 응답 객체로 오류 메시지와 상태 코드를 포함합니다.
    """
    return jsonify({
        "result": None,
        "isSuccess": False,
        "message": message
    }), status_code