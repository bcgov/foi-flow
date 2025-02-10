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

    const exportToHTMLString = async () => {
        try {
            if (container) {
                // const sfdtBlob = await container.current.documentEditor.saveAsBlob('Sfdt');
                // const reader = new FileReader();
                // reader.onload = async (event) => {
                //     const sfdtString = event.target?.result as string;
                //     container.current!.documentEditor.open(sfdtString); // Re-open SFDT
                //     const htmlBlob = await container.current!.documentEditor.saveAsBlob('Html');
                //     const htmlString = await htmlBlob.text();
                //     console.log(htmlString); // Output HTML string
                //     callBack(htmlString)
                // };
                // reader.readAsText(sfdtBlob);
                
                // const htmlBlob = await container.documentEditor.saveAsBlob('Html');
                const htmlBlob = await container.documentEditor.saveAsBlob('Docx');
                const htmlString = await htmlBlob.text();
                // console.log(htmlString); // Output HTML string
                preview(htmlString)
            }
        } catch (err) {
            console.error(err);
        }
    };

    const getSfdtString = () => {
        if (container) {
            // Use the document editor container reference here
            let sfdt: any = { content: container.documentEditor.serialize() };

            console.log("sfdt: ", sfdt);
            saveSfdtDraft(sfdt);
        }
    };

    React.useEffect(() => {
        if (saveSfdtDraftTrigger) {
            getSfdtString();
            setSaveSfdtDraftTrigger(false);
        }
    }, [saveSfdtDraftTrigger]);

    React.useEffect(() => {
        if (previewTrigger) {
            getSfdtString();
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
        />
    );
}