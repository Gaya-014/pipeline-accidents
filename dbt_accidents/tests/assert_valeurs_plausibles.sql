-- Aucune valeur aberrante ne doit subsister dans la table finale.
select *
from {{ ref('accidents_usagers') }}
where age < 0 or age > 100
   or heure < 0 or heure > 23
   or vma < 5 or vma > 130
   or nbv < 0 or nbv > 12
