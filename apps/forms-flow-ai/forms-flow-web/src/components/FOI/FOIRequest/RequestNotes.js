import React, { useEffect, useState }  from 'react';
import './requestnotes.scss';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { makeStyles } from '@material-ui/core/styles';
import {CommentSection} from '../customComponents/Comments'

const useStyles = makeStyles((theme) => ({
    root: {
      width: '100%',
      marginTop:'20px'
    },
    heading: {
      fontSize: theme.typography.pxToRem(15),
      fontWeight: theme.typography.fontWeightRegular,
    },
  }));
const RequestNotes = React.memo((props) => {
    const classes = useStyles();
    const data = [
      {
        "userId": "01a",
        "comId": "012",
        "fullName": "Abin Antony",
        "avatarUrl": "https://ui-avatars.com/api/name=Riya&background=random" ,
        "text": "Hey, Loved your blog! ",
        "replies": [
          {
            "userId": "02a",
            "comId": "013",
      
            "fullName": "Divya Viswanath",
            "avatarUrl": "https://ui-avatars.com/api/name=Adam&background=random" ,
            "text": "Thanks! It took me 1 month to finish this project but I am glad it helped out someone!🥰"
          },
          {
            "userId": "01a",
            "comId": "014",
      
            "fullName": "Abin Antony",
            "avatarUrl": "https://ui-avatars.com/api/name=Riya&background=random",
            "text": "thanks!😊"
          }
        ]
      },
      {
        "userId": "02a",
        "comId": "07",
        "fullName": "Divya Viswanath",
        "text": "Follow my page for more such interesting blogs!😇",
        "avatarUrl": "https://ui-avatars.com/api/name=Adam&background=random"
      },
      {
        "userId": "02a",
        "comId": "015",
        "fullName": "Robert Jae",
        "avatarUrl": "https://ui-avatars.com/api/name=Robert&background=random",
        "text": "Woah pretty helpful! how did you solve for x?",
        "replies": [
          {
            "userId": "01b",
            "comId": "016",
      
            "fullName": "Divya Viswanath",
            "text": "Thanks! refer to this link -> acs.com",
            "avatarUrl": "https://ui-avatars.com/api/name=Adam&background=random"
          }
        ]
      },
      {
        "userId": "02b",
        "comId": "017",
        "fullName": "Sumathi",
        "text": "I have a doubt about the 4th point🤔",
        "avatarUrl": "https://ui-avatars.com/api/name=Lily&background=random"
      }
    ]
    const [comment, setComment] = useState(data)
    const userId = "01a"
    const avatarUrl = "https://ui-avatars.com/api/name=Riya&background=random"
    const name = "xyz"
    const signinUrl = "/signin"
    const signupUrl = "/signup"
    let count = 0

  comment.map(i => { count += 1; i.replies && i.replies.map(i => count += 1) })
     return (
    <div className={classes.root}>
      {/* <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
          id="panel1a-header"
        >
          <Typography className={classes.heading}>REQUEST NOTES</Typography>
        </AccordionSummary>
        <AccordionDetails>
        
        </AccordionDetails>
      </Accordion> */}
      <CommentSection currentUser={userId && { userId: userId, avatarUrl: avatarUrl, name: name }} commentsArray={comment}
        setComment={setComment} signinUrl={signinUrl} signupUrl={signupUrl} />
    </div>
    );
  });

export default RequestNotes;