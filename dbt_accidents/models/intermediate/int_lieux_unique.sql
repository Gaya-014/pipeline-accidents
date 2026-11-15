-- Un seul lieu par accident : celui où la vitesse maximale autorisée est la plus élevée.
-- (À égalité, je garde la première ligne du fichier. Même règle que dans mon notebook.)
select *
from (
    select
        *,
        row_number() over (
            partition by num_acc
            order by vma_brute desc nulls last, annee, ligne
        ) as rang
    from {{ ref('stg_lieux') }}
) as classes
where rang = 1
