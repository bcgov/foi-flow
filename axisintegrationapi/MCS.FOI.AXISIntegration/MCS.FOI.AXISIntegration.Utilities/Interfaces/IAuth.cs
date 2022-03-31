using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MCS.FOI.AXISIntegration.Utilities.Interfaces
{
    public interface IAuth
    {
        public  string JWT_OIDC_WELL_KNOWN_CONFIG { get; set; }

        public  string JWT_OIDC_AUDIENCE { get; set; }

        public  string JWT_OIDC_ISSUER { get; set; }

        public  string JWT_OIDC_ALGORITHMS { get; set; }

        public  string JWT_OIDC_JWKS_URI { get; set; }

        public string IAOGroups { get; set; }

        public static string CORSORIGINS { get; set; }
    }
}
