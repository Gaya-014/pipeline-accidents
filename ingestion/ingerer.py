"""
Ingestion des données BAAC (accidents corporels de la route).

Étapes :
1. interroger l'API data.gouv.fr pour lister les fichiers du jeu de données ;
2. télécharger, pour chaque année, les 4 fichiers CSV (caractéristiques, lieux, usagers, véhicules) ;
3. les charger sans transformation, en texte, dans PostgreSQL (schéma "raw").

Le nettoyage est réalisé en aval avec dbt.
"""
import os
import re
import time
from pathlib import Path

import pandas as pd
import psycopg
import requests
from psycopg import sql

API = "https://www.data.gouv.fr/api/1/datasets/53698f4ca3a729239d2036df/"
DOSSIER = Path("/data/raw")
ANNEES = [int(a) for a in os.environ.get("ANNEES", "2023").split(",")]

# certaines années appellent la clé "accident_id" au lieu de "num_acc" : c'est la même colonne
# Noms de colonnes qui diffèrent selon l'année (ex. 2022 : accident_id au lieu de Num_Acc)
RENOMMAGES = {"accident_id": "num_acc"}

# Mots-clés recherchés dans le titre des fichiers (la nomenclature varie selon les années)
MOTS = {
    "carac": ["carac", "carc"],
    "lieux": ["lieux"],
    "usagers": ["usagers"],
    "vehicules": ["vehicules"],
}


def normaliser(noms):
    # Noms de colonnes en minuscules, sans espaces ni caractères spéciaux
    return [re.sub(r"[^0-9a-z_]+", "_", str(n).strip().lower()).strip("_") for n in noms]


def lister_ressources():
    reponse = requests.get(API, timeout=60)
    reponse.raise_for_status()
    return reponse.json()["resources"]


def trouver(ressources, table, annee):
    candidats = []
    for r in ressources:
        titre = (r.get("title") or "").lower()
        est_csv = titre.endswith(".csv") or (r.get("format") or "").lower() == "csv"
        if (est_csv and str(annee) in titre and any(m in titre for m in MOTS[table])
                and "immatricul" not in titre):
            candidats.append(r)
    if not candidats:
        de_cette_annee = [r.get("title") for r in ressources if str(annee) in (r.get("title") or "")]
        raise FileNotFoundError(f"aucun fichier '{table}' trouvé pour {annee}. Fichiers de cette année : {de_cette_annee}")
    candidats.sort(key=lambda r: len(r.get("title") or ""))   # en cas de doublon, retenir le titre le plus court
    return candidats[0]


def telecharger(ressource, annee, table):
    dest = DOSSIER / str(annee) / f"{table}.csv"
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  {annee} {table} : déjà téléchargé")
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp")
    print(f"  {annee} {table} : téléchargement de {ressource.get('title')}")
    with requests.get(ressource["url"], stream=True, timeout=120) as rep:
        rep.raise_for_status()
        with open(tmp, "wb") as f:
            for morceau in rep.iter_content(1 << 20):
                f.write(morceau)
    tmp.rename(dest)
    return dest


def lire_csv(chemin):
    # Lecture intégrale en texte (dtype=str) : seules les cellules vides deviennent NULL
    for sep in (";", ","):
        for encodage in ("utf-8-sig", "latin-1"):
            try:
                df = pd.read_csv(chemin, sep=sep, dtype=str, keep_default_na=False, na_values=[""],
                                 encoding=encodage)
            except UnicodeDecodeError:
                continue
            if df.shape[1] > 1:
                df.columns = [RENOMMAGES.get(c, c) for c in normaliser(df.columns)]
                if "num_acc" not in df.columns:
                    raise ValueError(f"{chemin} : pas de colonne num_acc (colonnes : {list(df.columns)})")
                return df
    raise ValueError(f"impossible de lire {chemin}")


def preparer_table(df, annee):
    # Ajout de l'année et du numéro de ligne d'origine (utile pour départager des lignes en aval)
    df = df.copy()
    df["annee"] = str(annee)
    df["ligne"] = [str(i) for i in range(1, len(df) + 1)]
    return df.astype(object).where(df.notna(), None)


def charger(cur, table, df, annee):
    df = preparer_table(df, annee)
    colonnes = list(df.columns)

    # Création de la table au premier chargement, puis ajout des colonnes manquantes
    cur.execute(sql.SQL("CREATE TABLE IF NOT EXISTS raw.{} (annee integer, ligne integer)").format(sql.Identifier(table)))
    for col in colonnes:
        if col not in ("annee", "ligne"):
            cur.execute(sql.SQL("ALTER TABLE raw.{} ADD COLUMN IF NOT EXISTS {} text")
                        .format(sql.Identifier(table), sql.Identifier(col)))

    # Suppression de l'année avant rechargement : le script est idempotent
    cur.execute(sql.SQL("DELETE FROM raw.{} WHERE annee = %s").format(sql.Identifier(table)), (annee,))

    ordre = sql.SQL(", ").join(sql.Identifier(c) for c in colonnes)
    with cur.copy(sql.SQL("COPY raw.{} ({}) FROM STDIN").format(sql.Identifier(table), ordre)) as copie:
        for ligne in df.itertuples(index=False, name=None):
            copie.write_row(ligne)


def connexion():
    info = (f"host={os.environ['POSTGRES_HOST']} port={os.environ['POSTGRES_PORT']} "
            f"dbname={os.environ['POSTGRES_DB']} user={os.environ['POSTGRES_USER']} "
            f"password={os.environ['POSTGRES_PASSWORD']}")
    for essai in range(10):
        try:
            return psycopg.connect(info)
        except psycopg.OperationalError as erreur:
            print(f"base pas encore prête ({erreur}), nouvel essai dans 3 s")
            time.sleep(3)
    raise RuntimeError("impossible de se connecter à la base")


def main():
    print("Liste des fichiers sur data.gouv.fr...")
    ressources = lister_ressources()
    resume = []

    with connexion() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.commit()

        for annee in ANNEES:
            print(f"\n=== Année {annee} ===")
            try:
                # Téléchargement et lecture des 4 fichiers avant toute écriture en base
                tables = {}
                for table in MOTS:
                    chemin = telecharger(trouver(ressources, table, annee), annee, table)
                    tables[table] = lire_csv(chemin)
                with conn.cursor() as cur:
                    for table, df in tables.items():
                        charger(cur, table, df, annee)
                conn.commit()
                resume.append((annee, "OK", {t: len(d) for t, d in tables.items()}))
                print(f"  -> année {annee} chargée")
            except Exception as erreur:
                conn.rollback()
                resume.append((annee, f"IGNORÉE : {erreur}", {}))
                print(f"  -> année {annee} IGNORÉE : {erreur}")

    print("\n===== RÉSUMÉ =====")
    for annee, statut, tailles in resume:
        print(annee, statut, tailles)


if __name__ == "__main__":
    main()
