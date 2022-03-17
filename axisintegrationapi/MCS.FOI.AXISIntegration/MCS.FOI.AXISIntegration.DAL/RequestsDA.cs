using MCS.FOI.AXISIntegration.DAL.Interfaces;
using MCS.FOI.AXISIntegration.DataModels;
using MCS.FOI.AXISIntegration.Utilities;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SqlClient;
using System.Linq;

namespace MCS.FOI.AXISIntegration.DAL
{
    public class RequestsDA : IRequestDA
    {
        private SqlConnection sqlConnection;

        private readonly ILogger Ilogger;
      
        public static string ConnectionString;

        public RequestsDA(ILogger _Ilogger)
        {
            Ilogger = _Ilogger;                     
            SettingsManager.DBConnectionInitializer();
        }

        public string GetAXISRequestString(string requestNumber)
        {
            AXISRequest axisRequest = GetAXISRequest(requestNumber);
            if(axisRequest.AXISRequestID != null)
                return RequestsHelper.ConvertRequestToJSON(axisRequest);
            return "{}";
        }

        private AXISRequest GetAXISRequest(string request)
        {
            AXISRequest axisRequest = new();
            DataTable axisDataTable = GetAxisRequestData(request);
            if (axisDataTable.Rows.Count > 0)
            {
                DataRow row = axisDataTable.Rows[0];
                try
                {
                    axisRequest.AXISRequestID = request;
                    axisRequest.Category = Convert.ToString(row["category"]);
                    axisRequest.RequestType = RequestsHelper.GetRequestType(Convert.ToString(row["requestType"]));

                    axisRequest.ReceivedDate = RequestsHelper.ConvertDateToString(row, "receivedDate", "yyyy-MM-dd");
                    axisRequest.ReceivedDateUF = RequestsHelper.ConvertDateToString(row, "receivedDate", "yyyy-MM-ddTHH:mm:ssZ");
                    axisRequest.StartDate = RequestsHelper.ConvertDateToString(row, "requestProcessStart", "yyyy-MM-dd");
                    axisRequest.DueDate = RequestsHelper.ConvertDateToString(row, "dueDate", "yyyy-MM-dd");

                    axisRequest.DeliveryMode = RequestsHelper.GetDeliveryMode(Convert.ToString(row["deliveryMode"]));
                    axisRequest.ReceivedMode = RequestsHelper.GetReceivedMode(Convert.ToString(row["receivedMode"]));

                    axisRequest.ApplicantFirstName = Convert.ToString(row["firstName"]);
                    axisRequest.ApplicantMiddleName = Convert.ToString(row["middleName"]);
                    axisRequest.ApplicantLastName = Convert.ToString(row["lastName"]);
                    axisRequest.BusinessName = Convert.ToString(row["businessName"]);

                    axisRequest.Address = Convert.ToString(row["address"]);
                    axisRequest.AddressSecondary = Convert.ToString(row["addressSecondary"]);
                    axisRequest.City = Convert.ToString(row["city"]);
                    axisRequest.PostalCode = Convert.ToString(row["postal"]);
                    axisRequest.Province = Convert.ToString(row["province"]);
                    axisRequest.Country = Convert.ToString(row["country"]);
                    axisRequest.Email = Convert.ToString(row["email"]);
                    axisRequest.PhonePrimary = Convert.ToString(row["phonePrimary"]);
                    axisRequest.PhoneSecondary = Convert.ToString(row["phoneSecondary"]);
                    axisRequest.WorkPhonePrimary = Convert.ToString(row["workPhonePrimary"]);
                    axisRequest.WorkPhoneSecondary = Convert.ToString(row["workPhoneSecondary"]);
                    string applicantDOB = RequestsHelper.ConvertDateToString(row, "birthDate", "yyyy-MM-dd");
                    axisRequest.AdditionalPersonalInfo = new AdditionalPersonalInformation(applicantDOB, Convert.ToString(row["onbehalfFirstName"]), Convert.ToString(row["onbehalfMiddleName"]), Convert.ToString(row["onbehalfLastName"]));

                    axisRequest.RequestDescription = Convert.ToString(row["description"]);
                    axisRequest.RequestDescriptionFromDate = RequestsHelper.ConvertDateToString(row, "reqDescriptionFromDate", "yyyy-MM-dd");
                    axisRequest.RequestDescriptionToDate = RequestsHelper.ConvertDateToString(row, "reqDescriptionToDate", "yyyy-MM-dd");
                    axisRequest.Ispiiredacted = true;
                    List<Ministry> ministryList = new()
                    {
                        new Ministry(RequestsHelper.GetMinistryCode(Convert.ToString(row["selectedMinistry"])))
                    };
                    axisRequest.SelectedMinistries = ministryList;
                    axisRequest.AxisSyncDate = DateTime.Now.ToString("yyyy-MM-ddTHH:mm:ssZ");
                    var extensions = GetAxisExtensionData(request);
                    axisRequest.Extensions = GetAXISExtensions(extensions);
                }
                catch (Exception e)
                {
                    Ilogger.Log(LogLevel.Error, e.Message);
                    throw;
                }
            }
            return axisRequest;
        }

        private static List<Extension> GetAXISExtensions(DataTable extensions)
        {
                var extensionList = (from rw in extensions.AsEnumerable()
                                     select new Extension()
                                     {
                                         ReasonId = Convert.ToInt32(RequestsHelper.GetExtensionReasonID(Convert.ToString(rw["reason"]))),
                                         Reason = Convert.ToString(rw["reason"]),
                                         ExtendedDueDays = Convert.ToInt32(rw["extensiondays"]),
                                         ExtendedDueDate = RequestsHelper.ConvertDateToString(rw, "extendedduedate", "yyyy-MM-dd"),
                                         StatusId = Convert.ToInt32(RequestsHelper.GetExtensionStatusId(Convert.ToString(rw["status"]))),
                                         Status = Convert.ToString(rw["status"]),
                                         ApprovedDueDays = Convert.ToInt32(rw["extensiondays"]),
                                         ApprovedDate = RequestsHelper.ConvertDateToString(rw, "decisiondate", "yyyy-MM-dd"),
                                         DeniedDate = RequestsHelper.ConvertDateToString(rw, "decisiondate", "yyyy-MM-dd"),
                                     }).ToList();

                return extensionList;
        }

        private DataTable GetAxisRequestData(string request)
        {
            ConnectionString = SettingsManager.ConnectionString;

            string query = @"SELECT requests.sdtReceivedDate as requestProcessStart, requests.sdtTargetDate as dueDate, requests.sdtOriginalTargetDate as originalDueDate,
                requests.vcDescription as [description], requests.sdtRqtDescFromdate as reqDescriptionFromDate, requests.sdtRqtDescTodate as reqDescriptionToDate, 
                requests.sdtRequestedDate as receivedDate, requests.sdtRequestedDate as receivedDateUF, office.OFFICE_CODE as selectedMinistry, 
                requesterTypes.vcDescription as category,
                (SELECT terminology.vcTerminology from tblTerminologyLookup terminology WHERE terminology.iLabelID = receivedModes.iLabelID and terminology.tiLocaleID = 1) as receivedMode,
                (SELECT terminology.vcTerminology from tblTerminologyLookup terminology WHERE terminology.iLabelID = deliveryModes.iLabelID and terminology.tiLocaleID = 1) as deliveryMode,
                (SELECT terminology.vcTerminology from tblTerminologyLookup terminology WHERE terminology.iLabelID = countries.iLabelID and terminology.tiLocaleID = 1) as country,
                (SELECT terminology.vcTerminology from tblTerminologyLookup terminology WHERE terminology.iLabelID = states.iLabelID and terminology.tiLocaleID = 1) as province,
                requesters.vcAddress1 as [address], requesters.vcAddress2 as addressSecondary, requesters.vcCity as city, requesters.vcZipCode as postal,
                requesters.vcHome as phonePrimary,
                requesters.vcMobile as phoneSecondary,
                requesters.vcWork1 as workPhonePrimary,
                requesters.vcWork2 as workPhoneSecondary,
                requesters.vcFirstName as firstName,
                requesters.vcLastName as lastName,
                requesters.vcMiddleName as middleName,
                [dbo].[cst_GetRqstCustFieldValue](requests.iRequestID, 'DOB') as birthDate,
                requesters.vcCompany as businessName,
                requesters.vcEmailID as email,
                onbehalf.vcFirstName as onbehalfFirstName,
                onbehalf.vcLastName as onbehalfLastName,
                onbehalf.vcMiddleName as onbehalfMiddleName,
                (SELECT terminology.vcTerminology from tblTerminologyLookup terminology WHERE terminology.iLabelID = requestTypes.iLabelID and terminology.tiLocaleID = 1) as requestType
                FROM
                tblRequests requests LEFT OUTER JOIN EC_OFFICE office ON requests.tiOfficeID = office.OFFICE_ID
                LEFT OUTER JOIN tblRequesterTypes requesterTypes ON requests.tiRequesterCategoryID = requesterTypes.tiRequesterTypeID
                LEFT OUTER JOIN tblReceivedModes receivedModes ON requests.tiReceivedType = receivedModes.tiReceivedModeID 
                LEFT OUTER JOIN tblDeliveryModes deliveryModes ON requests.tiDeliveryType = deliveryModes.tiDeliveryModeID
                LEFT OUTER JOIN tblRequesters requesters ON requests.iRequesterID = requesters.iRequesterID
                LEFT OUTER JOIN tblRequesters onbehalf ON requests.iOnBehalfOf = onbehalf.iRequesterID
                LEFT OUTER JOIN tblCountries countries ON requesters.siCountryID = countries.siCountryID
                LEFT OUTER JOIN tblStates states ON requesters.siStateID = states.siStateID
                LEFT OUTER JOIN tblRequestTypes requestTypes ON requests.tiRequestTypeID = requestTypes.tiRequestTypeID
                WHERE
                vcVisibleRequestID = @vcVisibleRequestID";
            DataTable dataTable = new();
            using (sqlConnection = new SqlConnection(ConnectionString))
            {
                using SqlDataAdapter sqlSelectCommand = new(query, sqlConnection);
                sqlSelectCommand.SelectCommand.Parameters.Add("@vcVisibleRequestID", SqlDbType.VarChar, 50).Value = request;
                try
                {
                    sqlConnection.Open();
                    sqlSelectCommand.Fill(dataTable);
                }
                catch(SqlException ex)
                {
                    Ilogger.Log(LogLevel.Error, ex.Message);
                    throw;
                }
                catch(Exception e)
                {
                    Ilogger.Log(LogLevel.Error, e.Message);
                    throw;
                }
            }
            return dataTable;
        }

        private DataTable GetAxisExtensionData(string request)
        {
            ConnectionString = SettingsManager.ConnectionString;

            string query = @"SELECT loc.vcTerminology AS reason, reqextn.cApprovedStatus AS [status], reqextn.sdtExtendedDate AS extendedduedate, 
                reqextn.siExtensionDays AS extensiondays, reqextn.dtApprovedDate AS decisiondate 
                FROM tblRequests req INNER JOIN tblRequestExtensions reqextn ON req.iRequestID = reqextn.iRequestID 
                AND req.tiExtension = reqextn.tiExtension 
                AND req.vcVisibleRequestID = @vcVisibleRequestID
                INNER JOIN tblExtensions extn ON req.tiExtension = extn.tiExtension 
                LEFT OUTER JOIN tblTerminologyLookup loc ON loc.iLabelID = extn.iLabelID AND loc.tiLocaleID = 1";
            DataTable dataTable = new();
            using (sqlConnection = new SqlConnection(ConnectionString))
            {
                using SqlDataAdapter sqlSelectCommand = new(query, sqlConnection);
                sqlSelectCommand.SelectCommand.Parameters.Add("@vcVisibleRequestID", SqlDbType.VarChar, 50).Value = request;
                try
                {
                    sqlConnection.Open();
                    sqlSelectCommand.Fill(dataTable);
                }
                catch (SqlException ex)
                {
                    Ilogger.Log(LogLevel.Error, ex.Message);
                }
                catch (Exception e)
                {
                    Ilogger.Log(LogLevel.Error, e.Message);
                }
            }
            return dataTable;
        }

    }    
}
