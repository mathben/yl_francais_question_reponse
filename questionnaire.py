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
import unicodedata

from logging import getLogger

logger = getLogger(__name__)

try:
    import pdfminer  # pylint: disable=W0404
    from pdfminer.converter import PDFPageAggregator  # pylint: disable=W0404
    from pdfminer.layout import LAParams  # pylint: disable=W0404
    from pdfminer.pdfdocument import PDFDocument  # pylint: disable=W0404
    from pdfminer.pdfinterp import PDFPageInterpreter  # pylint: disable=W0404
    from pdfminer.pdfinterp import PDFResourceManager  # pylint: disable=W0404
    from pdfminer.pdfpage import PDFPage  # pylint: disable=W0404
    from pdfminer.pdfparser import PDFParser  # pylint: disable=W0404
except ImportError:
    logger.debug("Can not import pdfminer")

PDF_PATH = "./test.pdf"
LST_MODEL_FONT = []
LST_FIELD_FONT = []
LST_HELP_FONT = []
LST_DATA_FONT = []
# DEBUG_LOGGER = False
DEBUG_LOGGER = True
NB_SKIP_PAGE = 0
PDF_PASSWORD = ""

lst_menu_line = []

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
    parser.add_argument("--test", action="store_true",
                        help="Génère la base de données à partir du fichier test.PDF.")
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
    if args.test:
        qp.test()
    else:

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
                    print(row[0].replace("\\n", "\n"))
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

    def createPDFDoc(self):
        fp = open(PDF_PATH, "rb")
        parser = PDFParser(fp)
        document = PDFDocument(parser, password=PDF_PASSWORD)
        # Check if the document allows text extraction. If not, abort.
        if not document.is_extractable:
            raise Exception("Not extractable")
        return document

    def createDeviceInterpreter(self):
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        return device, interpreter

    def parse_obj(self, objs, work, first_page=False):
        key_section = ["PARTIE A", "PARTIE B"]
        # Strategie : détecter un chiffre suivi d'un point, c'est une question.
        # Les key_section à ignorer, n'impacte pas les données
        # Détecter les bonnes réponses, on cherche "Corrigé"
        # Une page qui contient "avec corrigés à la suite" sont les débuts des choix de réponses
        # 'VOIR CORRIGÉ PAGES SUIVANTES' signifie une fin de réponses
        for obj in objs:
            if isinstance(obj, pdfminer.layout.LTTextBox):
                for o in obj._objs:
                    if not isinstance(o, pdfminer.layout.LTTextLine):
                        continue
                    origin_text = o.get_text()
                    if first_page:
                        clean_text = origin_text[: origin_text.find(".")].strip()
                        lst_menu_line.append(clean_text)
                        continue

                    text = unicodedata.normalize("NFKC", origin_text).replace(u'\xad', u'-').strip()

                    lst_int = [int(s) for s in text.split(".") if s.isdigit()]
                    if lst_int:
                        first_int = lst_int[0]
                        str_key = f"{first_int}."
                        if len(lst_int) == 1 and text.startswith(str_key):
                            if text[len(str_key):].strip():
                                work.add_number(first_int)
                                work.add_question(text)
                            else:
                                work.add_sub_question()
                    elif not work.number_is_int():
                        continue
                    elif text.startswith("a)"):
                        work.add_choix(text[3:])
                    elif text.startswith("b)"):
                        work.add_choix(text[3:])
                    elif text.startswith("c)"):
                        work.add_choix(text[3:])
                    elif text.startswith("d)"):
                        work.add_choix(text[3:])
                    else:
                        work.append_text(text)

                    # if not text:
                    #     work.add_data("")
                    last_fontname = ""
                    continue
                    for c in o._objs:
                        if (
                                isinstance(c, pdfminer.layout.LTChar)
                                # and c.fontname != last_fontname
                        ):
                            lst_int = [int(s) for s in text.split() if s.isdigit()]
                            if lst_int:
                                first_int = lst_int[0]
                                if len(lst_int) == 1 and text.startswith(f"{first_int}."):
                                    work.add_number(first_int)
                            if not work.number_is_int():
                                continue

                            last_fontname = c.fontname
                            tpl_info = (c.fontname, round(c.size, 2))
                            if tpl_info in LST_MODEL_FONT:
                                text_type = "MODEL"
                                work.add_model(text)
                            elif tpl_info in LST_FIELD_FONT:
                                text_type = "FIELD"
                                work.add_field(text)
                            elif tpl_info in LST_HELP_FONT:
                                text_type = "HELP"
                                work.add_help(text)
                            elif tpl_info in LST_DATA_FONT:
                                text_type = "DATA"
                                work.add_data(text)
                            else:
                                text_type = "UNKNOWN"
                                logger.warning("Cannot find this type of text.")
                            if DEBUG_LOGGER:
                                logger.info(
                                    f"type '{text_type}' text '{text}' fontname"
                                    f" '{c.fontname}' size '{round(c.size, 2)}'"
                                )
            # if it's a container, recurse
            elif isinstance(obj, pdfminer.layout.LTFigure):
                self.parse_obj(obj._objs, work)
            else:
                pass
            # Write last question
            # work.is_new_question()

    def test(self):
        document = self.createPDFDoc()
        device, interpreter = self.createDeviceInterpreter()
        pages = PDFPage.create_pages(document)
        work = Working()
        count_skip = -1
        while True:
            try:
                page_result = next(pages)
                count_skip += 1
                if NB_SKIP_PAGE > count_skip:
                    continue
                interpreter.process_page(page_result)
                layout = device.get_result()

                self.parse_obj(layout._objs, work)
            except StopIteration:
                break
        lst_result = work.get_result()
        with open(self.parser.database, "w") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_writer.writerow(EXPECTED_HEADERS_CSV.split(","))
            for dct_result in lst_result:
                question = dct_result.get("question")
                for sub_dct_result in dct_result.get("sub_question"):
                    csv_writer.writerow(
                        [question, "", sub_dct_result[0], sub_dct_result[1], sub_dct_result[2], sub_dct_result[3], ""])


class Working:
    """
    Order
    1. Model
    2. Field
    3. Help
    4. Data

    Field can not exist, and last can be help.
    """

    def __init__(self):
        self.last_line = ""

        # 0 not start
        # 1 is question
        # 2 is choix
        # self._state = 0

        self._number = None
        self.lst_result = []
        self.lst_sub_question = []
        self.lst_choix = []
        # self.dct_result = {}
        # self.dct_result = {
        #     "question": None,
        #     "reponse": 0,
        #     "lst_choix": [],
        #     "explication": "",
        # }
        self._question = []

    def is_new_question(self):
        if self._question:
            if self.lst_choix:
                self.add_sub_question()
            dct_result = {
                "question": self._question[0],
                "sub_question": self.lst_sub_question[:],
            }
            self.lst_sub_question = []
            self._question = []
            self.lst_result.append(dct_result)
            # self.dct_result = {}

    def number_is_int(self):
        return isinstance(self._number, int)

    def add_number(self, the_number):
        # if self._state == 0:
        self.is_new_question()
            # self._state = 1
        self._number = the_number

    def add_question(self, text):
        self._question.append(text)

    def add_sub_question(self):
        if self.lst_choix:
            self.lst_sub_question.append(self.lst_choix)
        self.lst_choix = []

    def add_choix(self, text):
        self.lst_choix.append(text)

    def append_text(self, text):
        # self.lst_choix.append(text)
        text = text.strip()
        if not text:
            return
        # if self._state == 1:
        if self._question:
            self._question[-1] += f"\n{text}"
        else:
            print("ERREUR MANQUE DE QUESTION LORS DE L'AJOUT DU TEXTE, HELP ME!")
    #
    # def add_field(self, line):
    #     status = self.check_data()
    #     if status or self.lst_help:
    #         self.lst_field = []
    #         self.lst_help = []
    #
    #     self.last_line = line
    #     self.lst_field.append(line)
    #
    #     while len(self.lst_field) > 1:
    #         if self.lst_field[0] in lst_menu_line:
    #             self.lst_field.pop(0)
    #
    # def add_help(self, line):
    #     status = self.check_data()
    #     if status:
    #         self.lst_field = []
    #         self.lst_help = []
    #     self.last_line = line
    #     self.lst_help.append(line)
    #
    # def add_data(self, line):
    #     self.last_line = line
    #     self.lst_data.append(line)

    def get_result(self):
        if not self.lst_result:
            self.is_new_question()
        return self.lst_result


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception(e)
