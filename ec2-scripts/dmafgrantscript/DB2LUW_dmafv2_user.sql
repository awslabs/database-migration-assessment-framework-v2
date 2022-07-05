grant CONNECT ON DATABASE  to user dmafuser;
grant EXECUTE ON PACKAGE NULLID.SYSSH200 to user dmafuser;
grant EXECUTE ON FUNCTION SYSPROC.ENV_GET_INST_INFO  to user dmafuser;
grant SELECT ON SYSIBMADM.ENV_INST_INFO to user dmafuser;
grant SELECT ON SYSIBMADM.ENV_SYS_INFO to user dmafuser;
grant EXECUTE ON FUNCTION SYSPROC.AUTH_LIST_AUTHORITIES_FOR_AUTHID to user dmafuser;
grant EXECUTE ON FUNCTION SYSPROC.AUTH_LIST_GROUPS_FOR_AUTHID to user dmafuser;
grant EXECUTE ON FUNCTION SYSPROC.AUTH_LIST_ROLES_FOR_AUTHID to user dmafuser;
grant SELECT ON SYSIBMADM.PRIVILEGES to user dmafuser;
grant SELECT ON SYSCAT.ATTRIBUTES to user dmafuser;
grant SELECT ON SYSCAT.CHECKS to user dmafuser;
grant SELECT ON SYSCAT.COLIDENTATTRIBUTES to user dmafuser;
grant SELECT ON SYSCAT.COLUMNS to user dmafuser;
grant SELECT ON SYSCAT.DATAPARTITIONEXPRESSION to user dmafuser;
grant SELECT ON SYSCAT.DATAPARTITIONS to user dmafuser;
grant SELECT ON SYSCAT.DATATYPEDEP to user dmafuser;
grant SELECT ON SYSCAT.DATATYPES to user dmafuser;
grant SELECT ON SYSCAT.HIERARCHIES to user dmafuser;
grant SELECT ON SYSCAT.INDEXCOLUSE to user dmafuser;
grant SELECT ON SYSCAT.INDEXES to user dmafuser;
grant SELECT ON SYSCAT.INDEXPARTITIONS to user dmafuser;
grant SELECT ON SYSCAT.KEYCOLUSE to user dmafuser;
grant SELECT ON SYSCAT.MODULEOBJECTS to user dmafuser;
grant SELECT ON SYSCAT.MODULES to user dmafuser;
grant SELECT ON SYSCAT.NICKNAMES to user dmafuser;
grant SELECT ON SYSCAT.PERIODS to user dmafuser;
grant SELECT ON SYSCAT.REFERENCES to user dmafuser;
grant SELECT ON SYSCAT.ROUTINEPARMS to user dmafuser;
grant SELECT ON SYSCAT.ROUTINES to user dmafuser;
grant SELECT ON SYSCAT.ROWFIELDS to user dmafuser;
grant SELECT ON SYSCAT.SCHEMATA to user dmafuser;
grant SELECT ON SYSCAT.SEQUENCES to user dmafuser;
grant SELECT ON SYSCAT.TABCONST to user dmafuser;
grant SELECT ON SYSCAT.TABLES to user dmafuser;
grant SELECT ON SYSCAT.TRIGGERS to user dmafuser;
grant SELECT ON SYSCAT.VARIABLEDEP to user dmafuser;
grant SELECT ON SYSCAT.VARIABLES to user dmafuser;
grant SELECT ON SYSCAT.VIEWS to user dmafuser;
grant SELECT ON SYSIBM.SYSDUMMY1 to user dmafuser;
grant usage on workload SYSDEFAULTUSERWORKLOAD  to user dmafuser;