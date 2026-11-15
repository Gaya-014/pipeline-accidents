-- La table finale doit avoir autant de lignes que les usagers dont la gravité est connue.
-- Sinon une jointure a dupliqué ou perdu des personnes.
select *
from (
    select
        (select count(*) from {{ ref('stg_usagers') }} where grav in ('1', '2', '3', '4')) as attendu,
        (select count(*) from {{ ref('accidents_usagers') }})                              as obtenu
) as comparaison
where attendu <> obtenu
