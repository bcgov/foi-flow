import React from "react";
import { shallow } from "enzyme";
import { useDispatch, useSelector } from "react-redux";
import { retryFOIRecordProcessing } from "../../../../apiManager/services/FOI/foiRecordServices";
import { RecordsLog } from "./index";

jest.mock("react-redux", () => ({ useSelector: jest.fn(), useDispatch: jest.fn() }));
jest.mock("client-zip", () => ({ downloadZip: jest.fn() }));
jest.mock("../../../../apiManager/services/FOI/foiRecordServices", () => ({
  retryFOIRecordProcessing: jest.fn(() => ({ type: "RETRY_RECORD" })),
}));
jest.mock("../../../../apiManager/services/FOI/foiOSSServices", () => ({}));
jest.mock("../../../../apiManager/services/FOI/foiAttachmentServices", () => ({}));
jest.mock("../../../../apiManager/services/FOI/foiRequestServices", () => ({}));
jest.mock("../../Dashboard/utils", () => ({ ClickableChip: () => null }));
jest.mock("../Attachments/AttachmentModal", () => () => null);
jest.mock("./MCFPersonal", () => () => null);
jest.mock("./MSDPersonal", () => () => null);
jest.mock("./PhaseMenu", () => () => null);
jest.mock("../DocumentSet/FileInfoBar", () => () => null);
jest.mock("../DocumentSet/DocumentSetWrapper", () => () => null);
jest.mock("../DocumentSet/DocumentSetModal", () => () => null);
jest.mock("../DocumentSet/DocumentSetDeleteModal", () => () => null);
jest.mock("./RedactRecordsButton", () => () => null);
jest.mock("../RequestHeaderRow", () => () => null);

const makeRecord = (overrides = {}) => ({
  recordid: 1,
  filename: "record.pdf",
  created_at: new Date().toString(),
  createdby: "tester",
  s3uripath: "records/record.pdf",
  attributes: { divisions: [], filesize: 1024 },
  attachments: [],
  isduplicate: false,
  isdedupecomplete: true,
  iscompressed: true,
  isredactionready: false,
  selectedfileprocessversion: null,
  ocrfilepath: null,
  ...overrides,
});

function renderRecord(record) {
  const state = {
    user: { userDetail: { groups: [] } },
    foiRequests: {
      foiRequestRecords: { records: [record] },
      isRecordsLoading: "completed",
      foiRequestDetail: { currentState: "Records Review" },
    },
  };
  useSelector.mockImplementation((selector) => selector(state));
  const records = shallow(<RecordsLog divisions={[]} bcgovcode="EDUC"
    validLockRecordsState={() => false}
    requestId="1" ministryId="2" iaoassignedToList={[]} ministryAssignedToList={[]} />);
  return records.findWhere((node) => node.prop("record") === record &&
    typeof node.prop("handlePopupButtonClick") === "function").first();
}

beforeEach(() => {
  jest.clearAllMocks();
  jest.useFakeTimers("modern");
  jest.setSystemTime(new Date("2026-09-29T17:30:00Z"));
  useDispatch.mockReturnValue(jest.fn());
});

afterEach(() => jest.useRealTimers());

test("record status changes from OCR processing to failure to ready", () => {
  const running = makeRecord();
  const row = renderRecord(running).dive();
  expect(row.text()).toContain("OCR in progress");

  row.setProps({ record: { ...running, failed: "OCR" } });
  expect(row.text()).toContain("Error during OCR");
  expect(row.text()).not.toContain("OCR in progress");

  row.setProps({ record: { ...running, isredactionready: true, ocrfilepath: "records/recordOCR.pdf" } });
  expect(row.text()).toContain("Ready for Redaction");
  expect(row.text()).not.toContain("Error during");
});

test("timeout remains visible unless an explicit failure takes precedence", () => {
  const record = makeRecord({ created_at: "2020 Jan 01 | 10:00 AM" });
  const row = renderRecord(record).dive();
  expect(row.text()).toContain("Error due to timeout");
  row.setProps({ record: { ...record, failed: "OCR" } });
  expect(row.text()).toContain("Error during OCR");
  expect(row.text()).not.toContain("Error due to timeout");
});

test("a selected file version keeps precedence over an OCR failure", () => {
  const row = renderRecord(makeRecord({ failed: "OCR", selectedfileprocessversion: 1 })).dive();
  expect(row.text()).toContain("Ready for Redaction");
  expect(row.text()).not.toContain("Error during OCR");
});

test.each(["OCR", "ocr", "ocr-queue. old message"])("retry routes %s to the OCR service", (failed) => {
  const record = makeRecord({ failed });
  renderRecord(record).prop("handlePopupButtonClick")("retry", record);
  expect(retryFOIRecordProcessing).toHaveBeenCalledWith("1", "2", {
    records: [expect.objectContaining({ service: "ocr", trigger: "recordretry" })],
  }, expect.any(Function));
});
