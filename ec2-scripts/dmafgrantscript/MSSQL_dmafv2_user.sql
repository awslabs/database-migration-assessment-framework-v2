--sample login for Running AWS Schema Conversion Tool Assessment and Performance Views.
CREATE LOGIN [dmafuser] WITH PASSWORD = 'test123';

use [master]
GO
GRANT VIEW ANY DATABASE TO [dmafuser] AS [admin]
GO
GRANT VIEW ANY DEFINITION TO [dmafuser] AS [admin]
GO
GRANT VIEW SERVER STATE TO [dmafuser] AS [admin]
GO

--for each Database to be assess.
/*
use AdventureWorks2019
create user [dmafuser] for login [dmafuser]

use AdventureWorks2019
GRANT VIEW DEFINITION TO dmafuser
GRANT VIEW DATABASE STATE TO dmafuser
*/