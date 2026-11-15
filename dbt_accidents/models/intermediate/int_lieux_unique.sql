-- Un seul lieu par accident : celui où la vitesse maximale autorisée est la plus élevée.
-- En cas d'égalité, la première ligne du fichier est retenue (même règle que dans le notebook).
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
