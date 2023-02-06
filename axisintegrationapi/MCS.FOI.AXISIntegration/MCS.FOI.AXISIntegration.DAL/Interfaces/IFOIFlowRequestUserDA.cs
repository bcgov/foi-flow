using MCS.FOI.AXISIntegration.DataModels;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MCS.FOI.AXISIntegration.DAL.Interfaces
{
    public interface IFOIFlowRequestUserDA
    {
        public List<FOIFlowRequestUser> GetAssigneesandWatchers(string axisrequestid);

        public bool IsRawRequest(string axisrequestid);
    }
}
