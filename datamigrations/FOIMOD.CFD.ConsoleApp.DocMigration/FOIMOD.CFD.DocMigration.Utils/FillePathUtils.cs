using FOIMOD.CFD.DocMigration.Models;
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
                            result.Add(new AXISFIle() { FileName = singlefileinfo[1], FilePathOnServer = singlefileinfo[0], FileExtension = singlefileinfo[1].Split('.')[1] });
                        }

                    }
                }
                else if(delimitedstring.IndexOf('*') >0 )
                {
                    string[] singlefileinfo = delimitedstring.Split('*');
                    if (singlefileinfo != null && singlefileinfo.Length > 0)
                    {
                        result.Add(new AXISFIle() { FileName = singlefileinfo[1], FilePathOnServer = singlefileinfo[0], FileExtension = singlefileinfo[1].Split('.')[1] });
                    }
                }

            }

            return result;

        }
    }
}
