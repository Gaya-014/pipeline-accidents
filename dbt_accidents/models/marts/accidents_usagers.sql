-- Table finale : une ligne par personne (dont on connaît la gravité), avec les infos de l'accident,
-- du lieu et du véhicule. C'est elle que le modèle de machine learning va lire.
with usagers as (
    select * from {{ ref('stg_usagers') }}
    where grav in ('1', '2', '3', '4')          -- je retire les personnes sans gravité renseignée
),

vehicules as (select * from {{ ref('stg_vehicules') }}),
carac     as (select * from {{ ref('stg_carac') }}),
lieux     as (select * from {{ ref('int_lieux_unique') }})

select
    u.annee,
    u.num_acc,
    u.id_vehicule,
    u.grav,
    case when u.grav in ('2', '3') then 1 else 0 end                         as grave,

    -- variables numériques (une valeur impossible devient NULL)
    case when c.an - u.an_nais between 0 and 100
         then (c.an - u.an_nais)::integer end                                as age,
    case when c.heure between 0 and 23 then c.heure end                      as heure,
    case when l.vma_brute between 5 and 130 then l.vma_brute end             as vma,
    case when l.nbv between 0 and 12 then l.nbv end                          as nbv,

    -- variables de catégories : '-1' veut dire "non renseigné" et reste une catégorie
    coalesce(u.place,  '-1')                                                 as place,
    coalesce(u.catu,   '-1')                                                 as catu,
    coalesce(u.sexe,   '-1')                                                 as sexe,
    coalesce(u.trajet, '-1')                                                 as trajet,
    coalesce(u.secu1,  '-1')                                                 as secu1,
    coalesce(u.secu2,  '-1')                                                 as secu2,
    coalesce(u.locp,   '-1')                                                 as locp,
    coalesce(u.actp,   '-1')                                                 as actp,
    coalesce(v.senc,   '-1')                                                 as senc,
    coalesce(v.catv,   '-1')                                                 as catv,
    coalesce(v.obs,    '-1')                                                 as obs,
    coalesce(v.obsm,   '-1')                                                 as obsm,
    coalesce(v.choc,   '-1')                                                 as choc,
    coalesce(v.manv,   '-1')                                                 as manv,
    coalesce(v.motor,  '-1')                                                 as motor,
    coalesce(c.lum,    '-1')                                                 as lum,
    coalesce(c.agg,    '-1')                                                 as agg,
    coalesce(c."int",  '-1')                                                 as "int",
    coalesce(c.atm,    '-1')                                                 as atm,
    coalesce(c."col",  '-1')                                                 as "col",
    coalesce(c.mois::text, '-1')                                             as mois,
    -- 0 = lundi ... 6 = dimanche, -1 si la date n'est pas valide
    coalesce((extract(isodow from c.date_accident) - 1)::integer::text, '-1') as jour_semaine,
    coalesce(l.catr,   '-1')                                                 as catr,
    coalesce(l.circ,   '-1')                                                 as circ,
    coalesce(l.vosp,   '-1')                                                 as vosp,
    coalesce(l.prof,   '-1')                                                 as prof,
    coalesce(l.plan,   '-1')                                                 as plan,
    coalesce(l.surf,   '-1')                                                 as surf,
    coalesce(l.infra,  '-1')                                                 as infra,
    coalesce(l.situ,   '-1')                                                 as situ

from usagers u
left join vehicules v on u.id_vehicule = v.id_vehicule and u.annee = v.annee
left join carac     c on u.num_acc = c.num_acc
left join lieux     l on u.num_acc = l.num_acc
