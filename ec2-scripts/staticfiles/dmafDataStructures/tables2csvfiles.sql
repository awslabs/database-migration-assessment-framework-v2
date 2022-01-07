CREATE EXTERNAL TABLE `actioncodes`(
  `source` string, 
  `target` string, 
  `lo` int, 
  `hi` int)
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY ',' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION 
's3://' 
TBLPROPERTIES (
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1627837517')

create external table `sctactionitems` (
`source` string,
`target` string,
`Topic` string,
`Severity` string,
`ActionCode` string,
`ActionMessage` string,
`ActionItem` string,
`doclink` string,
`doclink2` string,
`etic` string)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
LOCATION
  's3://'  
TBLPROPERTIES (
  'skip.header.line.count'='1'
  )

CREATE EXTERNAL TABLE `actionitemsummary`(
  `host` string, 
  `database` string, 
  `schema` string, 
  `actionitem` string, 
  `number_of_occurrences` string, 
  `learning_curve_efforts` string, 
  `efforts_per_occurrence` string)
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY ',' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://'
TBLPROPERTIES (
  'has_encrypted_data'='false', 
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1627797793')

CREATE EXTERNAL TABLE `aggtbl`(
  `Time` timestamp,
  `host` string, 
  `name` string, 
  `description` string, 
  `schema_name` string, 
  `pgcocpct` string, 
  `pgsocpct` string, 
  `pgsecpct` string, 
  `pgcc` string, 
  `mycocpct` string, 
  `mysocpct` string, 
  `mysecpct` string, 
  `mycc` string)
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY ',' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION 
's3://'
TBLPROPERTIES (
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1627821103')

CREATE EXTERNAL TABLE `msqlperftbl`(
  `host` string, 
  `database` string, 
  `banner` string, 
  `platform` string, 
  `rwiops` string, 
  `biops` string, 
  `cpu` string, 
  `memcache` string, 
  `physical_memory_mb` string, 
  `max_cpu_pct` string, 
  `sizemb` string,
  `version` string,
  `collected` string)
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY ',' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://'
TBLPROPERTIES (
  'skip.header.line.count'='1',
  'transient_lastDdlTime'='1627431731')

CREATE EXTERNAL TABLE `oraperftbl`(
  `host` string, 
  `database` string, 
  `platform` string, 
  `version` string, 
  `banner` string, 
  `rdiopsmax_hourly` string, 
  `rdiopsavg_hourly` string, 
  `wtiopsmax_hourly` string, 
  `wtiopsavg_hourly` string, 
  `rdbtpsmax_hourly` string, 
  `rdbtpsavg_hourly` string, 
  `wtbtpsmax_hourly` string, 
  `wtbtpsavg_hourly` string, 
  `hostcpupctmax_hourly` string, 
  `hostcpupctavg_hourly` string, 
  `redobtpsmax_hourly` string, 
  `redobtpsavg_hourly` string, 
  `cpusocket` string, 
  `cpucore` string, 
  `cpunumber` string, 
  `rammb` string, 
  `sgamb` string, 
  `pgamb` string, 
  `tbsizeusedmb` string, 
  `collected` string)
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY ',' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://'
TBLPROPERTIES (
  'skip.header.line.count'='1',
  'transient_lastDdlTime'='1627429154')

CREATE EXTERNAL TABLE `rdslookup`(
  `instance_type` string, 
  `vcpu` string, 
  `memory` string, 
  `bandwidth` string, 
  `monthly_price` string)
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY ',' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://' 
TBLPROPERTIES (
  'transient_lastDdlTime'='1627431930')

CREATE EXTERNAL TABLE `sctcomplexityweightage`(
  `high` double, 
  `medium` double, 
  `low` double)
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY ',' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://' 
TBLPROPERTIES (
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1627847450')

CREATE EXTERNAL TABLE `sctsinglecsv`(
  `host` string, 
  `database` string, 
  `schema` string, 
  `category` string, 
  `occurrence` string, 
  `actionitem` string, 
  `subject` string, 
  `group` string, 
  `description` string, 
  `documentation` string, 
  `recommended` string, 
  `filtered` string, 
  `complexity` string, 
  `line` string, 
  `position` string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   'separatorChar' = ',',
   'quoteChar' = '"',
   'escapeChar' = '\\'
   )
STORED AS TEXTFILE
LOCATION
  's3://'
TBLPROPERTIES (
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1627868943')

CREATE EXTERNAL TABLE `sctsummarycsv`(
  `host` string, 
  `database` string,
  `schema` string, 
  `category` string, 
  `noofobjects` string, 
  `autoconverted` string, 
  `simple` string, 
  `medium` string, 
  `complex` string, 
  `loc` string)
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY ',' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://'
TBLPROPERTIES (
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1627863937')

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
  's3://'
TBLPROPERTIES (
  'skip.header.line.count'='1', 
  'transient_lastDdlTime'='1627856502')

CREATE EXTERNAL TABLE `testimatesperschema`(
  `host` string, 
  `database` string, 
  `schema` string, 
  `occurence` string, 
  `actionitem` string, 
  `wqf_time` string, 
  `complexity` string, 
  `timeestimatewithlower` string, 
  `timeestimatewoutlower` string, 
  `90_10_hours` string, 
  `70_30_hours` string, 
  `50_50_hours` string)
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY ',' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://'
TBLPROPERTIES (
  'skip.header.line.count'='1',
  'transient_lastDdlTime'='1627592427')

CREATE EXTERNAL TABLE `testimatesperactionitem`(
  `occurence` string,
  `actionitem` string,
  `wqf_time` string,
  `complexity` string,
  `timeestimatewithlower` string,
  `timeestimatewoutlower` string,
  `90_10_hours` string,
  `70_30_hours` string,
  `50_50_hours` string)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
STORED AS INPUTFORMAT
  'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://'
TBLPROPERTIES (
  'skip.header.line.count'='1',
  'transient_lastDdlTime'='1627592427')

CREATE EXTERNAL TABLE `assmnt2pdfmap`(
  `host` string, 
  `database` string, 
  `schema` string, 
  `target` string,
  `urlpath` string)
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY ',' 
LOCATION
  's3://'
TBLPROPERTIES (
  'skip.header.line.count'='1') 

CREATE EXTERNAL TABLE `estimatedtimeperschemapartitions`(
  `host` string,
  `database` string,
  `schema` string,
  `occurence` string,
  `actionitem` string,
  `wqf_time` string,
  `complexity` string,
  `timeestimatewithlower` string,
  `timeestimatewoutlower` string,
  `90_10_hours` string,
  `70_30_hours` string,
  `50_50_hours` string)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
STORED AS INPUTFORMAT
  'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://'
TBLPROPERTIES (
  'skip.header.line.count'='1',
  'transient_lastDdlTime'='1629334822')
