namespace MCS.FOI.Integration.Application.Model
{
    public class CustomRestrictParameter
    {
        public string passwordBase64 { get; set; }
        public string saltBase64 { get; set; }
        public int spinCount { get; set; }
    }
}
