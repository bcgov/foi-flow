SELECT foiministryrequestid, version, isactive, filenumber, description, recordsearchfromdate, recordsearchtodate, 
startdate, duedate, assignedto, created_at, updated_at, createdby, updatedby, programareaid, requeststatusid, 
foirequest_id, foirequestversion_id, assignedgroup, assignedministryperson, assignedministrygroup, cfrduedate, closedate, closereasonid, axisrequestid, axissyncdate, requestpagecount
	FROM public."FOIMinistryRequests" where assignedgroup = 'Business Team';

select * from public."FOIRawRequestWatchers" where watchedbygroup = 'Business Team';
select * from public."FOIRequestWatchers" where watchedbygroup = 'Business Team';
select * from public."FOIRequestComments" where comment like '%Business Team%';



-- UPDATE public."FOIMinistryRequests" SET assignedgroup = 'Central Team' WHERE assignedgroup = 'Business Team';
-- UPDATE public."FOIRequestWatchers" SET watchedbygroup = 'Central Team' WHERE watchedbygroup = 'Business Team';


--CAMUNDA DB ---
select * from act_ru_variable where text_ like '%Business%'
select * from act_ru_authorization where group_id_ like '%Business%'
select * from act_ru_identitylink where group_id_ like '%Business%'