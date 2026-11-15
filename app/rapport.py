"""Textes, HTML et styles de la page. Aucune dépendance à Streamlit : ce fichier se teste seul."""

FOND, SURFACE, LIGNE, TEXTE, DOUX = "#0D1520", "#162131", "#263548", "#EEF2F7", "#9AABBD"
ROUGE, AMBRE, ARDOISE, CLAIR, BLEU = "#FF5C4D", "#FFB020", "#35495F", "#DDE6F0", "#6F8BA8"
FIN = " "  # espace fine insécable

NOMS = {
    "secu1": "Équipement de sécurité (1er)", "secu2": "Équipement de sécurité (2e)",
    "locp": "Position du piéton", "obs": "Obstacle fixe heurté", "obsm": "Obstacle mobile heurté",
    "age": "Âge", "col": "Type de collision", "vma": "Vitesse maximale autorisée",
    "catv": "Catégorie de véhicule", "manv": "Manœuvre avant l'accident", "choc": "Point de choc initial",
    "place": "Place dans le véhicule", "heure": "Heure", "catu": "Type d'usager", "lum": "Luminosité",
    "actp": "Action du piéton", "senc": "Sens de circulation", "motor": "Motorisation", "catr": "Type de route",
    "atm": "Conditions météo", "agg": "Agglomération", "int": "Type d'intersection", "mois": "Mois",
    "jour_semaine": "Jour de la semaine", "trajet": "Motif du trajet", "sexe": "Sexe", "nbv": "Nombre de voies",
    "circ": "Régime de circulation", "vosp": "Voie réservée", "prof": "Profil de la route",
    "plan": "Tracé de la route", "surf": "État de la surface", "infra": "Infrastructure", "situ": "Situation",
}
ETATS = ["La réalité", "Les alertes du modèle", "Les deux ensemble"]


def nom(code):
    return NOMS.get(code, code)


def nb(n):
    return f"{int(round(n)):,}".replace(",", FIN)


def dec(x, d=3):
    return f"{x:.{d}f}".replace(".", ",")


def pct(x):
    return f"{round(x * 100)}{FIN}%"


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Condensed:wght@600;700;800&display=swap');
[data-testid="stAppDeployButton"], #MainMenu, footer {display:none !important;}
.stApp, div[data-testid="stMarkdownContainer"] p, label, .stSelectbox, .stSlider {font-family: 'Barlow', 'Helvetica Neue', Arial, sans-serif;}
.block-container {max-width: 1000px !important; padding-top: 3rem !important; padding-bottom: 6rem !important;}
div[data-testid="stMarkdownContainer"] h1, div[data-testid="stMarkdownContainer"] h2, .grand {
  font-family: 'Barlow Condensed', 'Arial Narrow', Impact, sans-serif !important; color: #EEF2F7; }
div[data-testid="stMarkdownContainer"] h1 {font-size: 4.3rem !important; line-height: .98 !important; font-weight: 800 !important;
  letter-spacing: -0.005em; margin: 0 0 1.4rem 0 !important; padding: 0 !important; max-width: 13em;}
div[data-testid="stMarkdownContainer"] h2 {font-size: 2.7rem !important; line-height: 1.02 !important; font-weight: 700 !important;
  margin: 5rem 0 1rem 0 !important; padding: 0 !important; max-width: 16em;}
div[data-testid="stMarkdownContainer"] p {font-size: 1.22rem; line-height: 1.7; max-width: 36em; color: #DCE4ED;}
div[data-testid="stMarkdownContainer"] p.chapo {font-size: 1.4rem !important; line-height: 1.55 !important; max-width: 32em !important; color: #EEF2F7;}
div[data-testid="stMarkdownContainer"] p.legende {font-size: 1.02rem !important; color: #9AABBD; line-height: 1.55 !important;}
div[data-testid="stMarkdownContainer"] p.etat {font-family:'Barlow Condensed',sans-serif; font-size: 1.9rem !important; font-weight: 600; line-height: 1.15 !important; margin: 1.1rem 0 .3rem 0; color:#EEF2F7;}
div[role="radiogroup"] label p {font-size: 1.1rem !important; font-weight: 500;}

/* champ de points : 1 point = environ 126 personnes */
.champ {display:grid; grid-template-columns: repeat(50, 1fr); gap: .3rem; margin: 1.2rem 0 .4rem 0;}
.champ i {display:block; aspect-ratio: 1; border-radius: 50%; background:#35495F; opacity:0;
  animation: apparait .45s ease forwards; animation-delay: calc(var(--i) * 1.1ms);}
.champ i.tp {background: var(--tp);} .champ i.fn {background: var(--fn);} .champ i.fp {background: var(--fp);} .champ i.tn {background: #35495F;}
.champ.e0 {--tp:#FF5C4D; --fn:#FF5C4D; --fp:#35495F;}
.champ.e1 {--tp:#FFB020; --fn:#35495F; --fp:#FFB020;}
.champ.e2 {--tp:#FFB020; --fn:#FF5C4D; --fp:#DDE6F0;}
@keyframes apparait {to {opacity: 1;}}
@media (prefers-reduced-motion: reduce) {.champ i {animation: none; opacity: 1;}}
.cles {display:flex; flex-wrap:wrap; gap: .5rem 1.6rem; font-size: 1.08rem; color:#DCE4ED; margin: .6rem 0 0 0;}
.cles span {display:inline-flex; align-items:center; gap:.5rem;}
.cles b {display:inline-block; width:.95rem; height:.95rem; border-radius:50%;}

/* gros chiffres */
.chiffre {font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size: 7.5rem; line-height: .86; letter-spacing:-.01em; margin: 0 0 .6rem -.04em;}
.chiffre.amb {color:#FFB020;} .chiffre.cl {color:#DDE6F0;}
.chiffre-texte {font-size: 1.2rem; line-height:1.55; max-width: 17em; color:#DCE4ED; margin:0;}

/* barres comparées */
.cmp {margin: 1.4rem 0 .4rem 0; max-width: 40rem;}
.cmp .metrique {font-size:1.12rem; font-weight:600; margin: 1.5rem 0 .4rem 0; color:#EEF2F7;}
.cmp .ligne {display:grid; grid-template-columns: 9.5rem 1fr 3.6rem; align-items:center; gap:.7rem; margin:.28rem 0; font-size:1.02rem; color:#9AABBD;}
.cmp .piste {height:.95rem; background:#162131;}
.cmp .piste span {display:block; height:100%;}
.cmp .val {text-align:right; font-variant-numeric: tabular-nums; color:#EEF2F7; font-weight:600;}

/* importance des variables */
.imp {margin: 1.4rem 0; max-width: 46rem;}
.imp .ligne {display:grid; grid-template-columns: 15rem 1fr 3.6rem; align-items:center; gap:.9rem; margin:.4rem 0; font-size:1.08rem;}
.imp .piste {height:1.15rem; background:#162131;}
.imp .piste span {display:block; height:100%; background:#6F8BA8;}
.imp .ligne:first-child .piste span {background:#FFB020;}
.imp .val {text-align:right; font-variant-numeric: tabular-nums; font-weight:600;}

/* estimation : route et verdict */
.panneau {background:#162131; padding: 1.8rem 1.8rem 1.4rem 1.8rem;}
.panneau .score {font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:5.6rem; line-height:.9; margin:0;}
.panneau .verdict {font-family:'Barlow Condensed',sans-serif; font-weight:600; font-size:1.9rem; line-height:1.1; margin:.5rem 0 0 0;}
.route {position:relative; height: 1.9rem; background:#0D1520; margin: 2.2rem 0 3.4rem 0;}
.route::before {content:""; position:absolute; left:0; right:0; top:calc(50% - 2px); height:4px;
  background: repeating-linear-gradient(90deg, #FFB020 0 18px, transparent 18px 36px); opacity:.85;}
.route .vehicule {position:absolute; top:50%; width:1.7rem; height:1.7rem; border-radius:50%; transform:translate(-50%,-50%); border:3px solid #0D1520;}
.route .seuil {position:absolute; top:-.7rem; bottom:-.7rem; width:3px; background:#EEF2F7;}
.route .seuil span {position:absolute; top:100%; left:50%; transform:translateX(-50%); font-size:.95rem; white-space:nowrap; margin-top:.2rem; color:#EEF2F7;}

/* frise des années */
.annees {display:flex; align-items:flex-end; gap: 1.4rem; margin: 1.6rem 0 .6rem 0; max-width: 46rem;}
.annees .an {flex:1; display:flex; flex-direction:column; align-items:stretch; text-align:center;}
.annees .n {font-size:.98rem; color:#9AABBD; margin-bottom:.3rem; font-variant-numeric: tabular-nums;}
.annees .col {display:flex; flex-direction:column; background:#35495F;}
.annees .col b {display:block; background:#FF5C4D;}
.annees .a {font-family:'Barlow Condensed',sans-serif; font-size:1.7rem; font-weight:700; margin-top:.4rem;}
.annees .tx {font-size:.98rem; color:#FF8A7E;}

@media (max-width: 760px) {
  div[data-testid="stMarkdownContainer"] h1 {font-size: 2.9rem !important;}
  div[data-testid="stMarkdownContainer"] h2 {font-size: 2.1rem !important; margin-top: 3.4rem !important;}
  .champ {grid-template-columns: repeat(25, 1fr);} .chiffre {font-size: 5.6rem;}
  .imp .ligne {grid-template-columns: 1fr 3.4rem; gap:.2rem .6rem;} .imp .ligne .piste {grid-column: 1 / -1; order: 3;}
  .cmp .ligne {grid-template-columns: 7.2rem 1fr 3.4rem;} .annees {gap:.6rem;}
}
</style>
"""


def repartition(t, total=1000):
    """Ramène les 4 cases de la matrice de confusion à `total` points (méthode du plus fort reste)."""
    vals = {k: t[k] for k in ("tp", "fn", "fp", "tn")}
    s = sum(vals.values())
    brut = {k: v * total / s for k, v in vals.items()}
    base = {k: int(b) for k, b in brut.items()}
    for k in sorted(brut, key=lambda k: brut[k] - base[k], reverse=True)[: total - sum(base.values())]:
        base[k] += 1
    return base


def champ(c, etat):
    ordre = {0: ["tp", "fn", "fp", "tn"], 1: ["tp", "fp", "fn", "tn"], 2: ["tp", "fn", "fp", "tn"]}[etat]
    points = "".join(f'<i class="{k}" style="--i:{i}"></i>' for i, k in enumerate(k for k in ordre for _ in range(c[k])))
    return f'<div class="champ e{etat}" role="img" aria-label="1000 points représentant 1000 personnes">{points}</div>'


def cles(c, etat):
    def p(couleur, texte):
        return f'<span><b style="background:{couleur}"></b>{texte}</span>'
    if etat == 0:
        elements = [p(ROUGE, f"{c['tp'] + c['fn']} tuées ou hospitalisées"), p(ARDOISE, f"{c['fp'] + c['tn']} indemnes ou légèrement blessées")]
    elif etat == 1:
        elements = [p(AMBRE, f"{c['tp'] + c['fp']} alertes du modèle"), p(ARDOISE, f"{c['fn'] + c['tn']} personnes sans alerte")]
    else:
        elements = [p(AMBRE, f"{c['tp']} cas graves détectés"), p(ROUGE, f"{c['fn']} cas graves manqués"),
                    p(CLAIR, f"{c['fp']} fausses alertes"), p(ARDOISE, f"{c['tn']} personnes justement écartées")]
    return '<div class="cles">' + "".join(elements) + "</div>"


def phrase_etat(m, c, etat):
    annee = m["annee_test"]
    return [
        f"{c['tp'] + c['fn']} personnes sur 1 000 ont été tuées ou hospitalisées en {annee}.",
        f"Le modèle a déclenché {c['tp'] + c['fp']} alertes sur ces 1 000 personnes.",
        f"Sur {c['tp'] + c['fn']} cas graves, il en voit {c['tp']} et en rate {c['fn']}, et il se trompe sur {c['fp']} personnes.",
    ][etat]


def textes(m, c):
    t = m["test"]
    graves, alertes = t["tp"] + t["fn"], t["tp"] + t["fp"]
    return {
        "titre": f"Sur 1{FIN}000 personnes impliquées dans un accident, {c['tp'] + c['fn']} sont tuées ou hospitalisées",
        "chapo": (f"Chiffres de {m['annee_test']}, tirés des {nb(t['personnes'])} personnes recensées par l'ONISR. Un modèle appris sur "
                  f"{m['annees_apprentissage'][0]}-{m['annee_validation']} devait retrouver les cas graves sans avoir jamais vu cette année. "
                  f"Voici ce qu'il a vu, et ce qu'il a raté."),
        "echelle": f"Un point représente environ {nb(t['personnes'] / 1000)} personnes de {m['annee_test']}.",
        "h_bilan": "Ce que le modèle trouve, ce qu'il signale à tort",
        "rappel": pct(t["recall"]),
        "t_rappel": f"des cas graves sont détectés : {nb(t['tp'])} sur {nb(graves)}. Les {nb(t['fn'])} autres passent sous le radar.",
        "juste": pct(t["precision"]),
        "t_juste": (f"des alertes sont justes : {nb(t['tp'])} sur {nb(alertes)}. Le seuil de décision ({dec(m['seuil'], 2)}) a été fixé sur "
                    f"{m['annee_validation']} pour équilibrer les deux erreurs, puis laissé tel quel."),
        "accuracy": (f"Le taux de bonnes réponses ({pct(t['accuracy'])}) ne dit presque rien ici : un modèle qui répondrait toujours « pas grave » "
                     f"en obtiendrait {pct(t['accuracy_toujours_pas_grave'])}, parce que seulement {pct(t['taux_de_graves'])} des cas sont graves."),
        "h_stable": "Le résultat tient d'une année à l'autre",
        "p_stable": (f"Le seuil de décision a été choisi sur {m['annee_validation']}. Les scores sur {m['annee_test']}, année gardée de côté "
                     f"jusqu'au bout, en sont très proches : rien n'indique que le modèle ait mémorisé les particularités d'une année. "
                     f"Pour la PR-AUC, le hasard donnerait {dec(t['taux_de_graves'], 2)}."),
    }


def comparaison(m):
    v, t = m["validation"], m["test"]
    blocs = ""
    for lib, k in [("PR-AUC", "pr_auc"), ("Rappel : cas graves détectés", "recall"), ("Précision : alertes justes", "precision"), ("F1", "f1")]:
        blocs += f'<div class="metrique">{lib}</div>'
        for nom_, val, couleur in [(f"Validation {m['annee_validation']}", v[k], BLEU), (f"Test {m['annee_test']}", t[k], AMBRE)]:
            blocs += (f'<div class="ligne"><span>{nom_}</span><span class="piste"><span style="width:{val * 100:.1f}%;background:{couleur}"></span></span>'
                      f'<span class="val">{dec(val)}</span></div>')
    return f'<div class="cmp">{blocs}</div>'


def importance(serie, n=10):
    top = serie.head(n)
    lignes = "".join(
        f'<div class="ligne"><span>{nom(code)}</span><span class="piste"><span style="width:{val / top.max() * 100:.1f}%"></span></span>'
        f'<span class="val">{dec(val)}</span></div>' for code, val in top.items())
    return f'<div class="imp">{lignes}</div>'


def titre_importance(serie):
    return f"« {nom(serie.index[0])} » pèse {dec(serie.iloc[0] / serie.iloc[1], 1)} fois plus que « {nom(serie.index[1]).lower()} »"


def route(score, seuil):
    couleur = ROUGE if score >= seuil else BLEU
    return (f'<div class="route" role="img" aria-label="Score {dec(score, 2)}, seuil {dec(seuil, 2)}">'
            f'<div class="seuil" style="left:{min(seuil, 1) * 100:.1f}%"><span>seuil {dec(seuil, 2)}</span></div>'
            f'<div class="vehicule" style="left:{min(max(score, 0.02), 0.98) * 100:.1f}%;background:{couleur}"></div></div>')


def panneau(score, seuil):
    alerte = score >= seuil
    couleur = ROUGE if alerte else TEXTE
    verdict = "Le modèle déclenche une alerte" if alerte else "Le modèle ne déclenche pas d'alerte"
    return (f'<div class="panneau"><p class="score" style="color:{couleur}">{dec(score, 2)}</p>'
            f'<p class="verdict">{verdict}</p>{route(score, seuil)}'
            f'<p class="legende" style="margin:0 !important">Le score n\'est pas une probabilité : le modèle donne plus de poids aux cas graves '
            f'à l\'entraînement. Il sert à classer les profils entre eux.</p></div>')


def frise_annees(annees):
    maxi = max(n for _, n, _ in annees)
    cols = ""
    for a, n, tx in annees:
        h = 3 + 8 * n / maxi
        cols += (f'<div class="an"><span class="n">{nb(n)}</span><span class="col" style="height:{h:.2f}rem"><b style="height:{float(tx) * 100:.1f}%"></b></span>'
                 f'<span class="a">{a}</span><span class="tx">{dec(float(tx) * 100, 1)}{FIN}% graves</span></div>')
    return f'<div class="annees">{cols}</div>'
