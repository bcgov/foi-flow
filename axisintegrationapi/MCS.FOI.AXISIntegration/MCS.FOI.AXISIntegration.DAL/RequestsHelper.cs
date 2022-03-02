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

        public static string ConvertRequestToJSON(AXISRequest request)
        {
            return JsonConvert.SerializeObject(request);
        }

        public static string GetRequestType(string requestType)
        {
            if (requestType.ToLower().Contains(RequestTypes.General.ToString().ToLower()))
                return RequestTypes.General.ToString();
            else if (requestType.ToLower().Contains(RequestTypes.Personal.ToString().ToLower()))
                return RequestTypes.Personal.ToString();
            return "";
        }

        public static string GetMinistryCode(string code)
        {
            return code switch
            {
                "AED" => "AEST",
                "AGR" => "AFF",
                "MAG" => "AG",
                "CFD" => "MCF",
                "CTZ" => "CITZ",
                "EDU" => "EDUC",
                "EML" => "EMLI",
                "MOE" => "ENV",
                "FIN" => "FIN",
                "FNR" => "FLNR",
                "HLTH" => "HLTH",
                "IRR" => "IRR",
                "JER" => "JERI",
                "LBR" => "LBR",
                "MHA" => "MMHA",
                "MMA" => "MUNI",
                "PSS" => "PSSG",
                _ => code,
            };
        }
    }
}
