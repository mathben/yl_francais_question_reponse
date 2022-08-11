# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).
import argparse
import logging


def main():
    parser = argparse.ArgumentParser(description="Generate your vaccination QR code.")
    parser.add_argument("-d", "--database", type=str, help="Your database filename path",
                        default="./database.csv")
    parser.add_argument("--response_char", type=str, help="Your character to start the answer, 0, 1 or a (A)",
                        default="a")
    parser.add_argument("-q", "--question", type=int, help="Question index to begin, start at 0 by default", default=0)
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
        print("yeah")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception(e)
