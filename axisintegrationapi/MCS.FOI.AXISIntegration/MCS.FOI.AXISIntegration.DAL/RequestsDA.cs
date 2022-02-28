using MCS.FOI.AXISIntegration.DAL.Interfaces;
using MCS.FOI.AXISIntegration.DataModels;
using MCS.FOI.AXISIntegration.Utilities;
using Microsoft.Extensions.Logging;
using System;
using System.Data;
using System.Data.SqlClient;

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
            SettingsManager.Initializer();
        }

        public AXISRequest GetAXISRequest(string request)
        {
            AXISRequest axisRequest = new AXISRequest();
            DataTable axisDataTable = GetAxisRequestData(request);
            if (axisDataTable.Rows.Count > 0)
            {
                DataRow row = axisDataTable.Rows[0];
                axisRequest.AXISRequestID = request;
                axisRequest.Category = Convert.ToString(row["category"]);
                axisRequest.RequestType = GetRequestType(Convert.ToString(row["requestType"]));
                axisRequest.ReceivedDate = ConvertDateTimeToString(Convert.ToDateTime(row["receivedDate"]), "yyyy-MM-dd");
                axisRequest.ReceivedDateUF = ConvertDateTimeToString(Convert.ToDateTime(row["receivedDate"]), "yyyy-MM-ddTHH:mm:ss.fffffffK");
                axisRequest.StartDate = ConvertDateTimeToString(Convert.ToDateTime(row["requestProcessStart"]), "yyyy-MM-dd");
                axisRequest.DueDate = ConvertDateTimeToString(Convert.ToDateTime(row["dueDate"]), "yyyy-MM-dd");
                axisRequest.DeliveryMode = Convert.ToString(row["deliveryMode"]);
                axisRequest.ReceivedMode = Convert.ToString(row["receivedMode"]);

                axisRequest.ApplicantFirstName = Convert.ToString(row["firstName"]);
                axisRequest.ApplicantMiddleName = Convert.ToString(row["middleName"]);
                axisRequest.ApplicantLastName = Convert.ToString(row["lastName"]);
                axisRequest.ApplicantDOB = row["birthDate"] == DBNull.Value ? null : ConvertDateTimeToString(Convert.ToDateTime(row["birthDate"]), "yyyy-MM-dd");
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

                axisRequest.OnBehalfFirstName = Convert.ToString(row["onbehalfFirstName"]);
                axisRequest.OnBehalfMiddleName = Convert.ToString(row["onbehalfMiddleName"]);
                axisRequest.OnBehalfLastName = Convert.ToString(row["onbehalfLastName"]);

                axisRequest.RequestDescription = Convert.ToString(row["description"]);
                axisRequest.RequestDescriptionFromDate = Convert.ToString(row["reqDescriptionFromDate"]);
                axisRequest.RequestDescriptionToDate = Convert.ToString(row["reqDescriptionToDate"]);
                axisRequest.Ispiiredacted = true;
                axisRequest.SelectedMinistry = new Ministry(getMinistryCode(Convert.ToString(row["selectedMinistry"])));
            }
            return axisRequest;
        }
        private DataTable GetAxisRequestData(string request)
        {
            ConnectionString = SettingsManager.ConnectionString;

            string query = @"SELECT requests.sdtReceivedDate as requestProcessStart, requests.sdtTargetDate as dueDate, 
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
            DataTable dataTable = new DataTable();
            using (sqlConnection = new SqlConnection(ConnectionString))
            {
                using (SqlCommand sqlCommand = new SqlCommand(query, sqlConnection))
                {
                    sqlConnection.Open();
                    sqlCommand.CommandType = CommandType.Text;
                    sqlCommand.Parameters.Add("@vcVisibleRequestID", SqlDbType.VarChar);
                    sqlCommand.Parameters["@vcVisibleRequestID"].Value = request;
                    SqlDataAdapter sqlDataAdapter = new SqlDataAdapter(sqlCommand);
                    sqlDataAdapter.Fill(dataTable);
                }
            }
            return dataTable;
        }

        private string ConvertDateTimeToString(DateTime? date, string pattern)
        {
            return date?.ToString(pattern);
        }
        private string GetRequestType(string requestType)
        {
            if (requestType.ToLower().Contains(RequestTypes.General.ToString().ToLower()))
                return RequestTypes.General.ToString();
            else if (requestType.ToLower().Contains(RequestTypes.Personal.ToString().ToLower()))
                return RequestTypes.Personal.ToString();
            return "";
        }

        private string getMinistryCode(string code)
        {
            switch(code)
            {
                case "AED": 
                    return "AEST";
                case "AGR": 
                    return "AFF";
                case "MAG":
                    return "AG";
                case "CFD":
                    return "MCF";
                case "CTZ":
                    return "CITZ";
                case "EDU":
                    return "EDUC";
                case "EML":
                    return "EMLI";
                case "MOE":
                    return "ENV";
                case "FIN":
                    return "FIN";
                case "FNR":
                    return "FLNR";
                case "HLTH":
                    return "HLTH";
                case "IRR":
                    return "IRR";
                case "JER":
                    return "JERI";
                case "LBR":
                    return "LBR";
                case "MHA":
                    return "MMHA";
                case "MMA":
                    return "MUNI";
                case "PSS":
                    return "PSSG";
                default:
                    return code;
            }
        }
    }    
}
