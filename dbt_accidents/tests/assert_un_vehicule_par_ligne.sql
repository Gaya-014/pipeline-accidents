-- Un même véhicule (dans une même année) ne doit apparaître qu'une fois.
select id_vehicule, annee
from {{ ref('stg_vehicules') }}
group by id_vehicule, annee
having count(*) > 1
