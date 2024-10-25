import { useState, useEffect } from "react";
import "./iaoopeninfo.scss";
import IAOOpenInfoHeader from "./IAOOpenInfoHeader";
import IAOOpenInfoMain from "./IAOOpenInfoMain";
import user from "../../../../modules/userDetailReducer";

type OITransactionObject = {
  oipublicationstatus_id: number;
  oiexemption_id: number | null;
  oiexemptionapproved: boolean | null;
  pagereference: string;
  iaorationale: string;
  oifeedback: string;
};

const IAOOpenInfoPublishing = ({ requestNumber, requestDetails, userDetail, foiOITransactionData }: any) => {
  // const oiTxnData = {
  //   oipublicationstatus_id: 2,
  //   oiexemption_id: null,
  //   oiexemptionapproved: null,
  //   pagereference: "",
  //   iaorationale: "",
  //   oifeedback: "",
  //   isactive: true,
  //   foiministryrequestid: 1,
  //   foirequestopeninfoid: 1,
  //   version: 1
  // }; // AH NOTE -> if data is null -> use the above default state. REMOVE THIS AS A REQUEST WILL ALWAYS HAVE FOIOPENINFO DATA IN BE

  const userGroups: string[] = userDetail.groups.map((group : any) => group.slice(1));
  const isOIUser : boolean = userGroups.includes("OI Team");

  //Local State
  const [oiPublicationData, setOiPublicationData] = useState<OITransactionObject | null>(foiOITransactionData);
  console.log("BANG", oiPublicationData)
  console.log(userDetail, "userdetail")
  console.log("userGroups", userGroups)

  //Functions
  const handleOIDataChange = (value: number | string | boolean, oiDataKey: string) => {
    setOiPublicationData((prev: any) => ({
      ...prev,
      [oiDataKey]: value,
    }));
  };
  
  return (
    <div className="oi-section">
      <IAOOpenInfoHeader
        requestDetails={requestDetails}
        requestNumber={requestNumber}
      />
      <IAOOpenInfoMain 
        handleOIDataChange={handleOIDataChange} 
        oiPublicationData={oiPublicationData}
        isOIUser={isOIUser}
        />
      <button
        type="button"
        className="btn btn-bottom"
        onClick={() => {
          console.log("SAVE");
        }}
        disabled={(oiPublicationData?.oiexemption_id === null && oiPublicationData?.oipublicationstatus_id === 1) || requestDetails?.oiPublication === null} 
        // AH NOTE -> THIS WILL BE BUGGY IF CHANGED BACK TO PUBLISH. 
        // IF status changed back to any other besides do not publish -> wipe data? ASK MATT ON EDITING DATA AFTER AND WIPING DATA IF STATUS CHANGED
        // Save button disabled = if on original load no foiopeninforequest exists (and using default obj) OR exmeption reason is null && publicationSTatusid is not 2
      >
        Save
      </button>
    </div>
  );
};

export default IAOOpenInfoPublishing;

/* To do 
1. create get, post api route for foioirequest data
2. trigger get route in FE to gather all the data
3. trigger post route in FE to post foioi txn data (done when save button clicked and when request is closed)
4. finalzie FE ux for iao side of things
*/
