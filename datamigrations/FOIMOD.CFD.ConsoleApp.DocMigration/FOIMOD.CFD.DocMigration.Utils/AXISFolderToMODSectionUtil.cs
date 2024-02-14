using FOIMOD.CFD.DocMigration.Models;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace FOIMOD.CFD.DocMigration.Utils
{

    public static class ICMConstants
    {
        public static string FSCase = "FS Case";
        public static string Memo = "Memo";
        public static string CSCase = "CS Case";
        public static string Incident = "Incident";
        public static string AHCase = "AH Case";
        public static string SPCase = "SP Case";
        public static string RECase = "RE Case";
        public static string REComplaint = "RE Complaint";



    }

    public class AXISFolderToMODSectionUtil : IDisposable
    {
        private bool disposedValue;

        private List<FolderToSectionMapper> ICMfolderToSectionMapper = new List<FolderToSectionMapper>();

        private List<FolderToSectionMapper> _mappers = new List<FolderToSectionMapper>();
        public AXISFolderToMODSectionUtil(string jsonmapperlocation)
        {

            using (StreamReader r = new StreamReader(jsonmapperlocation))
            {
                string json = r.ReadToEnd();
                _mappers = JsonConvert.DeserializeObject<List<FolderToSectionMapper>>(json);
            }

            ICMfolderToSectionMapper.Add(new FolderToSectionMapper() { AXISFolder = ICMConstants.FSCase, MODSECTION = "ICM-FS Case Report" });
            ICMfolderToSectionMapper.Add(new FolderToSectionMapper() { AXISFolder = ICMConstants.Memo, MODSECTION = "ICM-Memo" });
            ICMfolderToSectionMapper.Add(new FolderToSectionMapper() { AXISFolder = ICMConstants.CSCase, MODSECTION = "ICM-CS Case Report" });
            ICMfolderToSectionMapper.Add(new FolderToSectionMapper() { AXISFolder = ICMConstants.Incident, MODSECTION = "ICM-Incident" });
            ICMfolderToSectionMapper.Add(new FolderToSectionMapper() { AXISFolder = ICMConstants.AHCase, MODSECTION = "ICM-AH Case Report" });
            ICMfolderToSectionMapper.Add(new FolderToSectionMapper() { AXISFolder = ICMConstants.SPCase, MODSECTION = "ICM-SP Case Report" });
            ICMfolderToSectionMapper.Add(new FolderToSectionMapper() { AXISFolder = ICMConstants.RECase, MODSECTION = "ICM-RE Case Report" });
            ICMfolderToSectionMapper.Add(new FolderToSectionMapper() { AXISFolder = ICMConstants.REComplaint, MODSECTION = "ICM-Complaint Report" });
        }


        public string GetFOIMODSectionByAXISFolder(string actualaxisFolder)
        {

            if (!string.IsNullOrEmpty(actualaxisFolder))
            {
                var exactfoldermatches = _mappers.Where(f => f.AXISFolder == actualaxisFolder).ToList();

                if (exactfoldermatches.Any())
                {
                    return exactfoldermatches?.FirstOrDefault().MODSECTION;
                }
                else
                {
                    if (actualaxisFolder.Contains("_"))
                    {
                        var splitbyUnderScores = actualaxisFolder.Split("_");


                        if (splitbyUnderScores.Length > 2)
                        {
                            var underscoreoccurenceCount = splitbyUnderScores.Length - 1;
                            var laststringpartoffolder = splitbyUnderScores[underscoreoccurenceCount];
                            var possibleresults = _mappers.Where(f => f.AXISFolder == laststringpartoffolder).ToList();

                            if (possibleresults.Any())
                            {
                                return possibleresults?.FirstOrDefault().MODSECTION;
                            }
                        }

                    }

                    if (actualaxisFolder.Contains("ICM") || actualaxisFolder.Contains("Memo") || actualaxisFolder.Contains("Incident")
                        || actualaxisFolder.Contains("FS Case") || actualaxisFolder.Contains("RE Case") || actualaxisFolder.Contains("RE Complaint")
                        || actualaxisFolder.Contains("CS Case") || actualaxisFolder.Contains("SP Case") || actualaxisFolder.Contains("AH Case"))
                    {
                        if (actualaxisFolder.Contains(ICMConstants.FSCase))
                        {
                            return ICMfolderToSectionMapper.Where(f => f.AXISFolder == ICMConstants.FSCase).First().MODSECTION;
                        }
                        else if (actualaxisFolder.Contains(ICMConstants.REComplaint))
                        {
                            return ICMfolderToSectionMapper.Where(f => f.AXISFolder == ICMConstants.REComplaint).First().MODSECTION;
                        }
                        else if (actualaxisFolder.Contains(ICMConstants.AHCase))
                        {
                            return ICMfolderToSectionMapper.Where(f => f.AXISFolder == ICMConstants.AHCase).First().MODSECTION;
                        }
                        else if (actualaxisFolder.Contains(ICMConstants.Incident))
                        {
                            return ICMfolderToSectionMapper.Where(f => f.AXISFolder == ICMConstants.Incident).First().MODSECTION;
                        }                       
                        else if (actualaxisFolder.Contains(ICMConstants.CSCase))
                        {
                            return ICMfolderToSectionMapper.Where(f => f.AXISFolder == ICMConstants.CSCase).First().MODSECTION;
                        }
                        else if (actualaxisFolder.Contains(ICMConstants.SPCase))
                        {
                            return ICMfolderToSectionMapper.Where(f => f.AXISFolder == ICMConstants.SPCase).First().MODSECTION;
                        }
                        else if (actualaxisFolder.Contains(ICMConstants.Memo))
                        {
                            return ICMfolderToSectionMapper.Where(f => f.AXISFolder == ICMConstants.Memo).First().MODSECTION;
                        }
                        else if (actualaxisFolder.Contains(ICMConstants.RECase))
                        {
                            return ICMfolderToSectionMapper.Where(f => f.AXISFolder == ICMConstants.RECase).First().MODSECTION;
                        }
                    }

                    if (actualaxisFolder.Contains(' '))
                    {
                        // THIS KIND OF FOLDERS, ex:  "1-3 Legal"
                        var splitbyspace = actualaxisFolder.Split(" ");

                        if (splitbyspace.Length == 2)
                        {
                            var spaceoccurenceCount = splitbyspace.Length - 1;
                            var laststringpartoffolder = splitbyspace[spaceoccurenceCount];
                            var possibleresults = _mappers.Where(f => f.AXISFolder == laststringpartoffolder).ToList();

                            if (possibleresults.Any())
                            {
                                return possibleresults?.FirstOrDefault().MODSECTION;
                            }
                        }
                        else if (splitbyspace.Length == 3)
                        {
                            var laststringpartoffolder = string.Format("{0} {1}", splitbyspace[1], splitbyspace[2]);
                            var possibleresults = _mappers.Where(f => f.AXISFolder == laststringpartoffolder).ToList();

                            if (possibleresults.Any())
                            {
                                return possibleresults?.FirstOrDefault().MODSECTION;
                            }
                        }
                    }

                   
                }


            }
            else
            {
                return String.Empty;
            }

            return "TBD";
        }

        protected virtual void Dispose(bool disposing)
        {
            if (!disposedValue)
            {
                if (disposing)
                {
                    // TODO: dispose managed state (managed objects)

                    _mappers = null;
                    ICMfolderToSectionMapper = null;
                }

                // TODO: free unmanaged resources (unmanaged objects) and override finalizer
                // TODO: set large fields to null
                disposedValue = true;
            }
        }



        void IDisposable.Dispose()
        {
            // Do not change this code. Put cleanup code in 'Dispose(bool disposing)' method
            Dispose(disposing: true);
            GC.SuppressFinalize(this);
        }
    }
}
