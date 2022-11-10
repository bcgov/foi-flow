select id_ from act_re_procdef where key_='foi-request-processing' and version_ = 2; 
select id_ from act_re_procdef where key_='foi-request-processing' and version_ = 1; 

-- Update Variables 
update  act_ru_variable set proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = 2)
where proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = 1);
 
-- Update Execution
update act_ru_execution  set proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = 2)
where proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = 1);
 
-- Update Jobs
update act_ru_job  set process_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = 2)
where process_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = 1);
 
update act_ru_jobdef  set proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = 2)
where proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = 1);
 
-- Update task
update act_ru_task  set proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = 2)
where proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = 1);