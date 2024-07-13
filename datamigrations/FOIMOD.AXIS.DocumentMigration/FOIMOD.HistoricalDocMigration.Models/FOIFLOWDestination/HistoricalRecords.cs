namespace FOIMOD.HistoricalDocMigration.Models.FOIFLOWDestination
{
    public class HistoricalRecords
    {       

        public string RecordFileName { get; set; }

        public string Description { get; set; }

        public string AXISRequestID { get; set; }

        public string S3Subfolder { get; set; }

        public string S3Path { get; set; }

        public bool IsCorrenpondenceDocument { get; set; }

        public string Attributes { get; set; }


        public DateTime CreatedAt { get; set; }

        public string CreatedBy { get; set; }

        public Stream FileStream { get; set; }
    }

    


}
