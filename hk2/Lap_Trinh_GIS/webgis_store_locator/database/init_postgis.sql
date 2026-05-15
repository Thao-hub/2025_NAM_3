CREATE EXTENSION IF NOT EXISTS postgis;
SELECT PostGIS_Version();
select * from auth_user
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO public;
