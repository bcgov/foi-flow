
 function namesort ( a, b )  {
    if ( a.firstname < b.lastname ){
      return -1;
    }
    if ( a.firstname > b.lastname ){
      return 1;
    }
    return 0;
  }

  const suggestionList = (teamlist) =>{
    teamlist.forEach(ful => {
        ful.name = ful.fullname;
        if(ful.fullname.indexOf(',')> 0)
        {
          let _name = ful.fullname.split(',')
          ful.firstname = _name[1].trim().toLowerCase()
          ful.lastname = _name[0].trim().toLowerCase()
        }        
      })

      return teamlist;
  }


  export {namesort, suggestionList}