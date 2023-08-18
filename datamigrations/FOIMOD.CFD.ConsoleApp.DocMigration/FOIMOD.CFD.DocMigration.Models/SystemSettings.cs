using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FOIMOD.CFD.DocMigration.Models
{
    public static class SystemSettings
    {
        public static string S3_AccessKey { get; set; }

       public static string S3_SecretKey { get; set; }


        public static string S3_EndPoint { get; set; }

        public static string AXISConnectionString{ get; set; }

        public static string RequestToMigrate { get; set; }

    }
}
