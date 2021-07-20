from pathlib import Path
import os
from NoSql.nosqldbhandler import NoSqlDbHandler
from pandas import DataFrame, Series

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

def write_list_in_file (file_path: Path, w_list_neg: list,  w_list_pos: list,  w_list_ok: list) -> None:
    """
    Scrive i nuovi sentimenti sul file date le tre liste
    """
    print('Sto scrivendo i nuovi sentimenti in: ' + str(file_path))
    sentiment_groupped = ["anger, disgust, fear, sadness", "joy, trust" , "anticipation, surprise"]
    data = {
        sentiment_groupped[0] : Series(w_list_neg),
        sentiment_groupped[1] : Series(w_list_pos),
        sentiment_groupped[2] : Series(w_list_ok)
    }
    df = DataFrame(data)
    df.to_csv(file_path)
    
def manage_pos_neg(file_path : Path, output_list: list)  -> None:
    """
    Appendi alla lista output tutte le righe presenti nel file del percorso indicato
    :param file_path: percorso del file da analizzare
    :param output_list: lista su cui effettuare l'append 
    """
    with open(file_path , 'r') as f:
        for line in f.readlines():
            output_list.append(line.strip())


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
    path_gen = Path('.') / 'data' / 'lexical-resources' / 'Generic' 
    path_cs = path_gen / 'ConScore'
    path1 = path_cs / 'afinn.txt'
    path2 = path_cs / 'anewPleas_tab.tsv'
    path3 = path_cs / 'Dal_Pleas.csv'
    manage_rl(path1, 0, 0, positive_list, negative_list, neutral_list)
    manage_rl(path2, 4.4, 5.5, positive_list, negative_list, neutral_list)
    manage_rl(path3, 1.8, 1.9, positive_list, negative_list, neutral_list)

    # popolazione delle liste negative con i txt delle cartelle Neg.
    dataset_dir = path_gen / 'Neg'
    for file_name in os.listdir(dataset_dir):
        file_path_neg = dataset_dir / file_name
        manage_pos_neg(file_path_neg, negative_list)

    # popolazione delle liste positive con i txt delle cartelle Pos.
    dataset_dir = path_gen / 'Pos'
    for file_name in os.listdir(dataset_dir):
        file_path_neg = dataset_dir / file_name
        manage_pos_neg(file_path_neg, positive_list)

    new_res_path = Path('.') / 'output' / 'sentiments_from_resources.csv'
    write_list_in_file(new_res_path, negative_list, positive_list, neutral_list)

if __name__ == "__main__":
    print("Sto gestendo le risorse lessicali con punteggio")
    wrapper_manage_lr()
    print("Ho finito di gestire le risorse lessicali")