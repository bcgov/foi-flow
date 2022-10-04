SELECT foiministryrequestid, version, isactive, filenumber, description, recordsearchfromdate, recordsearchtodate, 
startdate, duedate, assignedto, created_at, updated_at, createdby, updatedby, programareaid, requeststatusid, 
foirequest_id, foirequestversion_id, assignedgroup, assignedministryperson, assignedministrygroup, cfrduedate, closedate, closereasonid, axisrequestid, axissyncdate, requestpagecount
	FROM public."FOIMinistryRequests" where assignedgroup = 'Business Team';

--get latest version of all ministry ids where assignedgroup = 'Business Team'
SELECT foiministryrequestid, version FROM
public."FOIMinistryRequests" JOIN (
  SELECT foiministryrequestid, MAX(version) version
  FROM public."FOIMinistryRequests" where assignedgroup = 'Business Team'
  GROUP BY foiministryrequestid
  ) max_version USING (foiministryrequestid, version)


select * from public."FOIRawRequestWatchers" where watchedbygroup = 'Business Team';
select * from public."FOIRequestWatchers" where watchedbygroup = 'Business Team';



-- only the latest version will get updated.
UPDATE public."FOIMinistryRequests" ministryrequests SET assignedgroup = 'Central Team' FROM (
  SELECT foiministryrequestid, MAX(version) version
  FROM public."FOIMinistryRequests" where assignedgroup = 'Business Team'
  GROUP BY foiministryrequestid
  ) max_version WHERE ministryrequests.foiministryrequestid = max_version.foiministryrequestid and  ministryrequests.version = max_version.version
UPDATE public."FOIRequestWatchers" SET watchedbygroup = 'Central Team' WHERE watchedbygroup = 'Business Team';


--CAMUNDA DB ---
select * from act_ru_variable where text_ like '%Business%'
select * from act_ru_authorization where group_id_ like '%Business%'
select * from act_ru_identitylink where group_id_ like '%Business%'