-- Une ligne par véhicule.
select
    trim(num_acc)           as num_acc,
    trim(id_vehicule)       as id_vehicule,
    annee,
    {{ code('senc') }}      as senc,
    {{ code('catv') }}      as catv,
    {{ code('obs') }}       as obs,
    {{ code('obsm') }}      as obsm,
    {{ code('choc') }}      as choc,
    {{ code('manv') }}      as manv,
    {{ code('motor') }}     as motor
from {{ source('raw', 'vehicules') }}
