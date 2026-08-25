using Microsoft.Data.SqlClient;
using System.Data;

namespace FOIMOD.CFD.DocMigration.DAL;

public static class RecordLookupQuery
{
    private const string Query = @"
DECLARE @RequestID INT;
DECLARE @SectionList VARCHAR(MAX);

SELECT @RequestID = R.iRequestID
FROM dbo.tblRequests AS R
WHERE R.vcVisibleRequestID = @RequestNumber;

SELECT
    @SectionList = COALESCE(@SectionList + ':', '') + DRL.vcSectionList
FROM dbo.tblDocumentReviewLog AS DRL
WHERE DRL.iRequestID = @RequestID;

;WITH RequestDocumentIDs AS
(
    SELECT DRL.iDocID
    FROM dbo.tblDocumentReviewLog AS DRL
    WHERE DRL.iRequestID = @RequestID

    UNION

    SELECT D.iDocID
    FROM dbo.tblDocuments AS D
    WHERE D.iDocID IN
    (
        SELECT Data
        FROM dbo.AFX_Splitter(@SectionList, ':')
    )

    UNION

    SELECT RL.iDocID
    FROM dbo.tblRedactionLayers AS RL
    WHERE RL.iRequestID = @RequestID
      AND RL.iDeliveryID IS NULL
),
MatchedDocuments AS
(
    SELECT D.iDocID
    FROM dbo.tblDocuments AS D
    LEFT JOIN dbo.tblDocuments AS ParentD
        ON ParentD.iDocID = D.iParentDocID
    WHERE D.iDocID IN (SELECT iDocID FROM RequestDocumentIDs)
      AND CONCAT(
            REPLACE(ParentD.vcDocName, '''', ''),
            '_',
            REPLACE(D.vcDocName, '''', ''),
            '.pdf'
          ) = @FileName
)
SELECT DISTINCT
    D.iDocID,
    D.vcDocName AS FolderName,
    ParentD.vcDocName AS ParentFolderName,
    D.tiSections,
    P.vcFileName AS FilePath,
    REVERSE(SUBSTRING(REVERSE(P.vcFileName), 1, 4)) AS FileType,
    D.siFolderID,
    D.siPageCount,
    P.siPageNum,
    CAST(NULL AS VARCHAR(255)) AS PageReviewFlag
FROM dbo.tblDocuments AS D
LEFT JOIN dbo.tblDocuments AS ParentD
    ON ParentD.iDocID = D.iParentDocID
INNER JOIN dbo.tblPages AS P
    ON P.iDocID = D.iDocID
WHERE D.iDocID IN (SELECT iDocID FROM MatchedDocuments)
ORDER BY D.iDocID, P.siPageNum;";

    public static SqlCommand CreateCommand(
        SqlConnection connection,
        string requestNumber,
        string fileName)
    {
        var command = new SqlCommand(Query, connection);
        command.Parameters.Add("@RequestNumber", SqlDbType.VarChar, 50).Value =
            requestNumber.Trim();
        command.Parameters.Add("@FileName", SqlDbType.NVarChar, 260).Value =
            fileName.Trim();
        return command;
    }
}
