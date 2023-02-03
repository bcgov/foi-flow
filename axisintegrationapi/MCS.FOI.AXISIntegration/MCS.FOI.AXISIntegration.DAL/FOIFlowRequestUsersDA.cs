using MCS.FOI.AXISIntegration.DAL.Interfaces;
using MCS.FOI.AXISIntegration.DataModels;
using MCS.FOI.AXISIntegration.Utilities;
using Microsoft.Extensions.Logging;
using System;
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

        public List<FOIFlowRequestUser> GetAssigneesandWatchers(int id, string type)
        {
            ConnectionString = SettingsManager.FOIFlowConnectionString;

            string query = @"SELECT * FROM FOIRawRequestWatchers";   //TODO : WIP : NEed to refine. just for testing...         
            using (odbcConnection = new OdbcConnection(ConnectionString))
            {
                odbcConnection.Open();
                using OdbcCommand sqlSelectCommand = new(query, odbcConnection);
                OdbcDataReader DbReader = sqlSelectCommand.ExecuteReader();
                try
                {


                    while (DbReader.Read())
                    {

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
            return null;
        }
    }
}
