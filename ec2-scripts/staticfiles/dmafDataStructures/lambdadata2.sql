CREATE OR REPLACE VIEW lambdadata4 AS 
SELECT
  occurence
, actionitem
, wqf_time
, complexity
FROM
  (
   SELECT
     "count"(actionitem) occurence
   , actionitem
   , complexity
   FROM
     sctsinglecsv
   GROUP BY actionitem, complexity
)  sctsinglecsv
, sctwqfweightage
WHERE (sctsinglecsv.actionitem = sctwqfweightage.actioncode)

