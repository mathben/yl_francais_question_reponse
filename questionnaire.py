#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).
import argparse
import logging
import csv
from colorama import Fore, Style

EXPECTED_HEADERS_CSV = "Question,Réponse,Choix A,Choix B,Choix C,Choix D,Explication"


def main():
    parser = argparse.ArgumentParser(description="Generate your vaccination QR code.")
    parser.add_argument("-d", "--database", type=str, help="Your database filename path",
                        default="./database.csv")
    parser.add_argument("--response_char", type=str, help="Your character to start the answer, 0, 1 or a (A)",
                        default="a")
    parser.add_argument("-q", "--question", type=int, help="Question index to begin, start at 1 by default", default=1)
    parser.add_argument("--mot_souligne", type=str,
                        help="1 character, when detect 2 times this char, underline words when show question/answer",
                        default="X")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="verbose output")
    args = parser.parse_args()

    qp = QuestionParser(args)
    qp.start()


class QuestionParser:
    def __init__(self, parser):
        self.parser = parser

    def start(self):
        # x = input("Input Your Name")
        # print(x)

        with open(self.parser.database) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                    headers = ",".join(row)
                    if headers != EXPECTED_HEADERS_CSV:
                        raise Exception(f"Wrong headers in your csv file. Need '{EXPECTED_HEADERS_CSV}'")
                else:
                    line_count += 1
                    if self.parser.question >= line_count:
                        continue
                    question_number = line_count - 1
                    print(f'{Fore.GREEN}Question {question_number}{Style.RESET_ALL}')
                    print(f'{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
            print(f'Questionnaire complété!')


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception(e)
