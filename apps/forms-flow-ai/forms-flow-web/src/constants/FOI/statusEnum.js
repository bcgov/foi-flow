const StateList = Object.freeze({
    unopened: [{status: "Unopened", isSelected: false}, {status: "Intake in Progress", isSelected: false}],
    intakeinprogress: [{status:"Intake in Progress", isSelected: false}, {status: "Open", isSelected: false}, {status: "Closed", isSelected: false}, {status: "Redirect", isSelected: false}],
    open: [{status: "Open", isSelected: false}, {status: "Closed", isSelected: false}, {status: "Call For Records", isSelected: false}],
    closed: [{status: "Closed", isSelected: false},{status: "Open", isSelected: false}],
    redirect: [{status: "Redirect", isSelected: false},{status: "Closed", isSelected: false}],
    callforrecords: [{status: "Call For Records", isSelected: false},{status: "Review", isSelected: false},{status: "Fee Assessed", isSelected: false},{status: "Open", isSelected: false},{status: "Closed", isSelected: false}],
    review: [{status: "Review", isSelected: false},{status: "Call For Records", isSelected: false},{status: "Consult", isSelected: false},{status: "Ministry Sign Off", isSelected: false},{status: "Closed", isSelected: false}],
    consult: [{status: "Consult", isSelected: false},{status: "Review", isSelected: false},{status: "Closed", isSelected: false}],
    feeassessed: [{status: "Fee Assessed", isSelected: false},{status: "Review", isSelected: false},{status: "Consult", isSelected: false},{status: "Ministry Sign Off", isSelected: false},{status: "Closed", isSelected: false}],
    signoff: [{status: "Ministry Sign Off", isSelected: false},{status: "Closed", isSelected: false}],
});

const MinistryStateList = Object.freeze({
    unopened: [{status: "Unopened", isSelected: false}],
    intakeinprogress: [{status:"Intake in Progress", isSelected: false}],
    open: [{status: "Open", isSelected: false}],
    closed: [{status: "Closed", isSelected: false}],
    redirect: [{status: "Redirect", isSelected: false}],
    //callforrecords: [{status: "Call For Records", isSelected: false},{status: "Review", isSelected: false},{status: "Fee Assessed", isSelected: false}],
    callforrecords: [{status: "Call For Records", isSelected: false},{status: "Review", isSelected: false}],
    review: [{status: "Review", isSelected: false}],
    consult: [{status: "Consult", isSelected: false}],
    feeassessed: [{status: "Fee Assessed", isSelected: false}],
    signoff: [{status: "Ministry Sign Off", isSelected: false}],
});

const StateEnum = Object.freeze({
    open: {name: "Open", id: 1},
    callforrecords: {name: "Call For Records", id: 2},
    closed: {name: "Closed", id: 3},
    redirect: {name: "Redirect", id: 4},
    unopened: {name: "Unopened", id: 5},
    intakeinprogress: {name: "Intake in Progress", id: 6},
    review: {name: "Review", id: 7},
    feeassessed: {name: "Fee Assessed", id: 8},
    consult: {name: "Consult", id: 9},
    signoff: {name: "Ministry Sign Off", id: 10},
    callforrecordsoverdue: {name: "Call For Records Overdue", id: 11}
});

export { StateList, MinistryStateList, StateEnum };