
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
    return {
      id: index,
      divisionid: item.divisionid,
      stageid: item.stageid,
      divisionDueDate: item.divisionDueDate,
      eApproval: item.eApproval,
      divisionReceivedDate: item.divisionReceivedDate
    };
  });
};

export const updateDivisions = (e, id, minDivStages, setStates) => {
  let arr = minDivStages;
  const idExists = arr.some((st) => st.id === id);

  if (!idExists) {
    return;
  }

  arr
    .filter((item) => item.id === id)
    .forEach((item) => {
      item.divisionid = e.target.value;
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
      if(!(item.stageid == 5 || item.stageid == 7 || item.stageid == 9)){
        item.divisionDueDate = null;
        item.eApproval = null;
      }
      else if(!(item.stageid == 6 || item.stageid == 8 || item.stageid == 10)){
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
