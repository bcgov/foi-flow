namespace MCS.FOI.AXISIntegration.DataModels
{
    public class Extension
    {
        /// <summary>
        /// THIS EXTENSION POCO Class will have more prop.
        /// </summary>
        public string Type { get; set; }
        public string Reason { get; set; }
        public int ExtendedDueDays { get; set; }
        public int ApprovedDueDays { get; set; }
        public string ExtendedDueDate { get; set; }
        public string ApprovedDate { get; set; }
        public string DeniedDate { get; set; }
        public string Status { get; set; }
    }
}
