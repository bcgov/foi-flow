using MCS.FOI.AXISIntegration.DAL.Interfaces;
using MCS.FOI.AXISIntegration.DataModels;
using MCS.FOI.AXISIntegration.DataModels.Document;
using MCS.FOI.AXISIntegration.Utilities;
using Microsoft.Extensions.Logging;
using System;
using System.Collections;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Data;
using System.Data.Common;
using System.Data.Odbc;
using System.Data.SqlClient;
using System.Linq;
using System.Reflection.PortableExecutable;
using System.Text;
using System.Threading.Tasks;

namespace MCS.FOI.AXISIntegration.DAL
{
    public class FOIFlowRequestUsersDA : IFOIFlowRequestUserDA
    {
        private OdbcConnection odbcConnection;

        private readonly ILogger Ilogger;

        public static string ConnectionString;

        public FOIFlowRequestUsersDA(ILogger _Ilogger)
        {
            Ilogger = _Ilogger;
            SettingsManager.DBConnectionInitializer();
        }

        private string getrawrequestusersquery(string axisrequestid)
        {
            return @"(WITH summary AS (
                    SELECT w.watcherid, 
                           w.watchedby,
		                   w.isactive,
                           ROW_NUMBER() OVER(PARTITION BY w.watchedby,w.requestid 
                                                 ORDER BY w.created_at DESC) AS rank
                      FROM public.""FOIRawRequestWatchers"" w WHERE w.requestid in (SELECT requestid FROM public.""FOIRawRequests"" WHERE axisrequestid=? ORDER BY created_at DESC LIMIT 1))
                 SELECT watchedby as userid
                   FROM summary 
                 WHERE rank = 1 and summary.isactive=true)
 
                 union all
 
                 (SELECT assignedto as userid FROM public.""FOIRawRequests"" WHERE axisrequestid=? ORDER BY created_at DESC limit 1 )";
        }

        private string getministryrequestusersquery(string axisrequestid)
        {
            return @"(WITH summary AS (
                        SELECT w.watcherid, 
                               w.watchedby,
		                       w.isactive,
                               ROW_NUMBER() OVER(PARTITION BY w.watchedby,w.ministryrequestid 
                                                     ORDER BY w.created_at DESC) AS rank
                          FROM public.""FOIRequestWatchers"" w WHERE w.ministryrequestid in (SELECT foiministryrequestid FROM public.""FOIMinistryRequests"" where axisrequestid=? ORDER BY created_at DESC limit 1))
                     SELECT watchedby as userid
                       FROM summary 
                     WHERE rank = 1 and summary.isactive=true)
                      union all
 
                     (SELECT assignedto as userid FROM public.""FOIMinistryRequests"" WHERE axisrequestid=? ORDER BY created_at DESC limit 1 )";
        }

        public List<FOIFlowRequestUser> GetAssigneesandWatchers(string axisrequestid)
        {
            ConnectionString = SettingsManager.FOIFlowConnectionString;
            List<FOIFlowRequestUser> fOIFlowRequestUsers= null;
            string query = this.IsRawRequest(axisrequestid) ? getrawrequestusersquery(axisrequestid) : getministryrequestusersquery(axisrequestid);
           

            using (odbcConnection = new OdbcConnection(ConnectionString))
            {
                
                using OdbcCommand sqlSelectCommand = new OdbcCommand(query, odbcConnection);

                sqlSelectCommand.Parameters.Add("@id1", OdbcType.VarChar).Value = axisrequestid;
                sqlSelectCommand.Parameters.Add("@id1", OdbcType.VarChar).Value = axisrequestid;

                odbcConnection.Open();
                OdbcDataReader DbReader = sqlSelectCommand.ExecuteReader(CommandBehavior.CloseConnection);
                try
                {
                    if(DbReader.HasRows)
                    {
                        fOIFlowRequestUsers = new List<FOIFlowRequestUser>();
                    }


                    while (DbReader.Read())
                    {
                        var _username = Convert.ToString(DbReader["userid"]);

                        if (fOIFlowRequestUsers.Where(u => u.username == _username).Any() == false)
                        { fOIFlowRequestUsers.Add(new() { username = _username }); }
                    }
                }
                catch (SqlException ex)
                {
                    Ilogger.Log(LogLevel.Error, ex.Message);
                }
                catch (Exception e)
                {
                    Ilogger.Log(LogLevel.Error, e.Message);
                }
                finally
                {
                    DbReader.Close();
                    sqlSelectCommand.Dispose();
                    odbcConnection.Close();

                }
            }
            return fOIFlowRequestUsers;
        }

        public bool IsRawRequest(string axisrequestid)
        {
            var israwrequest = true;
            ConnectionString = SettingsManager.FOIFlowConnectionString;

            using (odbcConnection = new OdbcConnection(ConnectionString))
            {

                using OdbcCommand sqlSelectCommand = new OdbcCommand(@"SELECT isactive as isministryrequest FROM public.""FOIMinistryRequests"" WHERE axisrequestid=? ORDER BY created_at DESC limit 1", odbcConnection);

                sqlSelectCommand.Parameters.Add("@id1", OdbcType.VarChar).Value = axisrequestid;
               

                odbcConnection.Open();
                OdbcDataReader DbReader = sqlSelectCommand.ExecuteReader(CommandBehavior.CloseConnection);
                try
                {
                    if (DbReader.HasRows)
                    {
                        israwrequest = false;
                    }


                    while (DbReader.Read() && DbReader.HasRows)
                    {
                        israwrequest = Convert.ToString(DbReader["isministryrequest"]) == "1" ? false : true;                        
                    }
                }
                catch (SqlException ex)
                {
                    Ilogger.Log(LogLevel.Error, ex.Message);
                }
                catch (Exception e)
                {
                    Ilogger.Log(LogLevel.Error, e.Message);
                }
                finally
                {
                    DbReader.Close();
                    sqlSelectCommand.Dispose();
                    odbcConnection.Close();

                }
            }


            return israwrequest;
        }


        public bool InsertIntoMinistryRequestDocuments(string s3filepath, string actualfilename, string axisrequestnumber, int axiscorrespondenceid, string type, string userid)
        {
            ConnectionString = SettingsManager.FOIFlowConnectionString;
            using var dbConnection = new OdbcConnection(ConnectionString);

            if (dbConnection.State != ConnectionState.Open)
                dbConnection.Open();

            bool result = false;
            
            try
            {
                // Use a single query with a CTE (WITH clause) to link the two inserts
                var cmdString = @"
                    WITH inserted_doc AS (
                        INSERT INTO public.""FOIMinistryRequestDocuments"" 
                        (documentpath, created_at, createdby, foiministryrequest_id, foiministryrequestversion_id, filename, isactive, category, version) 
                        VALUES (?, NOW(), ?, 
                            (SELECT foiministryrequestid FROM public.""FOIMinistryRequests"" WHERE axisrequestid=? ORDER BY created_at DESC LIMIT 1), 
                            (SELECT version FROM public.""FOIMinistryRequests"" WHERE axisrequestid=? ORDER BY created_at DESC LIMIT 1), 
                            ?, True, 'applicant', 1)
                        RETURNING foiministrydocumentid
                    )
                    INSERT INTO public.""AXISCorrespondence"" (foiministrydocumentid, axiscorrespondenceid, type)
                    SELECT foiministrydocumentid, ?, ? FROM inserted_doc;";

                using (OdbcCommand comm = new OdbcCommand(cmdString, (OdbcConnection)dbConnection))
                {
                    // OdbcParameters use positional order (?)
                    comm.Parameters.AddWithValue("@path", s3filepath);
                    comm.Parameters.AddWithValue("@uid", userid);
                    comm.Parameters.AddWithValue("@axis1", axisrequestnumber);
                    comm.Parameters.AddWithValue("@axis2", axisrequestnumber);
                    comm.Parameters.AddWithValue("@filename", actualfilename);
                    comm.Parameters.AddWithValue("@axiscorr", axiscorrespondenceid);
                    comm.Parameters.AddWithValue("@t", type);

                    comm.ExecuteNonQuery();
                    result = true;
                }
            }
            catch (Exception ex)
            {
                // Log your error here
                throw; 
            }
            finally
            {
                if (dbConnection.State == ConnectionState.Open)
                    dbConnection.Close();
            }
            return result;
        }

        public List<AXISFile> GetAttachments(string axisRequestId)
        {
            ConnectionString = SettingsManager.FOIFlowConnectionString;
            List<AXISFile> Attachments= null;
            string query = @"SELECT
                                fm.axisrequestid as AXISRequestID,
                                ac.axiscorrespondenceid as CorresponcenceID,
                                ac.type as CorresponcenceType
                            FROM public.""FOIMinistryRequestDocuments"" fmd
                            INNER JOIN public.""FOIMinistryRequests"" fm ON fmd.foiministryrequest_id = fm.foiministryrequestid
                            INNER JOIN public.""AXISCorrespondence"" ac ON fmd.foiministrydocumentid = ac.foiministrydocumentid
                            WHERE fm.axisrequestid = ? AND fm.isactive = true AND fmd.isactive = true";

            using (odbcConnection = new OdbcConnection(ConnectionString))
            {
                
                using OdbcCommand sqlSelectCommand = new OdbcCommand(query, odbcConnection);

                sqlSelectCommand.Parameters.Add("@id1", OdbcType.VarChar).Value = axisRequestId;

                odbcConnection.Open();
                OdbcDataReader DbReader = sqlSelectCommand.ExecuteReader(CommandBehavior.CloseConnection);
                try
                {
                    if(DbReader.HasRows)
                    {
                        Attachments = new List<AXISFile>();
                    }

                    while (DbReader.Read())
                    {
                        Attachments.Add(new() {
                                                AXISRequestID = Convert.ToString(DbReader["AXISRequestID"]),
                                                CorrespondenceID = Convert.ToInt32(DbReader["CorrespondenceID"]),
                                                CorrespondenceType = Convert.ToString(DbReader["CorrespondenceType"])
                                        });
                    }
                }
                catch (SqlException ex)
                {
                    Ilogger.Log(LogLevel.Error, ex.Message);
                }
                catch (Exception e)
                {
                    Ilogger.Log(LogLevel.Error, e.Message);
                }
                finally
                {
                    DbReader.Close();
                    sqlSelectCommand.Dispose();
                    odbcConnection.Close();
                }
            }
            return Attachments;
        }
    }
}
