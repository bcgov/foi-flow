-- public."v_FOIRawRequests" source

CREATE OR REPLACE VIEW public."v_FOIRawRequests"
AS SELECT tmp.requestid::text AS rawrequestid,
    tmp.axisrequestid,
    tmp.foirequest_id,
    tmp.ministryrequestid,
    tmp.assignedto,
    tmp.assignedgroup,
    tmp.assignedministryperson,
    tmp.assignedministrygroup,
    tmp.assignedtoformatted,
    tmp.ministryassignedtoformatted,
    tmp.status,
    tmp.description,
    tmp.isiaorestricted
   FROM ( SELECT DISTINCT ON (fr.requestid) fr.requestid,
            fr.version,
                CASE
                    WHEN fr.axisrequestid IS NULL THEN ('U-00'::text || fr.requestid)::character varying
                    ELSE fr.axisrequestid
                END AS axisrequestid,
            NULL::integer AS foirequest_id,
            NULL::integer AS ministryrequestid,
            fr.assignedto,
            fr.assignedgroup,
            NULL::text AS assignedministryperson,
            NULL::text AS assignedministrygroup,
                CASE
                    WHEN asg.lastname IS NOT NULL AND asg.firstname IS NOT NULL THEN ((asg.lastname::text || ', '::text) || asg.firstname::text)::character varying
                    WHEN asg.lastname IS NOT NULL AND asg.firstname IS NULL THEN asg.lastname
                    WHEN asg.lastname IS NULL AND asg.firstname IS NOT NULL THEN asg.firstname
                    ELSE fr.assignedto
                END AS assignedtoformatted,
            NULL::text AS ministryassignedtoformatted,
            fr.status,
                CASE
                    WHEN fr.status::text = 'Unopened'::text THEN (fr.requestrawdata -> 'descriptionTimeframe'::text) ->> 'description'::text
                    ELSE fr.requestrawdata ->> 'description'::text
                END AS description,
            fr.isiaorestricted
           FROM "FOIRawRequests" fr
             LEFT JOIN "FOIAssignees" asg ON fr.assignedto::text = asg.username::text
          WHERE NOT (fr.axisrequestid::text IN ( SELECT "v_FOIRequests".axisrequestid
                   FROM "v_FOIRequests"
                  WHERE "v_FOIRequests".requeststatusid = 3))
          ORDER BY fr.requestid, fr.version DESC, fr.axisrequestid) tmp
  WHERE tmp.status::text <> ALL (ARRAY['Archived'::character varying, 'Unopened'::character varying, 'Closed'::character varying]::text[]);