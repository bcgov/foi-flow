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
Step-1 (Identify the latest deployed version - FOI Raw Request Processing) : Click on Process "FOI Raw Request Processing" and get the latest version. 
*/

/*
Step-2 Migrate Variables from version X to Y 
*/

do $$ 
declare
   process_def_key varchar(25) := 'foi-request';
   ru_variable_counter integer := 0;
   X_process_definition_id varchar(64) := '';
   Y_process_definition_id varchar(64) := '';
   X integer := 0;
   Y integer := 0;
   
begin 
   	select count(proc_def_id_) into ru_variable_counter from act_ru_variable where proc_def_id_ = (select id_ from act_re_procdef where key_ = process_def_key and version_ = X);
	raise notice'act_ru_variable has % proc_def_id_s found', ru_variable_counter;
	
	select id_ into X_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = X;
	select id_ into Y_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = Y;
	raise notice'The X_process_definition_id is %, The Y_process_definition_id is %', X_process_definition_id, Y_process_definition_id;
			
	if X_process_definition_id is NOT NULL and Y_process_definition_id is NOT NULL and ru_variable_counter > 0 then
 
 		raise notice'inside if: act_ru_variable has % proc_def_id_s found', ru_variable_counter;
		
 		update act_ru_variable set proc_def_id_ = Y_process_definition_id where proc_def_id_ = X_process_definition_id;
	
 	end if;
end $$;
/*
Step-3 Migrate Execution instances from version X to Y
*/
do $$ 
declare
   process_def_key varchar(25) := 'foi-request';
   ru_execution_counter integer := 0;
   X_process_definition_id varchar(64) := '';
   Y_process_definition_id varchar(64) := '';
   X integer := 0;
   Y integer := 0;
   
begin 
   	select count(proc_def_id_) into ru_execution_counter from act_ru_execution where proc_def_id_ = (select id_ from act_re_procdef where key_ = process_def_key and version_ = X);
	raise notice'act_ru_execution has % proc_def_id_s found', ru_execution_counter;
	
	select id_ into X_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = X;
	select id_ into Y_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = Y;
	raise notice'The X_process_definition_id is %, The Y_process_definition_id is %', X_process_definition_id, Y_process_definition_id;
	
 	if X_process_definition_id is NOT NULL and Y_process_definition_id is NOT NULL and ru_execution_counter > 0 then
 	
		raise notice'inside if: act_ru_execution has % proc_def_id_s found', ru_execution_counter;
		
 		update act_ru_execution  set proc_def_id_ = Y_process_definition_id where proc_def_id_ = X_process_definition_id;
	
 	end if;
end $$;

/*
Step-4 Migrate Jobs from version X to Y
*/

do $$ 
declare
   process_def_key varchar(25) := 'foi-request';
   ru_job_counter integer := 0;
   X_process_definition_id varchar(64) := '';
   Y_process_definition_id varchar(64) := '';
   X integer := 0;
   Y integer := 0;
   
begin 
   	select count(process_def_id_) into ru_job_counter from act_ru_job where process_def_id_ = (select id_ from act_re_procdef where key_ = process_def_key and version_ = X);
   	raise notice'act_ru_job has % proc_def_id_s found', ru_job_counter;

	select id_ into X_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = X;
	select id_ into Y_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = Y;
	raise notice'The X_process_definition_id is %, The Y_process_definition_id is %', X_process_definition_id, Y_process_definition_id;
			
 	if X_process_definition_id is NOT NULL and Y_process_definition_id is NOT NULL and ru_job_counter > 0 then
 	
		raise notice'inside if: act_ru_job has % proc_def_id_s found', ru_job_counter;
		
		update act_ru_job  set process_def_id_ = Y_process_definition_id where process_def_id_ = X_process_definition_id;
	
 	end if;
end $$;

/*
Step-5 Migrate Tasks from version X to Y
*/

do $$ 
declare
   process_def_key varchar(25) := 'foi-request';
   ru_task_counter integer := 0;
   X_process_definition_id varchar(64) := '';
   Y_process_definition_id varchar(64) := '';
   X integer := 0;
   Y integer := 0;
   
begin
	select count(proc_def_id_) into ru_task_counter from act_ru_task where proc_def_id_ = (select id_ from act_re_procdef where key_ = process_def_key and version_ = X);
	raise notice'act_ru_task has % proc_def_id_s found', ru_task_counter;
	
	select id_ into X_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = X;
	select id_ into Y_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = Y;
	raise notice'The X_process_definition_id is %, The Y_process_definition_id is %', X_process_definition_id, Y_process_definition_id;
	
 	if X_process_definition_id is NOT NULL and Y_process_definition_id is NOT NULL and ru_task_counter > 0 then
 	
		raise notice'inside if: act_ru_task has % proc_def_id_s found', ru_task_counter;
		
	 	update act_ru_task  set proc_def_id_ = Y_process_definition_id where proc_def_id_ = X_process_definition_id;
	
 	end if;
end $$;

/*
Step-1 (Identify the latest deployed version - FOI Request Processing) : Click on Process "FOI Request Processing" and get the latest version. 
*/

/*
Step-2 Migrate Variables from version X to Y 
*/

do $$ 
declare
   process_def_key varchar(25) := 'foi-request-processing';
   ru_variable_counter integer := 0;
   X_process_definition_id varchar(64) := '';
   Y_process_definition_id varchar(64) := '';
   X integer := 0;
   Y integer := 0;
   
begin 
   	select count(proc_def_id_) into ru_variable_counter from act_ru_variable where proc_def_id_ = (select id_ from act_re_procdef where key_ = process_def_key and version_ = X);
	raise notice'act_ru_variable has % proc_def_id_s found', ru_variable_counter;
	
	select id_ into X_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = X;
	select id_ into Y_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = Y;
	raise notice'The X_process_definition_id is %, The Y_process_definition_id is %', X_process_definition_id, Y_process_definition_id;
			
	if X_process_definition_id is NOT NULL and Y_process_definition_id is NOT NULL and ru_variable_counter > 0 then
 
 		raise notice'inside if: act_ru_variable has % proc_def_id_s found', ru_variable_counter;
		
 		update act_ru_variable set proc_def_id_ = Y_process_definition_id where proc_def_id_ = X_process_definition_id;
	
 	end if;
end $$;
/*
Step-3 Migrate Execution instances from version X to Y
*/
do $$ 
declare
   process_def_key varchar(25) := 'foi-request-processing';
   ru_execution_counter integer := 0;
   X_process_definition_id varchar(64) := '';
   Y_process_definition_id varchar(64) := '';
   X integer := 0;
   Y integer := 0;
   
begin 
   	select count(proc_def_id_) into ru_execution_counter from act_ru_execution where proc_def_id_ = (select id_ from act_re_procdef where key_ = process_def_key and version_ = X);
	raise notice'act_ru_execution has % proc_def_id_s found', ru_execution_counter;
	
	select id_ into X_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = X;
	select id_ into Y_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = Y;
	raise notice'The X_process_definition_id is %, The Y_process_definition_id is %', X_process_definition_id, Y_process_definition_id;
	
 	if X_process_definition_id is NOT NULL and Y_process_definition_id is NOT NULL and ru_execution_counter > 0 then
 	
		raise notice'inside if: act_ru_execution has % proc_def_id_s found', ru_execution_counter;
		
 		update act_ru_execution  set proc_def_id_ = Y_process_definition_id where proc_def_id_ = X_process_definition_id;
	
 	end if;
end $$;

/*
Step-4 Migrate Jobs from version X to Y
*/

do $$ 
declare
   process_def_key varchar(25) := 'foi-request-processing';
   ru_job_counter integer := 0;
   X_process_definition_id varchar(64) := '';
   Y_process_definition_id varchar(64) := '';
   X integer := 0;
   Y integer := 0;
   
begin 
   	select count(process_def_id_) into ru_job_counter from act_ru_job where process_def_id_ = (select id_ from act_re_procdef where key_ = process_def_key and version_ = X);
   	raise notice'act_ru_job has % proc_def_id_s found', ru_job_counter;

	select id_ into X_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = X;
	select id_ into Y_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = Y;
	raise notice'The X_process_definition_id is %, The Y_process_definition_id is %', X_process_definition_id, Y_process_definition_id;
			
 	if X_process_definition_id is NOT NULL and Y_process_definition_id is NOT NULL and ru_job_counter > 0 then
 	
		raise notice'inside if: act_ru_job has % proc_def_id_s found', ru_job_counter;
		
		update act_ru_job  set process_def_id_ = Y_process_definition_id where process_def_id_ = X_process_definition_id;
	
 	end if;
end $$;

/*
Step-5 Migrate Tasks from version X to Y
*/

do $$ 
declare
   process_def_key varchar(25) := 'foi-request-processing';
   ru_task_counter integer := 0;
   X_process_definition_id varchar(64) := '';
   Y_process_definition_id varchar(64) := '';
   X integer := 0;
   Y integer := 0;
   
begin
	select count(proc_def_id_) into ru_task_counter from act_ru_task where proc_def_id_ = (select id_ from act_re_procdef where key_ = process_def_key and version_ = X);
	raise notice'act_ru_task has % proc_def_id_s found', ru_task_counter;
	
	select id_ into X_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = X;
	select id_ into Y_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = Y;
	raise notice'The X_process_definition_id is %, The Y_process_definition_id is %', X_process_definition_id, Y_process_definition_id;
	
 	if X_process_definition_id is NOT NULL and Y_process_definition_id is NOT NULL and ru_task_counter > 0 then
 	
		raise notice'inside if: act_ru_task has % proc_def_id_s found', ru_task_counter;
		
	 	update act_ru_task  set proc_def_id_ = Y_process_definition_id where proc_def_id_ = X_process_definition_id;
	
 	end if;
end $$;

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
and name_ like '%IAO';
commit;

/* 
This needs to be run only in the marshals.
 */
update public.act_ru_event_subscr set activity_id_ = 'Event_1tvpamu' where activity_id_ = 'complete';

/*
Step-1 (Identify the latest deployed version - FOI Fee Processing) : Click on Process "FOI Fee Processing" and get the latest version. 
*/

/*
Step-2 Migrate Variables from version X to Y 
*/

do $$ 
declare
   process_def_key varchar(25) := 'foi-fee-processing';
   ru_variable_counter integer := 0;
   X_process_definition_id varchar(64) := '';
   Y_process_definition_id varchar(64) := '';
   X integer := 0;
   Y integer := 0;
   
begin 
   	select count(proc_def_id_) into ru_variable_counter from act_ru_variable where proc_def_id_ = (select id_ from act_re_procdef where key_ = process_def_key and version_ = X);
	raise notice'act_ru_variable has % proc_def_id_s found', ru_variable_counter;
	
	select id_ into X_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = X;
	select id_ into Y_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = Y;
	raise notice'The X_process_definition_id is %, The Y_process_definition_id is %', X_process_definition_id, Y_process_definition_id;
			
	if X_process_definition_id is NOT NULL and Y_process_definition_id is NOT NULL and ru_variable_counter > 0 then
 
 		raise notice'inside if: act_ru_variable has % proc_def_id_s found', ru_variable_counter;
		
 		update act_ru_variable set proc_def_id_ = Y_process_definition_id where proc_def_id_ = X_process_definition_id;
	
 	end if;
end $$;
/*
Step-3 Migrate Execution instances from version X to Y
*/
do $$ 
declare
   process_def_key varchar(25) := 'foi-fee-processing';
   ru_execution_counter integer := 0;
   X_process_definition_id varchar(64) := '';
   Y_process_definition_id varchar(64) := '';
   X integer := 0;
   Y integer := 0;
   
begin 
   	select count(proc_def_id_) into ru_execution_counter from act_ru_execution where proc_def_id_ = (select id_ from act_re_procdef where key_ = process_def_key and version_ = X);
	raise notice'act_ru_execution has % proc_def_id_s found', ru_execution_counter;
	
	select id_ into X_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = X;
	select id_ into Y_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = Y;
	raise notice'The X_process_definition_id is %, The Y_process_definition_id is %', X_process_definition_id, Y_process_definition_id;
	
 	if X_process_definition_id is NOT NULL and Y_process_definition_id is NOT NULL and ru_execution_counter > 0 then
 	
		raise notice'inside if: act_ru_execution has % proc_def_id_s found', ru_execution_counter;
		
 		update act_ru_execution  set proc_def_id_ = Y_process_definition_id where proc_def_id_ = X_process_definition_id;
	
 	end if;
end $$;

/*
Step-4 Migrate Jobs from version X to Y
*/

do $$ 
declare
   process_def_key varchar(25) := 'foi-fee-processing';
   ru_job_counter integer := 0;
   X_process_definition_id varchar(64) := '';
   Y_process_definition_id varchar(64) := '';
   X integer := 0;
   Y integer := 0;
   
begin 
   	select count(process_def_id_) into ru_job_counter from act_ru_job where process_def_id_ = (select id_ from act_re_procdef where key_ = process_def_key and version_ = X);
   	raise notice'act_ru_job has % proc_def_id_s found', ru_job_counter;

	select id_ into X_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = X;
	select id_ into Y_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = Y;
	raise notice'The X_process_definition_id is %, The Y_process_definition_id is %', X_process_definition_id, Y_process_definition_id;
			
 	if X_process_definition_id is NOT NULL and Y_process_definition_id is NOT NULL and ru_job_counter > 0 then
 	
		raise notice'inside if: act_ru_job has % proc_def_id_s found', ru_job_counter;
		
		update act_ru_job  set process_def_id_ = Y_process_definition_id where process_def_id_ = X_process_definition_id;
	
 	end if;
end $$;

/*
Step-5 Migrate Tasks from version X to Y
*/

do $$ 
declare
   process_def_key varchar(25) := 'foi-fee-processing';
   ru_task_counter integer := 0;
   X_process_definition_id varchar(64) := '';
   Y_process_definition_id varchar(64) := '';
   X integer := 0;
   Y integer := 0;
   
begin
	select count(proc_def_id_) into ru_task_counter from act_ru_task where proc_def_id_ = (select id_ from act_re_procdef where key_ = process_def_key and version_ = X);
	raise notice'act_ru_task has % proc_def_id_s found', ru_task_counter;
	
	select id_ into X_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = X;
	select id_ into Y_process_definition_id from act_re_procdef where key_ = process_def_key and version_ = Y;
	raise notice'The X_process_definition_id is %, The Y_process_definition_id is %', X_process_definition_id, Y_process_definition_id;
	
 	if X_process_definition_id is NOT NULL and Y_process_definition_id is NOT NULL and ru_task_counter > 0 then
 	
		raise notice'inside if: act_ru_task has % proc_def_id_s found', ru_task_counter;
		
	 	update act_ru_task  set proc_def_id_ = Y_process_definition_id where proc_def_id_ = X_process_definition_id;
	
 	end if;
end $$;