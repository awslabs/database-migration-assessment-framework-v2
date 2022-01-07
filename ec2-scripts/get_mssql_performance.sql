-- MSSQL

SET NOCOUNT ON
CREATE TABLE #Temp
(
[Index] int,
[Name] varchar(100),
Internal_Value varchar(100),
Character_Value varchar(500)
)

INSERT INTO #Temp
exec xp_msver;


SELECT
DB_NAME(database_id) AS [Database Name],
COUNT(*) * 8/1024.0 as[Cached Size (MB)]
into #tempresults
FROM sys.dm_os_buffer_descriptors WITH (NOLOCK)
WHERE database_id > 4 -- system databases
AND database_id <> 32767 -- ResourceDB
GROUP BY DB_NAME(database_id)
--ORDER BY [Cached Size (MB)] DESC OPTION (RECOMPILE);

declare @IsRDS varchar(3)
set @IsRDS = 'No'
select @IsRDS = 'Yes' from sys.databases where name = 'rdsadmin'

declare @hours bigint

select @hours=datediff(hh,a.login_time,getdate()) from master..sysprocesses a where a.spid=1;
-- If the system has been up less than 1 hour, we'll say it's been up for 1 hour
IF @hours = 0
	SET @hours=1;
with iops as
(
SELECT db_name(vfs.database_id) as database_name,
CAST(ROUND(SUM(num_of_reads + num_of_writes) *1.0 /@hours/3600,2) as decimal(20,2))  AS rwiops
FROM sys.dm_io_virtual_file_stats(NULL, NULL) AS vfs
group by vfs.database_id
),


bps as
(
SELECT db_name(vfs.database_id) as database_name,
CAST(ROUND(SUM(num_of_bytes_read + num_of_bytes_written) *1.0 /@hours/3600,2) as decimal(20,2))  AS biops
FROM sys.dm_io_virtual_file_stats(NULL, NULL) AS vfs
group by vfs.database_id
),

DB_CPU_Stats as
(
SELECT DB_Name(pa.DatabaseID) AS DatabaseName,
SUM(qs.total_worker_time/1000) AS [CPU_Time_Ms]
FROM sys.dm_exec_query_stats AS qs WITH (NOLOCK)
CROSS APPLY (SELECT CONVERT(int, value) AS [DatabaseID]
              FROM sys.dm_exec_plan_attributes(qs.plan_handle)
              WHERE attribute = N'dbid') AS pa
 GROUP BY DatabaseID having DatabaseID <> 32767
),

pct as
(
SELECT DatabaseName, [CPU_Time_Ms] AS [CPU Time (ms)],
CAST([CPU_Time_Ms] * 1.0 / SUM([CPU_Time_Ms]) OVER() * 100.0 AS DECIMAL(10, 2)) AS max_cpu_pct
FROM DB_CPU_Stats
),

pc as (
        select convert(int,internal_value) as cpu from #temp where name = 'ProcessorCount'
),
pm as (
        select convert(int,internal_value) as physical_memory from #temp where name = 'PhysicalMemory'
),
dbmem as (
	select [Database Name] database_name,
        CAST([Cached Size (MB)]  as decimal(20,2)) memcacheMB
from #tempresults
),
pv as (
        select character_value as product_version from #temp where name = 'ProductVersion'
),
bn as (
       select character_value as banner from #temp where name = 'FileDescription'
),
plt as (
        select character_value as platform from #temp where name = 'Platform'
),
wv as (
        select character_value as windows_version from #temp where name = 'WindowsVersion'
),
curdb as (
	select name from sys.databases where database_id = db_id()
),
fs as (
	SELECT
db_name(database_id) database_name,
sum((size*8)/1024) SizeMB
FROM sys.master_files
group by db_name(database_id)
)
select a.database_name,(banner+' v.'+product_version) as banner,(platform+' v.'+windows_version) as platform, @IsRDS as IsRDS,
a.rwiops,b.biops,cpu,memcacheMB,physical_memory as physical_memory_mb, CAST(osm.physical_memory_in_use_kb/1024.  as decimal(20,2)) as physical_memory_inuse_MB,
max_cpu_pct,SizeMB,
CAST(SERVERPROPERTY('edition') as varchar(128)) as [version]
from iops a,bps b, pct c,pc,pm,bn,pv,plt,wv,fs,dbmem, curdb , sys.dm_os_process_memory osm
where a.database_name=curdb.name and b.database_name=curdb.name
     and fs.database_name=curdb.name 
     and c.DatabaseName=curdb.name
	 and dbmem.database_name = curdb.name

drop table #tempresults
drop table #temp
