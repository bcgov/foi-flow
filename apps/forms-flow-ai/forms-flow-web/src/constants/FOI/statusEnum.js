const StateList = Object.freeze({
    unopened: [{status: "Unopened", isSelected: false}],
    intakeinprogress: [{status:"Intake in Progress", isSelected: false}, {status: "Open", isSelected: false}, {status: "Redirect", isSelected: false}, {status: "Closed", isSelected: false}],
    redirect: [{status: "Redirect", isSelected: false}, {status:"Intake in Progress", isSelected: false}, {status: "Closed", isSelected: false}],
    open: [{status: "Open", isSelected: false}, {status: "Call For Records", isSelected: false}, {status: "Closed", isSelected: false}],
    callforrecords: [{status: "Call For Records", isSelected: false}, {status: "Open", isSelected: false}, {status: "Closed", isSelected: false}],
    feeassessed: [{status: "Fee Estimate", isSelected: false}, {status: "On Hold", isSelected: false}, {status: "Call For Records", isSelected: false}, {status: "Closed", isSelected: false}],
    onhold: [{status: "On Hold", isSelected: false}, {status: "Call For Records", isSelected: false}, {status: "Closed", isSelected: false}],
    deduplication: [{status: "Deduplication", isSelected: false}, {status: "Harms Assessment", isSelected: false}, {status: "Records Review", isSelected: false}, {status: "Closed", isSelected: false}],
    harms: [{status: "Harms Assessment", isSelected: false}, {status: "Closed", isSelected: false}],
    consult: [{status: "Consult", isSelected: false}, {status: "Records Review", isSelected: false}, {status: "Ministry Sign Off", isSelected: false}, {status: "Closed", isSelected: false}],
    review: [{status: "Records Review", isSelected: false}, {status: "Call For Records", isSelected: false}, {status: "Consult", isSelected: false}, {status: "Ministry Sign Off", isSelected: false}, {status: "Response", isSelected: false}, {status: "Closed", isSelected: false}],
    signoff: [{status: "Ministry Sign Off", isSelected: false}, {status: "Closed", isSelected: false}],
    response: [{status: "Response", isSelected: false}, {status: "On Hold", isSelected: false}, {status: "Records Review", isSelected: false}, {status: "Closed", isSelected: false}],
    closed: [{status: "Closed", isSelected: false}, {status: "Records Review", isSelected: false}, {status: "Response", isSelected: false}],
});

const MinistryStateList = Object.freeze({
    unopened: [{status: "Unopened", isSelected: false}],
    intakeinprogress: [{status:"Intake in Progress", isSelected: false}],
    redirect: [{status: "Redirect", isSelected: false}],
    open: [{status: "Open", isSelected: false}],
    callforrecords: [{status: "Call For Records", isSelected: false}, {status: "Fee Estimate", isSelected: false}, {status: "Deduplication", isSelected: false}, {status: "Records Review", isSelected: false}, {status: "Ministry Sign Off", isSelected: false}],
    feeassessed: [{status: "Fee Estimate", isSelected: false}],
    onhold: [{status: "On Hold", isSelected: false}],
    deduplication: [{status: "Deduplication", isSelected: false}],
    harms: [{status: "Harms Assessment", isSelected: false}, {status: "Call For Records", isSelected: false}, {status: "Records Review", isSelected: false}],
    consult: [{status: "Consult", isSelected: false}],
    review: [{status: "Records Review", isSelected: false}],
    signoff: [{status: "Ministry Sign Off", isSelected: false}, {status: "Records Review", isSelected: false}, {status: "Response", isSelected: false}],
    response: [{status: "Response", isSelected: false}],
    closed: [{status: "Closed", isSelected: false}],
});

const StateEnum = Object.freeze({
    open: {name: "Open", id: 1},
    callforrecords: {name: "Call For Records", id: 2},
    closed: {name: "Closed", id: 3},
    redirect: {name: "Redirect", id: 4},
    unopened: {name: "Unopened", id: 5},
    intakeinprogress: {name: "Intake in Progress", id: 6},
    review: {name: "Records Review", id: 7},
    feeassessed: {name: "Fee Estimate", id: 8},
    consult: {name: "Consult", id: 9},
    signoff: {name: "Ministry Sign Off", id: 10},
    onhold: {name: "On Hold", id: 11},
    deduplication: {name: "Deduplication", id: 12},
    harms: {name: "Harms Assessment", id: 13},
    response: {name: "Response", id: 14}
});

export { StateList, MinistryStateList, StateEnum };