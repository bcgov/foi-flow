using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace MCS.FOI.AXISIntegration.DataModels
{
    public class AXISRequest
    {

        //MORE PROPERTIES TO ADD HERE. TODO

        public string AXISRequestID { get; set; }

        public string RequestDescription { get; set; }

        public string RequestType { get; set; }

        public string ReceivedDate { get; set; }

        public string Category { get; set; }

        public List<Extension> Extensions { get; set; }

    }
}
