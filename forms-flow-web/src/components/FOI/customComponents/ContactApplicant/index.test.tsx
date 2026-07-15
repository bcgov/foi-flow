import React from "react";
import { render, screen } from "@testing-library/react";
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
  it("mounts with empty files list", () => {
    const store = mockStore(baseState);
    render(
      <Provider store={store}>
        <ContactApplicant {...baseProps()} />
      </Provider>
    );
    // No attachment chips should be present on initial render
    expect(screen.queryByTestId("attachment-chip")).toBeNull();
  });

  it("clears files when requestId changes (defensive reset)", () => {
    const store = mockStore(baseState);
    const { rerender } = render(
      <Provider store={store}>
        <ContactApplicant {...baseProps({ requestId: 100 })} />
      </Provider>
    );
    rerender(
      <Provider store={store}>
        <ContactApplicant {...baseProps({ requestId: 200 })} />
      </Provider>
    );
    expect(screen.queryByTestId("attachment-chip")).toBeNull();
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
});
