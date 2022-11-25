import React from 'react';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';


const SubmissionError = React.memo((props) => {
    const { modalOpen=false, onConfirm, errors } = props;
    let message = "";
    if (errors?.includes("Token Expired")) {
        message = "Something went wrong. Please click Refresh button to reload the page."
    }
    console.log(`message === ${message}`);
    return (
      <>
          <Modal show={modalOpen}>
              <Modal.Header>
                 <Modal.Title>Error</Modal.Title>
              </Modal.Header>
              <Modal.Body>{message}</Modal.Body>
              <Modal.Footer>
              <Button type="button" className="btn btn-default" onClick={onConfirm}>Refresh</Button>
              </Modal.Footer>
          </Modal>
        </>
    )
})

export default SubmissionError;
