#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).
import argparse
import logging
import csv
from colorama import Fore, Style
import signal
import time

EXPECTED_HEADERS_CSV = "Question,Réponse,Choix A,Choix B,Choix C,Choix D,Explication"
CSV_COLON_LENGTH = 7


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
    # parser.add_argument("-v", "--verbose", action="store_true",
    #                     help="verbose output")
    args = parser.parse_args()

    qp = QuestionParser(args)

    # Setup signal handler to stop questionnaire
    def handler(signum, frame):
        res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
        if res == 'y':
            qp.print_result(exit=True)
            exit(1)

    signal.signal(signal.SIGINT, handler)

    qp.start()


class QuestionParser:
    def __init__(self, parser):
        self.parser = parser
        self._question_number = 0

    def print_result(self, exit=False):
        print("résultat")
        if exit:
            print("Commande pour recontinuer :")
            print(f"python3 questionnaire.py -q {self._question_number}")

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
                    self._question_number = line_count - 1

                    if len(row) != CSV_COLON_LENGTH:
                        raise Exception(
                            f"La question {self._question_number} ne contient pas {CSV_COLON_LENGTH} colonnes, fichier csv mal formaté.")
                    print(f'{Fore.GREEN}Question {self._question_number}{Style.RESET_ALL}')
                    print(row[0])
                    print()
                    self.print_response(row, 3)
                    self.print_response(row, 4)
                    self.print_response(row, 5)
                    self.print_response(row, 6)
                    # time.sleep(3)
                    print()
            print(f'Questionnaire complété!')
            self.print_result()

    def print_response(self, row, no):
        # mot_souligne
        response_char = no - 3
        transform_response_char = chr(ord(self.parser.response_char) + response_char).upper()
        print(f'\t{transform_response_char} - {row[no]}')


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception(e)
