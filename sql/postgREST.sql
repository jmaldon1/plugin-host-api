create role app_user nologin;

grant usage on schema api to app_user;
-- Change this to restrict `app_user` to certain actions or tables
grant select on all tables in schema api to app_user;

-- Password is in the .env
create role authenticator noinherit login password '*******';
grant web_anon to authenticator;


select
	t2.plugin_id,
	t3.name,
	t2.operating_system,
	t2.plugin_type,
	t1.download_link
from 
	data.plugin_downloads as t1
inner join
	data.plugin_variants as t2 on plugin_variant_id = t2.id
inner join
	data.plugins as t3 on t2.plugin_id = t3.id;
