"""
Entraînement du modèle sur la table marts.accidents_usagers (créée par dbt).

Je découpe dans le TEMPS, comme en vrai (on apprend sur le passé et on prédit le futur) :
  - validation : l'avant-dernière année (sert à choisir le seuil de décision)
  - test       : la dernière année (2023), jamais utilisée avant
  - le modèle final est réentraîné sur toutes les années avant le test
Je n'ai donc plus besoin de séparer "par accident" : deux années différentes ne partagent aucun accident.
"""
import io
import json
import os
import time
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import (ConfusionMatrixDisplay, PrecisionRecallDisplay, average_precision_score,
                             confusion_matrix, precision_recall_curve, roc_auc_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SORTIE = Path(os.environ.get("SORTIE", "/sortie"))
GRAINE = 42

COL_NUM = ["age", "heure", "vma", "nbv"]
COL_CAT = ["place", "catu", "sexe", "trajet", "secu1", "secu2", "locp", "actp",
           "senc", "catv", "obs", "obsm", "choc", "manv", "motor",
           "lum", "agg", "int", "atm", "col", "mois", "jour_semaine",
           "catr", "circ", "vosp", "prof", "plan", "surf", "infra", "situ"]

# réglages trouvés dans mon notebook (recherche aléatoire + validation croisée)
PARAMS = dict(learning_rate=0.03, max_depth=8, max_leaf_nodes=63, min_samples_leaf=100,
              max_iter=300, l2_regularization=0.0)


def connexion():
    import psycopg
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


def lire_table():
    colonnes = ", ".join(f'"{c}"' for c in COL_NUM + COL_CAT)
    requete = f"select annee, num_acc, grave, {colonnes} from marts.accidents_usagers"
    morceaux = []
    with connexion() as conn:
        with conn.cursor() as cur:
            with cur.copy(f"COPY ({requete}) TO STDOUT WITH (FORMAT CSV, HEADER)") as copie:
                for bloc in copie:
                    morceaux.append(bytes(bloc))
    types = {c: str for c in COL_CAT}
    return pd.read_csv(io.BytesIO(b"".join(morceaux)), dtype=types, keep_default_na=False, na_values=[""])


def nouveau_modele():
    num = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
    cat = Pipeline([("imputer", SimpleImputer(strategy="constant", fill_value="-1")),
                    ("onehot", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=0.01,
                                             sparse_output=False, dtype=np.float32))])
    prep = ColumnTransformer([("num", num, COL_NUM), ("cat", cat, COL_CAT)])
    return Pipeline([("prep", prep),
                     ("model", HistGradientBoostingClassifier(class_weight="balanced", random_state=GRAINE, **PARAMS))])


def mesures(y, proba, seuil):
    pred = (proba >= seuil).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    rappel = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * rappel / (precision + rappel) if (precision + rappel) else 0.0
    return {"pr_auc": round(float(average_precision_score(y, proba)), 4),
            "roc_auc": round(float(roc_auc_score(y, proba)), 4),
            "precision": round(float(precision), 4), "recall": round(float(rappel), 4), "f1": round(float(f1), 4),
            "accuracy": round(float((tp + tn) / len(y)), 4),
            "accuracy_toujours_pas_grave": round(float(1 - y.mean()), 4),
            "taux_de_graves": round(float(y.mean()), 4),
            "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp), "personnes": int(len(y))}


def entrainer(df):
    SORTIE.mkdir(parents=True, exist_ok=True)
    annees = sorted(int(a) for a in df["annee"].unique())
    if len(annees) < 3:
        raise ValueError(f"il me faut au moins 3 années dans la table, j'en ai {annees}")
    annee_test, annee_val = annees[-1], annees[-2]
    annees_train = annees[:-2]
    print(f"années d'apprentissage : {annees_train} | validation : {annee_val} | test : {annee_test}")

    X, y = df[COL_NUM + COL_CAT], df["grave"]
    masque = {"train": df["annee"].isin(annees_train), "val": df["annee"] == annee_val, "test": df["annee"] == annee_test}

    # 1) j'apprends sur le passé, je choisis le seuil sur l'année de validation
    debut = time.time()
    modele_a = nouveau_modele().fit(X[masque["train"]], y[masque["train"]])
    proba_val = modele_a.predict_proba(X[masque["val"]])[:, 1]
    prec, rapp, seuils = precision_recall_curve(y[masque["val"]], proba_val)
    f1_seuils = 2 * prec[:-1] * rapp[:-1] / (prec[:-1] + rapp[:-1] + 1e-12)
    seuil = float(seuils[np.argmax(f1_seuils)])
    mesures_val = mesures(y[masque["val"]], proba_val, seuil)
    print(f"validation {annee_val} : PR-AUC {mesures_val['pr_auc']} | seuil choisi {seuil:.2f} ({time.time() - debut:.0f} s)")

    # 2) j'entraîne le modèle final sur train + validation, j'évalue UNE fois sur le test
    debut = time.time()
    masque_final = masque["train"] | masque["val"]
    modele = nouveau_modele().fit(X[masque_final], y[masque_final])
    proba_test = modele.predict_proba(X[masque["test"]])[:, 1]
    mesures_test = mesures(y[masque["test"]], proba_test, seuil)
    print(f"test {annee_test} : {mesures_test} ({time.time() - debut:.0f} s)")

    # 3) figures
    pred_test = (proba_test >= seuil).astype(int)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    ConfusionMatrixDisplay.from_predictions(y[masque["test"]], pred_test, display_labels=["pas grave", "grave"],
                                            cmap="Blues", ax=axes[0])
    axes[0].set_title(f"Matrice de confusion (test {annee_test})")
    PrecisionRecallDisplay.from_predictions(y[masque["test"]], proba_test, ax=axes[1], name="modèle final")
    axes[1].axhline(y[masque["test"]].mean(), color="red", linestyle="--", label="hasard")
    axes[1].set_title(f"Precision-recall (test {annee_test})")
    axes[1].legend()
    plt.tight_layout()
    plt.savefig(SORTIE / "resultats_test.png", dpi=130)
    plt.close()

    # 4) importance des variables (mélange d'une variable à la fois sur un échantillon du test)
    echantillon = X[masque["test"]].sample(n=min(4000, int(masque["test"].sum())), random_state=GRAINE)
    imp = permutation_importance(modele, echantillon, y.loc[echantillon.index], scoring="average_precision",
                                 n_repeats=3, random_state=GRAINE, n_jobs=1)
    importances = pd.Series(imp.importances_mean, index=echantillon.columns).sort_values(ascending=False)
    importances.head(15).round(4).to_csv(SORTIE / "importance_variables.csv", header=["importance"])
    plt.figure(figsize=(6, 5))
    importances.head(15)[::-1].plot.barh(color="steelblue")
    plt.title("Importance des variables (baisse de PR-AUC si on les mélange)")
    plt.tight_layout()
    plt.savefig(SORTIE / "importance_variables.png", dpi=130)
    plt.close()

    # 5) sauvegarde : modèle + seuil + valeurs par défaut (pour l'application) + mesures
    defauts = {c: float(X.loc[masque_final, c].median()) for c in COL_NUM}
    defauts.update({c: str(X.loc[masque_final, c].mode()[0]) for c in COL_CAT})
    joblib.dump({"pipeline": modele, "seuil": seuil, "colonnes": COL_NUM + COL_CAT, "defauts": defauts,
                 "annees_apprentissage": annees_train + [annee_val], "annee_test": annee_test},
                SORTIE / "modele_gravite.joblib")
    resume = {"annees_apprentissage": annees_train, "annee_validation": annee_val, "annee_test": annee_test,
              "seuil": round(seuil, 3), "validation": mesures_val, "test": mesures_test,
              "variables_importantes": importances.head(8).round(4).to_dict()}
    (SORTIE / "metriques.json").write_text(json.dumps(resume, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n===== RÉSUMÉ =====")
    print(json.dumps(resume, indent=2, ensure_ascii=False))
    return resume


if __name__ == "__main__":
    entrainer(lire_table())
