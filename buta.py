import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import pickle
from pathlib import Path

if not Path("save.pkl").is_file():
    jarasok = pd.read_excel("jarasok.xls")
    telepules2jaras = {}
    for _, row in jarasok.iterrows():
        telepules2jaras[row["település"]] = row["járás"]

    szovegertes_10 = pd.read_csv("kompetencia_szovegertes_10.csv", sep=";")
    szovegertes_10_dict = {}
    for _, row in szovegertes_10.iterrows():
        szovegertes_10_dict[row["Járás"]] = row["50"]
    
    matematika_10 = pd.read_csv("kompetencia_matematika_10.csv", sep=";")
    matematika_10_dict = {}
    for _, row in matematika_10.iterrows():
        matematika_10_dict[row["Járás"]] = row["50"]

    valasztas_df = pd.read_excel("valasztas_2022/listas_eredmeny.xlsx")
    print("valasztas excel loaded")
    valasztas = {}
    for _, row in valasztas_df.iterrows():
        if not pd.isna(row["TELEPÜLÉS"]):
            aktualis_telepules = row["TELEPÜLÉS"]
            if aktualis_telepules not in valasztas.keys():
                valasztas[aktualis_telepules] = {"fidesz": 0, "ellen": 0}
        else:
            if "FIDESZ" in row["LISTA"] or "HAZÁNK" in row["LISTA"]:
                valasztas[aktualis_telepules]["fidesz"] += row["SZAVAZAT"]
            if "KOALÍCIÓ" in row["LISTA"] or "KÉTFARKÚ" in row["LISTA"]:
                valasztas[aktualis_telepules]["ellen"] += row["SZAVAZAT"]

    jarasok_fidesz = {jaras: 0 for jaras in set(telepules2jaras.values())}
    jarasok_ellen = {jaras: 0 for jaras in set(telepules2jaras.values())}
    for telepules in valasztas.keys():
        try:
            jarasok_fidesz[telepules2jaras[telepules]] += valasztas[telepules]["fidesz"]
            jarasok_ellen[telepules2jaras[telepules]] += valasztas[telepules]["ellen"]
        except KeyError:
            continue

    results_df = pd.DataFrame(index=jarasok_fidesz.keys())#, columns=["jaras"])
    results_df["jaras"] = results_df.index
    results_df["fidesz"] = jarasok_fidesz
    results_df["ellen"] = jarasok_ellen
    fidesz_ratio = results_df["fidesz"].to_numpy() / (results_df["fidesz"].to_numpy() + results_df["ellen"].to_numpy())
    results_df.insert(2, "fidesz_ratio", fidesz_ratio)
    total_voters = results_df["fidesz"].to_numpy() + results_df["ellen"].to_numpy()
    results_df.insert(3, "total_voters", total_voters)
    results_df.insert(4, "szovegertes_10", szovegertes_10_dict)
    results_df.insert(5, "matematika_10", matematika_10_dict)
    with open('save.pkl', 'wb') as file:
        pickle.dump(results_df, file)
else:
    with open('save.pkl', 'rb') as file:
        results_df = pickle.load(file)



fig = px.scatter(
    results_df,
    x="fidesz_ratio",
    y=["szovegertes_10", "matematika_10"],
    hover_data=["jaras"],
    size="total_voters",
    custom_data=["jaras"],
    title="Fidesz vs kompetencia járásonként",
    labels={
        "x": "Fidesz + Mi hazánk szavazók aránya",
        "y": "Országos kompetenciamérés medián pontszám",
    },
)

fig.show()

print("Hello")
