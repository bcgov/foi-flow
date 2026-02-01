using MCS.FOI.AXISIntegration.DataModels.Document;
using System.Text.RegularExpressions;
using System.Collections.Generic;
using System.Linq;

namespace MCS.FOI.AXISIntegration.Utilities
{
    public static class FilePathUtils
    {

        public static string getFileExtension(string filename)
        {
            var filenameparts = filename.Split('.');
            var fileextension = filenameparts.Length > 2 ? filenameparts[filenameparts.Length - 1] : filenameparts[1];
            return fileextension;
        }

        public static string CleanFileNameInput(string strIn)
        {
            // Replace invalid characters with empty strings.
            try
            {
                return Regex.Replace(strIn, @"[^\w\.@-]", "",
                                     RegexOptions.None, TimeSpan.FromSeconds(10.5));
            }
            // If we timeout when replacing invalid characters,
            // we should return Empty.
            catch (RegexMatchTimeoutException)
            {
                return String.Empty;
            }
        }
    }
}
