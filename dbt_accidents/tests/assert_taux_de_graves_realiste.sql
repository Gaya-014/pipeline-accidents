-- Contrôle de cohérence : la part de cas graves doit rester entre 5 % et 40 % (environ 18 % observé).
-- Un échec signale une anomalie dans le nettoyage ou les jointures.
select annee, avg(grave) as taux
from {{ ref('accidents_usagers') }}
group by annee
having avg(grave) not between 0.05 and 0.40
