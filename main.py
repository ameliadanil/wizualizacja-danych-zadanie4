# ============================================
# ZADANIE 4 — WIZUALIZACJA RYNKU KONCERTÓW W POLSCE
# ============================================

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ============================================
# GENEROWANIE DANYCH
# ============================================

np.random.seed(42)

n = 1200

miasta = {
    "Warszawa":   (52.2297, 21.0122, 1.00),
    "Kraków":     (50.0647, 19.9450, 0.75),
    "Wrocław":    (51.1079, 17.0385, 0.65),
    "Poznań":     (52.4064, 16.9252, 0.55),
    "Gdańsk":     (54.3520, 18.6466, 0.55),
    "Łódź":       (51.7592, 19.4560, 0.50),
    "Katowice":   (50.2649, 19.0238, 0.45),
    "Lublin":     (51.2465, 22.5684, 0.30),
    "Białystok":  (53.1325, 23.1688, 0.25),
    "Szczecin":   (53.4285, 14.5528, 0.35),
}

gatunki = ["rock", "pop", "hip-hop", "electronic", "jazz",
           "classical", "folk", "metal", "indie", "reggae"]

typy_obiektow = ["klub", "arena", "stadion", "festiwal", "teatr", "amfiteatr"]

kapacjety = {
    "klub": (200, 1500),
    "arena": (3000, 15000),
    "stadion": (20000, 70000),
    "festiwal": (10000, 80000),
    "teatr": (400, 2000),
    "amfiteatr": (1500, 8000),
}

cena_bazowa = {
    "rock": 150,
    "pop": 200,
    "hip-hop": 180,
    "electronic": 160,
    "jazz": 130,
    "classical": 110,
    "folk": 90,
    "metal": 140,
    "indie": 100,
    "reggae": 110,
}

cena_mnoznik = {
    "klub": 0.7,
    "arena": 1.3,
    "stadion": 1.8,
    "festiwal": 1.5,
    "teatr": 1.2,
    "amfiteatr": 1.0,
}

start_date = datetime(2024, 1, 1)
daty = [start_date + timedelta(days=int(d)) for d in np.random.randint(0, 730, n)]

wagi = np.array([miasta[m][2] for m in miasta])
miasto = np.random.choice(list(miasta.keys()), n, p=wagi / wagi.sum())

gatunek = np.random.choice(gatunki, n)

typ_obiektu = np.random.choice(
    typy_obiektow,
    n,
    p=[0.40, 0.15, 0.05, 0.10, 0.15, 0.15]
)

pojemnosc = np.array([np.random.randint(*kapacjety[t]) for t in typ_obiektu])

wypelnienie = np.clip(np.random.beta(5, 2, n), 0.15, 1.0)

sprzedane = (pojemnosc * wypelnienie).astype(int)

cena = np.array([
    cena_bazowa[g] * cena_mnoznik[t]
    for g, t in zip(gatunek, typ_obiektu)
])

cena = np.round(cena * np.random.uniform(0.7, 1.4, n), -1)

przychod = (cena * sprzedane).astype(int)

df = pd.DataFrame({
    "event_id": range(50001, 50001 + n),
    "data": daty,
    "miasto": miasto,
    "latitude": [miasta[m][0] for m in miasto],
    "longitude": [miasta[m][1] for m in miasto],
    "gatunek": gatunek,
    "typ_obiektu": typ_obiektu,
    "pojemnosc": pojemnosc,
    "bilety_sprzedane": sprzedane,
    "cena_biletu_pln": cena,
    "przychod_pln": przychod,
})

df.to_csv("koncerty_polska.csv", index=False)

print(f"Wygenerowano plik 'koncerty_polska.csv' — {len(df)} koncertów")


# ============================================
# WCZYTANIE DANYCH
# ============================================

df = pd.read_csv("koncerty_polska.csv", parse_dates=["data"])


# ============================================
# CZĘŚĆ 1 — WSTĘPNA EKSPLORACJA
# ============================================

print("\nSHAPE:")
print(df.shape)

print("\nHEAD:")
print(df.head())

print("\nDTYPES:")
print(df.dtypes)

print("\nLICZBA UNIKALNYCH MIAST:")
print(df["miasto"].nunique())

print("\nLICZBA UNIKALNYCH GATUNKÓW:")
print(df["gatunek"].nunique())


# ============================================
# CZĘŚĆ 2 — WYKRES SŁUPKOWY
# ============================================

przychod_miasto = (
    df.groupby("miasto", as_index=False)["przychod_pln"]
    .sum()
    .sort_values("przychod_pln", ascending=False)
)

fig = px.bar(
    przychod_miasto,
    x="miasto",
    y="przychod_pln",
    title="Łączny przychód z koncertów w poszczególnych miastach",
    labels={
        "miasto": "Miasto",
        "przychod_pln": "Łączny przychód [PLN]"
    },
    color="przychod_pln"
)

fig.update_layout(template="plotly_white")
fig.show()


# ============================================
# CZĘŚĆ 3 — WYKRESY LINIOWE
# ============================================

df["miesiac"] = df["data"].dt.to_period("M").astype(str)

koncerty_miesiac = (
    df.groupby("miesiac")
    .size()
    .reset_index(name="liczba_koncertow")
)

fig = px.line(
    koncerty_miesiac,
    x="miesiac",
    y="liczba_koncertow",
    markers=True,
    title="Łączna liczba koncertów w każdym miesiącu",
    labels={
        "miesiac": "Miesiąc",
        "liczba_koncertow": "Liczba koncertów"
    }
)

fig.update_layout(template="plotly_white")
fig.show()


koncerty_typ_obiektu = (
    df.groupby(["miesiac", "typ_obiektu"])
    .size()
    .reset_index(name="liczba_koncertow")
)

fig = px.line(
    koncerty_typ_obiektu,
    x="miesiac",
    y="liczba_koncertow",
    color="typ_obiektu",
    markers=True,
    title="Miesięczna liczba koncertów według typu obiektu",
    labels={
        "miesiac": "Miesiąc",
        "liczba_koncertow": "Liczba koncertów",
        "typ_obiektu": "Typ obiektu"
    }
)

fig.update_layout(template="plotly_white")
fig.show()


# ============================================
# CZĘŚĆ 4 — HISTOGRAM I BOXPLOT
# ============================================

fig = px.histogram(
    df,
    x="cena_biletu_pln",
    nbins=50,
    title="Rozkład cen biletów",
    labels={
        "cena_biletu_pln": "Cena biletu [PLN]"
    }
)

fig.update_layout(template="plotly_white")
fig.show()


fig = px.box(
    df,
    x="typ_obiektu",
    y="przychod_pln",
    color="typ_obiektu",
    title="Przychód z koncertów według typu obiektu",
    labels={
        "typ_obiektu": "Typ obiektu",
        "przychod_pln": "Przychód [PLN]"
    }
)

fig.update_layout(template="plotly_white")
fig.show()

print("""
KOMENTARZ:

Najwyższe przychody generują zazwyczaj największe typy obiektów,
czyli stadiony oraz festiwale. Wynika to z dużej pojemności tych miejsc
oraz większej liczby sprzedanych biletów.
""")


# ============================================
# CZĘŚĆ 5 — SCATTER PLOT
# ============================================

df["wypelnienie"] = df["bilety_sprzedane"] / df["pojemnosc"]

fig = px.scatter(
    df,
    x="cena_biletu_pln",
    y="wypelnienie",
    color="gatunek",
    size="pojemnosc",
    hover_data=["miasto", "typ_obiektu"],
    title="Cena biletu a wypełnienie obiektu",
    labels={
        "cena_biletu_pln": "Cena biletu [PLN]",
        "wypelnienie": "Wypełnienie obiektu",
        "gatunek": "Gatunek muzyczny",
        "pojemnosc": "Pojemność"
    }
)

fig.update_layout(template="plotly_white")
fig.show()

print("""
KOMENTARZ:

Na wykresie nie widać bardzo silnej zależności między ceną biletu
a wypełnieniem sali. Wypełnienie zależy prawdopodobnie od wielu czynników,
np. gatunku muzycznego, miasta, typu obiektu i jego pojemności.
""")


# ============================================
# CZĘŚĆ 6 — MAPA
# ============================================

miasta_agregacja = (
    df.groupby(["miasto", "latitude", "longitude"], as_index=False)
    .agg(
        srednia_cena_biletu=("cena_biletu_pln", "mean"),
        liczba_koncertow=("event_id", "count"),
        laczny_przychod=("przychod_pln", "sum")
    )
)

fig = px.scatter_mapbox(
    miasta_agregacja,
    lat="latitude",
    lon="longitude",
    size="liczba_koncertow",
    color="srednia_cena_biletu",
    hover_name="miasto",
    hover_data={
        "srednia_cena_biletu": ":.2f",
        "liczba_koncertow": True,
        "laczny_przychod": True,
        "latitude": False,
        "longitude": False
    },
    zoom=5,
    center={"lat": 52, "lon": 19},
    mapbox_style="open-street-map",
    title="Rynek koncertów muzycznych w polskich miastach",
    labels={
        "srednia_cena_biletu": "Średnia cena biletu [PLN]",
        "liczba_koncertow": "Liczba koncertów",
        "laczny_przychod": "Łączny przychód [PLN]"
    }
)

fig.update_layout(height=600)
fig.show()


# ============================================
# CZĘŚĆ 7 — SUBPLOTY 2x2
# ============================================

przychod_miasto_top = (
    df.groupby("miasto")["przychod_pln"]
    .sum()
    .sort_values(ascending=False)
)

koncerty_gatunek = df["gatunek"].value_counts()

fig = make_subplots(
    rows=2,
    cols=2,
    subplot_titles=(
        "Przychód według miasta",
        "Liczba koncertów według gatunku",
        "Rozkład cen biletów",
        "Wypełnienie według typu obiektu"
    )
)

fig.add_trace(
    go.Bar(
        x=przychod_miasto_top.index,
        y=przychod_miasto_top.values,
        name="Przychód"
    ),
    row=1,
    col=1
)

fig.add_trace(
    go.Bar(
        x=koncerty_gatunek.index,
        y=koncerty_gatunek.values,
        name="Liczba koncertów"
    ),
    row=1,
    col=2
)

fig.add_trace(
    go.Histogram(
        x=df["cena_biletu_pln"],
        nbinsx=50,
        name="Cena biletu"
    ),
    row=2,
    col=1
)

for typ in df["typ_obiektu"].unique():
    dane_typ = df[df["typ_obiektu"] == typ]

    fig.add_trace(
        go.Box(
            y=dane_typ["wypelnienie"],
            name=typ
        ),
        row=2,
        col=2
    )

fig.update_layout(
    title_text="Podsumowanie rynku koncertów muzycznych w Polsce",
    height=800,
    template="plotly_white",
    showlegend=False
)

fig.show()


# ============================================
# CZĘŚĆ 8 — WNIOSKI
# ============================================

miasto_najwiecej = df["miasto"].value_counts().idxmax()

miasto_najwiekszy_przychod = (
    df.groupby("miasto")["przychod_pln"]
    .sum()
    .idxmax()
)

typ_najwyzsza_cena = (
    df.groupby("typ_obiektu")["cena_biletu_pln"]
    .mean()
    .idxmax()
)

print(f"""
WNIOSKI:

1. Najwięcej koncertów odbyło się w mieście: {miasto_najwiecej}.

2. Największy łączny przychód wygenerowało miasto: {miasto_najwiekszy_przychod}.

3. Najwyższe średnie ceny biletów występowały w obiektach typu: {typ_najwyzsza_cena}.

4. Największe przychody generują przede wszystkim duże obiekty,
takie jak stadiony i festiwale, ponieważ mają dużą pojemność.

5. Na wykresach miesięcznych można zauważyć zmienność liczby koncertów w czasie,
co może wskazywać na sezonowość rynku koncertowego.
""")