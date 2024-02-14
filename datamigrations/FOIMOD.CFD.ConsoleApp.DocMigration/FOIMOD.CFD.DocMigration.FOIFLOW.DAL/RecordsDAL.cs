using FOIMOD.CFD.DocMigration.Models.Document;
using Newtonsoft.Json;
using System.Data;
using System.Data.Common;
using System.Data.Odbc;


namespace FOIMOD.CFD.DocMigration.FOIFLOW.DAL
{
    public class RecordsDAL
    {
        private IDbConnection dbfoiflowConnection;
        private IDbConnection dbfoidocreviewerConnection;
        public RecordsDAL(IDbConnection _dbflowConnection, IDbConnection _dbdocreviwerConnection)
        {
            dbfoiflowConnection = _dbflowConnection;
            dbfoidocreviewerConnection = _dbdocreviwerConnection;
        }

        /// <summary>
        /// RECORDS upload
        /// </summary>
        /// <param name="axisrequestnumber"></param>
        /// <param name="s3filepath"></param>
        /// <param name="actualfilename"></param>
        /// <param name="batchnumber"></param>
        /// <param name="migrationdatetime"></param>
        /// <param name="sectiondivisionid"></param>
        /// <param name="filesize"></param>
        /// <returns></returns>
        public int InsertIntoFOIRequestRecords(string axisrequestnumber, string s3filepath, string actualfilename, string documentattributeJSON, int ministryrequestid, int ministryrequestversion)
        {
            bool result = false;
            int recordid = -1;
            try
            {
                dbfoiflowConnection.Open();
                var cmdString = @"DO $$ DECLARE requestnumber VARCHAR; BEGIN requestnumber := '{0}' ; 
                    INSERT INTO public.""FOIRequestRecords""(version, foirequestid, ministryrequestid, ministryrequestversion, filename, s3uripath, createdby, created_at,  attributes, isactive) VALUES (1, (SELECT foirequest_id FROM public.""FOIMinistryRequests"" WHERE axisrequestid=requestnumber ORDER BY created_at DESC LIMIT 1), (SELECT foiministryrequestid FROM public.""FOIMinistryRequests"" WHERE axisrequestid=requestnumber ORDER BY created_at DESC LIMIT 1), (SELECT version FROM public.""FOIMinistryRequests"" WHERE axisrequestid=requestnumber ORDER BY created_at DESC LIMIT 1), '{1}', '{2}', 'migrationservice', NOW(), '{3}', true);                    
                     END $$";
                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoiflowConnection;

                    comm.CommandText = string.Format(cmdString, axisrequestnumber, actualfilename, s3filepath, documentattributeJSON, ministryrequestid, ministryrequestversion, s3filepath);
                    comm.CommandType = CommandType.Text;
                    comm.ExecuteNonQuery();

                }


                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoiflowConnection;
                    var selectSQL = @"SELECT recordid FROM public.""FOIRequestRecords"" 
                    WHERE ministryrequestid={0} and ministryrequestversion={1} and s3uripath='{2}' and isactive=true and createdby='migrationservice' 
                    ORDER BY created_at DESC LIMIT 1;";

                    comm.CommandText = string.Format(selectSQL, ministryrequestid, ministryrequestversion, s3filepath);
                    comm.CommandType = CommandType.Text;
                    OdbcDataReader odbcDataReader = comm.ExecuteReader();
                    while (odbcDataReader.Read())
                    {

                        recordid = Convert.ToInt32(odbcDataReader["recordid"]);
                    }
                }
                result = true;
                dbfoiflowConnection.Close();
            }
            catch (Exception ex)
            {
                dbfoiflowConnection.Close();
                result = false;
                throw;
            }
            return recordid;
        }

        public (int, int) GetMinistryRequestDetails(string axisrequestnumber)
        {
            var retVal = (-1, -1);
            try
            {

                dbfoiflowConnection.Open();
                var cmdString = @"SELECT foiministryrequestid,version FROM public.""FOIMinistryRequests"" WHERE axisrequestid='{0}' ORDER BY created_at DESC LIMIT 1";
                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoiflowConnection;

                    comm.CommandText = string.Format(cmdString, axisrequestnumber);
                    comm.CommandType = CommandType.Text;

                    OdbcDataReader odbcDataReader = comm.ExecuteReader();

                    while (odbcDataReader.Read())
                    {

                        retVal = (Convert.ToInt32(odbcDataReader["foiministryrequestid"]), Convert.ToInt32(odbcDataReader["version"]));

                    }



                }
            }
            catch (Exception ex)
            {
                dbfoiflowConnection.Close();

                throw;
            }
            finally
            {
                dbfoiflowConnection.Close();

            }
            return retVal;
        }

        public int InsertIntoDocumentMaster(int ministryrequestid, string s3filepath, int foiflowrecordid)
        {
            int result = -1;
            try
            {
                dbfoidocreviewerConnection.Open();
                var cmdString = @"INSERT INTO public.""DocumentMaster""(
                                    filepath, ministryrequestid, recordid,  isredactionready, created_at, createdby)
                                    VALUES ('{0}', {1}, {2}, true, NOW(), 'migrationservice');";


                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoidocreviewerConnection;

                    comm.CommandText = string.Format(cmdString, s3filepath, ministryrequestid, foiflowrecordid);
                    comm.CommandType = CommandType.Text;
                    comm.ExecuteNonQuery();


                }

                var documentmasterSQL = @"SELECT documentmasterid FROM   public.""DocumentMaster"" WHERE createdby='migrationservice' AND recordid={0} AND filepath='{1}' AND ministryrequestid={2};";
                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoidocreviewerConnection;

                    comm.CommandText = string.Format(documentmasterSQL, foiflowrecordid, s3filepath, ministryrequestid);
                    comm.CommandType = CommandType.Text;
                    OdbcDataReader odbcDataReader = comm.ExecuteReader();

                    while (odbcDataReader.Read())
                    {
                        result = Convert.ToInt32(odbcDataReader["documentmasterid"]);
                    }


                }

                dbfoidocreviewerConnection.Close();

            }
            catch (Exception ex)
            {
                dbfoidocreviewerConnection.Close();
                result = -1;
                throw;
            }
            return result;
        }


        public int InsertIntoDocuments(int ministryrequestid, string filename, int pagecount, int documentmasterid)
        {
            int result = -1;
            try
            {
                dbfoidocreviewerConnection.Open();
                var cmdString = @"INSERT INTO public.""Documents""(version,filename,foiministryrequestid,createdby,created_at,statusid,pagecount,documentmasterid,incompatible)
                            values(1,'{0}',{1},'{{""user"":""migrationservice""}}',NOW(),1,{2},{3},false)";


                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoidocreviewerConnection;

                    comm.CommandText = string.Format(cmdString, filename, ministryrequestid, pagecount, documentmasterid);
                    comm.CommandType = CommandType.Text;
                    comm.ExecuteNonQuery();


                }

                var documentmasterSQL = @"SELECT documentid FROM   public.""Documents"" WHERE  documentmasterid ={0} AND filename='{1}' AND foiministryrequestid={2};";
                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoidocreviewerConnection;

                    comm.CommandText = string.Format(documentmasterSQL, documentmasterid, filename, ministryrequestid);
                    comm.CommandType = CommandType.Text;
                    OdbcDataReader odbcDataReader = comm.ExecuteReader();

                    while (odbcDataReader.Read())
                    {
                        result = Convert.ToInt32(odbcDataReader["documentid"]);
                    }


                }

                dbfoidocreviewerConnection.Close();

            }
            catch (Exception ex)
            {
                dbfoidocreviewerConnection.Close();
                result = -1;
                throw;
            }
            return result;
        }

        public bool InsertIntoDocumentAttributes(int documentmasterid, string docattributes)
        {
            bool result = false;
            try
            {
                dbfoidocreviewerConnection.Open();
                var cmdString = @"INSERT INTO public.""DocumentAttributes""(
	                                documentmasterid, attributes, createdby, created_at, version,  isactive)
	                            VALUES ({0}, '{1}','""migrationservice""',NOW(), 1,true);";


                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoidocreviewerConnection;

                    comm.CommandText = string.Format(cmdString, documentmasterid, docattributes);
                    comm.CommandType = CommandType.Text;
                    comm.ExecuteNonQuery();
                }

                dbfoidocreviewerConnection.Close();
                result = true;
            }
            catch (Exception ex)
            {
                dbfoidocreviewerConnection.Close();
                result = false;
                throw;
            }
            return result;
        }

        public bool InsertIntoDocumentHashcodes(int documentid, string hash)
        {
            bool result = false;
            try
            {
                dbfoidocreviewerConnection.Open();
                var cmdString = @"INSERT INTO public.""DocumentHashCodes""(
	                            documentid, rank1hash,  created_at)
                                VALUES ({0}, '{1}',  NOW());";


                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoidocreviewerConnection;

                    comm.CommandText = string.Format(cmdString, documentid, hash);
                    comm.CommandType = CommandType.Text;
                    comm.ExecuteNonQuery();
                }

                dbfoidocreviewerConnection.Close();
                result = true;
            }
            catch (Exception ex)
            {
                dbfoidocreviewerConnection.Close();
                result = false;
                throw;
            }
            return result;
        }

        public bool InsertIntoDeduplicationJob(int documentmasterid, int ministryrequestid, string batch, string filename)
        {
            bool result = false;
            try
            {
                dbfoidocreviewerConnection.Open();
                var cmdString = @"INSERT INTO public.""DeduplicationJob""(
	                                version, ministryrequestid, createdat, batch, trigger, type, filename, status, message, documentmasterid)
	                                VALUES (3, {0}, NOW(), '{1}', 'recordupload', 'rank1', '{2}', 'completed', 'migrated document', {3});";


                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoidocreviewerConnection;

                    comm.CommandText = string.Format(cmdString, ministryrequestid, batch, filename, documentmasterid);
                    comm.CommandType = CommandType.Text;
                    comm.ExecuteNonQuery();
                }

                dbfoidocreviewerConnection.Close();
                result = true;

            }
            catch (Exception ex)
            {
                dbfoidocreviewerConnection.Close();
                result = false;
                throw;
            }
            return result;
        }

        public void InsertDocumentPageFlags(List<DocumentToMigrate> documentPages, int documentid, int ministryrequestid)
        {
            try
            {
                var _sorteddocPages = documentPages.Where(row => row.ReviewFlag == "NOT RELEVANT" || row.ReviewFlag == "DUPLICATE");
                if (_sorteddocPages.Any())
                {

                    List<PageFlag> pageFlags = new List<PageFlag>();
                    foreach (DocumentToMigrate documentPage in _sorteddocPages)
                    {
                        int _flagid = -1;
                        if (documentPage.ReviewFlag == "NOT RELEVANT")
                        {
                            _flagid = 6;
                        }
                        else if (documentPage.ReviewFlag == "DUPLICATE")
                        {
                            _flagid = 5;
                        }

                        if (_flagid != -1)
                        {
                            pageFlags.Add(new PageFlag() { flagid = _flagid, page = documentPage.PageSequenceNumber });
                        }

                    }

                    string pageflagsjson = JsonConvert.SerializeObject(pageFlags);


                    dbfoidocreviewerConnection.Open();
                    var cmdString = @"INSERT INTO public.""DocumentPageflags""(
	                                 foiministryrequestid, documentid, documentversion, pageflag,created_at,createdby, redactionlayerid)
	                                VALUES ({0},{1},1,'{2}',NOW(),'{{""userid"":""migrationservice@idir""}}',1);";


                    using (OdbcCommand comm = new OdbcCommand())
                    {
                        comm.Connection = (OdbcConnection)dbfoidocreviewerConnection;

                        comm.CommandText = string.Format(cmdString, ministryrequestid, documentid, pageflagsjson);
                        comm.CommandType = CommandType.Text;
                        comm.ExecuteNonQuery();
                    }

                    dbfoidocreviewerConnection.Close();


                }
            }
            catch (Exception ex)
            {
                dbfoidocreviewerConnection.Close();               
                throw;
            }

        }


        public int GetSectionIDByName(string sectionname)
        {
            int retVal =-1 ;
            try
            {

                dbfoiflowConnection.Open();
                var cmdString = @"SELECT divisionid FROM public.""ProgramAreaDivisions"" WHERE 
                                    issection=true and 
                                    specifictopersonalrequests=true and 
                                    programareaid=(SELECT programareaid from public.""ProgramAreas"" WHERE bcgovcode='MCF' LIMIT 1) 
                                    and LOWER(name) = LOWER('{0}') LIMIT 1";
                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoiflowConnection;

                    comm.CommandText = string.Format(cmdString, sectionname);
                    comm.CommandType = CommandType.Text;

                    OdbcDataReader odbcDataReader = comm.ExecuteReader();

                    while (odbcDataReader.Read())
                    {

                        retVal = Convert.ToInt32(odbcDataReader["divisionid"]);

                    }



                }
            }
            catch (Exception ex)
            {
                dbfoiflowConnection.Close();

                throw;
            }
            finally
            {
                dbfoiflowConnection.Close();

            }
            return retVal;
        }

    }
}
