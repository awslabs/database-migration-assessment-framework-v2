use master
go
CREATE login dmafuser WITH PASSWORD test123
go
sp_adduser dmafuser
go
grant role mon_role to dmafuser
go
grant select on dbo.spt_values to dmafuser
go
grant select on asehostname to dmafuser
go

--Grant for Individual Database

use pubs3
go
sp_adduser dmafuser
go
grant role mon_role to dmafuser
go
grant select on dbo.sysusers to dmafuser
go
grant select on dbo.sysobjects to dmafuser
go
grant select on dbo.sysindexes to dmafuser
go
grant select on dbo.syscolumns to dmafuser
go
grant select on dbo.sysreferences to dmafuser
go
grant select on dbo.syscomments to dmafuser
go
grant select on dbo.syspartitions to dmafuser
go
grant select on dbo.syspartitionkeys to dmafuser
go
grant select on dbo.sysconstraints to dmafuser
go
grant select on dbo.systypes to dmafuser
go
grant select on dbo.sysqueryplans to dmafuser
go
