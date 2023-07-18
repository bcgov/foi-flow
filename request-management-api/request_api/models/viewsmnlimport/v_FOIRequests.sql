-- public."v_FOIRequests" source

CREATE OR REPLACE VIEW public."v_FOIRequests"
AS SELECT DISTINCT ON (fr.foiministryrequestid) fr.foiministryrequestid,
    fr.version,
    fr.axisrequestid,
    fr.foirequest_id,
    NULL::text AS rawrequestid,
    fr.assignedto,
    fr.assignedgroup,
    fr.assignedministryperson,
    fr.assignedministrygroup,
        CASE
            WHEN asg.lastname IS NOT NULL AND asg.firstname IS NOT NULL THEN ((asg.lastname::text || ', '::text) || asg.firstname::text)::character varying
            WHEN asg.lastname IS NOT NULL AND asg.firstname IS NULL THEN asg.lastname
            WHEN asg.lastname IS NULL AND asg.firstname IS NOT NULL THEN asg.firstname
            ELSE coalesce(fr.assignedto, fr.assignedgroup)
        END AS assignedtoformatted,
        CASE
            WHEN msg.lastname IS NOT NULL AND msg.firstname IS NOT NULL THEN ((msg.lastname::text || ', '::text) || msg.firstname::text)::character varying
            WHEN msg.lastname IS NOT NULL AND msg.firstname IS NULL THEN msg.lastname
            WHEN msg.lastname IS NULL AND msg.firstname IS NOT NULL THEN msg.firstname
            ELSE coalesce(fr.assignedministryperson, fr.assignedministrygroup) 
        END AS ministryassignedtoformatted,
    fr.requeststatusid,
    fs2.name AS status,
    fr.description, to_char(fr.created_at,'YYYYMMDDHH24MMSSMSUS') crtid
   FROM "FOIMinistryRequests" fr
     JOIN "FOIRequestStatuses" fs2 ON fr.requeststatusid = fs2.requeststatusid
     LEFT JOIN "FOIAssignees" asg ON fr.assignedto::text = asg.username::text
     LEFT JOIN "FOIAssignees" msg ON fr.assignedministryperson::text = msg.username::text
  ORDER BY fr.foiministryrequestid, fr.version DESC, fr.axisrequestid;