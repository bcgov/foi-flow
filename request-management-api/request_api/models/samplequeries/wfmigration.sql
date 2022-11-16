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
 
-- Update task
update act_ru_task  set proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = 2)
where proc_def_id_ = (select id_ from act_re_procdef where key_='foi-request-processing' and version_ = 1);

INSERT INTO public.act_ru_event_subscr (id_, rev_, event_type_, event_name_, execution_id_, 
proc_inst_id_, activity_id_, configuration_, created_, tenant_id_)
select gen_random_uuid (),1, 'message', 'foi-iao-correnspodence', ext.execution_id_, tmp1.proc_inst_id_,
'correnspodance', NULL, now(), null from
(select distinct proc_inst_id_  from act_ru_variable arv where name_='status' and text_ <> 'Open' 
and proc_inst_id_  not in (select proc_inst_id_ from act_ru_event_subscr arv where event_name_='foi-iao-correnspodence')) as tmp1,
act_ru_task ext where tmp1.proc_inst_id_ = ext.proc_inst_id_
and name_ like '%IAO'
commit;