import 'react-quill/dist/quill.snow.css';
const EmailExport = ({handleExport, content, handleExportAsPdfButton}) => {

  return (
    <>
    <button 
        className="btn-bottom btn-save" 
        onClick={() => {
          handleExportAsPdfButton();
      }}
        >
          Export as PDF
        </button>
    </>
  )

}

export default EmailExport