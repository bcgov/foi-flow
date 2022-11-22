/*
*********************************************************************************************************************
The purpose of this document is to capture the instructions to do the migration of workflow instances for Fee.

Change Details:
New FOI Request Processes (related to Fee)
1. FOI Fee Processing
2.     FOI Email Processing
Modified FOI Request Processes (related to Fee)
1. FOI Request Processing (Key: foi-request-processing)

**********************************************************************************************************************
Below given instructions are for migrating foi-request-processing to latest deployed definition version
Note#1: The approach that would be taken for migration is incremental (semi-automation) with manual verification between the steps.
Note#2: The below given instructions to be followed after deploying the WF
**********************************************************************************************************************
*/

/*
Step-0 (Login & Navigate to Processes): Login to Camunda application as admin - > Navigate to Cockpit -> Navigate to Processes
*/

/*
Step-1 (Identify the latest deployed version - FOI Request Processing) : Click on Process "FOI Request Processing" and get the latest version. 
*/

/*
Step-2 Migrate Variables from version X to Y 
*/

update  act_ru_variable set proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = Y)
where proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = X);
 
/*
Step-3 Migrate Execution instances from version X to Y
*/
update act_ru_execution  set proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = Y)
where proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = X);
 
/*
Step-4 Migrate Jobs from version X to Y
*/
update act_ru_job  set process_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = Y)
where process_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = X);
 
/*
Step-5 Migrate Tasks from version X to Y
*/
update act_ru_task  set proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = Y)
where proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = X);

/*
Step-6[SPECIAL-INSTRUCTION] PURPOSE: Create entries for correspondence (Specific to Fee)
Note: This to be ran after completion of Step 2 to 5 i.e. migration of all instances
*/
INSERT INTO public.act_ru_event_subscr (id_, rev_, event_type_, event_name_, execution_id_, 
proc_inst_id_, activity_id_, configuration_, created_, tenant_id_)
select tmp1.proc_inst_id_, 1, 'message', 'foi-iao-correnspodence', ext.execution_id_, tmp1.proc_inst_id_,
'correnspodance', NULL, now(), null from
(select distinct proc_inst_id_  from act_ru_variable arv where name_='status' and text_ <> 'Open' 
and proc_inst_id_  not in (select proc_inst_id_ from act_ru_event_subscr arv where event_name_='foi-iao-correnspodence')) as tmp1,
act_ru_task ext where tmp1.proc_inst_id_ = ext.proc_inst_id_
and name_ like '%IAO'
commit;

/* 
This needs to be run only in the marshals.
 */
update public.act_ru_event_subscr set activity_id_ = 'Event_1tvpamu' where activity_id_ = 'complete'