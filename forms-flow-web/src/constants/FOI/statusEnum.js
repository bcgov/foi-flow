const StateList = Object.freeze({
    unopened: [{status: "Unopened", isSelected: false}, {status:"Intake in Progress", isSelected: false}],
    intakeinprogress: [{status:"Intake in Progress", isSelected: false}, {status: "Open", isSelected: false}, {status:"Peer Review", isSelected: false}, {status: "Redirect", isSelected: false}, {status: "Closed", isSelected: false}],
    redirect: [{status: "Redirect", isSelected: false}, {status:"Intake in Progress", isSelected: false}, {status: "Closed", isSelected: false}],
    open: [{status: "Open", isSelected: false}, {status: "Call For Records", isSelected: false}, {status:"Peer Review", isSelected: false},{status: "Closed", isSelected: false}],
    callforrecords: [{status: "Call For Records", isSelected: false}, {status: "Open", isSelected: false}, {status: "Closed", isSelected: false}],
    feeassessed: [{status: "Fee Estimate", isSelected: false}, {status: "On Hold", isSelected: false}, {status: "Call For Records", isSelected: false}, {status: "Closed", isSelected: false}],
    feeassessedforpersonal: [{status: "Fee Estimate", isSelected: false}, {status: "Call For Records", isSelected: false}, {status: "Closed", isSelected: false}],
    onhold: [{status: "On Hold", isSelected: false}, {status: "Call For Records", isSelected: false}, {status: "Closed", isSelected: false}],
    deduplication: [{status: "Deduplication", isSelected: false}, {status: "Harms Assessment", isSelected: false}, {status: "Records Review", isSelected: false}, {status: "Closed", isSelected: false}],
    harms: [{status: "Harms Assessment", isSelected: false}, {status: "Closed", isSelected: false}],
    consult: [{status: "Consult", isSelected: false}, {status: "Records Review", isSelected: false}, {status: "Ministry Sign Off", isSelected: false}, {status:"Peer Review", isSelected: false}, {status: "Closed", isSelected: false}],
    review: [{status: "Records Review", isSelected: false}, {status: "Call For Records", isSelected: false}, {status: "Consult", isSelected: false}, {status: "Ministry Sign Off", isSelected: false}, {status:"Peer Review", isSelected: false}, {status: "Response", isSelected: false}, {status: "Closed", isSelected: false}],
    signoff: [{status: "Ministry Sign Off", isSelected: false}, {status: "Closed", isSelected: false}],
    response: [{status: "Response", isSelected: false}, {status: "On Hold", isSelected: false}, {status: "Records Review", isSelected: false}, {status:"Peer Review", isSelected: false}, {status: "Closed", isSelected: false}],
    responseforpersonal: [{status: "Response", isSelected: false}, {status: "Records Review", isSelected: false}, {status:"Peer Review", isSelected: false}, {status: "Closed", isSelected: false}],
    //peerreview: [{status:"Peer Review", isSelected: false},{status:"Intake in Progress", isSelected: false}, {status: "Open", isSelected: false},{status: "Records Review", isSelected: false},{status: "Consult", isSelected: false},{status: "Response", isSelected: false}],
    peerreview: [{status:"Peer Review", isSelected: false}]
  });

const MinistryStateList = Object.freeze({
    unopened: [{status: "Unopened", isSelected: false}],
    intakeinprogress: [{status:"Intake in Progress", isSelected: false}],
    redirect: [{status: "Redirect", isSelected: false}],
    open: [{status: "Open", isSelected: false}],
    callforrecords: [{status: "Call For Records", isSelected: false}, {status: "Fee Estimate", isSelected: false}, {status: "Harms Assessment", isSelected: false}, {status: "Deduplication", isSelected: false}, {status: "Records Review", isSelected: false}, {status: "Ministry Sign Off", isSelected: false}],
    callforrecordsforpersonal: [{status: "Call For Records", isSelected: false}, {status: "Harms Assessment", isSelected: false}, {status: "Deduplication", isSelected: false}, {status: "Records Review", isSelected: false}, {status: "Ministry Sign Off", isSelected: false}],
    feeassessed: [{status: "Fee Estimate", isSelected: false}],
    onhold: [{status: "On Hold", isSelected: false}],
    deduplication: [{status: "Deduplication", isSelected: false}],
    harms: [{status: "Harms Assessment", isSelected: false}, {status: "Call For Records", isSelected: false}, {status: "Records Review", isSelected: false}],
    consult: [{status: "Consult", isSelected: false}],
    review: [{status: "Records Review", isSelected: false}],
    signoff: [{status: "Ministry Sign Off", isSelected: false}, {status: "Records Review", isSelected: false}, {status: "Response", isSelected: false}],
    response: [{status: "Response", isSelected: false}],
    closed: [{status: "Closed", isSelected: false}],
    peerreview: [{status: "Peer Review", isSelected: false}],
});

const StateEnum = Object.freeze({
    open: {name: "Open", id: 1},
    callforrecords: {name: "Call For Records", id: 2},
    callforrecordsoverdue: {name: "Call For Records Overdue", id: 17},
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
    response: {name: "Response", id: 14},
    archived: {name: "Archived", id: 15},
    peerreview: {name: "Peer Review", id: 16}
});

const StateTransitionCategories = Object.freeze({
  cfrreview: {
    name: "cfr-review",
    fromState: "Call For Records",
    toState: "Records Review",
  },
  cfrfeeassessed: {
    name: "cfr-feeassessed",
    fromState: "Call For Records",
    toState: "Fee Estimate",
  },
  signoffresponse: {
    name: "signoff-response",
    fromState: "Ministry Sign Off",
    toState: "Response",
  },
  harmsreview: {
    name: "harms-review",
    fromState: "Harms Assessment",
    toState: "Records Review",
  },
  feeonhold: {
    name: "feeassessed-onhold",
    fromState: "Fee Estimate",
    toState: "On Hold",
  },
  responseonhold: {
    name: "response-onhold",
    fromState: "Response",
    toState: "On Hold",
  },
  responsereview: {
    name: "response-review",
    fromState: "Response",
    toState: "Records Review",
  },
  signoffreview: {
    name: "signoff-review",
    fromState: "Ministry Sign Off",
    toState: "Records Review",
  },
});

const AttachmentCategories = Object.freeze({
  categorys: [
    {
      name: "general",
      tags: ["general"],
      display: "General",
      bgcolor: "#003366",
      type: ["tag"],
    },
    {
      name: "personal",
      tags: ["personal"],
      display: "Personal",
      bgcolor: "#FAA915",
      type: ["personal"],
    },
    {
      name: "extension - denied",
      tags: ["extension - denied"],
      display: "Extension - Denied",
      bgcolor: "#F03E22",
      type: ["extension"],
    },
    {
      name: "extension - approved",
      tags: ["extension - approved"],
      display: "Extension - Approved",
      bgcolor: "#136C14",
      type: ["extension"],
    },
    {
      name: "cfr-review",
      tags: ["cfr-review"],
      display: "CFR > Review",
      bgcolor: "#04596C",
      type: ["transition"],
    },
    {
      name: "cfr-feeassessed",
      tags: ["cfr-feeassessed"],
      display: "CFR > Fee Estimate",
      bgcolor: "#721121",
      type: ["transition"],
    },
    {
      name: "signoff-response",
      tags: ["signoff-response"],
      display: "Sign Off > Response",
      bgcolor: "#020A80",
      type: ["transition"],
    },
    {
      name: "harms-review",
      tags: ["harms-review"],
      display: "Harms > Review",
      bgcolor: "#04596C",
      type: ["transition"],
    },
    { // tag: Add Attachment Modal
      name: "applicant",
      tags: ["applicant"],
      display: "Applicant",
      bgcolor: "#F99F16",
      type: ["tag"],
    },
    { // transition: Fee estimate -> On hold
      name: "feeassessed-onhold",
      tags: ["applicant", "feeassessed-onhold"],
      display: "Applicant",
      bgcolor: "#F99F16",
      type: ["transition"],
    },
    {
      name: "cfr",
      tags: ["cfr"],
      display: "CFR",
      bgcolor: "#D0017A",
      type: ["tag"],
    },
    {
      name: "recordsreview",
      tags: ["recordsreview"],
      display: "Records Review",
      bgcolor: "#04596C",
      type: ["tag"],
    },
    {
      name: "fees",
      tags: ["fees"],
      display: "Fees",
      bgcolor: "#721121",
      type: ["tag"],
    },
    {
      name: "response",
      tags: ["response"],
      display: "Response",
      bgcolor: "#020A80",
      type: ["tag"],
    },
    {
      name: "harms",
      tags: ["harms"],
      display: "Harms",
      bgcolor: "#832AB7",
      type: ["tag"],
    },
    {
      name: "oipc",
      tags: ["oipc"],
      display: "OIPC",
      bgcolor: "#595959",
      type: ["tag"],
    },
    {
      name: "extensions",
      tags: ["extensions"],
      display: "Extensions",
      bgcolor: "#1A1A1A",
      type: ["tag"],
    },
	{
      name: "ministrysignoff",
      tags: ["ministrysignoff"],
      display: "Ministry Sign Off",
      bgcolor: "#4B296B",
      type: ["tag"],
    },
    { // transition: Response -> On hold
      name: "response-onhold",
      tags: ["response-onhold"],
      display: "Response > On Hold",
      bgcolor: "#F99F16",
      type: ["transition"],
    },
    { // transition: Records Review -> Response
      name: "response-review",
      tags: ["response-review"],
      display: "Response > Review",
      bgcolor: "#04596C",
      type: ["transition"],
    },
    { // transition: Records Review -> Response
      name: "signoff-review",
      tags: ["signoff-review"],
      display: "Sign Off > Review",
      bgcolor: "#04596C",
      type: ["transition"],
    },
  ]
});

const AttachmentLetterCategories = Object.freeze({
  feeestimateletter: {
    name: "fee estimate - letter",
  },
  feeestimatefailed: {
    name: "fee estimate - correspondence - failed",
  },
  feeestimatesuccessful: {
    name: "fee estimate - successful",
  },
  feeestimatepaymentreceipt: {
    name: "fee estimate - payment receipt"
  },
  feeestimatepaymentcorrespondencesuccessful: {
    name: "fee estimate - payment success"
  },
  feeestimatepaymentcorrespondencefailed: {
    name: "fee estimate - payment success - correspondence failed"
  },
  feeestimateoutstandingletter: {
    name: "fee balance outstanding - letter",
  },
});

export { StateList, MinistryStateList, StateEnum, StateTransitionCategories, AttachmentCategories, AttachmentLetterCategories };