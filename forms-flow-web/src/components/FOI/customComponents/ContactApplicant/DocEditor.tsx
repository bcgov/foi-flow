import './DocEditor.scss'
import * as React from 'react';
import { DocumentEditorContainerComponent, Toolbar, CustomToolbarItemModel, ToolbarItem } from "@syncfusion/ej2-react-documenteditor";
DocumentEditorContainerComponent.Inject(Toolbar);

export const DocEditor = ({
    curTemplate
}: any) => {
    const [container, setContainer] = React.useState<DocumentEditorContainerComponent | null>(null);
    // let container: DocumentEditorContainerComponent;

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

    React.useEffect(() => {
        if (container && curTemplate) {
            container.documentEditor.open(curTemplate);
        }
    }, [curTemplate]);

    return (
        <DocumentEditorContainerComponent
            id="container"
            // ref={(scope) => { container = scope; }}
            ref={setContainer}
            serviceUrl="http://localhost:62870/api/documenteditor/"
            height={'590px'}
            toolbarItems={items}
            enableToolbar={true}
        />
    );
}