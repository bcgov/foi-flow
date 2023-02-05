using MCS.FOI.AXISIntegration.DAL.Interfaces;
using MCS.FOI.AXISIntegration.DataModels;
using MCS.FOI.AXISIntegration.Utilities;
using Microsoft.Extensions.Logging;
using System;
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

        public List<FOIFlowRequestUser> GetAssigneesandWatchers(string axisrequestid, string type)
        {
            ConnectionString = SettingsManager.FOIFlowConnectionString;
            List<FOIFlowRequestUser> fOIFlowRequestUsers= null;
            string query = type == "rawrequest" ? getrawrequestusersquery(axisrequestid) : getministryrequestusersquery(axisrequestid);
           

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
    }
}
