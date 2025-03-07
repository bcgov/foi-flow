INSERT INTO "public"."TemplateFieldMapping" ("FieldName", "FieldType", "FieldMapping", "IsActive", "CreatedBy", "CreatedAt", "UpdatedBy", "UpdatedAt") VALUES ('[CORRECTIONNUMBER]', 'String', '[CORRECTIONNUMBER]', 'True', '-1', '01/01/2025', NULL, NULL);

--Cleanup data
DELETE FROM "public"."TemplateFieldMapping" WHERE "FieldName" = '[CUSTOMFIELD39]' AND EXISTS (SELECT 1 FROM "public"."TemplateFieldMapping" WHERE "FieldName" = '[CUSTOMFIELD39]');
INSERT INTO "public"."TemplateFieldMapping" ("FieldName", "FieldType", "FieldMapping", "IsActive", "CreatedBy", "CreatedAt", "UpdatedBy", "UpdatedAt") VALUES ('[CUSTOMFIELD39]', 'String', '[OIPCNUMBER]', 'True', '-1', '01/01/2025', NULL, NULL);
