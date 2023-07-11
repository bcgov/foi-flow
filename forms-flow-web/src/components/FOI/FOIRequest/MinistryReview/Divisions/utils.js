
export const calculateStageCounter = (existingDivStages) => {
  if (existingDivStages.length === 0 || !existingDivStages) {
    return [{
      id: 0,
      divisionid: -1,
      stageid: -1,
      divisionDueDate: null,
      eApproval: null,
      divisionReceivedDate: null
    }];
  }

  return existingDivStages.map((item, index) => {
    item.id = index;
    return item;
  });
};

export const stageForReceivedDateExists = (divisionstageList, selectedStageId) => {
  if(selectedStageId != -1){
    const stagesForReceivedDate = divisionstageList?.filter(
      (element) => (element.name === "Records Received" || element.name === "Harms Received" || 
      element.name === "Sign Off Complete")
    ).map(obj => obj.stageid);
    return !!(stagesForReceivedDate.includes(selectedStageId))
  }
  return false;
}

export const stageForDueDateExists = (divisionstageList, selectedStageId) => {
  if(selectedStageId != -1){
    const stagesForDueDate = divisionstageList?.filter(
      (element) => (element.name === "Gathering Records" || element.name === "Awaiting Harms" || 
      element.name === "Pending Sign Off")
    ).map(obj => obj.stageid);
    return !!(stagesForDueDate.includes(selectedStageId))
  }
  return false;
}

export const updateDivisions = (newValue, id, minDivStages, setStates) => {
  let arr = minDivStages;
  const idExists = arr.some((st) => st.id === id);

  if (!idExists) {
    return;
  }

  arr
    .filter((item) => item.id === id)
    .forEach((item) => {
      item.divisionid = newValue.divisionid;
      item.divisionname = newValue.label
    });

  setStates(arr);
};

export const updateDivisionsState = (e, id, minDivStages, setStates) => {
  let arr = minDivStages;
  const exists = arr.some((st) => st.id === id);

  if (!exists) {
    return;
  }

  arr
    .filter((st) => st.id === id)
    .forEach((item) => {
      item.stageid = e.target.value;
      if(!stageForDueDateExists(arr, item.stageid)){
        item.divisionDueDate = null;
        item.eApproval = null;
      }
      if(!stageForReceivedDateExists(arr, item.stageid)){
        item.divisionReceivedDate = null;
      }

    });
  setStates(arr);
};

export const addDivisionalStage = (stageIterator, divisionList, setStates) => {
  let existing = stageIterator;
  let val =
    stageIterator.length > 0
      ? stageIterator[stageIterator.length - 1].id + 1
      : 0;
  if (divisionList.length > stageIterator.length) {
    existing.push({ id: val, divisionid: -1, stageid: -1, divisionDueDate: null, eApproval: null });
    setStates(existing);
  }
};

export const updateEApproval = (e, id, minDivStages, setStates) => {
  let arr = minDivStages;

  const exists = arr.some((st) => st.id === id);

  if (!exists) {
    return;
  }

  arr
    .filter((st) => st.id === id)
    .forEach((item) => {
        item.eApproval = e.target.value;
    });
  setStates(arr);
};

export const updateDivisonDate = (e, id, dateType, minDivStages, setStates) => {
  let arr = minDivStages;

  const exists = arr.some((st) => st.id === id);

  if (!exists) {
    return;
  }

  arr
    .filter((st) => st.id === id)
    .forEach((item) => {
        if(dateType.toLowerCase() == 'duedate')
          item.divisionDueDate = e.target.value;
        else if(dateType.toLowerCase() == 'receiveddate')
          item.divisionReceivedDate = e.target.value;
    });
  setStates(arr);
};
