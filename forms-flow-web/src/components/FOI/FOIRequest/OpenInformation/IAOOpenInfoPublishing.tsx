import { useState } from "react";
import "./iaoopeninfo.scss";
import IAOOpenInfoHeader from "./IAOOpenInfoHeader";
import IAOOpenInfoMain from "./IAOOpenInfoMain";

type OITransactionObject = {
  oipublicationstatusid: number;
  oiexemptionid: number;
  oiApproved: boolean | null;
  pagereferences: string;
  analystrationale: string;
  oifeedback: string;
};

const IAOOpenInfoPublishing = ({ requestNumber, requestDetails }: any) => {
  // const oiTxnData = {
  //   oipublicationstatusid: 1,
  //   oiexemptionid: 3,
  //   oiApproved: null,
  //   pagereferences: "",
  //   analystrationale: "",
  //   oifeedback: "",
  // };
  const oiTxnData = null;
  
  //Local State
  const [oiPublicationData, setOiPublicationData] = useState<OITransactionObject | null>(oiTxnData);
  console.log("BANG", oiPublicationData);

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
        oiPublicationData={oiPublicationData}/>
      <button
        type="button"
        className="btn btn-bottom"
        onClick={() => {
          console.log("SAVE");
        }}
        disabled={oiPublicationData === null}
      >
        Save
      </button>
    </div>
  );
};

export default IAOOpenInfoPublishing;
