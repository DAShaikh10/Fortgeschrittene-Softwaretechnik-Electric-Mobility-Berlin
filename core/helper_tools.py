import time
import math
import random
import pickle
import functools

import pandas as pd

from collections import Counter, OrderedDict


def timer(func):
    """
    Print the runtime of the decorated function
    """

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        print(" ====> Duration {:.2f} secs: {}".format(run_time, func.__doc__))
        return value

    return wrapper_timer  # no "()" here, we need the object to be returned.


# ------------------------------------------------------------------------------
# predicates
def isElFilled(el, liste):
    return (el in liste) and (liste[el] is not None)


# Are there NO row duplicates?      #Types: pandas dataframe --> Boolean
validateIndex = lambda d: False if True in d.duplicated(keep="first") else False


# ------------------------------------------------------------------------------
# Serialisierung
@timer
def pickle_out(objName, dateiName):
    """Serialization"""
    with open(dateiName, "wb") as p_out:
        pickle.dump(objName, p_out)


@timer
def pickle_in(dateiName):
    """Deserialization"""
    with open(dateiName, "rb") as p_in:
        return pickle.load(p_in)


# ------------------------------------------------------------------------------
def col_base_features(col, pattern):
    a = list(col.str.split(pat=pattern))
    return list([x[0] for x in a])


def determine_dyn_colorder(colvals, colorder_fixedpart, pdict):
    col_order = list(colvals)
    remList = [
        "Index",
        "ID",
        pdict["meta_typ"],
        pdict["meta_description"],
        "Wertebereich",
        "F_Aktiv",
        "F_PCA",
        "F_Szen",
    ]
    for i in remList:
        try:
            col_order.remove(i)
        except:
            print(i + " nicht vorhanden")

    # col_order.remove("Index")
    # col_order.remove("ID")
    # col_order.remove(pdict["meta_typ"])
    # col_order.remove(pdict["meta_description"])
    # col_order.remove("Wertebereich")
    # col_order.remove("F_Aktiv")
    # col_order.remove("F_PCA")
    # col_order.remove("F_Szen")

    return colorder_fixedpart + col_order


lam_split = lambda x: x.split("$")[1]

tupToStr = lambda t: ". ".join(str(e) for e in [int(t[0]), t[1]])

# dfcn: DataFrame Col Name; zeichen: char der weg soll
# colNameRemChar = lambda x, y: x.str.replace(ch,'') for ch in list(y)


def cleanse_colnames(dfcn, zeichen):
    # dfcn ist kein Dataframe, sondern df.columns
    for v in list(zeichen):
        dfcn = dfcn.str.replace(v, "")
    return dfcn


ohlist_To_FeaturesList = lambda l: list(set([i.split("$")[0] for i in l]))
sortDictReverseOrderIntKey = lambda d: sorted(list(d.items()), key=lambda x: x[0], reverse=True)

# -----------------------------------------------------------------------------
# prüfen ob "nan", "None" in liste, dictionary weg kann:
# x: list
remNanFromListFloat = lambda x: [i for i in x if str(i) != "nan"]
remNullItemsFromList = lambda x: [i for i in x if i is not None]
# d: dictionary
remNanFromDict = lambda d: {k: v for k, v in d.items() if str(v) != "nan"}
remNullItemsFromDict = lambda d: {k: v for k, v in d.items() if v is not None}

# -----------------------------------------------------------------------------
# Math: Sets
intersect = lambda x, y: list(set(x).intersection(y))

# ------------------------------------------------------------------------------
# Math: Combinatorics
binom = lambda n, k: math.factorial(n) // math.factorial(k) // math.factorial(n - k)

# ------------------------------------------------------------------------------
# Random generator for colors
getRandomColor = lambda _: "#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)])


# ------------------------------------------------------------------------------
# FreqCounter
def countFreqs(arr):
    lcounter = Counter(arr)
    return OrderedDict(sorted(lcounter.items()))


# ------------------------------------------------------------------------------
# Dataframe nach Reihen sortieren, neues mit neuem Index erzeugen - BEGIN
def popRowFromDF(dframe, indexVal):
    poppedRow = dframe.loc[indexVal, :].tolist()
    ShrinkedDF = dframe.drop(indexVal)
    return poppedRow, ShrinkedDF


@timer
def sortDF(dframe, col, asc):  # Pandas-df, String, Boolean
    """Sorts DataFrame"""

    dfColList = dframe.columns.values
    retDF = pd.DataFrame(columns=dfColList)
    while not dframe.empty:
        # for i in range(4):

        dfCol = dframe[col]

        poppedStackdfCol = min(dfCol) if asc == True else max(dfCol)
        poppedStackIndexVal = dframe.index[dframe[col] == poppedStackdfCol].tolist()

        # falls höchster/niedrigster Rang mehrfach vorliegt, wird der erste in Liste genommen
        poppedRow, dframe = popRowFromDF(dframe, poppedStackIndexVal[0])
        dict_row = dict(zip(dfColList, poppedRow))
        #        retDF = pd.concat([retDF, dict_row], axis = 1, ignore_index = True)

        # retDF = retDF \
        #     .append(dict_row, ignore_index = True)

        retDF = pd.concat([retDF, pd.DataFrame([dict_row])], ignore_index=True)

    return retDF


# END
# ------------------------------------------------------------------------------
# Dataframes: Column name aliases (compare SQL "as")

# x: dframe, y: pdict
df_cols_assign_alias = lambda x, y: x.rename(columns=dict(zip(y["scenario"], y["sc_alias"])))
