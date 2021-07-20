from pathlib import Path
import os


def manage_rl(
        file_path: Path,
        lim_neg: float, lim_pos: float,
        positive_list: list, negative_list: list, neutral_list: list) -> None:
    """
    Dato un file in input divide il contenuto in tre sottoliste, in base a delle soglie numeriche predeterminate
    :param file_path: path del file
    :param lim_neg: limite numerico (lower bound)
    :param lim_pos: limite numerico (upper bound)
    :param positive_list: lista di parole dal significato positivo
    :param negative_list: lista di parole dal significato negativo
    :param neutral_list: lista di parole dal significato neutro
    """

    with open(file_path, 'r') as f:
        for line in f.readlines():
            splitted = line.split('\t')  # Split on tab
            word = splitted[0].strip()  # parola
            s = splitted[1].strip()  # score
            score = float(s)

            if score < lim_neg:
                negative_list.append(word)
            elif score > lim_pos:
                positive_list.append(word)
            else:
                neutral_list.append(word)


def wrapper_manage_lr() -> None:
    """
    Per ogni file in input con liste di parole con score viene applicato un filtro che suddivide le parole in tre liste,
    una lista per parole positive, una per parole classificate negative e una per quelle neutre.
    Create le tre liste di parole esse vengono inserite nei file corrispondenti.
    """
    positive_list = []
    negative_list = []
    neutral_list = []

    # popolazione delle tre liste a partire dai 3 file di input con score.
    path_gen = Path('.') / 'data' / 'lexical-resources' / \
        'Generic' / 'ConScore'
    path1 = path_gen / 'afinn.txt'
    path2 = path_gen / 'anewPleas_tab.tsv'
    path3 = path_gen / 'Dal_Pleas.csv'
    manage_rl(path1, 0, 0, positive_list, negative_list, neutral_list)
    manage_rl(path2, 4.4, 5.5, positive_list, negative_list, neutral_list)
    manage_rl(path3, 1.8, 1.9, positive_list, negative_list, neutral_list)

    print(Hello)


if __name__ == "__main__":
    print("Sto gestendo le risorse lessicali con punteggio")
    wrapper_manage_lr()