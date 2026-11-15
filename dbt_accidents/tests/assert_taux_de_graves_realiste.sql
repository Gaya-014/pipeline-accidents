-- Contrôle de bon sens : la part de personnes graves doit rester entre 5 % et 40 %
-- (elle vaut environ 18 % en 2023). Un test qui échoue ici = quelque chose a mal tourné dans le nettoyage.
select annee, avg(grave) as taux
from {{ ref('accidents_usagers') }}
group by annee
having avg(grave) not between 0.05 and 0.40
