set serveroutput on;
variable rdscheck char(1)

--Grants for running AWS Schema Conversion Tool
PROMPT ======================================================
PROMPT This Script will grant necessary access to user dmafuser for running Assessment and AWR Miner.
PROMPT ======================================================

PROMPT
PROMPT
PROMPT ======================================================
PROMPT Granting necessary permission for Assessment using AWS Schema Conversion Tool
PROMPT ======================================================

GRANT CONNECT to dmafuser;
grant SELECT_CATALOG_ROLE to dmafuser;
grant SELECT ANY DICTIONARY to dmafuser;
grant SELECT on SYS.USER$ TO  dmafuser;

--Grants for running AWS Data Migration services diagnostics 

PROMPT
PROMPT ======================================================
PROMPT Granting necessary permission for DMS Diagnistics data
PROMPT ======================================================
PROMPT

GRANT CREATE SESSION TO dmafuser;

begin
	:rdscheck := 'N';
    SELECT 'Y' INTO :rdscheck FROM DBA_USERS WHERE USERNAME = 'RDSADMIN' AND ACCOUNT_STATUS = 'OPEN' AND DEFAULT_TABLESPACE = 'RDSADMIN';
	exception when no_data_found then
		:rdscheck  := 'N';
end;
/

whenever sqlerror exit failure

DECLARE 
RDSINSTANCE CHAR(1) := 'N';
begin
	RDSINSTANCE := :rdscheck ;
	
	IF RDSINSTANCE = 'N' THEN
		EXECUTE IMMEDIATE 'GRANT SELECT on V_$DATABASE to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on V_$VERSION to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on GV_$SGA to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on GV_$INSTANCE to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on GV_$DATAGUARD_CONFIG to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on GV_$LOG to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_TABLESPACES to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_DATA_FILES to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_SEGMENTS to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_LOBS to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on V_$ARCHIVED_LOG to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_TAB_MODIFICATIONS to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_TABLES to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_TAB_PARTITIONS to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_MVIEWS to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_OBJECTS to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_TAB_COLUMNS to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_LOG_GROUPS to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_LOG_GROUP_COLUMNS to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on V_$ARCHIVE_DEST to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_SYS_PRIVS to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_TAB_PRIVS to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_TYPES to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_CONSTRAINTS to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on V_$TRANSACTION to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on GV_$ASM_DISK_STAT to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on GV_$SESSION to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on GV_$SQL to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_ENCRYPTED_COLUMNS to dmafuser';
		EXECUTE IMMEDIATE 'GRANT SELECT on DBA_PDBS to dmafuser';
		EXECUTE IMMEDIATE 'GRANT EXECUTE on dbms_utility to dmafuser';
	END IF;
	
	
	IF RDSINSTANCE = 'Y' THEN
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''V_$DATABASE'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''V_$VERSION'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''GV_$SGA'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''GV_$INSTANCE'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''GV_$DATAGUARD_CONFIG'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''GV_$LOG'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_TABLESPACES'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_DATA_FILES'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_SEGMENTS'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_LOBS'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''V_$ARCHIVED_LOG'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_TAB_MODIFICATIONS'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_TABLES'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_TAB_PARTITIONS'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_MVIEWS'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_OBJECTS'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_TAB_COLUMNS'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_LOG_GROUPS'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_LOG_GROUP_COLUMNS'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''V_$ARCHIVE_DEST'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_SYS_PRIVS'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_TAB_PRIVS'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_TYPES'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_CONSTRAINTS'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''V_$TRANSACTION'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''GV_$ASM_DISK_STAT'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''GV_$SESSION'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''GV_$SQL'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_ENCRYPTED_COLUMNS'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBA_PDBS'',''DMAFUSER'',''SELECT''); end ;');
		EXECUTE IMMEDIATE('begin rdsadmin.rdsadmin_util.grant_sys_object(''DBMS_UTILITY'',''DMAFUSER'',''EXECUTE''); end ;');
	END IF;

end;
/