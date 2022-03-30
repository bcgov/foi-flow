using MCS.FOI.AXISIntegration.Utilities.Interfaces;

namespace MCS.FOI.AXISIntegration.Utilities.Types
{
    public class KCAuthentication : IAuth
    {
        public string JWT_OIDC_WELL_KNOWN_CONFIG { get; set; }
        public string JWT_OIDC_AUDIENCE { get; set; }
        public string JWT_OIDC_ISSUER { get; set; }
        public string JWT_OIDC_ALGORITHMS { get; set; }
        public string JWT_OIDC_JWKS_URI { get; set; }

        public string IAOGroups { get; set; }

        public  string CORSORIGINS { get; set; }
    }
}
