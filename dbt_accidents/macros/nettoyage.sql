{# Petites fonctions de nettoyage réutilisées dans tous les modèles #}

{# to_int : un texte qui est un entier -> entier, sinon NULL (ex : '#VALEUR!' devient NULL) #}
{% macro to_int(col) -%}
    (case when trim({{ col }}) ~ '^-?[0-9]{1,9}$' then trim({{ col }})::integer end)
{%- endmacro %}

{# to_num : comme to_int mais accepte les décimales avec virgule ('5,5' -> 5.5) #}
{% macro to_num(col) -%}
    (case when replace(trim({{ col }}), ',', '.') ~ '^-?[0-9]{1,9}(\.[0-9]+)?$'
          then replace(trim({{ col }}), ',', '.')::numeric end)
{%- endmacro %}

{# code : une catégorie en texte propre. '07' et '7' deviennent '7' (les années n'écrivent pas pareil),
   les lettres sont gardées, une case vide devient NULL #}
{% macro code(col) -%}
    (case when trim({{ col }}) ~ '^-?[0-9]{1,9}$' then (trim({{ col }})::integer)::text
          else nullif(trim({{ col }}), '') end)
{%- endmacro %}
