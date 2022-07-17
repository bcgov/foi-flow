import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';


const RequestNotes = React.memo(() => {
    const notes = [
      {
        username: "Username1",
        time: "2021 MAY 8 | 08:30 AM",
        content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse malesuada lacus ex, sit amet blandit leo lobortis eget."
      },
      {
        username: "Username2",
        time: "2021 MAY 17 | 03:30 PM",
        content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse malesuada lacus ex, sit amet blandit leo lobortis eget."
      },
    ];

    let notesArray = [];
    for(let i=0; i<notes.length; i++) {
      notesArray.push(<Note key={i} note={notes[i]} />);
    }

    return (
             
        <Card className="foi-details-card">            
            <label className="foi-details-label">REQUEST NOTES</label>
            <CardContent>          
                {notesArray}

                <input type="note" className="form-control" id="note" placeholder="Add a new note" name="note" />
            </CardContent>
        </Card>       
    );
})

const Note = React.memo((note) => {
  const _note = note.note;

  return (
    <div className="container-fluid">
      <div className="row foi-details-row">
        <div className="row foi-details-row">
          <div className="col-lg-12 foi-details-col">
            <div className="col-lg-5" style={{display:'inline-block'}}>
              <div style={{display:'inline',paddingRight:15+'px'}}>                      
                <b>{_note.username}</b>
              </div>
              <div style={{display:'inline'}}>                      
                {_note.time}
              </div>
            </div>
            <div className="col-lg-7" style={{display:'inline-block'}}>
              <div className="col-lg-1" style={{marginLeft:'auto'}}>
                ...
              </div>                      
            </div>
          </div>
        </div>
        <div className="row foi-details-row" style={{paddingTop:15+'px',paddingBottom:15+'px'}}>
          <div className="col-lg-12 foi-details-col">                      
            {_note.content}
          </div>
        </div>
        <div className="row foi-details-row" style={{paddingBottom:15+'px'}}>
          <div className="col-lg-12 foi-details-col">                      
            <hr className="solid" />
          </div>
        </div>
      </div>
    </div>
  );
})

export default RequestNotes;