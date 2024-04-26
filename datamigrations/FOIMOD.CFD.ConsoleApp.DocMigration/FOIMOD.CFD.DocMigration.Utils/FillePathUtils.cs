using FOIMOD.CFD.DocMigration.Models;
using System.Text.RegularExpressions;
namespace FOIMOD.CFD.DocMigration.Utils
{
    public static class FilePathUtils
    {

        public static List<AXISFIle>? GetFileDetailsFromdelimitedstring(string delimitedstring)
        {
            List<AXISFIle>? result = null;
            if (!string.IsNullOrEmpty(delimitedstring))
            {                
                string[] files = delimitedstring.Split('|');
                result = new List<AXISFIle>();
                if (files != null && files.Length > 0)
                {
                    
                    foreach (string fileinfodelimited in files)
                    {
                        string[] singlefileinfo = fileinfodelimited.Split('*');
                        if (singlefileinfo != null && singlefileinfo.Length > 0)
                        {
                            
                            result.Add(new AXISFIle() { FileName = singlefileinfo[1], FilePathOnServer = singlefileinfo[0], FileExtension = getFileExtension(singlefileinfo[1]) });
                        }

                    }
                }
                else if(delimitedstring.IndexOf('*') >0 )
                {
                    string[] singlefileinfo = delimitedstring.Split('*');
                    if (singlefileinfo != null && singlefileinfo.Length > 0)
                    {
                        result.Add(new AXISFIle() { FileName = singlefileinfo[1], FilePathOnServer = singlefileinfo[0], FileExtension = getFileExtension(singlefileinfo[1]) });
                    }
                }

            }

            return result;

        }


        private static string getFileExtension(string filename)
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
