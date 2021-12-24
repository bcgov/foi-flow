
export const calculateStageCounter = (existingDivStages) => {
  if (existingDivStages.length === 0 || !existingDivStages) {
    return [{
      id: 0,
      divisionid: -1,
      stageid: -1,
    }];
  }

  return existingDivStages.map((item, index) => {
    return {
      id: index,
      divisionid: item.divisionid,
      stageid: item.stageid,
    };
  });
};

export const updateDivisions = (e, id, minDivStages, setStates) => {
  let arr = minDivStages;
  const idExists = arr.some((st) => st.id === id);

  if (!idExists) {
    console.log("No Id found - handleDivisionChange ");
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
    console.log("No Id found - handleDivisionStageChange ");
    return;
  }

  arr
    .filter((st) => st.id === id)
    .forEach((item) => {
      item.stageid = e.target.value;
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
    existing.push({ id: val, divisionid: -1, stageid: -1 });
    setStates(existing);
  }
};
