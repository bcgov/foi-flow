import './DocEditor.scss'
import * as React from 'react';
import { DocumentEditorContainerComponent, Toolbar, CustomToolbarItemModel, ToolbarItem, SpellChecker } from "@syncfusion/ej2-react-documenteditor";
import { ClickEventArgs } from '@syncfusion/ej2-navigations';
import { FOI_TEMPLATE_API_URL } from "../../../../apiManager/endpoints/config"
import { SF_KEY } from "../../../../constants/constants";
import { registerLicense } from '@syncfusion/ej2-base';

registerLicense(SF_KEY);
DocumentEditorContainerComponent.Inject(Toolbar, SpellChecker);

export const DocEditor = ({
    curTemplate,
    saveSfdtDraft,
    saveSfdtDraftTrigger,
    setSaveSfdtDraftTrigger,
    preview,
    previewTrigger,
    setPreviewTrigger,
    addAttachment,
    savepdf,
    editDraftTrigger,
    setEditDraftTrigger,
    editSfdtDraft
}: any) => {
    const [container, setContainer] = React.useState<DocumentEditorContainerComponent | null>(null);
    // let container: DocumentEditorContainerComponent;
    // console.log("FormatType: ", FormatType);

    const onToolbarClick = (args: ClickEventArgs): void => {
        switch (args.item.id) {
            case "savepdf":
                savepdf(getSfdtString());
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
    let attachmentBtn: CustomToolbarItemModel = {
        prefixIcon: "e-icons e-large e-custom-attachment",
        tooltipText: "Add attachments",
        text: "Attachment",
        id: "attachments"
    };

    let items: (CustomToolbarItemModel | ToolbarItem)[] = [
        savePdfBtn,
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

    function onCreated(): void  {
        //initialze enable spell checker
        if(container) {
            container.documentEditor.spellChecker.languageID = 1033; // LCID for "en-US"
            container.documentEditor.spellChecker.removeUnderline = false;
            container.documentEditor.spellChecker.allowSpellCheckAndSuggestion = true;
            container.documentEditor.spellChecker.enableOptimizedSpellCheck = true;
            //load template/draft
            if (curTemplate) {
                container.documentEditor.open(curTemplate);
            }
        }
    };

    React.useEffect(() => {
        // load template
        if (container && curTemplate) {
            container.documentEditor.open(curTemplate);
        }
    }, [curTemplate]);

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

    return (
        <DocumentEditorContainerComponent
            id="container"
            // ref={(scope) => { container = scope; }}
            ref={setContainer}
            serviceUrl={FOI_TEMPLATE_API_URL+"/api/documenteditor/"}
            // serviceUrl={"http://localhost:62870/api/documenteditor/"}
            height={'590px'}
            toolbarItems={items}
            enableToolbar={true}
            toolbarClick={onToolbarClick.bind(this)}
            enableSpellCheck={true}
            created={onCreated}
            documentEditorSettings={fontFamilies}
        />
    );
}