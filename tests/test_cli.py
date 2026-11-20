import re
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import TestCase

from givemes import main


def table_cells(line):
    return [cell.strip() for cell in line.strip("|").split("|")]


class CliTests(TestCase):
    def test_all_documented_targets(self):
        readme = Path(__file__).resolve().parents[1] / "README.md"
        rows = re.findall(r"^\| (\d+)명 \| ([\d, ]+) \|", readme.read_text(encoding="utf-8"), re.M)
        self.assertEqual([int(count) for count, _ in rows], list(range(2, 16)))
        grade_scores = {"S": 100, "A": 90, "B": 80, "C": 70}

        for count, row in rows:
            with self.subTest(count=count), redirect_stdout(output := StringIO()):
                main(["-n", count])
                header, divider, *result_rows = output.getvalue().splitlines()
                self.assertEqual(table_cells(header), ["등수", "점수", "업무40", "업무30", "업무20", "업무10"])
                self.assertTrue(all(set(cell) == {"-"} for cell in table_cells(divider)))
                targets = [int(score) for score in row.split(",")]
                self.assertEqual(len(result_rows), int(count))
                for rank, (result, target) in enumerate(zip(result_rows, targets, strict=True), 1):
                    rank_cell, score_cell, *tasks = table_cells(result)
                    self.assertEqual(rank_cell, f"{rank}등")
                    self.assertEqual(score_cell, str(target))
                    self.assertEqual(len(tasks), 4)
                    total = 0
                    for weight, cell in zip((40, 30, 20, 10), tasks, strict=True):
                        grade, score = cell.split(" / ")
                        self.assertEqual(int(score), grade_scores[grade])
                        total += weight * int(score)
                    self.assertEqual(total, 100 * target)

    def test_single_rank_prefers_higher_weight(self):
        with redirect_stdout(output := StringIO()):
            main(["-n", "10", "-r", "1"])
        self.assertEqual(output.getvalue().splitlines(), [
            "| 등수 | 점수 | 업무40  | 업무30  | 업무20  | 업무10  |",
            "|------|------|---------|---------|---------|---------|",
            "| 1등  | 98   | S / 100 | S / 100 | S / 100 | B / 80  |",
        ])

    def test_invalid_inputs(self):
        cases = [[], ["-r", "1"], ["-n"], ["-n", "1"], ["-n", "16"],
                 ["-n", "x"], ["-n", "2", "-r", "0"], ["-n", "2", "-r", "3"],
                 ["-n", "2", "-r", "1.5"]]
        for args in cases:
            with self.subTest(args=args), redirect_stderr(StringIO()), redirect_stdout(output := StringIO()):
                with self.assertRaises(SystemExit) as error:
                    main(args)
                self.assertEqual(error.exception.code, 2)
                self.assertEqual(output.getvalue(), "")
