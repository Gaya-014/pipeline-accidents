-- Une ligne par accident. Conversion des textes bruts en types natifs.
with brut as (
    select
        trim(num_acc)                                as num_acc,
        annee,
        {{ to_int('jour') }}                         as jour,
        {{ to_int('mois') }}                         as mois,
        {{ to_int('an') }}                           as an,
        {{ to_int('substr(trim(hrmn), 1, 2)') }}     as heure,      -- '06:00' -> 6
        {{ code('lum') }}                            as lum,
        {{ code('agg') }}                            as agg,
        {{ code('"int"') }}                          as "int",
        {{ code('atm') }}                            as atm,
        {{ code('"col"') }}                          as "col"
    from {{ source('raw', 'carac') }}
)

select
    *,
    -- Date reconstituée uniquement si elle est valide (31 février -> NULL au lieu d'une erreur)
    case
        when an is not null and mois between 1 and 12 and jour between 1 and 31
             and pg_input_is_valid(
                 lpad(an::text, 4, '0') || '-' || lpad(mois::text, 2, '0') || '-' || lpad(jour::text, 2, '0'),
                 'date')
        then make_date(an, mois, jour)
    end as date_accident
from brut
