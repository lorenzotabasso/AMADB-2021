import csv
import sys
from pathlib import Path
from optparse import OptionParser


def load_data():
    """
    It reads che definition's CSV
    :return: four list containing the read definitions.
    """
    emoSN = []

    with open(options.input, "r", encoding="utf-8") as dataset:
        for line in dataset:
            emoSN.append(line)

        print("finished!")
        return emoSN


def post_process(raw_data):
    post_processed_data = []

    for line in raw_data:
        if "_" not in line:
            post_processed_data.append(line)

    print("{0} ok!".format(len(post_processed_data)))


if __name__ == "__main__":

    sentiment_path = Path('../..') / 'data' / 'lexical-resources' / 'Sentiments'
    anger_p = sentiment_path / "Anger" / "EmoSN_anger.txt"

    argv = sys.argv[1:]
    parser = OptionParser()

    parser.add_option("-i", "--input", help='input file', action="store", type="string", dest="input",
                      default=anger_p)

    # TODO usare pathlib
    parser.add_option("-o", "--output", help='output directory', action="store", type="string", dest="output",
                      default="../../output/Es1/")

    (options, args) = parser.parse_args()

    data = load_data()
    post_process(data)

    if options.input is None:
        print("Missing mandatory parameters")
        sys.exit(2)
