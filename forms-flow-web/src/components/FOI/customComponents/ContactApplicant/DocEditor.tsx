import './DocEditor.scss'
import * as React from 'react';
import { useSelector } from "react-redux";
import { DocumentEditorContainerComponent, Toolbar, CustomToolbarItemModel, ToolbarItem, SpellChecker } from "@syncfusion/ej2-react-documenteditor";
import { ClickEventArgs } from '@syncfusion/ej2-navigations';
import { FOI_TEMPLATE_API_URL } from "../../../../apiManager/endpoints/config"
import { SF_KEY } from "../../../../constants/constants";
import { registerLicense } from '@syncfusion/ej2-base';
import { HeaderLogoBase64 } from '../../../../assets/FOI/images/HeaderLogoBase64';

registerLicense(SF_KEY);
DocumentEditorContainerComponent.Inject(Toolbar, SpellChecker);

export const DocEditor = ({
    curTemplate,
    selectedTemplate,
    saveSfdtDraft,
    saveSfdtDraftTrigger,
    setSaveSfdtDraftTrigger,
    preview,
    previewTrigger,
    setPreviewTrigger,
    addAttachment,
    savepdf,
    emailSubject,
    attachpdf,
    attachPdfTrigger,
    setAttachPdfTrigger,
    exportAsPdf,
    exportPdfTrigger,
    setExportPdfTrigger,
    editDraftTrigger,
    setEditDraftTrigger,
    editSfdtDraft,
    enableAutoFocus,
    selectedEmails,
    selectedCCEmails
}: any) => {
    const EMAILLISTTEMPLATEVARIABLE = '[SELECTEDEMAILSLIST-NONESELECTED]'
    // These are the phrases from the templates the precede email and file, to ensure that emails and numbers in other locations aren't replaced
    const EMAILPREFIXES = [`Sent via email:  `, `Sent via email: `, `Sent by email to: `, `Sent by email to:  `, `Applicant email address:  `]
    const FILEPREFIXES = ['File:  292-40/', 'File:  292-30/', 'File:  292-30\\', 'File:  292- 30/', 'File:  292- 40/']
    const SKIPHEADERFOOTERINSERT = ['A - Applicant Cover Email', 'Fee Estimate', 'Outstanding Fee']
    const [container, setContainer] = React.useState<DocumentEditorContainerComponent | null>(null);
    const userDetail: any|null = useSelector((state: any)=> state.user.userDetail);
    let requestDetails: any|null = useSelector((state: any) => state.foiRequests.foiRequestDetail);
    const requestNumber = requestDetails?.axisRequestId ? requestDetails.axisRequestId : requestDetails?.idNumber;

    // let container: DocumentEditorContainerComponent;
    // console.log("FormatType: ", FormatType);

    const onToolbarClick = (args: ClickEventArgs): void => {
        switch (args.item.id) {
            case "savepdf":
                savepdf(getSfdtString());
                break;
            case "savedocx":
                container?.documentEditor.save(emailSubject, 'Docx')
                break;
            case "attachpdf":
                attachpdf(getSfdtString());
                break;
            case "attachments":
                addAttachment();
                break;
            default:
                break;
        }
    };
    const onWrapText = (text: string): string=> {
      let content: string = '';
        const index : number = text.lastIndexOf(' ');
    
        if (index !== -1) {
            content = text.slice(0, index) + "<div class='e-de-text-wrap'>" + text.slice(index + 1) + "</div>";
        } else {
            content = text;
        }
    
        return content;
    }

    //Custom toolbar item.
    let savePdfBtn: CustomToolbarItemModel = {
        prefixIcon: "e-icons e-large e-custom-export-pdf",
        tooltipText: "Save as a PDF File",
        text: onWrapText("Save as PDF"),
        id: "savepdf"
    };
    let saveDocxBtn: CustomToolbarItemModel = {
        prefixIcon: "e-icons e-large e-custom-export-docx",
        tooltipText: "Save as a docx file",
        text: onWrapText("Save as docx"),
        id: "savedocx"
    };
    // let attachPdfBtn: CustomToolbarItemModel = {
    //     prefixIcon: "e-icons e-large e-custom-export-pdf",
    //     tooltipText: "Attach current content as a PDF File",
    //     text: onWrapText("Attach as PDF"),
    //     id: "attachpdf"
    // };
    let attachmentBtn: CustomToolbarItemModel = {
        prefixIcon: "e-icons e-large e-custom-attachment",
        tooltipText: "Add attachments",
        text: "Attachment",
        id: "attachments"
    };

    let items: (CustomToolbarItemModel | ToolbarItem)[] = [
        savePdfBtn,
        saveDocxBtn,
        // attachPdfBtn,
        "Separator",
        "Undo",
        "Redo",
        "Separator",
        attachmentBtn,
        "Image",
        "Table",
        "Hyperlink",
        // "Bookmark",
        // "TableOfContents",
        "Separator",
        // "Header",
        // "Footer",
        // "PageSetup",
        // "PageNumber",
        "Break",
        // "InsertFootnote",
        // "InsertEndnote",
        "Separator",
        "Find",
        // "Separator",
        // "Comments",
        // "TrackChanges",
        // "Separator",
        // "LocalClipboard",
        // "RestrictEditing",
        // "Separator",
        // "FormFields",
        // "UpdateFields",
        // "ContentControl"
    ];

    // Add required font families to list it in font drop down
    let fontFamilies = {
        fontFamilies: ['Algerian', 'Arial', 'Calibri', 'Cambria', 'BC Sans'],
    };

    const insertHeader = () => {
        if (container && !SKIPHEADERFOOTERINSERT.includes(selectedTemplate?.label)) {
            container.documentEditor.selection.sectionFormat.differentFirstPage = true;
            container.documentEditor.selection.goToPage(1);
            container.documentEditor.selection.goToHeader();
            container.documentEditor.selection.sectionFormat.headerDistance = 0;
            container.documentEditor.selection.paragraphFormat.textAlignment = 'Center';
            container.documentEditor.editor.insertImage(HeaderLogoBase64, 144, 135);
            container.documentEditor.selection.closeHeaderFooter();
        }
    }

    const insertFooter = () => {
        if (container && !SKIPHEADERFOOTERINSERT.includes(selectedTemplate?.label)) {
            container.documentEditor.selection.sectionFormat.differentFirstPage = true;
            container.documentEditor.selection.goToPage(1);
            container.documentEditor.selection.goToFooter();
            container.documentEditor.selection.sectionFormat.footerDistance = 10;
            container.documentEditor.selection.characterFormat.fontSize = 7;
            container.documentEditor.selection.characterFormat.fontFamily = 'BC Sans';
            container.documentEditor.editor.insertTable(1,4)
            container.documentEditor.editor.applyBorders({type: 'NoBorder'});
            container.documentEditor.editor.applyBorders({type: 'TopBorder'});
            container.documentEditor.selection.characterFormat.bold = true;
            container.documentEditor.editor.insertText("Ministry of Citizens' Services");
            container.documentEditor.selection.characterFormat.bold = false;
            container.documentEditor.selection.moveNextPosition();
            container.documentEditor.editor.applyBorders({type: 'NoBorder'});
            container.documentEditor.editor.applyBorders({type: 'TopBorder'});
            container.documentEditor.editor.insertText("Information Access Operations / Children and Family Access Services");
            container.documentEditor.selection.moveNextPosition();
            container.documentEditor.editor.applyBorders({type: 'NoBorder'});
            container.documentEditor.editor.applyBorders({type: 'TopBorder'});
            container.documentEditor.editor.insertText("Mailing Address:\nPO Box 9569 Stn Prov Govt\nVictoria BC V8W 9K1");
            container.documentEditor.selection.moveNextPosition();
            container.documentEditor.editor.applyBorders({type: 'NoBorder'});
            container.documentEditor.editor.applyBorders({type: 'TopBorder'});
            container.documentEditor.editor.insertText("Website: \n");
            container.documentEditor.editor.insertHyperlink('https://www.gov.bc.ca/freedomofinformation', 'www.gov.bc.ca/freedomofinformation');
            container.documentEditor.editor.insertText("\n");
            container.documentEditor.selection.characterFormat.fontSize = 7;
            container.documentEditor.selection.characterFormat.fontFamily = 'BC Sans';
            container.documentEditor.editor.insertText("Telephone: 250 387-1321\nFax: 250 387-9843");
            container.documentEditor.selection.closeHeaderFooter();
        }
    }

    const insertPageNumbers = () => {
        if (container) {
            container.documentEditor.selection.goToPage(2);
            container.documentEditor.selection.goToHeader();
            container.documentEditor.selection.paragraphFormat.textAlignment = 'Center';
            container.documentEditor.selection.characterFormat.fontFamily = 'BC Sans';
            container.documentEditor.editor.insertPageNumber();
            container.documentEditor.selection.closeHeaderFooter();
        }
    }

    function onCreated(): void  {
        //initialze enable spell checker
        if(container) {
            container.documentEditor.spellChecker.languageID = 4105; // 1033 is LCID for "en-US", 4105 is LCID for "en-CA"
            container.documentEditor.spellChecker.removeUnderline = false;
            container.documentEditor.spellChecker.allowSpellCheckAndSuggestion = true;
            container.documentEditor.spellChecker.enableOptimizedSpellCheck = true;
            container.documentEditor.currentUser = userDetail.preferred_username;
            container.documentEditor.enableTrackChanges = false;
            container.documentEditor.setDefaultCharacterFormat({ fontFamily: 'BC Sans', fontSize: 10 });
            container.documentEditor.characterFormat.fontFamily = 'BC Sans';
            //load template/draft
            if (curTemplate) {
                container.documentEditor.open(curTemplate);
            }
        }
    };

    const replaceEmailList = () => {
        if (container && curTemplate) {
            let newEmailList = ''
            selectedEmails?.forEach((email: any, index: number) => {
                newEmailList = newEmailList + email
                if (index < selectedEmails?.length - 1 || selectedCCEmails?.length > 0) newEmailList = newEmailList + ', '
            })
            selectedCCEmails?.forEach((email: any, index: number) => {
                newEmailList = newEmailList + email
                if (index < selectedCCEmails?.length - 1) newEmailList = newEmailList + ', '
            })
            if (newEmailList === '') newEmailList = EMAILLISTTEMPLATEVARIABLE
            for (let prefix of EMAILPREFIXES) {
                container.documentEditor.search.findAll(prefix + EMAILLISTTEMPLATEVARIABLE)
                if (container.documentEditor.search.searchResults.length > 0) {
                    container.documentEditor.search.searchResults.replaceAll(prefix + newEmailList)
                    setEmailListString(newEmailList)
                    break;
                } else if (newEmailList != emailListString && emailListString.length > 3) {
                    container.documentEditor.search.findAll(emailListString)
                    container.documentEditor.search.searchResults.replaceAll(newEmailList)
                    setEmailListString(newEmailList)
                    break;
                }
            }
        }
    }

    const replaceFileNumber = () => {
        if (container && curTemplate) {
            let selectedNumber = '';
            if (requestDetails?.requestType == 'general') selectedNumber = '30';
            if (requestDetails?.requestType == 'personal') selectedNumber = '40';
            // if (externalConsult) numberToFill = '45';
            for (let file of FILEPREFIXES) {
                container.documentEditor.search.findAll(file + requestNumber)
                if (container.documentEditor.search.searchResults.length > 0) {
                    const replacedFile = file.replace(/-\s?\d{2}/g, `-${selectedNumber}`);
                    container.documentEditor.search.searchResults.replaceAll(replacedFile + requestNumber)
                    break;
                }
            }
        }
    }

    React.useEffect(() => {
        // load template
        if (container && curTemplate) {
            container.documentEditor.open(curTemplate);
            insertHeader();
            insertFooter();
            insertPageNumbers();
        }
    }, [curTemplate]);

    // This is used to dynamically replace the list of selectec emails in the template
    const [emailListString, setEmailListString] = React.useState<string>('');
    React.useEffect(() => {
        if (container && curTemplate) {
            replaceEmailList();
            replaceFileNumber();
        }
    }, [selectedEmails, selectedCCEmails, curTemplate]);

    const getSfdtString = () => {
        if (container) {
            // Use the document editor container reference here
            return container.documentEditor.serialize();
        } else {
            return '';
        }
    };

    React.useEffect(() => {
        if (saveSfdtDraftTrigger) {
            saveSfdtDraft( getSfdtString() );
            setSaveSfdtDraftTrigger(false);
        }
    }, [saveSfdtDraftTrigger]);

    React.useEffect(() => {
        if (editDraftTrigger) {
            editSfdtDraft( getSfdtString() );
            setEditDraftTrigger(false);
        }
    }, [editDraftTrigger]);

    React.useEffect(() => {
        if (previewTrigger) {
            preview( getSfdtString() );
            setPreviewTrigger(false);
        }
    }, [previewTrigger]);

    React.useEffect(() => {
        if (attachPdfTrigger) {
            attachpdf(getSfdtString());
            setAttachPdfTrigger(false);
        }
    }, [attachPdfTrigger]);

    React.useEffect(() => {
        if (exportPdfTrigger) {
            exportAsPdf(getSfdtString());
            setExportPdfTrigger(false);
        }
    }, [exportPdfTrigger]);

    return (
        <DocumentEditorContainerComponent
            id="container"
            // ref={(scope) => { container = scope; }}
            ref={setContainer}
            serviceUrl={FOI_TEMPLATE_API_URL+"/api/documenteditor/"}
            height={'590px'}
            toolbarItems={items}
            enableToolbar={true}
            toolbarClick={onToolbarClick.bind(this)}
            enableSpellCheck={true}
            created={onCreated}
            enableAutoFocus={enableAutoFocus}
            documentEditorSettings={fontFamilies}
        />
    );
}