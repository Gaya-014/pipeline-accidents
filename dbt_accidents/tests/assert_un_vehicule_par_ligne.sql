-- Un véhicule ne doit apparaître qu'une fois par année.
select id_vehicule, annee
from {{ ref('stg_vehicules') }}
group by id_vehicule, annee
having count(*) > 1
