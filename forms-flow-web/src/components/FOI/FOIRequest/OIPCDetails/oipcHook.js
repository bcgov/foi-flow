import { useState } from "react";
import { useSelector } from "react-redux";

const useOIPCHook = () => {
  //OIPC State
  const requestDetails = useSelector((state) => state.foiRequests.foiRequestDetail);
  const stageOIPCData = (oipcData) => {
    if (oipcData?.length > 0) {
      return oipcData.map((item, index) => {
        item.id = index;
        return item;
      });
    } else {
      return [{
        id: 0,
        oipcno: "", 
        reviewtypeid: null, 
        reasonid: null, 
        statusid: null, 
        isinquiry: false,
        inquiryattributes: null,  
        receiveddate: "",
        closeddate: "",
        investigator: "", 
        outcomeid: null, 
        isjudicialreview: false, 
        issubsequentappeal: false,
      }];
    }
  }
  const [oipcData, setOipcData] = useState(stageOIPCData(requestDetails.oipcdetails));

  //OIPC Functions
  const addOIPC = () => {
    setOipcData((prev) => {
      return [...prev, {
        id: oipcData.length > 0 ? oipcData[oipcData.length - 1].id + 1 : 0,
        oipcno: "", 
        reviewtypeid: null, 
        reasonid: null, 
        statusid: null, 
        isinquiry: false,
        inquiryattributes: null,  
        receiveddate: "",
        closeddate: "",
        investigator: "", 
        outcomeid: null, 
        isjudicialreview: false, 
        issubsequentappeal: false,
      }];
    })
  }
  const removeOIPC = (oipcId) => {
    setOipcData((prev) => {
      const previousOIPCData = [...prev];
      return previousOIPCData.filter(oipc => oipcId !== oipc.id);
    });
  }
  const updateOIPC = (newOIPCObj) => {
    setOipcData((prev) => {
      const previousOIPCData = [...prev];
      return previousOIPCData.map((oipc) => {
        if (oipc.id === newOIPCObj.id) {
          return newOIPCObj;
        } else {
          return oipc;
        }
      });
    });
  }

  return {
    oipcData,
    addOIPC,
    removeOIPC,
    updateOIPC,
  };
};

export default useOIPCHook;