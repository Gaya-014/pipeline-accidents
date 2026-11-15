-- Une ligne par personne impliquée dans un accident.
select
    trim(num_acc)           as num_acc,
    trim(id_vehicule)       as id_vehicule,
    annee,
    {{ code('place') }}     as place,
    {{ code('catu') }}      as catu,
    {{ code('grav') }}      as grav,
    {{ code('sexe') }}      as sexe,
    {{ to_num('an_nais') }} as an_nais,
    {{ code('trajet') }}    as trajet,
    {{ code('secu1') }}     as secu1,
    {{ code('secu2') }}     as secu2,
    {{ code('locp') }}      as locp,
    {{ code('actp') }}      as actp
from {{ source('raw', 'usagers') }}
