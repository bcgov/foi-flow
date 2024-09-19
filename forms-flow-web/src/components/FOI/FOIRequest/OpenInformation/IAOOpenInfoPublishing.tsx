import { useState } from "react";
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

const IAOOpenInfoPublishing = ({ requestNumber, requestDetails, userDetail }: any) => {
  const oiTxnData = {
    oipublicationstatus_id: 2,
    oiexemption_id: null,
    oiexemptionapproved: null,
    pagereference: "",
    iaorationale: "",
    oifeedback: "",
  }; // AH NOTE -> if data is null -> use the above default state
  const userGroups: string[] = userDetail.groups.map((group : any) => group.slice(1));
  const isOIUser : boolean = userGroups.includes("OI Team");

  //Local State
  const [oiPublicationData, setOiPublicationData] = useState<OITransactionObject | null>(oiTxnData);
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
        disabled={oiPublicationData?.oipublicationstatus_id === 2} // AH NOTE -> THIS WILL BE BUGGY IF CHANGED BACK TO PUBLISH
      >
        Save
      </button>
    </div>
  );
};

export default IAOOpenInfoPublishing;
