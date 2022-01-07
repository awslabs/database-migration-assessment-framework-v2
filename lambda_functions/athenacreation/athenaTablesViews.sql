CREATE EXTERNAL TABLE `actionitemsummary`(
  `source` string COMMENT 'from deserializer', 
  `target` string COMMENT 'from deserializer', 
  `hostname` string COMMENT 'from deserializer', 
  `databasename` string COMMENT 'from deserializer', 
  `schemaname` string COMMENT 'from deserializer', 
  `actionitem` string COMMENT 'from deserializer', 
  `noocc` string COMMENT 'from deserializer', 
  `learncurve` string COMMENT 'from deserializer', 
  `effortper1` string COMMENT 'from deserializer')
ROW FORMAT SERDE 
  'org.apache.hadoop.hive.serde2.OpenCSVSerde' 
WITH SERDEPROPERTIES ( 
  'quoteChar'='\"', 
  'separatorChar'=',') 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://S3_BUCKET/actionitemsummary'
TBLPROPERTIES (
  'classification'='csv', 
  'skip.header.line.count'='1');

CREATE EXTERNAL TABLE `aggtbl`(
  `timestamp` string, 
  `databasename` string, 
  `schemaname` string, 
  `hostname` string, 
  `name` int, 
  `description` int, 
  `schemaname2` string, 
  `target` string, 
  `code_obj_conv_pcs` string, 
  `storage_obj_conv_pcs` string, 
  `syntax_obj_conv_pcs` string, 
  `schema_complexity` string,
  `customer` string,
  `batch` string
  )
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY ',' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://S3_BUCKET/aggregated'
TBLPROPERTIES (
  'classification'='csv', 
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1636643736');


CREATE EXTERNAL TABLE `msqlperftbl`(
  `host` string COMMENT 'from deserializer', 
  `database_name` string COMMENT 'from deserializer', 
  `banner` string COMMENT 'from deserializer', 
  `platform` string COMMENT 'from deserializer', 
  `isrds` string COMMENT 'from deserializer', 
  `rwiops` string COMMENT 'from deserializer', 
  `biops` string COMMENT 'from deserializer', 
  `cpu` string COMMENT 'from deserializer', 
  `memcache` string COMMENT 'from deserializer', 
  `physical_memory_mb` string COMMENT 'from deserializer', 
  `physical_memory_inuse_mb` string COMMENT 'from deserializer', 
  `max_cpu_pct` string COMMENT 'from deserializer', 
  `sizemb` string COMMENT 'from deserializer', 
  `version` string COMMENT 'from deserializer')
ROW FORMAT SERDE 
  'org.apache.hadoop.hive.serde2.OpenCSVSerde' 
WITH SERDEPROPERTIES ( 
  'quoteChar'='\"', 
  'separatorChar'=',') 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://S3_BUCKET/msqlperf'
TBLPROPERTIES (
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1640708825');

CREATE EXTERNAL TABLE `oraperftbl`(
  `host` string COMMENT 'from deserializer', 
  `database_name` string COMMENT 'from deserializer', 
  `platform_name` string COMMENT 'from deserializer', 
  `version` string COMMENT 'from deserializer', 
  `banner` string COMMENT 'from deserializer', 
  `rdiopsmax_hourly` string COMMENT 'from deserializer', 
  `rdiopsavg_hourly` string COMMENT 'from deserializer', 
  `wtiopsmax_hourly` string COMMENT 'from deserializer', 
  `wtiopsavg_hourly` string COMMENT 'from deserializer', 
  `rdbtpsmax_hourly` string COMMENT 'from deserializer', 
  `rdbtpsavg_hourly` string COMMENT 'from deserializer', 
  `wtbtpsmax_hourly` string COMMENT 'from deserializer', 
  `wtbtpsavg_hourly` string COMMENT 'from deserializer', 
  `hostcpupctmax_hourly` string COMMENT 'from deserializer', 
  `hostcpupctavg_hourly` string COMMENT 'from deserializer', 
  `redobtpsmax_hourly` string COMMENT 'from deserializer', 
  `redobtpsavg_hourly` string COMMENT 'from deserializer', 
  `cpusocket` string COMMENT 'from deserializer', 
  `cpucore` string COMMENT 'from deserializer', 
  `cpunumber` string COMMENT 'from deserializer', 
  `rammb` string COMMENT 'from deserializer', 
  `sgamb` string COMMENT 'from deserializer', 
  `pgamb` string COMMENT 'from deserializer', 
  `tbsizeusedmb` string COMMENT 'from deserializer', 
  `collected` string COMMENT 'from deserializer')
ROW FORMAT SERDE 
  'org.apache.hadoop.hive.serde2.OpenCSVSerde' 
WITH SERDEPROPERTIES ( 
  'quoteChar'='\"', 
  'separatorChar'=',') 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://S3_BUCKET/oraperf'
TBLPROPERTIES (
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1633504903');

CREATE EXTERNAL TABLE `rdslookup`(
`instance_category` string,
  `instance_type` string, 
  `vcpu` string, 
  `memory` string, 
  `bandwidth` string, 
  `monthly_price` string
 )
 ROW FORMAT SERDE 
  'org.apache.hadoop.hive.serde2.OpenCSVSerde' 
WITH SERDEPROPERTIES ( 
  'quoteChar'='\"', 
  'separatorChar'=',') 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://S3_BUCKET/instancelookup'
TBLPROPERTIES (
  'classification'='csv', 
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1636643733');

CREATE EXTERNAL TABLE `sctpdf`(
  `hostname` string COMMENT 'from deserializer', 
  `databasename` string COMMENT 'from deserializer', 
  `schemaname` string COMMENT 'from deserializer', 
  `source` string COMMENT 'from deserializer', 
  `target` string COMMENT 'from deserializer', 
  `path` string COMMENT 'from deserializer')
ROW FORMAT SERDE 
  'org.apache.hadoop.hive.serde2.OpenCSVSerde' 
WITH SERDEPROPERTIES ( 
  'quoteChar'='\"', 
  'separatorChar'=',') 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://S3_BUCKET/assmnt2pdfmap'
TBLPROPERTIES (
  'classification'='csv', 
  'skip.header.line.count'='1');

CREATE EXTERNAL TABLE `sctsinglescv`(
  `source` string COMMENT 'from deserializer', 
  `target` string COMMENT 'from deserializer', 
  `hostname` string COMMENT 'from deserializer', 
  `databasename` string COMMENT 'from deserializer', 
  `schemaname` string COMMENT 'from deserializer', 
  `category` string COMMENT 'from deserializer', 
  `occurrence` string COMMENT 'from deserializer', 
  `actionitem` string COMMENT 'from deserializer', 
  `subject` string COMMENT 'from deserializer', 
  `group` string COMMENT 'from deserializer', 
  `description` string COMMENT 'from deserializer', 
  `document` string COMMENT 'from deserializer', 
  `recommendedaction` string COMMENT 'from deserializer', 
  `filtered` string COMMENT 'from deserializer', 
  `complexity` string COMMENT 'from deserializer', 
  `line` string COMMENT 'from deserializer', 
  `position` string COMMENT 'from deserializer')
ROW FORMAT SERDE 
  'org.apache.hadoop.hive.serde2.OpenCSVSerde' 
WITH SERDEPROPERTIES ( 
  'quoteChar'='\"', 
  'separatorChar'=',') 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://S3_BUCKET/sctfile'
TBLPROPERTIES (
  'classification'='csv', 
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1632394302');

CREATE EXTERNAL TABLE `sctsummarycsv`(
  `source` string COMMENT 'from deserializer', 
  `target` string COMMENT 'from deserializer', 
  `banner` string COMMENT 'from deserializer', 
  `hostname` string COMMENT 'from deserializer', 
  `databasename` string COMMENT 'from deserializer', 
  `schemaname` string COMMENT 'from deserializer', 
  `category` string COMMENT 'from deserializer', 
  `noobj` string COMMENT 'from deserializer', 
  `autoconverted` string COMMENT 'from deserializer', 
  `simple` string COMMENT 'from deserializer', 
  `medium` string COMMENT 'from deserializer', 
  `complex` string COMMENT 'from deserializer', 
  `totallinescode` string COMMENT 'from deserializer')
ROW FORMAT SERDE 
  'org.apache.hadoop.hive.serde2.OpenCSVSerde' 
WITH SERDEPROPERTIES ( 
  'quoteChar'='\"', 
  'separatorChar'=',') 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://S3_BUCKET/reportsummary'
TBLPROPERTIES (
  'classification'='csv', 
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1632475163');

CREATE EXTERNAL TABLE `sctwqfweightage`(
  `source` string, 
  `target` string, 
  `actioncode` string, 
  `wqf_time` double, 
  `feature` string, 
  `exceptiondetails` string)
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY ',' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://S3_BUCKET/wqfestimatedefault/'
TBLPROPERTIES (
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1633352651');

CREATE EXTERNAL TABLE `sctwqfweightage2exceptions`(
  `actionitem` string, 
  `eeteffort` double, 
  `limit` int, 
  `description` string)
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY ',' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://S3_BUCKET/wqf2/'
TBLPROPERTIES (
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1632997624');

CREATE EXTERNAL TABLE `urldocumentation`(
  `name` string, 
  `link` string)
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY ',' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://S3_BUCKET/documenturls/'
TBLPROPERTIES (
  'classification'='csv', 
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1633411104');


CREATE OR REPLACE VIEW instancelookup AS 
SELECT
instance_category
,  instance_type
, CAST(vcpu AS bigint) vcpu
, CAST(memory AS bigint) memory
, CAST(REPLACE(REPLACE(LOWER(bandwidth),'up to ',''),',','') AS bigint) bandwidth
FROM
  rdslookup;

CREATE OR REPLACE VIEW vw_actionitemsummary AS 
SELECT
  "upper"("replace"(source, ' ', '')) source
, "upper"("replace"(target, ' ', '')) target
, "upper"("replace"(hostname, ' ', '')) hostname
, "upper"("replace"(databasename, ' ', '')) databasename
, "replace"("upper"("substr"(schemaname, ("strpos"(schemaname, ',') + 1), "length"(schemaname))), ' ', '') schemaname
, actionitem
, noocc
, learncurve
, effortper1
FROM
  actionitemsummary;


CREATE OR REPLACE VIEW msqlperfdata AS 
WITH
  p AS (
   SELECT
     host
   , database_name
   , banner
   , platform
   , isrds  
   , rwiops
   , biops
   , cpu
   , memcache
   , physical_memory_mb
   , physical_memory_inuse_mb
   , max_cpu_pct
   , sizemb
   , version
   FROM
     msqlperftbl
) 
SELECT DISTINCT
  host
, database_name
, banner
, platform
, isrds
, "round"(CAST(NULLIF(rwiops, '') AS double), 4) rwiops
, "round"(CAST(NULLIF(biops, '') AS double), 4) biops
, CAST(NULLIF(cpu, '') AS double) cpu
, "round"(CAST(NULLIF(memcache, '') AS double), 4) memcache
, CAST(NULLIF(physical_memory_mb, '') AS double) physical_memory_mb
, CAST(NULLIF(physical_memory_inuse_mb, '') AS double) physical_memory_inuse_mb
, "round"(CAST(NULLIF(max_cpu_pct, '') AS double), 4) max_cpu_pct
, CAST(NULLIF(sizemb, '') AS double) sizemb
, version
FROM
  p;

CREATE OR REPLACE VIEW oraperfdata AS 
WITH
  p AS (
   SELECT
     host
   , database_name
   , platform_name
   , version
   , banner
   , rdiopsmax_hourly
   , rdiopsavg_hourly
   , wtiopsmax_hourly
   , wtiopsavg_hourly
   , rdbtpsmax_hourly
   , rdbtpsavg_hourly
   , wtbtpsmax_hourly
   , wtbtpsavg_hourly
   , hostcpupctmax_hourly
   , hostcpupctavg_hourly
   , redobtpsmax_hourly
   , redobtpsavg_hourly
   , cpusocket
   , cpucore
   , cpunumber
   , rammb
   , sgamb
   , pgamb
   , tbsizeusedmb
   , collected
   FROM
     oraperftbl
) 
SELECT
  host
, database_name
, platform_name
, version
, banner
, CAST(NULLIF(rdiopsmax_hourly, '') AS double) rdiopsmax_hourly
, CAST(NULLIF(rdiopsavg_hourly, '') AS double) rdiopsavg_hourly
, CAST(NULLIF(wtiopsmax_hourly, '') AS double) wtiopsmax_hourly
, CAST(NULLIF(wtiopsavg_hourly, '') AS double) wtiopsavg_hourly
, CAST(NULLIF(rdbtpsmax_hourly, '') AS double) rdbtpsmax_hourly
, CAST(NULLIF(rdbtpsavg_hourly, '') AS double) rdbtpsavg_hourly
, CAST(NULLIF(wtbtpsmax_hourly, '') AS double) wtbtpsmax_hourly
, CAST(NULLIF(wtbtpsavg_hourly, '') AS double) wtbtpsavg_hourly
, CAST(NULLIF(hostcpupctmax_hourly, '') AS double) hostcpupctmax_hourly
, CAST(NULLIF(hostcpupctavg_hourly, '') AS double) hostcpupctavg_hourly
, CAST(NULLIF(redobtpsmax_hourly, '') AS double) redobtpsmax_hourly
, CAST(NULLIF(redobtpsavg_hourly, '') AS double) redobtpsavg_hourly
, CAST(NULLIF(cpusocket, '') AS bigint) cpusocket
, CAST(NULLIF(cpucore, '') AS bigint) cpucore
, CAST(NULLIF(cpunumber, '') AS bigint) cpunumber
, CAST(NULLIF(rammb, '') AS double) rammb
, CAST(NULLIF(sgamb, '') AS double) sgamb
, CAST(NULLIF(pgamb, '') AS double) pgamb
, CAST(NULLIF(tbsizeusedmb, '') AS bigint) tbsizeusedmb
, collected
FROM
  p;

CREATE OR REPLACE VIEW performanceview AS 
SELECT
  host_name "host"
, database_name
, "instance_type_aws" "instance_type"
, instance_category
, "cpu_prem_count" "cpu_prem"
, "cpu_aws_count" "cpu_aws"
, "memory_prem_gb" "memory_prem"
, "memory_aws_gb" "memory_aws"
, "bandwidth_prem_mbps" "iops"
, "bandwidth_aws_mbps" max_bandwidth
, "db_size_gb" "size_gb"
FROM
  (
   SELECT
     "host_name"
   , "replace"("database_name", '"', '') "database_name"
   , "memory_prem_gb"
   , "i"."memory" "memory_aws_gb"
   , ("i"."memory" - "memory_prem_gb") "mem_diff"
   , "cpu_prem_count"
   , "i"."vcpu" "cpu_aws_count"
   , ("i"."vcpu" - "cpu_prem_count") "cpu_diff"
   , "bandwidth_prem_mbps"
   , "i"."bandwidth" "bandwidth_aws_mbps"
   , ("i"."bandwidth" - "d"."bandwidth_prem_mbps") "bandwith_diff"
   , "db_size_gb"
   , "i"."instance_type" "instance_type_aws"
   , i.instance_category
   , "rank"() OVER (PARTITION BY "database_name", "host_name" ORDER BY ("i"."vcpu" - "cpu_prem_count") ASC, ("i"."memory" - "memory_prem_gb") ASC, ("i"."bandwidth" - "bandwidth_prem_mbps") ASC) "rnk"
   FROM
     (
      SELECT
        "p"."host_name"
      , "p"."database_name"
      , "round"(("sum"(((("cpunumber" * "cpupct") / 1E2) / "cpu_weight")) * 1.2E0), 2) "cpu_prem_count"
      , "round"(("sum"(("db_memory_mb" / 1.024E3)) * 1.2E0), 2) "memory_prem_gb"
      , "round"("max"((("db_sizeusage_mb" / 1.024E3) * 1.2E0)), 2) "db_size_gb"
      , "round"(("sum"("db_bandwidth_prem_mbps") * 1.2E0), 0) "bandwidth_prem_mbps"
      FROM
        (
         SELECT
           "database_name"
         , "host_name"
         , "cpunumber"
         , "db_sizeusage_mb"
         , "hostcpupctmax_hourly" "cpupct"
         , "db_memory_mb"
         FROM
           (
            SELECT DISTINCT
              "database_name"
            , host "host_name"
            , "hostcpupctmax_hourly"
            , (CASE "cpunumber" WHEN 0 THEN 1 ELSE "cpunumber" END) "cpunumber"
            , "row_number"() OVER (PARTITION BY "database_name", "host" ORDER BY ("hostcpupctmax_hourly" * (CASE "cpunumber" WHEN 0 THEN 1 ELSE "cpunumber" END)) DESC) "rn"
            , "count"(*) OVER (PARTITION BY "database_name", "host") "cnt"
            , "max"(("sgamb" + "pgamb")) OVER (PARTITION BY "database_name", "host") "db_memory_mb"
            , "tbsizeusedmb" "db_sizeusage_mb"
            FROM
              oraperfdata
            WHERE ("lower"(banner) LIKE 'oracle database%')
         ) 
      )  p
      , (
         SELECT
           "database_name"
         , "host_name"
         , "db_bandwidth_prem_mbps"
         FROM
           (
            SELECT
              database_name
            , host "host_name"
            , (((("rdbtpsavg_hourly" + "wtbtpsavg_hourly") * 8) / 1024) / 1024) "db_bandwidth_prem_mbps"
            , "row_number"() OVER (PARTITION BY "database_name", "host" ORDER BY ("rdbtpsavg_hourly" + "wtbtpsavg_hourly") DESC) "rn"
            , "count"(*) OVER (PARTITION BY "database_name", "host") "cnt"
            FROM
              oraperfdata
            WHERE ("lower"(banner) LIKE 'oracle database%')
         ) 
      )  s
      , (
         SELECT
           host "host_name"
         , "count"(DISTINCT "database_name") "cpu_weight"
         FROM
           oraperfdata
         WHERE ("lower"(banner) LIKE 'oracle database%')
         GROUP BY "host"
      )  h
      WHERE ((("p"."database_name" = "s"."database_name") AND ("p"."host_name" = "s"."host_name")) AND ("p"."host_name" = "h"."host_name"))
      GROUP BY "p"."host_name", "p"."database_name"
   )  d
   , instancelookup i
   WHERE (((("i"."memory" - "d"."memory_prem_gb") >= 0) AND (("i"."vcpu" - "cpu_prem_count") >= 0)) AND (("i"."bandwidth" - "bandwidth_prem_mbps") >= 0))
) 
WHERE ("rnk" = 1)
UNION ALL
 select host,database_name ,instance_type , instance_category , 
 cpu "cpu_prem" , vcpu "cpu_aws" , physical_memory_mb/1024 as "memory_prem"  , memory  as "memory_aws" 
 ,round(((biops*60*60*8)/1024)/1024,0) "iops" , bandwidth "max_bandwidth" , sizemb/1024 as "size_gb" from  (select mssqlperf.*,
 "rank"() OVER (PARTITION BY "database_name", "host" ORDER BY cpudiff ASC, memorydiff ASC, tpdiff ASC) "rnk"
 from (select i.* ,a.*, ("i"."vcpu" -  a."cpu")  cpudiff, ("i"."memory" - (a.physical_memory_mb/1024)) memorydiff,("i"."bandwidth" - ((a.biops*60*60*8)/1024)/1024)
tpdiff
from (select distinct host , database_name , cpu , physical_memory_mb ,sum(sizemb) over (partition by host ) as "sizemb", SUM(round(((biops*60*60*8)/1024)/1024,0)) over (partition by host ) as biops
from msqlperfdata ) a  , instancelookup i
 WHERE ((("i"."memory" - (a.physical_memory_mb/1024))  >= 0) AND (("i"."vcpu" -  a."cpu") >= 0) AND (("i"."bandwidth" - ((a.biops*60*60*8)/1024)/1024) >= 0))  ) mssqlperf) 
 where rnk =1;





CREATE OR REPLACE VIEW vw_aggregated AS 
SELECT
  "upper"("substr"(target, ("strpos"(target, 'for') + 4))) target
, "upper"(hostname) hostname
, "upper"(databasename) databasename
, "upper"(schemaname) schemaname
, code_obj_conv_pcs
, storage_obj_conv_pcs
, syntax_obj_conv_pcs
, schema_complexity
, customer
, batch
FROM
  aggtbl;


CREATE OR REPLACE VIEW vw_sctsinglecsv AS 
(
   SELECT
     source
   , target
   , "upper"("replace"(hostname, ' ', '')) hostname
   , "upper"("replace"(databasename, ' ', '')) databasename
   , "upper"("replace"(schemaname, ' ', '')) schemaname
   , category
   , "count"(occurrence) occurrence
   , actionitem
   , subject
   , "group"
   , description
   , "replace"(document, 'http:', 'https:') document
   , recommendedaction
   , filtered
   , complexity
   FROM
     sctsinglescv
   GROUP BY source, target, hostname, databasename, schemaname, category, actionitem, subject, "group", description, document, recommendedaction, filtered, complexity
); 

CREATE OR REPLACE VIEW vw_sctwqf2exception AS 
SELECT
  actionitem
, eeteffort eeteffort2
, (eeteffort * limit) maxtime
, description
FROM
  sctwqfweightage2exceptions;

CREATE OR REPLACE VIEW vw_summary_agg AS 
WITH
  currated AS (
   SELECT
     source
   , target
   , (CASE WHEN ("banner" LIKE '%Microsoft%') THEN "substr"(banner, 1, ("strpos"(banner, ' - ') - 1)) WHEN ("banner" LIKE '%Oracle%') THEN "substr"(banner, 1, ("strpos"(banner, ',') - 1)) ELSE banner END) banner
   , "replace"(hostname, ' ', '') hostname
   , "replace"(databasename, ' ', '') databasename
   , "replace"(schemaname, ' ', '') schemaname
   , category
   , CAST(COALESCE(NULLIF(noobj, ''), '0') AS int) noobj
   , CAST(COALESCE(NULLIF(autoconverted, ''), '0') AS int) autoconverted
   , CAST(COALESCE(NULLIF(simple, ''), '0') AS int) simple
   , CAST(COALESCE(NULLIF(medium, ''), '0') AS int) medium
   , CAST(COALESCE(NULLIF(complex, ''), '0') AS int) complex
   , CAST(COALESCE(NULLIF(totallinescode, ''), '0') AS int) totallinescode
   FROM
     sctsummarycsv
   WHERE (NOT (category IN ('SQL_syntax_elements_number', 'Storage_objects_count', 'Code_objects_count')))
) 
SELECT
  "upper"(source) source
, "upper"(target) target
, "upper"(hostname) hostname
, "upper"(databasename) databasename
, "upper"(schemaname) schemaname
, banner
, "sum"(noobj) noobj
, "sum"(autoconverted) autoconverted
FROM
  currated
GROUP BY source, target, banner, hostname, databasename, schemaname;

CREATE OR REPLACE VIEW vw_urldocumentation AS 
SELECT
  name
, "replace"(link, 'https://', '') link
FROM
  "urldocumentation";

CREATE OR REPLACE VIEW vw_wqf_actionitemsummary AS 
WITH
  a AS (
   SELECT
     source
   , target
   , hostname
   , databasename
   , schemaname
   , category
   , actionitem
   , "sum"(occurrence) noocc
   FROM
     vw_sctsinglecsv
   GROUP BY source, target, hostname, databasename, schemaname, category, actionitem
) 
, efforts AS (
   SELECT
     a.source
   , a.target
   , "replace"(a.hostname, ' ', '') hostname
   , "replace"(a.databasename, ' ', '') databasename
   , "replace"(a.schemaname, ',', '.') schemaname
   , a.actionitem
   , a.category
   , CAST(a.noocc AS int) noocc
   , b.wqf_time
   , "round"((("ceiling"((CAST(a.noocc AS int) * 1E-1)) * b.wqf_time) + (((CAST(a.noocc AS int) - "ceiling"((CAST(a.noocc AS int) * 1E-1))) * b.wqf_time) * 5E-1)), 2) wqf_10_90
   , "round"((("ceiling"((CAST(a.noocc AS int) * 3E-1)) * b.wqf_time) + (((CAST(a.noocc AS int) - "ceiling"((CAST(a.noocc AS int) * 3E-1))) * b.wqf_time) * 5E-1)), 2) wqf_30_70
   , "round"((("ceiling"((CAST(a.noocc AS int) * 5E-1)) * b.wqf_time) + (((CAST(a.noocc AS int) - "ceiling"((CAST(a.noocc AS int) * 5E-1))) * b.wqf_time) * 5E-1)), 2) wqf_50_50
   , "round"(((("ceiling"((CAST(a.noocc AS int) * 1E-1)) * b.wqf_time) + (((CAST(a.noocc AS int) - "ceiling"((CAST(a.noocc AS int) * 1E-1))) * b.wqf_time) * 5E-1)) / CAST(a.noocc AS int)), 2) wqf_10_90_per
   , "round"(((("ceiling"((CAST(a.noocc AS int) * 3E-1)) * b.wqf_time) + (((CAST(a.noocc AS int) - "ceiling"((CAST(a.noocc AS int) * 3E-1))) * b.wqf_time) * 5E-1)) / CAST(a.noocc AS int)), 2) wqf_30_70_per
   , "round"(((("ceiling"((CAST(a.noocc AS int) * 5E-1)) * b.wqf_time) + (((CAST(a.noocc AS int) - "ceiling"((CAST(a.noocc AS int) * 5E-1))) * b.wqf_time) * 5E-1)) / CAST(a.noocc AS int)), 2) wqf_50_50_per
   FROM
     (a
   LEFT JOIN sctwqfweightage b ON (a.actionitem = b.actioncode))
) 
SELECT
  source
, target
, hostname
, databasename
, schemaname
, actionitem
, category
, "sum"(noocc) noocc
, wqf_time
, "round"("sum"(wqf_10_90), 2) wqf_10_90
, "round"("sum"(wqf_30_70), 2) wqf_30_70
, "round"("sum"(wqf_50_50), 2) wqf_50_50
, "round"(("sum"(wqf_10_90) / "sum"(noocc)), 2) wqf_10_90_per
, "round"(("sum"(wqf_30_70) / "sum"(noocc)), 2) wqf_30_70_per
, "round"(("sum"(wqf_50_50) / "sum"(noocc)), 2) wqf_50_50_per
FROM
  efforts
GROUP BY source, target, hostname, databasename, schemaname, actionitem, category, wqf_time;

CREATE OR REPLACE VIEW vw_datamart AS 
WITH
  cte1 AS (
   SELECT
     a.source
   , a.target
   , a.hostname
   , a.databasename
   , a.schemaname
   , a.category
   , a.actionitem
   , a.occurrence
   , d.wqf_10_90_per
   , d.wqf_30_70_per
   , d.wqf_50_50_per
   , a.subject
   , a."group"
   , a.description
   , "replace"("replace"(a.document, 'http://', ''), 'https://', '') document
   , a.recommendedaction
   , a.filtered
   , a.complexity
   , b.noobj
   , b.autoconverted
   , "replace"(b.banner, 'Production', '') banner
   , "replace"(c.path, 'https://', '') pdf_url
   FROM
     (((vw_sctsinglecsv a
   LEFT JOIN vw_summary_agg b ON (((((a.source = b.source) AND (a.target = b.target)) AND (a.hostname = b.hostname)) AND (a.databasename = b.databasename)) AND (a.schemaname = b.schemaname)))
   LEFT JOIN sctpdf c ON (((((a.source = "upper"(c.source)) AND (a.target = "upper"(c.target))) AND (a.hostname = "upper"("replace"(c.hostname, ' ', '')))) AND (a.databasename = "upper"("replace"(c.databasename, ' ', '')))) AND (a.schemaname = "upper"("replace"(c.schemaname, ' ', '')))))
   LEFT JOIN vw_wqf_actionitemsummary d ON (a.source = d.source) AND (a.target = d.target) AND (a.hostname = d.hostname) AND (a.databasename = d.databasename) AND (a.schemaname = d.schemaname) AND (a.actionitem = d.actionitem)  AND (a.category = d.category))
UNION ALL    
SELECT
     b.source
   , b.target
   , b.hostname
   , b.databasename
   , b.schemaname
   , null
   , null
   , null
   , 0
   , 0
   , 0
   , null
   , null
   , null
   , null
   , null
   , null
   , 'AutoConverted' complexity
   , 0 noobj
   , 0 autoconverted
   , "replace"(b.banner, 'Production', '') banner
   , "replace"(c.path, 'https://', '') pdf_url
   FROM
     (vw_summary_agg b
   LEFT JOIN sctpdf c ON (((((b.source = "upper"(c.source)) AND (b.target = "upper"(c.target))) AND (b.hostname = "upper"("replace"(c.hostname, ' ', '')))) AND (b.databasename = "upper"("replace"(c.databasename, ' ', '')))) AND (b.schemaname = "upper"("replace"(c.schemaname, ' ', '')))))
   WHERE ((noobj = autoconverted) AND (NOT (EXISTS (SELECT 1
FROM
  sctsinglescv a
WHERE (((((a.source = b.source) AND (a.target = b.target)) AND (a.hostname = b.hostname)) AND (a.databasename = b.databasename)) AND (a.schemaname = b.schemaname))
))))
) 
, autoconvertedagg AS (
   SELECT
     source
   , target
   , hostname
   , databasename
   , schemaname
   , '' category
   , '-10' actionitem
   , "sum"(autoconverted) occurrence
   , 0 wqf_10_90_per
   , 0 wqf_30_70_per
   , 0 wqf_50_50_per
   , '' subject
   , '' "group"
   , '' description
   , '' document
   , '' recommendedaction
   , '' filtered
   , 'AutoConverted' complexity
   , 0 noobj
   , 0 autoconverted
   , banner
   , pdf_url
   FROM
     cte1
   GROUP BY source, target, hostname, databasename, schemaname, banner, pdf_url
) 
, uniontable AS (
   SELECT *
   FROM
     cte1
UNION    SELECT *
   FROM
     autoconvertedagg
) 
SELECT
  u.*
  , "round"((u.occurrence * wqf_10_90_per), 2) wqf_10_90
, "round"((u.occurrence * wqf_30_70_per), 2) wqf_30_70
, "round"((u.occurrence * wqf_50_50_per), 2) wqf_50_50
, (CASE WHEN (agg.schema_complexity IN ('1', '2', '3')) THEN 'Easy' WHEN (agg.schema_complexity IN ('4', '5', '6')) THEN 'Medium' WHEN (agg.schema_complexity IN ('7', '8', '9')) THEN 'Complex' ELSE 'Very Complex' END) schema_complexity
, agg.code_obj_conv_pcs
, agg.storage_obj_conv_pcs
, agg.syntax_obj_conv_pcs
, agg.customer
, agg.batch
, exc.maxtime
, exc.eeteffort2
, COALESCE(p.instance_type, 'No Performance Data') recommended_instance
, COALESCE(p.instance_category, 'No Performance Data') recommended_instance_category
FROM
  (((uniontable u
LEFT JOIN vw_aggregated agg ON ((((u.target = agg.target) AND (u.databasename = "replace"(agg.databasename, ' ', ''))) AND (u.hostname = "replace"(agg.hostname, ' ', ''))) AND (u.schemaname = "replace"(agg.schemaname, ' ', ''))))
LEFT JOIN vw_sctwqf2exception exc ON (u.actionitem = exc.actionitem))
LEFT JOIN performanceview p ON ((u.hostname = "upper"("replace"(p.host, ' ', ''))) AND ("upper"(u.databasename) = "upper"("replace"(p.database_name, ' ', '')))));
