const stateList = Object.freeze({
    unopened: [{status: "Unopened", isSelected: false}, {status: "Intake in Progress", isSelected: false}],
    intakeinprogress: [{status:"Intake in Progress", isSelected: false}, {status: "Open", isSelected: false}, {status: "Closed", isSelected: false}, {status: "Redirect", isSelected: false}],
    open: [{status: "Open", isSelected: false}, {status: "Closed", isSelected: false}, {status: "Call For Records", isSelected: false}],
    closed: [{status: "Closed", isSelected: false},{status: "Open", isSelected: false}],
    redirect: [{status: "Redirect", isSelected: false},{status: "Closed", isSelected: false}],
    callforrecords: [{status: "Call For Records", isSelected: false},{status: "Redirect", isSelected: false},{status: "Closed", isSelected: false}],
});

export { stateList };