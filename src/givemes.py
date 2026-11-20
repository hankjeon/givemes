import argparse
from itertools import product
from unicodedata import east_asian_width


TARGET_SCORES = {
    2: (94, 87),
    3: (95, 90, 85),
    4: (96, 92, 88, 84),
    5: (96, 93, 90, 87, 84),
    6: (97, 94, 91, 89, 86, 83),
    7: (97, 94, 92, 90, 88, 86, 83),
    8: (97, 95, 93, 91, 89, 87, 85, 83),
    9: (97, 96, 94, 92, 90, 88, 86, 84, 83),
    10: (98, 96, 94, 92, 91, 89, 88, 86, 84, 82),
    11: (98, 96, 94, 92, 91, 90, 89, 88, 86, 84, 82),
    12: (98, 96, 95, 93, 92, 91, 89, 88, 87, 85, 84, 82),
    13: (98, 96, 95, 94, 93, 91, 90, 89, 87, 86, 85, 84, 82),
    14: (98, 97, 95, 94, 93, 92, 91, 89, 88, 87, 86, 85, 83, 82),
    15: (98, 97, 96, 94, 93, 92, 91, 90, 89, 88, 87, 86, 84, 83, 82),
}

TASK_WEIGHTS = (40, 30, 20, 10)
GRADE_SCORES = (("S", 100), ("A", 90), ("B", 80), ("C", 70))


def task_grades(target: int) -> tuple[tuple[str, int], ...]:
    # 업무40에 C를 사용하지 않고, A 개수가 가장 많은 조합을 선택한다.
    # A 개수가 같으면 업무40부터 높은 배점을 먼저 탐색하므로 첫 일치 조합이 남는다.
    best: tuple[tuple[str, int], ...] | None = None
    best_a_count = -1
    for grades in product(GRADE_SCORES, repeat=len(TASK_WEIGHTS)):
        if grades[0][0] == "C":
            continue
        weighted_total = sum(weight * score for weight, (_, score) in zip(TASK_WEIGHTS, grades))
        if weighted_total != target * 100:
            continue
        a_count = sum(1 for grade, _ in grades if grade == "A")
        if a_count > best_a_count:
            best = grades
            best_a_count = a_count
    if best is None:
        raise ValueError(f"목표 점수 {target}점을 만드는 업무 배점 조합이 없습니다.")
    return best


def integer(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"정수를 입력하세요 ({value!r}).") from None


def table_line(cells: list[str], widths: tuple[int, ...]) -> str:
    padded = []
    for cell, width in zip(cells, widths, strict=True):
        display_width = sum(2 if east_asian_width(char) in {"W", "F"} else 1 for char in cell)
        padded.append(cell + " " * (width - display_width))
    return "| " + " | ".join(padded) + " |"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="givemes", usage="%(prog)s -n N [-r R]", description="등수별 업무 배점을 조회합니다."
    )
    parser.add_argument("-n", metavar="N", type=integer, help="평가 대상 인원 수 (필수, 2~15명)")
    parser.add_argument("-r", metavar="R", type=integer, help="조회할 등수 (생략하면 전체 등수)")
    args = parser.parse_args(argv)

    if args.n is None:
        parser.error("평가 대상 인원 수를 -n으로 지정하세요.")
    if args.n not in TARGET_SCORES:
        parser.error("-n은 2부터 15까지 입력하세요.")
    if args.r is not None and not 1 <= args.r <= args.n:
        parser.error(f"-r은 1부터 {args.n}까지 입력하세요.")

    ranks = range(1, args.n + 1) if args.r is None else (args.r,)
    headers = ["등수", "점수", *(f"업무{weight}" for weight in TASK_WEIGHTS)]
    widths = (4, 4, 7, 7, 7, 7)
    lines = [table_line(headers, widths), "|" + "|".join("-" * (width + 2) for width in widths) + "|"]
    for rank in ranks:
        target = TARGET_SCORES[args.n][rank - 1]
        grades = [f"{grade} / {score}" for grade, score in task_grades(target)]
        lines.append(table_line([f"{rank}등", str(target), *grades], widths))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
