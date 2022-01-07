CREATE OR REPLACE VIEW lambdadata3 AS 
SELECT
  host
, database
, schema
, occurence
, actionitem
, wqf_time
, complexity
FROM
  (
   SELECT
     host
   , database
   , schema
   , "count"(actionitem) occurence
   , actionitem
   , complexity
   FROM
     sctsinglecsv
   GROUP BY actionitem, complexity, host, database, schema
)  sctsinglecsv
, sctwqfweightage
WHERE (sctsinglecsv.actionitem = sctwqfweightage.actioncode)

