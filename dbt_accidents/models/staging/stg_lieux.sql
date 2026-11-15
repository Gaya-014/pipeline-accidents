-- Une ligne par lieu (en 2023 certains accidents ont plusieurs lieux).
-- Seules les colonnes utiles à la modélisation sont conservées (pr, pr1, larrout, lartpc, v1, v2, voie écartées).
select
    trim(num_acc)           as num_acc,
    annee,
    ligne,                                   -- numéro de ligne dans le fichier d'origine
    {{ code('catr') }}      as catr,
    {{ code('circ') }}      as circ,
    {{ to_int('nbv') }}     as nbv,
    {{ code('vosp') }}      as vosp,
    {{ code('prof') }}      as prof,
    {{ code('plan') }}      as plan,
    {{ code('surf') }}      as surf,
    {{ code('infra') }}     as infra,
    {{ code('situ') }}      as situ,
    {{ to_int('vma') }}     as vma_brute     -- vitesse maximale autorisée, avant filtrage des valeurs aberrantes
from {{ source('raw', 'lieux') }}
