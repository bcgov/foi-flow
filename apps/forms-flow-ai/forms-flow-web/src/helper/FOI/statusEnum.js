const stateList = Object.freeze({
    unopened: [{status: "Unopened", isSelected: false}, {status: "Intake in Progress", isSelected: false}],
    intakeinprogress: [{status:"Intake in Progress", isSelected: false}, {status: "Open", isSelected: false}, {status: "Closed", isSelected: false}, {status: "Redirect", isSelected: false}],
    open: [{status: "Open", isSelected: false}, {status: "Closed", isSelected: false}, {status: "Call for Records", isSelected: false}],
    closed: [{status: "Closed", isSelected: false},{status: "Open", isSelected: false}]
});

export { stateList };