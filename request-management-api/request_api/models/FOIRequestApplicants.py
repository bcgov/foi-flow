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
from .FOIRequestStatus import FOIRequestStatus
from sqlalchemy import and_, or_, func, case
import uuid

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
    applicantcategoryid = db.Column(db.Integer, unique=False, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    applicantprofileid = db.Column(db.String(120), unique=False, nullable=True)

    @classmethod
    def createapplicant(cls, firstname, lastname, middlename, businessname, alsoknownas, dob, userid):
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

    @classmethod
    def updateapplicantprofile(cls, foirequestapplicantid, firstname, lastname, middlename, businessname, alsoknownas, dob, applicantcategoryid, userid):
        applicant_query = db.session.query(
                                        FOIRequestApplicant
                                    ).filter_by(
                                        foirequestapplicantid = foirequestapplicantid
                                    )
        applicant = applicant_query.first()

        # create an applicant profile id if it's not set
        if(applicant.applicantprofileid is None):
            # applicant.isactive = False
            applicant_query.update({FOIRequestApplicant.applicantprofileid:str(uuid.uuid4())})

        applicantfromform = FOIRequestApplicant().prepareapplicantforcomparing(firstname, lastname, middlename, businessname, alsoknownas, dob, applicantcategoryid)
        applicantfromdb = FOIRequestApplicant().prepareapplicantforcomparing(applicant.firstname, applicant.lastname, applicant.middlename, applicant.businessname, applicant.alsoknownas, applicant.dob, applicant.applicantcategoryid)
        if applicantfromform != applicantfromdb:
            _applicant = FOIRequestApplicant()
            _applicant.createdby = userid
            _applicant.firstname = applicantfromform.firstname
            _applicant.lastname = applicantfromform.lastname
            _applicant.middlename = applicantfromform.middlename
            _applicant.businessname = applicantfromform.businessname
            _applicant.alsoknownas = applicantfromform.alsoknownas
            _applicant.dob = applicantfromform.dob
            _applicant.applicantprofileid = applicant.applicantprofileid
            _applicant.applicantcategoryid = applicantfromform.applicantcategoryid
            db.session.add(_applicant)
            db.session.commit()
            return DefaultMethodResult(True,'Applicant profile updated',_applicant.foirequestapplicantid)
        else:
            return DefaultMethodResult(True,'No update',applicant.foirequestapplicantid)

    # Search applicant by id
    @classmethod
    def getapplicantbyid(cls, applicantid):
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
            FOIRequestApplicant.applicantprofileid.label('applicantprofileid'),
            func.to_char(FOIRequestApplicantMapping.created_at, 'YYYY-MM-DD HH24:MI:SS').label('updatedat'),
            FOIRequestApplicant.foirequestapplicantid.label('foirequestapplicantid'),
            FOIRequestApplicant.firstname.label('firstname'),
            FOIRequestApplicant.middlename.label('middlename'),
            FOIRequestApplicant.lastname.label('lastname'),
            FOIRequestApplicant.alsoknownas.label('alsoknownas'),
            func.to_char(FOIRequestApplicant.dob, 'YYYY-MM-DD').label('dob'),
            FOIRequestApplicant.businessname.label('businessname'),
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
                                FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid
                                # and_(
                                #     FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid,
                                #     FOIRequestApplicant.isactive != False
                                # )
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
                                    city.dataformat == 'city'),
                                isouter=True
                            ).join(
                                province,
                                and_(
                                    province.foirequest_id == FOIRequest.foirequestid,
                                    province.foirequestversion_id == FOIRequest.version,
                                    province.contacttypeid == 2,
                                    province.contactinformation is not None,
                                    province.dataformat == 'province'),
                                isouter=True
                            ).join(
                                country,
                                and_(
                                    country.foirequest_id == FOIRequest.foirequestid,
                                    country.foirequestversion_id == FOIRequest.version,
                                    country.contacttypeid == 2,
                                    country.contactinformation is not None,
                                    country.dataformat == 'country'),
                                isouter=True
                            ).join(
                                postal,
                                and_(
                                    postal.foirequest_id == FOIRequest.foirequestid,
                                    postal.foirequestversion_id == FOIRequest.version,
                                    postal.contacttypeid == 2,
                                    postal.contactinformation is not None,
                                    postal.dataformat == 'postal'),
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
                                FOIRequestApplicant.foirequestapplicantid == applicantid
                            ).order_by(FOIRequest.foirequestid.desc()).subquery()

        query_aggregate = _session.query(
            func.array_agg(subquery_all.c.applicantprofileid).label('applicantprofileid'),
            func.array_agg(subquery_all.c.updatedat).label('updatedat'),
            subquery_all.c.foirequestapplicantid,
            func.array_agg(subquery_all.c.firstname).label('firstname'),
            func.array_agg(subquery_all.c.middlename).label('middlename'),
            func.array_agg(subquery_all.c.lastname).label('lastname'),
            func.array_agg(subquery_all.c.alsoknownas).label('alsoknownas'),
            func.array_agg(subquery_all.c.dob).label('dob'),
            func.array_agg(subquery_all.c.businessname).label('businessname'),
            func.array_agg(subquery_all.c.foirequestid).label('foirequestid'),
            func.array_agg(subquery_all.c.foirequestversion).label('foirequestversion'),
            func.array_agg(subquery_all.c.requesttype).label('requesttype'),
            func.array_agg(subquery_all.c.applicantcategory).label('applicantcategory'),
            func.array_agg(subquery_all.c.email).label('email'),
            func.array_agg(subquery_all.c.address).label('address'),
            func.array_agg(subquery_all.c.city).label('city'),
            func.array_agg(subquery_all.c.province).label('province'),
            func.array_agg(subquery_all.c.postal).label('postal'),
            func.array_agg(subquery_all.c.country).label('country'),
            func.array_agg(subquery_all.c.homephone).label('homephone'),
            func.array_agg(subquery_all.c.workphone).label('workphone'),
            func.array_agg(subquery_all.c.workphone2).label('workphone2'),
            func.array_agg(subquery_all.c.mobilephone).label('mobilephone'),
            func.array_agg(subquery_all.c.othercontactinfo).label('othercontactinfo'),
            func.array_agg(subquery_all.c.employeenumber).label('employeenumber'),
            func.array_agg(subquery_all.c.correctionnumber).label('correctionnumber'),
            func.array_agg(subquery_all.c.phn).label('phn')
        ).group_by(subquery_all.c.foirequestapplicantid)


        print("query_by_id", query_aggregate)

        applicantprofile_schema = ApplicantProfileSchema()
        return applicantprofile_schema.dump(query_aggregate.first())
    
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

        #aliase for search
        searchcontactemail = aliased(FOIRequestContactInformation)

        #max foirequest version
        subquery_foirequest_maxversion = _session.query(FOIRequest.foirequestid, func.max(FOIRequest.version).label('max_version')).group_by(FOIRequest.foirequestid).subquery()
        joincondition = [
            subquery_foirequest_maxversion.c.foirequestid == FOIRequest.foirequestid,
            subquery_foirequest_maxversion.c.max_version == FOIRequest.version,
        ]

        #generate query
        selectedcolumns = [
            FOIRequestApplicant.applicantprofileid.label('applicantprofileid'),
            func.to_char(FOIRequestApplicantMapping.created_at, 'YYYY-MM-DD HH24:MI:SS').label('updatedat'),
            FOIRequestApplicant.foirequestapplicantid.label('foirequestapplicantid'),
            FOIRequestApplicant.firstname.label('firstname'),
            FOIRequestApplicant.middlename.label('middlename'),
            FOIRequestApplicant.lastname.label('lastname'),
            FOIRequestApplicant.alsoknownas.label('alsoknownas'),
            func.to_char(FOIRequestApplicant.dob, 'YYYY-MM-DD').label('dob'),
            FOIRequestApplicant.businessname.label('businessname'),
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
                            ).distinct(
                                FOIRequest.foirequestid
                            ).join(
                                FOIRequestApplicantMapping,
                                and_(
                                    FOIRequestApplicantMapping.foirequest_id == FOIRequest.foirequestid,
                                    FOIRequestApplicantMapping.foirequestversion_id == FOIRequest.version,
                                    FOIRequestApplicantMapping.requestortypeid == 1),
                            ).join(
                                FOIRequestApplicant,
                                FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid
                                # and_(
                                #     FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid,
                                #     FOIRequestApplicant.isactive != False
                                # )
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
                                    city.dataformat == 'city'),
                                isouter=True
                            ).join(
                                province,
                                and_(
                                    province.foirequest_id == FOIRequest.foirequestid,
                                    province.foirequestversion_id == FOIRequest.version,
                                    province.contacttypeid == 2,
                                    province.contactinformation is not None,
                                    province.dataformat == 'province'),
                                isouter=True
                            ).join(
                                country,
                                and_(
                                    country.foirequest_id == FOIRequest.foirequestid,
                                    country.foirequestversion_id == FOIRequest.version,
                                    country.contacttypeid == 2,
                                    country.contactinformation is not None,
                                    country.dataformat == 'country'),
                                isouter=True
                            ).join(
                                postal,
                                and_(
                                    postal.foirequest_id == FOIRequest.foirequestid,
                                    postal.foirequestversion_id == FOIRequest.version,
                                    postal.contacttypeid == 2,
                                    postal.contactinformation is not None,
                                    postal.dataformat == 'postal'),
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
                            ).join(
                                searchcontactemail,
                                and_(
                                    searchcontactemail.foirequest_id == FOIRequest.foirequestid,
                                    searchcontactemail.contacttypeid == 1,
                                    searchcontactemail.contactinformation == email),
                            ).filter(
                                # FOIMinistryRequest.requeststatusid != 3,
                                FOIRequest.isactive == True
                                # searchcontactemail.contactinformation == email
                            ).order_by(FOIRequest.foirequestid.desc()).subquery()
        
        query_aggregate = _session.query(
            func.array_agg(subquery_all.c.applicantprofileid).label('applicantprofileid'),
            func.array_agg(subquery_all.c.updatedat).label('updatedat'),
            subquery_all.c.foirequestapplicantid,
            func.array_agg(subquery_all.c.firstname).label('firstname'),
            func.array_agg(subquery_all.c.middlename).label('middlename'),
            func.array_agg(subquery_all.c.lastname).label('lastname'),
            func.array_agg(subquery_all.c.alsoknownas).label('alsoknownas'),
            func.array_agg(subquery_all.c.dob).label('dob'),
            func.array_agg(subquery_all.c.businessname).label('businessname'),
            func.array_agg(subquery_all.c.foirequestid).label('foirequestid'),
            func.array_agg(subquery_all.c.foirequestversion).label('foirequestversion'),
            func.array_agg(subquery_all.c.requesttype).label('requesttype'),
            func.array_agg(subquery_all.c.applicantcategory).label('applicantcategory'),
            func.array_agg(subquery_all.c.email).label('email'),
            func.array_agg(subquery_all.c.address).label('address'),
            func.array_agg(subquery_all.c.city).label('city'),
            func.array_agg(subquery_all.c.province).label('province'),
            func.array_agg(subquery_all.c.postal).label('postal'),
            func.array_agg(subquery_all.c.country).label('country'),
            func.array_agg(subquery_all.c.homephone).label('homephone'),
            func.array_agg(subquery_all.c.workphone).label('workphone'),
            func.array_agg(subquery_all.c.workphone2).label('workphone2'),
            func.array_agg(subquery_all.c.mobilephone).label('mobilephone'),
            func.array_agg(subquery_all.c.othercontactinfo).label('othercontactinfo'),
            func.array_agg(subquery_all.c.employeenumber).label('employeenumber'),
            func.array_agg(subquery_all.c.correctionnumber).label('correctionnumber'),
            func.array_agg(subquery_all.c.phn).label('phn')
        ).group_by(subquery_all.c.foirequestapplicantid)

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

        city = aliased(FOIRequestContactInformation)
        province = aliased(FOIRequestContactInformation)
        postal = aliased(FOIRequestContactInformation)
        country = aliased(FOIRequestContactInformation)

        #aliase for getting personal attributes
        personalemployeenumber = aliased(FOIRequestPersonalAttribute)
        personalcorrectionnumber = aliased(FOIRequestPersonalAttribute)
        personalhealthnumber = aliased(FOIRequestPersonalAttribute)

        #aliase for search
        searchapplicant = aliased(FOIRequestApplicant)
        searchapplicantmapping = aliased(FOIRequestApplicantMapping)
        searchcontactinfo = aliased(FOIRequestContactInformation)

        #max foirequest version
        subquery_foirequest_maxversion = _session.query(FOIRequest.foirequestid, func.max(FOIRequest.version).label('max_version')).group_by(FOIRequest.foirequestid).subquery()
        joincondition = [
            subquery_foirequest_maxversion.c.foirequestid == FOIRequest.foirequestid,
            subquery_foirequest_maxversion.c.max_version == FOIRequest.version,
        ]
        
        #generate query
        selectedcolumns = [
            FOIRequestApplicant.applicantprofileid.label('applicantprofileid'),
            func.to_char(FOIRequestApplicantMapping.created_at, 'YYYY-MM-DD HH24:MI:SS').label('updatedat'),
            FOIRequestApplicant.foirequestapplicantid.label('foirequestapplicantid'),
            FOIRequestApplicant.firstname.label('firstname'),
            FOIRequestApplicant.middlename.label('middlename'),
            FOIRequestApplicant.lastname.label('lastname'),
            FOIRequestApplicant.alsoknownas.label('alsoknownas'),
            func.to_char(FOIRequestApplicant.dob, 'YYYY-MM-DD').label('dob'),
            FOIRequestApplicant.businessname.label('businessname'),
            FOIRequest.foirequestid.label('foirequestid'),
            FOIRequest.version.label('foirequestversion'),
            FOIRequest.requesttype.label('requesttype'),
            ApplicantCategory.name.label('applicantcategory'),
            contactemail.contactinformation.label('email'),
            contactaddress.contactinformation.label('address'),
            city.contactinformation.label('city'),
            province.contactinformation.label('province'),
            postal.contactinformation.label('postal'),
            country.contactinformation.label('country'),
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
                            ).distinct(
                                FOIRequest.foirequestid
                            ).join(
                                FOIRequestApplicantMapping,
                                and_(
                                    FOIRequestApplicantMapping.foirequest_id == FOIRequest.foirequestid,
                                    FOIRequestApplicantMapping.foirequestversion_id == FOIRequest.version,
                                    FOIRequestApplicantMapping.requestortypeid == 1),
                            ).join(
                                FOIRequestApplicant,
                                FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid
                                # and_(
                                #     FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid,
                                #     FOIRequestApplicant.isactive != False
                                # )
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
                                city,
                                and_(
                                    city.foirequest_id == FOIRequest.foirequestid,
                                    city.foirequestversion_id == FOIRequest.version,
                                    city.contacttypeid == 2,
                                    city.contactinformation is not None,
                                    city.dataformat == 'city'),
                                isouter=True
                            ).join(
                                province,
                                and_(
                                    province.foirequest_id == FOIRequest.foirequestid,
                                    province.foirequestversion_id == FOIRequest.version,
                                    province.contacttypeid == 2,
                                    province.contactinformation is not None,
                                    province.dataformat == 'province'),
                                isouter=True
                            ).join(
                                country,
                                and_(
                                    country.foirequest_id == FOIRequest.foirequestid,
                                    country.foirequestversion_id == FOIRequest.version,
                                    country.contacttypeid == 2,
                                    country.contactinformation is not None,
                                    country.dataformat == 'country'),
                                isouter=True
                            ).join(
                                postal,
                                and_(
                                    postal.foirequest_id == FOIRequest.foirequestid,
                                    postal.foirequestversion_id == FOIRequest.version,
                                    postal.contacttypeid == 2,
                                    postal.contactinformation is not None,
                                    postal.dataformat == 'postal'),
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
                            ).join(
                                searchapplicantmapping,
                                and_(
                                    searchapplicantmapping.foirequest_id == FOIRequest.foirequestid,
                                    searchapplicantmapping.requestortypeid == 1),
                                isouter=True
                            ).join(
                                searchapplicant,
                                searchapplicant.foirequestapplicantid == searchapplicantmapping.foirequestapplicantid,
                                isouter=True
                            ).join(
                                searchcontactinfo,
                                and_(
                                    searchcontactinfo.foirequest_id == FOIRequest.foirequestid,
                                    contacthomephone.contactinformation is not None),
                                isouter=True
                            ).filter(
                                # FOIMinistryRequest.requeststatusid != 3,
                                FOIRequest.isactive == True,
                                or_(*FOIRequestApplicant.getsearchfilters(searchapplicant, searchcontactinfo, keywords, contactemail, contacthomephone, contactworkphone, contactworkphone2, contactmobilephone))
                            ).order_by(FOIRequest.foirequestid.desc()).subquery()

        query_aggregate = _session.query(
            func.array_agg(subquery_all.c.applicantprofileid).label('applicantprofileid'),
            func.array_agg(subquery_all.c.updatedat).label('updatedat'),
            subquery_all.c.foirequestapplicantid,
            func.array_agg(subquery_all.c.firstname).label('firstname'),
            func.array_agg(subquery_all.c.middlename).label('middlename'),
            func.array_agg(subquery_all.c.lastname).label('lastname'),
            func.array_agg(subquery_all.c.alsoknownas).label('alsoknownas'),
            func.array_agg(subquery_all.c.dob).label('dob'),
            func.array_agg(subquery_all.c.businessname).label('businessname'),
            func.array_agg(subquery_all.c.foirequestid).label('foirequestid'),
            func.array_agg(subquery_all.c.foirequestversion).label('foirequestversion'),
            func.array_agg(subquery_all.c.requesttype).label('requesttype'),
            func.array_agg(subquery_all.c.applicantcategory).label('applicantcategory'),
            func.array_agg(subquery_all.c.email).label('email'),
            func.array_agg(subquery_all.c.address).label('address'),
            func.array_agg(subquery_all.c.city).label('city'),
            func.array_agg(subquery_all.c.province).label('province'),
            func.array_agg(subquery_all.c.postal).label('postal'),
            func.array_agg(subquery_all.c.country).label('country'),
            func.array_agg(subquery_all.c.homephone).label('homephone'),
            func.array_agg(subquery_all.c.workphone).label('workphone'),
            func.array_agg(subquery_all.c.workphone2).label('workphone2'),
            func.array_agg(subquery_all.c.mobilephone).label('mobilephone'),
            func.array_agg(subquery_all.c.othercontactinfo).label('othercontactinfo'),
            func.array_agg(subquery_all.c.employeenumber).label('employeenumber'),
            func.array_agg(subquery_all.c.correctionnumber).label('correctionnumber'),
            func.array_agg(subquery_all.c.phn).label('phn')
        ).group_by(subquery_all.c.foirequestapplicantid)

        applicantprofile_schema = ApplicantProfileSchema(many=True)
        return applicantprofile_schema.dump(query_aggregate.all())


    @classmethod
    def getsearchfilters(cls, searchapplicant, searchcontactinfo, keywords, contactemail, contacthomephone, contactworkphone, contactworkphone2, contactmobilephone):
        searchfilters = []
        if(len(keywords) > 0):
            if('firstname' in keywords):
                searchfilters.append(searchapplicant.firstname.ilike('%'+keywords['firstname']+'%'))

            if('lastname' in keywords):
                searchfilters.append(searchapplicant.lastname.ilike('%'+keywords['lastname']+'%'))

            if('email' in keywords):
                searchfilters.append(searchcontactinfo.contactinformation.ilike('%'+keywords['email']+'%'))

            if('homephone' in keywords):
                searchfilters.append(searchcontactinfo.contactinformation.ilike('%'+keywords['homephone']+'%'))

            if('workphone' in keywords):
                searchfilters.append(searchcontactinfo.contactinformation.ilike('%'+keywords['workphone']+'%'))

            if('workphone2' in keywords):
                searchfilters.append(searchcontactinfo.contactinformation.ilike('%'+keywords['workphone2']+'%'))

            if('mobilephone' in keywords):
                searchfilters.append(searchcontactinfo.contactinformation.ilike('%'+keywords['mobilephone']+'%'))

        return searchfilters


    # applicant history
    @classmethod
    def getapplicanthistory(cls, applicantid):
        #for queue/dashboard
        _session = db.session

        applicantprofile = aliased(FOIRequestApplicant)

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

        #generate query
        selectedcolumns = [
            applicantprofile.applicantprofileid.label('applicantprofileid'),
            func.to_char(FOIRequestApplicantMapping.created_at, 'YYYY-MM-DD HH24:MI:SS').label('updatedat'),
            FOIRequestApplicant.foirequestapplicantid.label('foirequestapplicantid'),
            FOIRequestApplicant.firstname.label('firstname'),
            FOIRequestApplicant.middlename.label('middlename'),
            FOIRequestApplicant.lastname.label('lastname'),
            FOIRequestApplicant.alsoknownas.label('alsoknownas'),
            func.to_char(FOIRequestApplicant.dob, 'YYYY-MM-DD').label('dob'),
            FOIRequestApplicant.businessname.label('businessname'),
            FOIRequest.foirequestid.label('foirequestid'),
            FOIRequest.version.label('foirequestversion'),
            FOIRequest.requesttype.label('requesttype'),
            FOIRequest.createdby.label('createdby'),
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

        query_all = _session.query(
                                *selectedcolumns
                            ).join(
                                applicantprofile,
                                or_(
                                    and_(
                                        applicantprofile.foirequestapplicantid == applicantid,
                                        applicantprofile.applicantprofileid == FOIRequestApplicant.applicantprofileid
                                    ),
                                    and_(
                                        FOIRequestApplicant.foirequestapplicantid == applicantid,
                                        applicantprofile.applicantprofileid.is_(None)
                                    )
                                )
                            ).join(
                                FOIRequestApplicantMapping,
                                and_(
                                    FOIRequestApplicantMapping.requestortypeid == 1,
                                    FOIRequestApplicantMapping.foirequestapplicantid == FOIRequestApplicant.foirequestapplicantid)
                            ).join(
                                FOIRequest,
                                and_(
                                    FOIRequest.foirequestid == FOIRequestApplicantMapping.foirequest_id,
                                    FOIRequest.version == FOIRequestApplicantMapping.foirequestversion_id)
                            ).join(
                                ApplicantCategory,
                                ApplicantCategory.applicantcategoryid == FOIRequest.applicantcategoryid
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
                                    city.dataformat == 'city'),
                                isouter=True
                            ).join(
                                province,
                                and_(
                                    province.foirequest_id == FOIRequest.foirequestid,
                                    province.foirequestversion_id == FOIRequest.version,
                                    province.contacttypeid == 2,
                                    province.contactinformation is not None,
                                    province.dataformat == 'province'),
                                isouter=True
                            ).join(
                                country,
                                and_(
                                    country.foirequest_id == FOIRequest.foirequestid,
                                    country.foirequestversion_id == FOIRequest.version,
                                    country.contacttypeid == 2,
                                    country.contactinformation is not None,
                                    country.dataformat == 'country'),
                                isouter=True
                            ).join(
                                postal,
                                and_(
                                    postal.foirequest_id == FOIRequest.foirequestid,
                                    postal.foirequestversion_id == FOIRequest.version,
                                    postal.contacttypeid == 2,
                                    postal.contactinformation is not None,
                                    postal.dataformat == 'postal'),
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
                                FOIRequest.isactive == True
                            ).order_by(FOIRequestApplicantMapping.created_at.desc())

        # print("query_applicant_history", query_all)

        applicantprofile_schema = ApplicantProfileSchema(many=True)
        return applicantprofile_schema.dump(query_all.all())


    # requests by applicant id
    @classmethod
    def getapplicantrequests(cls, applicantid):
        from .FOIMinistryRequests import FOIMinistryRequest

        #for queue/dashboard
        _session = db.session

        applicantprofile = aliased(FOIRequestApplicant)

        #max foirequest version
        subquery_foirequest_maxversion = _session.query(FOIRequest.foirequestid, func.max(FOIRequest.version).label('max_version')).group_by(FOIRequest.foirequestid).subquery()
        joincondition = [
            subquery_foirequest_maxversion.c.foirequestid == FOIRequest.foirequestid,
            subquery_foirequest_maxversion.c.max_version == FOIRequest.version,
        ]

        #generate query
        selectedcolumns = [
            FOIRequestApplicant.applicantprofileid.label('applicantprofileid'),
            FOIRequestApplicant.foirequestapplicantid.label('foirequestapplicantid'),
            FOIMinistryRequest.axisrequestid,
            FOIMinistryRequest.filenumber,
            FOIRequestStatus.name.label('requeststatus'),
            func.to_char(FOIRequest.receiveddate, 'MON DD YYYY').label('receiveddate'),
            FOIMinistryRequest.description
        ]

        query_all = _session.query(
                                *selectedcolumns
                            ).distinct(
                                FOIRequest.foirequestid
                            ).join(
                                applicantprofile,
                                or_(
                                    and_(
                                        applicantprofile.foirequestapplicantid == applicantid,
                                        applicantprofile.applicantprofileid == FOIRequestApplicant.applicantprofileid
                                    ),
                                    and_(
                                        FOIRequestApplicant.foirequestapplicantid == applicantid,
                                        applicantprofile.applicantprofileid.is_(None)
                                    )
                                )
                            ).join(
                                FOIRequestApplicantMapping,
                                and_(
                                    FOIRequestApplicantMapping.requestortypeid == 1,
                                    FOIRequestApplicantMapping.foirequestapplicantid == FOIRequestApplicant.foirequestapplicantid)
                            ).join(
                                FOIRequest,
                                and_(
                                    FOIRequest.foirequestid == FOIRequestApplicantMapping.foirequest_id,
                                    FOIRequest.version == FOIRequestApplicantMapping.foirequestversion_id,
                                    FOIRequest.isactive == True)
                            ).join(
                                subquery_foirequest_maxversion,
                                and_(*joincondition)
                            ).join(
                                FOIMinistryRequest,
                                and_(
                                    FOIMinistryRequest.foirequest_id == FOIRequest.foirequestid,
                                    FOIMinistryRequest.isactive == True)
                            ).join(
                                FOIRequestStatus,
                                FOIRequestStatus.requeststatusid == FOIMinistryRequest.requeststatusid
                            ).order_by(FOIRequest.foirequestid.desc())
        
        # print('query_all', query_all)

        applicantrequest_schema = ApplicantRequestSchema(many=True)
        return applicantrequest_schema.dump(query_all.all())

    @classmethod
    def prepareapplicantforcomparing(cls, firstname, lastname, middlename, businessname, alsoknownas, dob, applicantcategoryid):
        return {
            'firstname': firstname if firstname is not None or firstname != '' else None,
            'lastname': lastname if lastname is not None or lastname != '' else None,
            'middlename': middlename if middlename is not None or middlename != '' else None,
            'businessname': businessname if businessname is not None or businessname != '' else None,
            'alsoknownas': alsoknownas if alsoknownas is not None or alsoknownas != '' else None,
            'dob': datetime.strptime(dob, "%Y-%m-%d") if dob is not None or dob != '' else None,
            'applicantcategoryid': applicantcategoryid if applicantcategoryid is not None or alsoknownas != 0 else None,
        }


class FOIRequestApplicantSchema(ma.Schema):
    class Meta:
        fields = ('foirequestapplicantid','firstname','middlename','lastname','alsoknownas','dob','businessname')

class ApplicantProfileSchema(ma.Schema):
    class Meta:
        fields = ('applicantprofileid','updatedat','createdby','foirequestapplicantid','firstname','middlename','lastname',
                  'alsoknownas','dob','businessname','foirequestid','foirequestversion','requesttype','applicantcategory',
                  'email','address','city','province','postal','country','homephone','workphone',
                  'workphone2','mobilephone','othercontactinfo','employeenumber','correctionnumber','phn')

class ApplicantRequestSchema(ma.Schema):
    class Meta:
        fields = ('applicantprofileid','foirequestapplicantid','axisrequestid','filenumber', 'requeststatus','receiveddate','description')