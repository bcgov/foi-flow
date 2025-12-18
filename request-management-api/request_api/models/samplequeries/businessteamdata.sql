--get latest version of all ministry ids where assignedgroup = 'Business Team'
SELECT foiministryrequestid, version FROM
public."FOIMinistryRequests" JOIN (
  SELECT foiministryrequestid, MAX(version) as version
  FROM public."FOIMinistryRequests" where assignedgroup = 'Business Team'
  GROUP BY foiministryrequestid
  ) max_version USING (foiministryrequestid, version);
  

select * from public."FOIMinistryRequests" where assignedgroup = 'Business Team' order by foiministryrequestid, version desc
select assignedgroup,* from public."FOIMinistryRequests" where foiministryrequestid in (5214,5215,5216,5255,5257,5258,5260) order by foiministryrequestid, version desc 


select * from public."FOIRawRequestWatchers" where watchedbygroup = 'Business Team';
select * from public."FOIRequestWatchers" where watchedbygroup = 'Business Team';



-- only the latest version will get updated.
UPDATE public."FOIMinistryRequests" ministryrequests SET assignedgroup = 'Central Team' FROM (
  SELECT foiministryrequestid, MAX(version) as version
  FROM public."FOIMinistryRequests" where assignedgroup = 'Business Team'
  GROUP BY foiministryrequestid
  ) max_version WHERE ministryrequests.foiministryrequestid = max_version.foiministryrequestid and  ministryrequests.version = max_version.version;

UPDATE public."FOIRequestWatchers" SET watchedbygroup = 'Central Team' WHERE watchedbygroup = 'Business Team';
UPDATE public."FOIRawRequestWatchers" SET watchedbygroup = 'Central Team' WHERE watchedbygroup = 'Business Team';


--CAMUNDA DB ---
select * from act_ru_variable where text_ like '%Business%';
select * from act_ru_authorization where group_id_ like '%Business%';
select * from act_ru_identitylink where group_id_ like '%Business%';


UPDATE act_ru_variable SET text_ = replace(text_,'Business','Central') where text_ like '%Business%';
UPDATE act_ru_authorization SET group_id_ = 'Central Team' where group_id_ like '%Business%';
UPDATE act_ru_identitylink SET group_id_ = 'Central Team' where group_id_ like '%Business%';