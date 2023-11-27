import { useState, useEffect } from "react";
import { useSelector } from "react-redux";

const useOIPCHook = () => {
  //OIPC State
  const requestDetails = useSelector((state) => state.foiRequests.foiRequestDetail);
  const stageOIPCData = (isoipcreview, oipcData) => {
    if (isoipcreview) {
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
          receiveddate: null,
          closeddate: null,
          investigator: "", 
          outcomeid: null, 
          isjudicialreview: false, 
          issubsequentappeal: false,
        }];
      }
    } else {
      return [];
    }
  }
  const [oipcData, setOipcData] = useState(requestDetails.oipcdetails);

  useEffect(() => {
    const stagedOIPCData = stageOIPCData(requestDetails.isoipcreview, requestDetails.oipcdetails);
    setOipcData(stagedOIPCData);
  }, [requestDetails])

  console.log("HOOK", oipcData)

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
        receiveddate: null,
        closeddate: null,
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
    stageOIPCData,
  };
};

export default useOIPCHook;