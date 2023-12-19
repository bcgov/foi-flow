from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship, backref, aliased
from .default_method_result import DefaultMethodResult
from .FOIRequestApplicantMappings import FOIRequestApplicantMapping
from .ApplicantCategories import ApplicantCategory
from .FOIRequests import FOIRequest
from .FOIRequestContactInformation import FOIRequestContactInformation
from .FOIRequestPersonalAttributes import FOIRequestPersonalAttribute
from sqlalchemy import and_, or_, func, case

class FOIRequestApplicant(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestApplicants' 
    # Defining the columns
    foirequestapplicantid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    

    firstname = db.Column(db.String(50), unique=False, nullable=True)
    middlename = db.Column(db.String(50), unique=False, nullable=True)
    lastname = db.Column(db.String(50), unique=False, nullable=True)

    alsoknownas = db.Column(db.String(50), unique=False, nullable=True)
    dob = db.Column(db.DateTime, unique=False, nullable=True)
    businessname = db.Column(db.String(255), unique=False, nullable=True)
                
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    version = db.Column(db.Integer, unique=False, nullable=True)

    @classmethod
    def saveapplicant(cls,firstname, lastname, middlename, businessname, alsoknownas, dob, userid):
        dbquery = db.session.query(FOIRequestApplicant)
        dbquery = dbquery.filter_by(firstname=firstname)
        applicant = dbquery.filter_by(lastname=lastname)
        if (applicant.count() > 0):
            _applicant = {
                FOIRequestApplicant.updatedby: userid, 
                FOIRequestApplicant.updated_at: datetime.now(),
                FOIRequestApplicant.middlename: middlename,
                FOIRequestApplicant.businessname: businessname,
                FOIRequestApplicant.alsoknownas: alsoknownas
            }
            if dob is not None and dob != "":
                _applicant[FOIRequestApplicant.dob] = dob
            else:
                _applicant[FOIRequestApplicant.dob] = None
            applicant.update(_applicant)
            return DefaultMethodResult(True,'Applicant updated',applicant.first().foirequestapplicantid)
        else:
            applicant = FOIRequestApplicant()
            applicant.createdby = userid
            applicant.firstname = firstname
            applicant.lastname = lastname
            applicant.middlename = middlename
            applicant.businessname = businessname
            applicant.alsoknownas = alsoknownas
            if dob is not None and dob != "":
                applicant.dob = dob
            else:
                applicant.dob = None
            db.session.add(applicant)
            db.session.commit()               
            return DefaultMethodResult(True,'Applicant added',applicant.foirequestapplicantid)

    # Search applicant by email
    @classmethod
    def getapplicantbyemail(cls, email):
        from .FOIMinistryRequests import FOIMinistryRequest

        #for queue/dashboard
        _session = db.session

        #aliase for getting contact info
        contactemail = aliased(FOIRequestContactInformation)
        contactaddress = aliased(FOIRequestContactInformation)
        contactaddress2 = aliased(FOIRequestContactInformation)
        contacthomephone = aliased(FOIRequestContactInformation)
        contactworkphone = aliased(FOIRequestContactInformation)
        contactworkphone2 = aliased(FOIRequestContactInformation)
        contactmobilephone = aliased(FOIRequestContactInformation)
        contactother = aliased(FOIRequestContactInformation)
        
        city = aliased(FOIRequestContactInformation)
        province = aliased(FOIRequestContactInformation)
        postal = aliased(FOIRequestContactInformation)
        country = aliased(FOIRequestContactInformation)

        #aliase for getting personal attributes
        personalemployeenumber = aliased(FOIRequestPersonalAttribute)
        personalcorrectionnumber = aliased(FOIRequestPersonalAttribute)
        personalhealthnumber = aliased(FOIRequestPersonalAttribute)

        #max foirequest version
        subquery_foirequest_maxversion = _session.query(FOIRequest.foirequestid, func.max(FOIRequest.version).label('max_version')).group_by(FOIRequest.foirequestid).subquery()
        joincondition = [
            subquery_foirequest_maxversion.c.foirequestid == FOIRequest.foirequestid,
            subquery_foirequest_maxversion.c.max_version == FOIRequest.version,
        ]

        #generate query
        selectedcolumns = [
            FOIRequestApplicant.foirequestapplicantid.label('foirequestapplicantid'),
            FOIRequestApplicant.firstname.label('firstname'),
            FOIRequestApplicant.middlename.label('middlename'),
            FOIRequestApplicant.lastname.label('lastname'),
            FOIRequestApplicant.alsoknownas.label('alsoknownas'),
            func.to_char(FOIRequestApplicant.dob, 'YYYY-MM-DD').label('dob'),
            FOIRequestApplicant.businessname.label('businessname'),
            FOIRequestApplicant.version.label('applicantversion'),
            FOIRequest.foirequestid.label('foirequestid'),
            FOIRequest.version.label('foirequestversion'),
            FOIRequest.requesttype.label('requesttype'),
            ApplicantCategory.name.label('applicantcategory'),
            contactemail.contactinformation.label('email'),
            contactaddress.contactinformation.label('address'),
            contactaddress2.contactinformation.label('address2'),
            contacthomephone.contactinformation.label('homephone'),
            contactworkphone.contactinformation.label('workphone'),
            contactworkphone2.contactinformation.label('workphone2'),
            contactmobilephone.contactinformation.label('mobilephone'),
            contactother.contactinformation.label('othercontactinfo'),
            city.contactinformation.label('city'),
            province.contactinformation.label('province'),
            postal.contactinformation.label('postal'),
            country.contactinformation.label('country'),
            personalemployeenumber.attributevalue.label('employeenumber'),
            personalcorrectionnumber.attributevalue.label('correctionnumber'),
            personalhealthnumber.attributevalue.label('phn')
        ]

        subquery_all = _session.query(
                                *selectedcolumns
                            ).join(
                                FOIRequestApplicantMapping,
                                and_(
                                    FOIRequestApplicantMapping.foirequest_id == FOIRequest.foirequestid,
                                    FOIRequestApplicantMapping.foirequestversion_id == FOIRequest.version,
                                    FOIRequestApplicantMapping.requestortypeid == 1),
                            ).join(
                                FOIRequestApplicant,
                                # FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid
                                and_(
                                    FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid,
                                    FOIRequestApplicant.version == FOIRequestApplicantMapping.foirequestapplicant_version
                                )
                            ).join(
                                ApplicantCategory,
                                ApplicantCategory.applicantcategoryid == FOIRequest.applicantcategoryid
                            ).join(
                                subquery_foirequest_maxversion,
                                and_(*joincondition)
                            ).join(
                                FOIMinistryRequest,
                                and_(
                                    FOIMinistryRequest.foirequest_id == FOIRequest.foirequestid,
                                    FOIMinistryRequest.isactive == True)
                            ).join(
                                contactemail,
                                and_(
                                    contactemail.foirequest_id == FOIRequest.foirequestid,
                                    contactemail.foirequestversion_id == FOIRequest.version,
                                    contactemail.contacttypeid == 1),
                            ).join(
                                contactaddress,
                                and_(
                                    contactaddress.foirequest_id == FOIRequest.foirequestid,
                                    contactaddress.foirequestversion_id == FOIRequest.version,
                                    contactaddress.contacttypeid == 2,
                                    contactaddress.contactinformation is not None,
                                    contactaddress.dataformat == 'address'),
                                isouter=True
                            ).join(
                                contactaddress2,
                                and_(
                                    contactaddress2.foirequest_id == FOIRequest.foirequestid,
                                    contactaddress2.foirequestversion_id == FOIRequest.version,
                                    contactaddress2.contacttypeid == 2,
                                    contactaddress2.contactinformation is not None,
                                    contactaddress2.dataformat == 'addressSecondary'),
                                isouter=True
                            ).join(
                                contacthomephone,
                                and_(
                                    contacthomephone.foirequest_id == FOIRequest.foirequestid,
                                    contacthomephone.foirequestversion_id == FOIRequest.version,
                                    contacthomephone.contacttypeid == 3,
                                    contacthomephone.contactinformation is not None),
                                isouter=True
                            ).join(
                                contactworkphone,
                                and_(
                                    contactworkphone.foirequest_id == FOIRequest.foirequestid,
                                    contactworkphone.foirequestversion_id == FOIRequest.version,
                                    contactworkphone.contacttypeid == 4,
                                    contactworkphone.contactinformation is not None),
                                isouter=True
                            ).join(
                                contactworkphone2,
                                and_(
                                    contactworkphone2.foirequest_id == FOIRequest.foirequestid,
                                    contactworkphone2.foirequestversion_id == FOIRequest.version,
                                    contactworkphone2.contacttypeid == 5,
                                    contactworkphone2.contactinformation is not None),
                                isouter=True
                            ).join(
                                contactmobilephone,
                                and_(
                                    contactmobilephone.foirequest_id == FOIRequest.foirequestid,
                                    contactmobilephone.foirequestversion_id == FOIRequest.version,
                                    contactmobilephone.contacttypeid == 6,
                                    contactmobilephone.contactinformation is not None),
                                isouter=True
                            ).join(
                                contactother,
                                and_(
                                    contactother.foirequest_id == FOIRequest.foirequestid,
                                    contactother.foirequestversion_id == FOIRequest.version,
                                    contactother.contacttypeid == 7,
                                    contactother.contactinformation is not None),
                                isouter=True
                            ).join(
                                city,
                                and_(
                                    city.foirequest_id == FOIRequest.foirequestid,
                                    city.foirequestversion_id == FOIRequest.version,
                                    city.contacttypeid == 2,
                                    city.contactinformation is not None,
                                    city.format == 'city'),
                                isouter=True
                            ).join(
                                province,
                                and_(
                                    province.foirequest_id == FOIRequest.foirequestid,
                                    province.foirequestversion_id == FOIRequest.version,
                                    province.contacttypeid == 2,
                                    province.contactinformation is not None,
                                    city.format == 'province'),
                                isouter=True
                            ).join(
                                country,
                                and_(
                                    country.foirequest_id == FOIRequest.foirequestid,
                                    country.foirequestversion_id == FOIRequest.version,
                                    country.contacttypeid == 2,
                                    country.contactinformation is not None,
                                    city.format == 'country'),
                                isouter=True
                            ).join(
                                postal,
                                and_(
                                    postal.foirequest_id == FOIRequest.foirequestid,
                                    postal.foirequestversion_id == FOIRequest.version,
                                    postal.contacttypeid == 2,
                                    postal.contactinformation is not None,
                                    city.format == 'postal'),
                                isouter=True
                            ).join(
                                personalemployeenumber,
                                and_(
                                    personalemployeenumber.foirequest_id == FOIRequest.foirequestid,
                                    personalemployeenumber.foirequestversion_id == FOIRequest.version,
                                    personalemployeenumber.personalattributeid == 1,
                                    personalemployeenumber.attributevalue is not None),
                                isouter=True
                            ).join(
                                personalcorrectionnumber,
                                and_(
                                    personalcorrectionnumber.foirequest_id == FOIRequest.foirequestid,
                                    personalcorrectionnumber.foirequestversion_id == FOIRequest.version,
                                    personalcorrectionnumber.personalattributeid == 2,
                                    personalcorrectionnumber.attributevalue is not None),
                                isouter=True
                            ).join(
                                personalhealthnumber,
                                and_(
                                    personalhealthnumber.foirequest_id == FOIRequest.foirequestid,
                                    personalhealthnumber.foirequestversion_id == FOIRequest.version,
                                    personalhealthnumber.personalattributeid == 3,
                                    personalhealthnumber.attributevalue is not None),
                                isouter=True
                            ).filter(
                                # FOIMinistryRequest.requeststatusid != 3,
                                FOIRequest.isactive == True,
                                contactemail.contactinformation == email
                            ).order_by(FOIRequest.foirequestid.desc()).subquery()

        query_aggregate = _session.query(
            subquery_all.c.foirequestapplicantid,
            func.array_agg(subquery_all.c.firstname).label('firstname'),
            func.array_agg(subquery_all.c.middlename).label('middlename'),
            func.array_agg(subquery_all.c.lastname).label('lastname'),
            func.array_agg(subquery_all.c.alsoknownas).label('alsoknownas'),
            func.array_agg(subquery_all.c.dob).label('dob'),
            func.array_agg(subquery_all.c.businessname).label('businessname'),
            subquery_all.c.applicantversion,
            func.array_agg(subquery_all.c.foirequestid).label('foirequestid'),
            func.array_agg(subquery_all.c.foirequestversion).label('foirequestversion'),
            func.array_agg(subquery_all.c.requesttype).label('requesttype'),
            func.array_agg(subquery_all.c.applicantcategory).label('applicantcategory'),
            func.array_agg(subquery_all.c.email).label('email'),
            func.array_agg(subquery_all.c.address).label('address'),
            func.array_agg(subquery_all.c.homephone).label('homephone'),
            func.array_agg(subquery_all.c.workphone).label('workphone'),
            func.array_agg(subquery_all.c.workphone2).label('workphone2'),
            func.array_agg(subquery_all.c.mobilephone).label('mobilephone'),
            func.array_agg(subquery_all.c.othercontactinfo).label('othercontactinfo'),
            func.array_agg(subquery_all.c.employeenumber).label('employeenumber'),
            func.array_agg(subquery_all.c.correctionnumber).label('correctionnumber'),
            func.array_agg(subquery_all.c.phn).label('phn')
        ).group_by(subquery_all.c.foirequestapplicantid, subquery_all.c.applicantversion)

        applicantprofile_schema = ApplicantProfileSchema(many=True)
        return applicantprofile_schema.dump(query_aggregate.all())


    # Search applicant by keywords
    @classmethod
    def searchapplicant(cls, keywords):
        from .FOIMinistryRequests import FOIMinistryRequest

        #for queue/dashboard
        _session = db.session

        #aliase for getting contact info
        contactemail = aliased(FOIRequestContactInformation)
        contactaddress = aliased(FOIRequestContactInformation)
        contacthomephone = aliased(FOIRequestContactInformation)
        contactworkphone = aliased(FOIRequestContactInformation)
        contactworkphone2 = aliased(FOIRequestContactInformation)
        contactmobilephone = aliased(FOIRequestContactInformation)
        contactother = aliased(FOIRequestContactInformation)

        #aliase for getting personal attributes
        personalemployeenumber = aliased(FOIRequestPersonalAttribute)
        personalcorrectionnumber = aliased(FOIRequestPersonalAttribute)
        personalhealthnumber = aliased(FOIRequestPersonalAttribute)

        #max foirequest version
        subquery_foirequest_maxversion = _session.query(FOIRequest.foirequestid, func.max(FOIRequest.version).label('max_version')).group_by(FOIRequest.foirequestid).subquery()
        joincondition = [
            subquery_foirequest_maxversion.c.foirequestid == FOIRequest.foirequestid,
            subquery_foirequest_maxversion.c.max_version == FOIRequest.version,
        ]
        
        #generate query
        selectedcolumns = [
            FOIRequestApplicant.foirequestapplicantid.label('foirequestapplicantid'),
            FOIRequestApplicant.firstname.label('firstname'),
            FOIRequestApplicant.middlename.label('middlename'),
            FOIRequestApplicant.lastname.label('lastname'),
            FOIRequestApplicant.alsoknownas.label('alsoknownas'),
            func.to_char(FOIRequestApplicant.dob, 'YYYY-MM-DD').label('dob'),
            FOIRequestApplicant.businessname.label('businessname'),
            FOIRequestApplicant.version.label('applicantversion'),
            FOIRequest.foirequestid.label('foirequestid'),
            FOIRequest.version.label('foirequestversion'),
            FOIRequest.requesttype.label('requesttype'),
            ApplicantCategory.name.label('applicantcategory'),
            contactemail.contactinformation.label('email'),
            contactaddress.contactinformation.label('address'),
            contacthomephone.contactinformation.label('homephone'),
            contactworkphone.contactinformation.label('workphone'),
            contactworkphone2.contactinformation.label('workphone2'),
            contactmobilephone.contactinformation.label('mobilephone'),
            contactother.contactinformation.label('othercontactinfo'),
            personalemployeenumber.attributevalue.label('employeenumber'),
            personalcorrectionnumber.attributevalue.label('correctionnumber'),
            personalhealthnumber.attributevalue.label('phn')
        ]

        subquery_all = _session.query(
                                *selectedcolumns
                            ).join(
                                FOIRequestApplicantMapping,
                                and_(
                                    FOIRequestApplicantMapping.foirequest_id == FOIRequest.foirequestid,
                                    FOIRequestApplicantMapping.foirequestversion_id == FOIRequest.version,
                                    FOIRequestApplicantMapping.requestortypeid == 1),
                            ).join(
                                FOIRequestApplicant,
                                # FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid
                                and_(
                                    FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid,
                                    FOIRequestApplicant.version == FOIRequestApplicantMapping.foirequestapplicant_version
                                )
                            ).join(
                                ApplicantCategory,
                                ApplicantCategory.applicantcategoryid == FOIRequest.applicantcategoryid
                            ).join(
                                subquery_foirequest_maxversion,
                                and_(*joincondition)
                            ).join(
                                FOIMinistryRequest,
                                and_(
                                    FOIMinistryRequest.foirequest_id == FOIRequest.foirequestid,
                                    FOIMinistryRequest.isactive == True)
                            ).join(
                                contactemail,
                                and_(
                                    contactemail.foirequest_id == FOIRequest.foirequestid,
                                    contactemail.foirequestversion_id == FOIRequest.version,
                                    contactemail.contacttypeid == 1),
                                isouter=True
                            ).join(
                                contactaddress,
                                and_(
                                    contactaddress.foirequest_id == FOIRequest.foirequestid,
                                    contactaddress.foirequestversion_id == FOIRequest.version,
                                    contactaddress.contacttypeid == 2,
                                    contactaddress.contactinformation is not None),
                                isouter=True
                            ).join(
                                contacthomephone,
                                and_(
                                    contacthomephone.foirequest_id == FOIRequest.foirequestid,
                                    contacthomephone.foirequestversion_id == FOIRequest.version,
                                    contacthomephone.contacttypeid == 3,
                                    contacthomephone.contactinformation is not None),
                                isouter=True
                            ).join(
                                contactworkphone,
                                and_(
                                    contactworkphone.foirequest_id == FOIRequest.foirequestid,
                                    contactworkphone.foirequestversion_id == FOIRequest.version,
                                    contactworkphone.contacttypeid == 4,
                                    contactworkphone.contactinformation is not None),
                                isouter=True
                            ).join(
                                contactworkphone2,
                                and_(
                                    contactworkphone2.foirequest_id == FOIRequest.foirequestid,
                                    contactworkphone2.foirequestversion_id == FOIRequest.version,
                                    contactworkphone2.contacttypeid == 5,
                                    contactworkphone2.contactinformation is not None),
                                isouter=True
                            ).join(
                                contactmobilephone,
                                and_(
                                    contactmobilephone.foirequest_id == FOIRequest.foirequestid,
                                    contactmobilephone.foirequestversion_id == FOIRequest.version,
                                    contactmobilephone.contacttypeid == 6,
                                    contactmobilephone.contactinformation is not None),
                                isouter=True
                            ).join(
                                contactother,
                                and_(
                                    contactother.foirequest_id == FOIRequest.foirequestid,
                                    contactother.foirequestversion_id == FOIRequest.version,
                                    contactother.contacttypeid == 7,
                                    contactother.contactinformation is not None),
                                isouter=True
                            ).join(
                                personalemployeenumber,
                                and_(
                                    personalemployeenumber.foirequest_id == FOIRequest.foirequestid,
                                    personalemployeenumber.foirequestversion_id == FOIRequest.version,
                                    personalemployeenumber.personalattributeid == 1,
                                    personalemployeenumber.attributevalue is not None),
                                isouter=True
                            ).join(
                                personalcorrectionnumber,
                                and_(
                                    personalcorrectionnumber.foirequest_id == FOIRequest.foirequestid,
                                    personalcorrectionnumber.foirequestversion_id == FOIRequest.version,
                                    personalcorrectionnumber.personalattributeid == 2,
                                    personalcorrectionnumber.attributevalue is not None),
                                isouter=True
                            ).join(
                                personalhealthnumber,
                                and_(
                                    personalhealthnumber.foirequest_id == FOIRequest.foirequestid,
                                    personalhealthnumber.foirequestversion_id == FOIRequest.version,
                                    personalhealthnumber.personalattributeid == 3,
                                    personalhealthnumber.attributevalue is not None),
                                isouter=True
                            ).filter(
                                # FOIMinistryRequest.requeststatusid != 3,
                                FOIRequest.isactive == True,
                                or_(*FOIRequestApplicant.getsearchfilters(keywords, contactemail, contacthomephone, contactworkphone, contactworkphone2, contactmobilephone))
                            ).order_by(FOIRequest.foirequestid.desc()).subquery()

        query_aggregate = _session.query(
            subquery_all.c.foirequestapplicantid,
            func.array_agg(subquery_all.c.firstname).label('firstname'),
            func.array_agg(subquery_all.c.middlename).label('middlename'),
            func.array_agg(subquery_all.c.lastname).label('lastname'),
            func.array_agg(subquery_all.c.alsoknownas).label('alsoknownas'),
            func.array_agg(subquery_all.c.dob).label('dob'),
            func.array_agg(subquery_all.c.businessname).label('businessname'),
            subquery_all.c.applicantversion,
            func.array_agg(subquery_all.c.foirequestid).label('foirequestid'),
            func.array_agg(subquery_all.c.foirequestversion).label('foirequestversion'),
            func.array_agg(subquery_all.c.requesttype).label('requesttype'),
            func.array_agg(subquery_all.c.applicantcategory).label('applicantcategory'),
            func.array_agg(subquery_all.c.email).label('email'),
            func.array_agg(subquery_all.c.address).label('address'),
            func.array_agg(subquery_all.c.homephone).label('homephone'),
            func.array_agg(subquery_all.c.workphone).label('workphone'),
            func.array_agg(subquery_all.c.workphone2).label('workphone2'),
            func.array_agg(subquery_all.c.mobilephone).label('mobilephone'),
            func.array_agg(subquery_all.c.othercontactinfo).label('othercontactinfo'),
            func.array_agg(subquery_all.c.employeenumber).label('employeenumber'),
            func.array_agg(subquery_all.c.correctionnumber).label('correctionnumber'),
            func.array_agg(subquery_all.c.phn).label('phn')
        ).group_by(subquery_all.c.foirequestapplicantid, subquery_all.c.applicantversion)

        applicantprofile_schema = ApplicantProfileSchema(many=True)
        return applicantprofile_schema.dump(query_aggregate.all())


    @classmethod
    def getsearchfilters(cls, keywords, contactemail, contacthomephone, contactworkphone, contactworkphone2, contactmobilephone):
        searchfilters = []
        if(len(keywords) > 0):
            if('firstname' in keywords):
                searchfilters.append(FOIRequestApplicant.firstname.ilike('%'+keywords['firstname']+'%'))

            if('lastname' in keywords):
                searchfilters.append(FOIRequestApplicant.lastname.ilike('%'+keywords['lastname']+'%'))

            if('email' in keywords):
                searchfilters.append(contactemail.contactinformation.ilike('%'+keywords['email']+'%'))

            if('homephone' in keywords):
                searchfilters.append(contacthomephone.contactinformation.ilike('%'+keywords['homephone']+'%'))

            if('workphone' in keywords):
                searchfilters.append(contactworkphone.contactinformation.ilike('%'+keywords['workphone']+'%'))

            if('workphone2' in keywords):
                searchfilters.append(contactworkphone2.contactinformation.ilike('%'+keywords['workphone2']+'%'))

            if('mobilephone' in keywords):
                searchfilters.append(contactmobilephone.contactinformation.ilike('%'+keywords['mobilephone']+'%'))

        return searchfilters

class FOIRequestApplicantSchema(ma.Schema):
    class Meta:
        fields = ('foirequestapplicantid','firstname','middlename','lastname','alsoknownas','dob','businessname')

class ApplicantProfileSchema(ma.Schema):
    class Meta:
        fields = ('foirequestapplicantid','firstname','middlename','lastname','alsoknownas','dob',
                  'businessname','applicantversion','foirequestid','foirequestversion','requesttype',
                  'applicantcategory','email','address','homephone','workphone','workphone2','mobilephone',
                  'othercontactinfo','employeenumber','correctionnumber','phn')
