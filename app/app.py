"""Rapport interactif : résultats du modèle de gravité, évalués sur 2023."""
import json
import os
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

import rapport as r

SORTIE = Path(os.environ.get("SORTIE", "/sortie"))
st.set_page_config(page_title="Gravité des accidents de la route", layout="centered")
st.markdown(r.CSS, unsafe_allow_html=True)

if not (SORTIE / "modele_gravite.joblib").exists():
    st.error("Modèle introuvable. Lance d'abord l'entraînement : docker compose run --rm train")
    st.stop()


@st.cache_resource
def charger():
    return joblib.load(SORTIE / "modele_gravite.joblib"), json.loads((SORTIE / "metriques.json").read_text(encoding="utf-8"))


@st.cache_data(ttl=600)
def donnees_par_annee():
    """Personnes et taux de cas graves par année, lus dans la base. None si la base n'est pas joignable."""
    try:
        import psycopg
        with psycopg.connect(host=os.environ["POSTGRES_HOST"], port=os.environ["POSTGRES_PORT"], dbname=os.environ["POSTGRES_DB"],
                             user=os.environ["POSTGRES_USER"], password=os.environ["POSTGRES_PASSWORD"], connect_timeout=3) as conn:
            return conn.execute("select annee, count(*), avg(grave) from marts.accidents_usagers group by annee order by annee").fetchall()
    except Exception:
        return None


objet, m = charger()
t = m["test"]
c = r.repartition(t)
txt = r.textes(m, c)

# --- ouverture : 1 000 personnes ---------------------------------------------------------------
st.markdown(f"# {txt['titre']}")
st.markdown(f'<p class="chapo">{txt["chapo"]}</p>', unsafe_allow_html=True)
vue = st.radio("Vue", r.ETATS, horizontal=True, label_visibility="collapsed")
etat = r.ETATS.index(vue)
st.markdown(f'<p class="etat">{r.phrase_etat(m, c, etat)}</p>', unsafe_allow_html=True)
st.markdown(r.champ(c, etat), unsafe_allow_html=True)
st.markdown(r.cles(c, etat), unsafe_allow_html=True)
st.markdown(f'<p class="legende" style="margin-top:.9rem !important">{txt["echelle"]}</p>', unsafe_allow_html=True)

# --- bilan -------------------------------------------------------------------------------------
st.markdown(f"## {txt['h_bilan']}")
gauche, droite = st.columns([6, 5], gap="large")
with gauche:
    st.markdown(f'<div class="chiffre amb">{txt["rappel"]}</div><p class="chiffre-texte">{txt["t_rappel"]}</p>', unsafe_allow_html=True)
with droite:
    st.markdown(f'<div class="chiffre cl">{txt["juste"]}</div><p class="chiffre-texte">{txt["t_juste"]}</p>', unsafe_allow_html=True)
st.markdown(f'<p class="legende" style="margin-top:2rem !important">{txt["accuracy"]}</p>', unsafe_allow_html=True)

# --- stabilité ---------------------------------------------------------------------------------
st.markdown(f"## {txt['h_stable']}")
st.markdown(txt["p_stable"])
st.markdown(r.comparaison(m), unsafe_allow_html=True)

# --- variables ---------------------------------------------------------------------------------
fichier = SORTIE / "importance_variables.csv"
if fichier.exists():
    imp = pd.read_csv(fichier, index_col=0)["importance"].sort_values(ascending=False)
    st.markdown(f"## {r.titre_importance(imp)}")
    st.markdown("Importance mesurée par permutation : on mélange une variable au hasard et on regarde de combien le modèle se dégrade. "
                "Plus la baisse de PR-AUC est forte, plus le modèle s'appuie sur cette variable.")
    st.markdown(r.importance(imp), unsafe_allow_html=True)
    st.markdown("Ces poids décrivent le modèle, pas la réalité. Les cases « non renseigné » de l'équipement de sécurité sont presque "
                "toujours associées à des cas non graves : le modèle peut donc lire autant la façon dont la fiche a été remplie que "
                "l'effet de la ceinture ou du casque. La position du piéton, elle, n'est renseignée que pour les piétons.")

# --- estimer un cas ----------------------------------------------------------------------------
st.markdown("## Estimer un cas")
st.markdown("Choisis un profil : le modèle calcule son score. Les variables qui ne sont pas proposées ici prennent leur valeur la plus fréquente.")
d = objet["defauts"]
formulaire, resultat = st.columns([5, 6], gap="large")
with formulaire:
    age = st.slider("Âge", 0, 100, int(d["age"]))
    heure = st.slider("Heure de l'accident", 0, 23, int(d["heure"]))
    vma = st.slider("Vitesse maximale autorisée (km/h)", 10, 130, min(max(int(d["vma"]), 10), 130), step=10)
    usager = {"1": "Conducteur", "2": "Passager", "3": "Piéton"}
    catu = st.selectbox("Usager", list(usager), format_func=usager.get)
    vehicule = {"7": "Voiture", "10": "Utilitaire", "1": "Vélo", "2": "Cyclomoteur (50 cm³ et moins)", "33": "Moto (plus de 125 cm³)"}
    catv = st.selectbox("Véhicule", list(vehicule), format_func=vehicule.get)
    equipement = {"1": "Ceinture", "2": "Casque", "3": "Dispositif enfant", "0": "Aucun équipement", "-1": "Non renseigné"}
    secu1 = st.selectbox("Équipement de sécurité", list(equipement), format_func=equipement.get)
    luminosite = {"1": "Plein jour", "2": "Aube ou crépuscule", "3": "Nuit, sans éclairage public",
                  "4": "Nuit, éclairage public éteint", "5": "Nuit, éclairage public allumé"}
    lum = st.selectbox("Luminosité", list(luminosite), format_func=luminosite.get)

ligne = dict(d)
ligne.update({"age": age, "heure": heure, "vma": vma, "catu": catu, "catv": catv, "secu1": secu1, "lum": lum})
score = float(objet["pipeline"].predict_proba(pd.DataFrame([ligne])[objet["colonnes"]])[0, 1])
with resultat:
    st.markdown(r.panneau(score, objet["seuil"]), unsafe_allow_html=True)

# --- limites -----------------------------------------------------------------------------------
st.markdown("## Ce que ces résultats ne disent pas")
a, b = st.columns(2, gap="large")
with a:
    st.markdown("Plusieurs variables (obstacle heurté, point de choc, manœuvre, type de collision) ne sont connues qu'après l'accident. "
                "Le modèle aide donc à comprendre la gravité d'accidents déjà survenus ; il ne prévoit pas un risque avant qu'il se produise.")
with b:
    st.markdown("Le critère « grave » regroupe les personnes tuées et hospitalisées. L'année 2020, marquée par les confinements, est atypique. "
                "Quand un accident compte plusieurs lignes de lieu, une seule est retenue (celle de la vitesse maximale autorisée la plus élevée) : "
                "c'est une hypothèse de travail.")

# --- données -----------------------------------------------------------------------------------
st.markdown("## Cinq ans de données")
annees = donnees_par_annee()
if annees:
    st.markdown("La part de chaque colonne en rouge indique la proportion de personnes tuées ou hospitalisées.")
    st.markdown(r.frise_annees(annees), unsafe_allow_html=True)
st.markdown('<p class="legende">Bases annuelles des accidents corporels de la circulation routière, ONISR / ministère de l\'Intérieur, '
            'licence ouverte (data.gouv.fr). Chargées dans PostgreSQL, nettoyées avec dbt (23 tests de qualité) puis modélisées avec scikit-learn.</p>',
            unsafe_allow_html=True)
