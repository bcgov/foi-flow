from .db import db, ma
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import insert

class FOIAssignee(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIAssignees' 
    # Defining the columns
    foiassigneeid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    firstname = db.Column(db.String(100), unique=False, nullable=False)
    middlename = db.Column(db.String(100), unique=False, nullable=True)
    lastname = db.Column(db.String(100), unique=False, nullable=False)
    isactive = db.Column(db.Boolean, unique=False, nullable=False, default=True)

    @classmethod
    def saveassignee(cls, username, firstname, middlename, lastname)->DefaultMethodResult:

        insertstmt = insert(FOIAssignee).values(
                                            username=username,
                                            firstname=firstname,
                                            middlename=middlename,
                                            lastname=lastname
                                        )
        updatestmt = insertstmt.on_conflict_do_update(index_elements=[FOIAssignee.username], set_={"firstname": firstname,"middlename":middlename,"lastname":lastname})
        db.session.execute(updatestmt)               
        db.session.commit()   
        return DefaultMethodResult(True, 'Assignee added', username)

    @classmethod
    def getassignees(cls):
        assignee_schema = FOIAssigneeSchema(many=True)
        query = db.session.query(FOIAssignee).filter_by(isactive=True).all()
        return assignee_schema.dump(query)

    @classmethod
    def getassignee(cls,username):
        assignee_schema = FOIAssigneeSchema()
        query = db.session.query(FOIAssignee).filter_by(username=username).first()
        return assignee_schema.dump(query)

class FOIAssigneeSchema(ma.Schema):
    class Meta:
        fields = ('foiassigneeid','username','firstname','middlename','lastname','isactive')
