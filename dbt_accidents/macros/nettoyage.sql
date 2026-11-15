{# Macros de conversion réutilisées par les modèles de staging #}

{# to_int : texte représentant un entier -> entier, sinon NULL (ex. '#VALEUR!' -> NULL) #}
{% macro to_int(col) -%}
    (case when trim({{ col }}) ~ '^-?[0-9]{1,9}$' then trim({{ col }})::integer end)
{%- endmacro %}

{# to_num : comme to_int, avec décimales à virgule acceptées ('5,5' -> 5.5) #}
{% macro to_num(col) -%}
    (case when replace(trim({{ col }}), ',', '.') ~ '^-?[0-9]{1,9}(\.[0-9]+)?$'
          then replace(trim({{ col }}), ',', '.')::numeric end)
{%- endmacro %}

{# code : normalise un code catégoriel en texte. '07' et '7' deviennent '7' (formats variables selon les années),
   les valeurs alphabétiques sont conservées, une valeur vide devient NULL #}
{% macro code(col) -%}
    (case when trim({{ col }}) ~ '^-?[0-9]{1,9}$' then (trim({{ col }})::integer)::text
          else nullif(trim({{ col }}), '') end)
{%- endmacro %}
