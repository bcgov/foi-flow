using MCS.FOI.AXISIntegration.DataModels;
using MCS.FOI.AXISIntegration.DataModels.Document;
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
        public bool InsertIntoMinistryRequestDocuments(string s3filepath, string actualfilename, string axisrequestnumber, int axiscorrespondenceid, string type, string userid);
        public List<AXISFile> GetAttachments(string axisRequestId);
    }
}
