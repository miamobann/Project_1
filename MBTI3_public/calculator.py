"""
무역 적성 MBTI 진단 프로그램 (Trade-MBTI)
직무 점수 연산 및 결과 판정 모듈
"""

import os
import sys
from typing import Dict, Any, List, Tuple

# Streamlit.io 클라우드 배포 시 다른 폴더와의 모듈명 충돌 및 임포트 에러 방지 (최우선 경로 지정)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from questions import QUESTIONS, JOB_PROFILES


def calculate_trade_mbti(user_answers: Dict[int, int]) -> Dict[str, Any]:
    """
    사용자의 응답 점수를 바탕으로 6대 직무별 점수를 계산하고 최종 결과를 도출하는 함수

    :param user_answers: {질문_id: 선택한_점수(1~4)} 형태의 딕셔너리
    :return: 최종 판정 직무, 1/2위 직무 정보, 직무별 총점 및 백분율 딕셔너리
    """
    # 1. 직무별 기본 누적 점수, 가중치 2인 중요 문항 점수 누적, 최대 가능 점수 초기화
    scores: Dict[str, int] = {job_code: 0 for job_code in JOB_PROFILES.keys()}
    primary_weights_scores: Dict[str, int] = {job_code: 0 for job_code in JOB_PROFILES.keys()}
    max_scores: Dict[str, int] = {job_code: 0 for job_code in JOB_PROFILES.keys()}

    # 2. 문항별 가중치 누적 계산
    for q in QUESTIONS:
        q_id = q["id"]
        weights = q["weights"]
        user_score = user_answers.get(q_id, 1)  # 응답이 없으면 최하점 1점 기본 적용

        for job_code, weight in weights.items():
            # 응답 점수(1~4) * 해당 직무 가중치(1 또는 2)
            scores[job_code] += user_score * weight
            # 주 가중치(2) 문항의 순수 사용자 응답 점수 누적 (동점자 해결용)
            if weight == 2:
                primary_weights_scores[job_code] += user_score
            # 백분율 환산을 위한 최대 점수 (응답 최고점 4점 기준)
            max_scores[job_code] += 4 * weight

    # 3. 백분율(100점 만점 기준) 점수 환산
    percentage_scores: Dict[str, float] = {}
    for job_code, score in scores.items():
        max_possible = max_scores[job_code]
        percentage_scores[job_code] = round((score / max_possible) * 100, 1) if max_possible > 0 else 0.0

    # 4. 동점 발생 시 해결 규칙 적용 정렬
    # 정렬 기준 우선순위:
    #   1) 백분율 점수 (내림차순)
    #   2) 주 가중치(2)를 가진 질문들의 순수 응답 점수의 합 (내림차순)
    #   3) 직무 코드의 알파벳 역순 (일관된 순서 유지)
    sorted_jobs: List[Tuple[str, float]] = sorted(
        percentage_scores.items(),
        key=lambda item: (item[1], primary_weights_scores[item[0]], item[0]),
        reverse=True
    )

    # 1위(Primary) 및 2위(Secondary) 직무 도출
    primary_code = sorted_jobs[0][0]
    secondary_code = sorted_jobs[1][0]

    return {
        "primary": {
            "code": primary_code,
            "score": percentage_scores[primary_code],
            "raw_score": scores[primary_code],
            "primary_weight_score": primary_weights_scores[primary_code],
            "profile": JOB_PROFILES[primary_code]
        },
        "secondary": {
            "code": secondary_code,
            "score": percentage_scores[secondary_code],
            "raw_score": scores[secondary_code],
            "primary_weight_score": primary_weights_scores[secondary_code],
            "profile": JOB_PROFILES[secondary_code]
        },
        "all_scores": percentage_scores,
        "raw_scores": scores,
        "primary_weights_scores": primary_weights_scores,
        "ranking": sorted_jobs
    }


if __name__ == "__main__":
    # 로직 단독 테스트용 가상 응답 데이터 (모든 문항에 3점 응답 가정)
    test_answers = {q["id"]: 3 for q in QUESTIONS}
    result = calculate_trade_mbti(test_answers)
    print("=== 단독 테스트 결과 ===")
    print(f"1순위 직무: {result['primary']['profile']['name']} ({result['primary']['score']}%)")
    print(f"2순위 직무: {result['secondary']['profile']['name']} ({result['secondary']['score']}%)")
    print(f"전체 점수 분포: {result['all_scores']}")
