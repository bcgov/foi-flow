import './DocEditor.scss'
import * as React from 'react';
import { DocumentEditorContainerComponent, Toolbar, CustomToolbarItemModel, ToolbarItem, SpellChecker } from "@syncfusion/ej2-react-documenteditor";
import {DOC_EDITOR_API_URL} from "../../../../apiManager/endpoints/config"
DocumentEditorContainerComponent.Inject(Toolbar, SpellChecker);

export const DocEditor = ({
    curTemplate,
    saveSfdtDraft,
    saveSfdtDraftTrigger,
    setSaveSfdtDraftTrigger,
    preview,
    previewTrigger,
    setPreviewTrigger,
}: any) => {
    const [container, setContainer] = React.useState<DocumentEditorContainerComponent | null>(null);
    // let container: DocumentEditorContainerComponent;
    // console.log("FormatType: ", FormatType);

    let items: (CustomToolbarItemModel | ToolbarItem)[] = [
        "Undo",
        "Redo",
        "Separator",
        "Image",
        "Table",
        "Hyperlink",
        // "Bookmark",
        // "TableOfContents",
        "Separator",
        "Header",
        "Footer",
        "PageSetup",
        "PageNumber",
        "Break",
        // "InsertFootnote",
        // "InsertEndnote",
        "Separator",
        "Find",
        // "Separator",
        // "Comments",
        // "TrackChanges",
        "Separator",
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
        if(container) {
            container.documentEditor.spellChecker.languageID = 1033; // LCID for "en-US"
        }
    };

    React.useEffect(() => {
        componentDidMount()
    }, []);
    function componentDidMount(): void {
        if(container) {
            container.documentEditor.spellChecker.languageID = 1033 //LCID of "en-us";
            container.documentEditor.spellChecker.removeUnderline = false;
            container.documentEditor.spellChecker.allowSpellCheckAndSuggestion = true;
            container.documentEditor.spellChecker.enableOptimizedSpellCheck = true;
        }
    }

    React.useEffect(() => {
        if (container && curTemplate) {
            container.documentEditor.open(curTemplate);
        }
    }, [curTemplate]);

    const getSfdtString = () => {
        if (container) {
            // Use the document editor container reference here
            return { content: container.documentEditor.serialize() };
        } else {
            return { content: '' };
        }
    };

    React.useEffect(() => {
        if (saveSfdtDraftTrigger) {
            saveSfdtDraft( getSfdtString() );
            setSaveSfdtDraftTrigger(false);
        }
    }, [saveSfdtDraftTrigger]);

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
            // serviceUrl={DOC_EDITOR_API_URL+"/api/documenteditor/"}
            serviceUrl={"http://localhost:62870/api/documenteditor/"}
            height={'590px'}
            toolbarItems={items}
            enableToolbar={true}
            enableSpellCheck={true}
            created={onCreated}
            documentEditorSettings={fontFamilies}
        />
    );
}