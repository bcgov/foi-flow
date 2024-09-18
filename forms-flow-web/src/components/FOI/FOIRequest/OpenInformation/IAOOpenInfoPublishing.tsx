import "./iaoopeninfo.scss";
import IAOOpenInfoHeader from "./IAOOpenInfoHeader";
import IAOOpenInfoMain from "./IAOOpenInfoMain";

const IAOOpenInfoPublishing = ({ requestNumber, requestDetails }: any) => {

  const oiTxnData = {
    oipublicationstatusid: 1,
    oiexemptionid: 3,
    oiApproved: null,
    pagereferences: "",
    analystrationale: "",
    oifeedback: "",
  }

  return (
    <div className="oi-section">
      <IAOOpenInfoHeader
        requestDetails={requestDetails}
        requestNumber={requestNumber}
      />
      <IAOOpenInfoMain oiPublicaitionObj={null} />
    </div>
  );
};

export default IAOOpenInfoPublishing;
