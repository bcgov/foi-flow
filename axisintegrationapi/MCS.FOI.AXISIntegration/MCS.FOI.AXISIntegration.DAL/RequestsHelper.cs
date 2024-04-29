using MCS.FOI.AXISIntegration.DataModels;
using Newtonsoft.Json;
using System;
using System.Data;
using System.Globalization;

namespace MCS.FOI.AXISIntegration.DAL
{
    public static class RequestsHelper
    {
        public static string ConvertDateToString(DataRow row, string property, string format)
        {
            return row[property] == DBNull.Value ? null : Convert.ToDateTime(row[property]).ToString(format, CultureInfo.InvariantCulture);
        }

        public static string ConvertRequestToJSON(Object _object)
        {
            return JsonConvert.SerializeObject(_object);
        }


        public static string GetRequestType(string requestType)
        {
            if (requestType.ToLower().Contains(RequestTypes.General.ToString().ToLower()))
                return RequestTypes.General.ToString().ToLower();
            else if (requestType.ToLower().Contains(RequestTypes.Personal.ToString().ToLower()))
                return RequestTypes.Personal.ToString().ToLower();
            return "";
        }

        public static string GetMinistryCode(string code)
        {
            return code switch
            {
                "AED" => "AEST",
                "AGR" => "AGR",
                "MAG" => "AG",
                "CFD" => "MCF",
                "CTZ" => "CITZ",
                "EDU" => "EDU",
                "EML" => "EMLI",
                "MOE" => "ENV",
                "FIN" => "FIN",
                "FNR" => "FOR",
                "HLTH" => "HLTH",
                "IRR" => "IRR",
                "JER" => "JERI",
                "LBR" => "LBR",
                "MHA" => "MMHA",
                "MMA" => "MUNI",
                "PSS" => "PSSG",
                "TAC" => "TACS",
                "TRA" => "TRAN",
                _ => code,
            };
        }
        public static string GetExtensionReasonID(string reason)
        {           
            return reason switch
            {
                //"OIPC - Applicant Consent" => "OIPC - Applicant Consent",
                //"OIPC - Consultation" => "OIPC - Consultation",
                //"OIPC - Fair and Reasonable to do so" => "OIPC - Fair and Reasonable",
                //"OIPC - Further Detail from Applicant Needed" => "OIPC - Further Detail from Applicant Required",
                //"OIPC - Large Volume and/or Volume of Search" => "OIPC - Large Volume and/or Volume of Search",
                //"OIPC - Large Volume and/or Volume of Search and Consultation" => "OIPC - Large Volume and/or Volume of Search and Consultation",
                //"PB - Applicant Consent" => "Public Body - Applicant Consent",
                //"PB - Consultation" => "Public Body - Consultation",
                //"PB - Further Detail from Applicant Needed" => "Public Body - Further Detail from Applicant Required",
                //"PB - Large Volume and/or Volume of Search" => "Public Body - Large Volume and/or Volume of Search",
                //"PB - Large Volume and/or Volume of Search and Consultation" => "Public Body - Large Volume and/or Volume of Search and Consultation",
                "OIPC - Applicant Consent" => "6",
                "OIPC - Consultation" => "7",
                "OIPC - Fair and Reasonable to do so" => "11",
                "OIPC - Further Detail from Applicant Needed" => "8",
                "OIPC - Large Volume and/or Volume of Search" => "9",
                "OIPC - Large Volume and/or Volume of Search and Consultation" => "10",
                "PB - Applicant Consent" => "1",
                "PB - Consultation" => "2",
                "PB - Further Detail from Applicant Needed" => "3",
                "PB - Large Volume and/or Volume of Search" => "4",
                "PB - Large Volume and/or Volume of Search and Consultation" => "5",
                _ => "0",
            };
        }

        public static string GetExtensionStatusId(string code)
        {
            return code switch
            {
                "N" => "1", //Pending
                "A" => "2", // Approved
                "D" => "3", // Denied
                _ => "0",
            };
        }

        public static string GetExtensionStatus(string code)
        {
            return code switch
            {
                "N" => "Pending", //Pending
                "A" => "Approved", // Approved
                "D" => "Denied", // Denied
                _ => "Pending",
            };
        }

        //check with business
        public static string GetReceivedMode(string receivedMode)
        {
            return receivedMode switch
            {

                "Courier" => "Mail",
                "E-mail" => "Email",
                "Fax" => "Fax",
                "National FOIA Portal" => "Online Form",
                "Forward from Public Body" => "Email",
                "Hand Delivered" => "Mail",
                "Internal" => "Email",
                "Online Form" => "Online Form",
                "Post" => "Mail",
                _ => "Email",
            };
        }

        //check with business
        public static string GetDeliveryMode(string deliveryMode)
        {
            return deliveryMode switch
            {
                "E-mail" => "Secure File Transfer",
                "System to System" => "Secure File Transfer",
                "Paper - Post" => "In Person Pick up",
                "CD - Post" => "In Person Pick up",
                "Post" => "In Person Pick up",
                "Secure File Transfer" => "Secure File Transfer",
                _ => "Secure File Transfer",
            };
        }
    }
}
