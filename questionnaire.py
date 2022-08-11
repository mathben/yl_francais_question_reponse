#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).
import argparse
import logging
import csv
from colorama import Fore, Style
import signal
import os
import time

EXPECTED_HEADERS_CSV = "Question,Réponse,Choix A,Choix B,Choix C,Choix D,Explication"
CSV_COLON_LENGTH = 7


def main():
    parser = argparse.ArgumentParser(description="Generate your vaccination QR code.")
    parser.add_argument("-d", "--database", type=str, help="Your database filename path",
                        default="./database.csv")
    parser.add_argument("--response_char", type=str,
                        help="BRISÉ, ne pas changer le paramètre. Le caractère qui représente la réponse. Suggestion : 0, 1, a. Elle est insensible (minuscule ou majuscule).",
                        default="a")
    parser.add_argument("-q", "--question", type=int, help="Question index to begin, start at 1 by default", default=1)
    parser.add_argument("--mot_souligne", type=str,
                        help="Ensemble de caractère à détecter, lorqu'il apparait 2 fois, il met le(s) mot(s) en couleur dans le choix de réponse.",
                        default="X")
    # parser.add_argument("-v", "--verbose", action="store_true",
    #                     help="verbose output")
    parser.add_argument("--debug", action="store_true",
                        help="Affiche toutes les questions et réponses en ignorant la saisie de données des réponses.")
    parser.add_argument("--debug_delay", type=int,
                        help="Lorsque debug est activé, délai pour faire afficher la réponse en seconde.", default=0)
    args = parser.parse_args()

    if len(args.response_char) != 1:
        raise Exception(
            f"Le paramètre --response_char doit contenir seulement 1 caractère. Présentement '{args.response_char}'.")

    if args.question <= 0:
        raise Exception(f"Le numéro de question doit être supérieur ou égale à 1, valeur actuel : '{args.question}'")

    if not os.path.exists(args.database):
        raise Exception(f"Le fichier de base de données n'existe pas, path : '{args.database}'")

    qp = QuestionParser(args)

    # Setup signal handler to stop questionnaire
    def handler(signum, frame):
        print(f"{Fore.RED}Ctrl-c a été appuyé, fin du questionnaire.{Style.RESET_ALL}")
        qp.print_result(exit=True)
        exit(1)

    signal.signal(signal.SIGINT, handler)

    qp.start()


class QuestionParser:
    def __init__(self, parser):
        self.parser = parser
        self._question_number = 0
        self._nb_good_response = 0
        self._nb_wrong_response = 0

    def print_result(self, exit=False):
        print()
        if not self.parser.debug:
            print(f"{Fore.YELLOW}Résultat :{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{self._nb_good_response}{Style.RESET_ALL} bonne(s) réponse(s).")
            print(f"{Fore.RED}{self._nb_wrong_response}{Style.RESET_ALL} mauvaise(s) réponse(s).")
        if exit:
            print("Commande pour recontinuer :")
            print(f"python3 questionnaire.py -q {self._question_number}")

    def start(self):
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
                    self.print_response(row, 2)
                    self.print_response(row, 3)
                    self.print_response(row, 4)
                    self.print_response(row, 5)
                    print()
                    if self.parser.debug:
                        if self.parser.debug_delay:
                            time.sleep(self.parser.debug_delay)
                        print(f"Réponse : {Fore.RED}{row[1]}{Style.RESET_ALL}")
                    else:
                        self.get_answer(row[1])
                    print()
                    print(f"Explication : {Fore.BLUE}{row[6]}{Style.RESET_ALL}")
                    print()
            print(f'{Fore.RED}Questionnaire complété!{Style.RESET_ALL}')
            self.print_result()

    def get_answer(self, expected_value):
        x = ""
        while not x:
            x = input("Votre réponse : ")
            x = x.upper().strip()
            if x not in ("A", "B", "C", "D"):
                x = ""

        if expected_value == x:
            print(f"{Fore.GREEN}Bonne réponse! ☺{Style.RESET_ALL}")
            self._nb_good_response += 1
        else:
            print(
                f"{x} est la {Fore.RED}mauvaise réponse{Style.RESET_ALL}, réponse {Fore.GREEN}{expected_value}{Style.RESET_ALL}")
            self._nb_wrong_response += 1

    def print_response(self, row, no):
        # mot_souligne
        response_char = no - 2
        transform_response_char = chr(ord(self.parser.response_char) + response_char).upper()
        sentence = row[no]
        # Detect special word
        if sentence.count(self.parser.mot_souligne) >= 2:
            lst_sentence = sentence.split(self.parser.mot_souligne)
            new_sentence = ""
            for index, s in enumerate(lst_sentence):
                if index % 2:
                    # Pour tous les mots pairs, on les colore
                    new_sentence += f"{Fore.MAGENTA}{s}{Style.RESET_ALL}"
                else:
                    new_sentence += s
            sentence = new_sentence
        print(f'\t{transform_response_char} - {sentence}')


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception(e)
