-- public."v_FOINotifications" source

CREATE OR REPLACE VIEW public."v_FOINotifications"
AS select fn.idnumber::text || to_char(fnu.created_at,'YYYYMMDDHH24MMSSMSUS') || fn.axisnumber::text||fnu.userid||fnu.createdby  AS id,
    fn.idnumber,
    fn.axisnumber,
    fn.notification ->> 'message'::text AS notification,
    fn.notificationtypeid,
    fnu.userid,
    fnu.createdby,
    fnu.created_at,
        CASE
            WHEN usr.lastname IS NOT NULL AND usr.firstname IS NOT NULL THEN ((usr.lastname || ', '::text) || usr.firstname)::character varying
            WHEN usr.lastname IS NOT NULL AND usr.firstname IS NULL THEN usr.lastname::character varying
            WHEN usr.lastname IS NULL AND usr.firstname IS NOT NULL THEN usr.firstname::character varying
            ELSE fnu.userid
        END AS userformatted,
        CASE
            WHEN ctr.lastname IS NOT NULL AND ctr.firstname IS NOT NULL THEN ((ctr.lastname || ', '::text) || ctr.firstname)::character varying
            WHEN ctr.lastname IS NOT NULL AND ctr.firstname IS NULL THEN ctr.lastname::character varying
            WHEN ctr.lastname IS NULL AND ctr.firstname IS NOT NULL THEN ctr.firstname::character varying
            ELSE fnu.createdby
        END AS creatorformatted,
    nt.name AS notificationtype,
    to_char(fnu.created_at  at time zone 'utc' at time zone 'pdt', 'YYYY Mon DD | HH12:MI AM') as createdatformatted
   FROM "FOIRequestNotifications" fn
     JOIN "FOIRequestNotificationUsers" fnu ON fn.notificationid = fnu.notificationid
     LEFT JOIN "FOIUsers" usr ON fnu.userid::text = usr.preferred_username
     LEFT JOIN "FOIUsers" ctr ON fnu.createdby::text = ctr.preferred_username
     JOIN "NotificationTypes" nt ON fn.notificationtypeid = nt.notificationtypeid
UNION ALL
 SELECT fn.idnumber::text || to_char(fnu.created_at,'YYYYMMDDHH24MMSSMSUS') || fn.axisnumber::text||fnu.userid||fnu.createdby  AS id,
    fn.idnumber,
    fn.axisnumber,
    fn.notification ->> 'message'::text AS notification,
    fn.notificationtypeid,
    fnu.userid,
    fnu.createdby,
    fnu.created_at,
        CASE
            WHEN usr.lastname IS NOT NULL AND usr.firstname IS NOT NULL THEN ((usr.lastname || ', '::text) || usr.firstname)::character varying
            WHEN usr.lastname IS NOT NULL AND usr.firstname IS NULL THEN usr.lastname::character varying
            WHEN usr.lastname IS NULL AND usr.firstname IS NOT NULL THEN usr.firstname::character varying
            ELSE fnu.userid
        END AS userformatted,
        CASE
            WHEN ctr.lastname IS NOT NULL AND ctr.firstname IS NOT NULL THEN ((ctr.lastname || ', '::text) || ctr.firstname)::character varying
            WHEN ctr.lastname IS NOT NULL AND ctr.firstname IS NULL THEN ctr.lastname::character varying
            WHEN ctr.lastname IS NULL AND ctr.firstname IS NOT NULL THEN ctr.firstname::character varying
            ELSE fnu.createdby
        END AS creatorformatted,
    nt.name AS notificationtype,
    to_char(fnu.created_at  at time zone 'utc' at time zone 'pdt', 'YYYY Mon DD | HH12:MI AM') as createdatformatted
   FROM "FOIRawRequestNotifications" fn
     JOIN "FOIRawRequestNotificationUsers" fnu ON fn.notificationid = fnu.notificationid
     LEFT JOIN "FOIUsers" usr ON fnu.userid::text = usr.preferred_username
     LEFT JOIN "FOIUsers" ctr ON fnu.createdby::text = ctr.preferred_username
     JOIN "NotificationTypes" nt ON fn.notificationtypeid = nt.notificationtypeid;