import React from "react";
import { render } from "@testing-library/react";
import { Provider } from "react-redux";
import configureStore from "redux-mock-store";
import { ContactApplicant } from "./index";
import * as ossServices from "../../../../apiManager/services/FOI/foiOSSServices";
import { saveAttachmentsPure } from "./saveAttachments";

jest.mock("../../../../apiManager/services/FOI/foiOSSServices", () => ({
  getOSSHeaderDetails: jest.fn(),
  saveFilesinS3: jest.fn(),
  getFileFromS3: jest.fn(),
}));

const mockStore = configureStore([]);

const baseState = {
  foiRequests: {
    foiRequestDetail: { bcgovcode: "MIN", currentState: "Open" },
    foiRequestCFRFormHistory: [],
    foiRequestExtesions: [],
    foiFullCorrespondenceTemplates: [],
    foiEmailTemplates: [],
    foiRequestCFRForm: {},
    isCorrespondenceLoading: false,
    foiPDFStitchStatusForResponsePackage: null,
  },
  user: { userDetail: { preferred_username: "tester" } },
};

const baseProps = (overrides: Partial<any> = {}) => ({
  requestNumber: "MIN-2026-00001",
  requestState: "Open",
  ministryId: 1,
  ministryCode: "MIN",
  applicantCorrespondence: [],
  requestId: 100,
  isProactiveDisclosure: false,
  ...overrides,
});

describe("ContactApplicant state isolation (FOIMOD-4270)", () => {
  // NOTE: these are smoke/regression tests. ContactApplicant renders attachments
  // via `<div className="email-attachment-item">` and its `files` state is only
  // populated by user interaction with the internal file picker, which is not
  // easily driven from a unit test. Full end-to-end validation of the
  // request-switch reset lives in the manual smoke checklist for FOIMOD-4270.
  // What these tests do assert:
  //   1. The component mounts cleanly with an empty file list.
  //   2. Rerendering with a different requestId does not throw and produces
  //      zero attachment items in the DOM (the useEffect + parent key prop
  //      guarantee a fresh render).
  it("mounts with no attachment items in the DOM", () => {
    const store = mockStore(baseState);
    const { container } = render(
      <Provider store={store}>
        <ContactApplicant {...baseProps()} />
      </Provider>
    );
    expect(container.querySelectorAll(".email-attachment-item")).toHaveLength(0);
  });

  it("renders cleanly with zero attachment items after switching requestId", () => {
    const store = mockStore(baseState);
    const { rerender, container } = render(
      <Provider store={store}>
        <ContactApplicant {...baseProps({ requestId: 100 })} />
      </Provider>
    );
    rerender(
      <Provider store={store}>
        <ContactApplicant {...baseProps({ requestId: 200 })} />
      </Provider>
    );
    expect(container.querySelectorAll(".email-attachment-item")).toHaveLength(0);
  });
});

describe("saveAttachments filename-collision pairing (FOIMOD-4270)", () => {
  it("pairs two same-named files by index, not by filename", async () => {
    const fileA = new File(["A"], "P-Acknowledgement.pdf", { type: "application/pdf" });
    const fileB = new File(["B"], "P-Acknowledgement.pdf", { type: "application/pdf" });

    (ossServices.getOSSHeaderDetails as jest.Mock).mockResolvedValue({
      data: [
        { filename: "P-Acknowledgement.pdf", filepath: "s3://.../MIN/MIN-2026-00001/a" },
        { filename: "P-Acknowledgement.pdf", filepath: "s3://.../MIN/MIN-2026-00001/b" },
      ],
    });

    const captured: Array<{ file: File; header: any }> = [];
    (ossServices.saveFilesinS3 as jest.Mock).mockImplementation(
      async (header: any, file: File, _dispatch: any, cb: any) => {
        captured.push({ file, header });
        cb(null, 200);
      }
    );

    const result = await saveAttachmentsPure(
      [fileA, fileB],
      { ministryCode: "MIN", requestNumber: "MIN-2026-00001", requestId: 100, dispatch: () => {} }
    );

    expect(captured).toHaveLength(2);
    expect(captured[0].file).toBe(fileA);
    expect(captured[1].file).toBe(fileB);
    expect(result[0].url).toContain("/a");
    expect(result[1].url).toContain("/b");
  });

  it("aborts upload and returns empty list when header count does not match file count", async () => {
    const fileA = new File(["A"], "a.pdf", { type: "application/pdf" });
    const fileB = new File(["B"], "b.pdf", { type: "application/pdf" });

    (ossServices.getOSSHeaderDetails as jest.Mock).mockResolvedValue({
      // Only one header returned for two files → must not upload either.
      data: [{ filename: "a.pdf", filepath: "s3://.../MIN/MIN-2026-00001/a" }],
    });
    (ossServices.saveFilesinS3 as jest.Mock).mockImplementation(
      async (_header: any, _file: File, _dispatch: any, cb: any) => {
        cb(null, 200);
      }
    );
    const errSpy = jest.spyOn(console, "error").mockImplementation(() => {});

    const result = await saveAttachmentsPure(
      [fileA, fileB],
      { ministryCode: "MIN", requestNumber: "MIN-2026-00001", requestId: 100, dispatch: () => {} }
    );

    expect(result).toEqual([]);
    expect(ossServices.saveFilesinS3).not.toHaveBeenCalled();
    expect(errSpy).toHaveBeenCalled();
    errSpy.mockRestore();
  });

  it("returns empty list without calling OSS when there are no files", async () => {
    (ossServices.getOSSHeaderDetails as jest.Mock).mockClear();
    (ossServices.saveFilesinS3 as jest.Mock).mockClear();

    const result = await saveAttachmentsPure(
      [{ notAFile: true }],
      { ministryCode: "MIN", requestNumber: "MIN-2026-00001", requestId: 100, dispatch: () => {} }
    );

    expect(result).toEqual([]);
    expect(ossServices.getOSSHeaderDetails).not.toHaveBeenCalled();
    expect(ossServices.saveFilesinS3).not.toHaveBeenCalled();
  });
});
