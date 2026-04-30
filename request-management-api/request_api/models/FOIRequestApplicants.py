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
from sqlalchemy import and_, or_, func, text, desc, cast, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects import postgresql
from sqlalchemy.inspection import inspect
from marshmallow import fields
import uuid

class FOIRequestApplicant(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestApplicants' 
    # Defining the columns
    foirequestapplicantid = db.Column(db.Integer, primary_key=True,autoincrement=True)

    firstname = db.Column(db.String(50), unique=False, nullable=True)
    middlename = db.Column(db.String(50), unique=False, nullable=True)
    lastname = db.Column(db.String(50), unique=False, nullable=True)

    alsoknownas = db.Column(db.String(255), unique=False, nullable=True)
    dob = db.Column(db.DateTime, unique=False, nullable=True)
    businessname = db.Column(db.String(255), unique=False, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    applicantprofileid = db.Column(db.String(120), unique=False, nullable=True)

    axisapplicantid = db.Column(db.Integer, unique=False, nullable=True)
    email = db.Column(db.Text, nullable=True)
    category = db.Column(db.Text, nullable=True)
    address = db.Column(db.Text, nullable=True)
    address_secondary = db.Column(db.Text, nullable=True)
    city = db.Column(db.Text, nullable=True)
    province = db.Column(db.Text, nullable=True)
    postal = db.Column(db.Text, nullable=True)
    country = db.Column(db.Text, nullable=True)
    home_phone = db.Column(db.Text, nullable=True)
    mobile_phone = db.Column(db.Text, nullable=True)
    work_phone = db.Column(db.Text, nullable=True)
    alternative_phone = db.Column(db.Text, nullable=True)
    other_contact_info = db.Column(db.Text, nullable=True)
    personal_health_number = db.Column(db.Text, nullable=True)
    employee_number = db.Column(db.Text, nullable=True)
    correction_number = db.Column(db.Text, nullable=True)
    other_notes = db.Column(db.Text, unique=False, nullable=True)
    section43_info = db.Column(db.Text, nullable=True)
    request_history = db.Column(JSON, nullable=True)
    is_active = db.Column(db.Boolean)
    merged_into_id = db.Column(db.Integer, unique=False, nullable=True)

    @classmethod
    def from_request_data(cls, requestdata, is_new = False):
        applicant = FOIRequestApplicant()
        if is_new:
            applicant.applicantprofileid = str(uuid.uuid4())
        else:
            applicant.applicantprofileid = requestdata.get("applicantprofileid")
        applicant.firstname = requestdata.get("firstName")
        applicant.middlename = requestdata.get("middleName")
        applicant.lastname = requestdata.get("lastName")
        alsoknownas = requestdata.get("additionalPersonalInfo", {}).get("alsoKnownAs", None)
        applicant.alsoknownas = alsoknownas if alsoknownas else None
        dob_str = requestdata.get("additionalPersonalInfo", {}).get("birthDate")
        if dob_str and dob_str.strip():
            date = datetime.fromisoformat(dob_str).replace(tzinfo=None) # normalize to naive datetime to match DB
            applicant.dob = date
        else:
            applicant.dob = None
        applicant.businessname = requestdata.get("businessName")
        applicant.axisapplicantid = requestdata.get("axisapplicantid")
        applicant.email = requestdata.get("email")
        applicant.category = requestdata.get("category")
        applicant.address = requestdata.get("address")
        applicant.address_secondary = requestdata.get("addressSecondary")
        applicant.city = requestdata.get("city")
        applicant.province = requestdata.get("province")
        applicant.postal = requestdata.get("postal")
        applicant.country = requestdata.get("country")
        applicant.home_phone = requestdata.get("phonePrimary")
        applicant.mobile_phone = requestdata.get("phoneSecondary")
        applicant.work_phone = requestdata.get("workPhonePrimary")
        applicant.alternative_phone = requestdata.get("workPhoneSecondary")
        # applicant.other_contact_info = requestdata.get("")
        applicant.personal_health_number = requestdata.get("additionalPersonalInfo", {}).get("personalHealthNumber")
        applicant.employee_number = requestdata.get("publicServiceEmployeeNumber")
        applicant.correction_number = requestdata.get("correctionalServiceNumber")
        applicant.other_notes = requestdata.get("other_notes")
        applicant.is_active = True
        # section43_info, request_history missing.
        return applicant

    @classmethod
    def child_from_additional_personal_info(cls, addlapplicantinfo, is_new = False):
        applicant = FOIRequestApplicant()
        applicant.firstname = addlapplicantinfo.get("childFirstName", None)
        applicant.middlename = addlapplicantinfo.get("childMiddleName", None)
        applicant.lastname = addlapplicantinfo.get("childLastName", None)
        alsoknownas = addlapplicantinfo.get("childAlsoKnownAs", None)
        applicant.alsoknownas = alsoknownas if alsoknownas else None
        dob_str = addlapplicantinfo.get("childBirthDate")
        if dob_str and dob_str.strip():
            date = datetime.fromisoformat(dob_str).replace(tzinfo=None) # normalize to naive datetime to match DB
            applicant.dob = date
        else:
            applicant.dob = None
        applicant.businessname = None
        if is_new:
            applicant.applicantprofileid = str(uuid.uuid4())
        else:
            applicant.applicantprofileid = addlapplicantinfo.get("applicantprofileid")
        applicant.is_active = True
        return applicant

    @classmethod
    def onbehalfof_from_applicantschema(cls, applicantschema, is_new = False):
        addlapplicantinfo = applicantschema.get("additionalPersonalInfo", {})
        applicant = FOIRequestApplicant()
        applicant.firstname = addlapplicantinfo.get("anotherFirstName", None)
        applicant.middlename = addlapplicantinfo.get("anotherMiddleName", None)
        applicant.lastname = addlapplicantinfo.get("anotherLastName", None)
        alsoknownas = addlapplicantinfo.get("anotherAlsoKnownAs", None)
        applicant.alsoknownas = alsoknownas if alsoknownas else None
        dob = addlapplicantinfo.get("anotherBirthDate", None)
        applicant.dob = datetime.fromisoformat(dob) if dob else None
        applicant.businessname = None
        if is_new:
            applicant.applicantprofileid = str(uuid.uuid4())
        else:
            applicant.applicantprofileid = applicantschema.get("applicantprofileid")
        applicant.is_active = True
        return applicant

    @classmethod
    def save_instance(cls, applicantobject, userid):
        applicantobject.createdby = userid
        db.session.add(applicantobject)
        db.session.commit()
        return DefaultMethodResult(True,'Applicant added',applicantobject.foirequestapplicantid)

    @classmethod
    def createapplicant(cls, firstname, lastname, middlename, businessname, alsoknownas, dob, axisapplicantid, other_notes, userid):
        applicant = FOIRequestApplicant()
        applicant.createdby = userid
        applicant.firstname = firstname
        applicant.lastname = lastname
        applicant.middlename = middlename
        applicant.businessname = businessname
        applicant.alsoknownas = alsoknownas
        applicant.applicantprofileid = str(uuid.uuid4())
        applicant.axisapplicantid = axisapplicantid
        applicant.other_notes = other_notes
        if dob is not None and dob != "":
            applicant.dob = datetime.strptime(dob, "%Y-%m-%d")
        else:
            applicant.dob = None
        db.session.add(applicant)
        db.session.commit()               
        return DefaultMethodResult(True,'Applicant added',applicant.foirequestapplicantid)

    @classmethod
    def update_applicant_profile(cls, updatedapplicant, foirequestapplicantid, userid):

        applicantprofile = aliased(FOIRequestApplicant)

        applicant_query = db.session.query(
                                        FOIRequestApplicant
                                    ).join(
                                        applicantprofile,
                                        or_(
                                            and_(
                                                applicantprofile.foirequestapplicantid == foirequestapplicantid,
                                                applicantprofile.applicantprofileid == FOIRequestApplicant.applicantprofileid
                                            ),
                                            and_(
                                                FOIRequestApplicant.foirequestapplicantid == foirequestapplicantid,
                                                applicantprofile.applicantprofileid.is_(None)
                                            )
                                        )
                                    )
        oldapplicant = applicant_query.order_by(FOIRequestApplicant.foirequestapplicantid.desc()).first()
        # Old logic checked for updates using applicants_differ = FOIRequestApplicant().applicants_differ(updatedapplicant, oldapplicant)
        # This just goes ahead and makes the update
        updatedapplicant.createdby = userid
        # Persist these values as they will never be updated by the frontend
        if oldapplicant:
            updatedapplicant.section43_info = oldapplicant.section43_info
            updatedapplicant.request_history = oldapplicant.request_history
        db.session.add(updatedapplicant)
        db.session.commit()
        return DefaultMethodResult(True,'Applicant profile updated',updatedapplicant.foirequestapplicantid)
        
    @classmethod
    def getlatestprofilebyapplicantid(cls, applicantid):
        schema = FOIRequestApplicantSchema(many=False)
        sq = db.session.query(FOIRequestApplicant).filter_by(foirequestapplicantid=applicantid).first()
        if sq is None or (not sq.applicantprofileid):
            return schema.dump(sq)
        query = db.session.query(FOIRequestApplicant).filter(FOIRequestApplicant.applicantprofileid == sq.applicantprofileid).order_by(FOIRequestApplicant.foirequestapplicantid.desc()).first()
        return schema.dump(query)

    @classmethod
    def get_latest_applicant_profile_by_id(cls, foirequestapplicantid):
        applicantprofileid = db.session.query(FOIRequestApplicant.applicantprofileid)\
            .filter_by(foirequestapplicantid=foirequestapplicantid)\
            .order_by(FOIRequestApplicant.foirequestapplicantid.desc())\
            .limit(1)\
            .scalar()

        if applicantprofileid is None:
            query = db.session.query(FOIRequestApplicant)\
                .filter(FOIRequestApplicant.foirequestapplicantid == foirequestapplicantid)
        else:
            query = db.session.query(FOIRequestApplicant)\
                .filter(FOIRequestApplicant.applicantprofileid == applicantprofileid)\
                .order_by(FOIRequestApplicant.foirequestapplicantid.desc())

        applicantrequest_schema = ApplicantProfileBaseSchema(many=False)
        return applicantrequest_schema.dump(query.first())
    
    @classmethod
    def getlatestprofilebyaxisapplicantid(cls, axisapplicantid):
        schema = FOIRequestApplicantSchema(many=False)
        sq = db.session.query(FOIRequestApplicant).filter_by(axisapplicantid=axisapplicantid).first()
        if sq is None or (not sq.applicantprofileid):
            return schema.dump(sq)
        query = db.session.query(FOIRequestApplicant).filter(FOIRequestApplicant.applicantprofileid == sq.applicantprofileid).order_by(FOIRequestApplicant.foirequestapplicantid.desc()).first()
        return schema.dump(query)

    @classmethod
    def get_applicantprofileid_from_foirequestapplicantid(cls, foirequestapplicantid):
        applicantprofileid = db.session.query(FOIRequestApplicant.applicantprofileid)\
            .filter_by(foirequestapplicantid=foirequestapplicantid)\
            .order_by(FOIRequestApplicant.foirequestapplicantid.desc())\
            .limit(1)\
            .scalar()
        return applicantprofileid
    
    @classmethod
    def get_foirequestapplicantid_from_applicantprofileid(cls, applicantprofileid):
        foirequestapplicantid = db.session.query(FOIRequestApplicant.foirequestapplicantid)\
            .filter_by(applicantprofileid=applicantprofileid)\
            .order_by(FOIRequestApplicant.foirequestapplicantid.desc())\
            .limit(1)\
            .scalar()
        return foirequestapplicantid

    # Search applicant by id
    @classmethod
    def get_composite_applicant_profile_by_id(cls, applicantid):
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
            personalhealthnumber.attributevalue.label('phn'),
            FOIRequestApplicant.axisapplicantid.label('axisapplicantid'),
            FOIRequestApplicant.other_notes.label('other_notes')
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
            func.array_agg(subquery_all.c.address2).label('address2'),
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
            func.array_agg(subquery_all.c.phn).label('phn'),
            func.array_agg(subquery_all.c.axisapplicantid).label('axisapplicantid'),
            func.array_agg(subquery_all.c.other_notes).label('other_notes')
        ).group_by(subquery_all.c.foirequestapplicantid)

        applicantprofile_schema = ApplicantProfileCompositeSchema()
        return applicantprofile_schema.dump(query_aggregate.first())

    @classmethod
    def search_applicant_profiles(cls, keywords):
        conditions = []
        for key, value in keywords.items():
            column = getattr(FOIRequestApplicant, key, None)
            if column is not None and value:
                conditions.append(cast(column, String).ilike(f"%{value}%"))
        if not conditions:
            return []

        query = (
            db.session.query(FOIRequestApplicant)
            .filter(and_(*conditions))
            .filter(FOIRequestApplicant.is_active.is_(True))
            .order_by(
                FOIRequestApplicant.applicantprofileid,
                desc(FOIRequestApplicant.foirequestapplicantid)
            )
            .distinct(FOIRequestApplicant.applicantprofileid)
        )

        schema = ApplicantProfileBaseSchema(many=True)
        return schema.dump(query.all())

    # Search applicant by keywords
    @classmethod
    def search_composite_applicant(cls, keywords):
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
            contactaddress2.contactinformation.label('address2'),
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
            personalhealthnumber.attributevalue.label('phn'),
            FOIRequestApplicant.axisapplicantid.label('axisapplicantid'),
            FOIRequestApplicant.other_notes.label('other_notes')
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
                                    contactaddress.contactinformation is not None,
                                    contactaddress.dataformat == "address"),
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
                                    searchcontactinfo.contactinformation is not None),
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
            func.array_agg(subquery_all.c.address2).label('address2'),
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
            func.array_agg(subquery_all.c.phn).label('phn'),
            func.array_agg(subquery_all.c.axisapplicantid).label('axisapplicantid'),
            func.array_agg(subquery_all.c.other_notes).label('other_notes')
        ).group_by(subquery_all.c.foirequestapplicantid)

        applicantprofile_schema = ApplicantProfileCompositeSchema(many=True)
        return applicantprofile_schema.dump(query_aggregate.all())

    @classmethod
    def getsearchfilters(cls, searchapplicant, searchcontactinfo, keywords, contactemail, contacthomephone, contactworkphone, contactworkphone2, contactmobilephone):
        searchfilters = []
        if(len(keywords) > 0):
            if('applicantprofileids' in keywords):
                searchfilters.append(searchapplicant.applicantprofileid.in_(keywords['applicantprofileids']))
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
            FOIRequestApplicant.createdby.label('createdby'),
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
            personalhealthnumber.attributevalue.label('phn'),
            FOIRequestApplicant.axisapplicantid.label('axisapplicantid'),
            FOIRequestApplicant.other_notes.label('other_notes')
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
                                        applicantprofile.foirequestapplicantid == FOIRequestApplicant.foirequestapplicantid,
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
                                    contactaddress.contactinformation.isnot(None),
                                    contactaddress.dataformat == 'address'),
                                isouter=True
                            ).join(
                                contactaddress2,
                                and_(
                                    contactaddress2.foirequest_id == FOIRequest.foirequestid,
                                    contactaddress2.foirequestversion_id == FOIRequest.version,
                                    contactaddress2.contacttypeid == 2,
                                    contactaddress2.contactinformation.isnot(None),
                                    contactaddress2.dataformat == 'addressSecondary'),
                                isouter=True
                            ).join(
                                contacthomephone,
                                and_(
                                    contacthomephone.foirequest_id == FOIRequest.foirequestid,
                                    contacthomephone.foirequestversion_id == FOIRequest.version,
                                    contacthomephone.contacttypeid == 3,
                                    contacthomephone.contactinformation.isnot(None)),
                                isouter=True
                            ).join(
                                contactworkphone,
                                and_(
                                    contactworkphone.foirequest_id == FOIRequest.foirequestid,
                                    contactworkphone.foirequestversion_id == FOIRequest.version,
                                    contactworkphone.contacttypeid == 4,
                                    contactworkphone.contactinformation.isnot(None)),
                                isouter=True
                            ).join(
                                contactworkphone2,
                                and_(
                                    contactworkphone2.foirequest_id == FOIRequest.foirequestid,
                                    contactworkphone2.foirequestversion_id == FOIRequest.version,
                                    contactworkphone2.contacttypeid == 5,
                                    contactworkphone2.contactinformation.isnot(None)),
                                isouter=True
                            ).join(
                                contactmobilephone,
                                and_(
                                    contactmobilephone.foirequest_id == FOIRequest.foirequestid,
                                    contactmobilephone.foirequestversion_id == FOIRequest.version,
                                    contactmobilephone.contacttypeid == 6,
                                    contactmobilephone.contactinformation.isnot(None)),
                                isouter=True
                            ).join(
                                contactother,
                                and_(
                                    contactother.foirequest_id == FOIRequest.foirequestid,
                                    contactother.foirequestversion_id == FOIRequest.version,
                                    contactother.contacttypeid == 7,
                                    contactother.contactinformation.isnot(None)),
                                isouter=True
                            ).join(
                                city,
                                and_(
                                    city.foirequest_id == FOIRequest.foirequestid,
                                    city.foirequestversion_id == FOIRequest.version,
                                    city.contacttypeid == 2,
                                    city.contactinformation.isnot(None),
                                    city.dataformat == 'city'),
                                isouter=True
                            ).join(
                                province,
                                and_(
                                    province.foirequest_id == FOIRequest.foirequestid,
                                    province.foirequestversion_id == FOIRequest.version,
                                    province.contacttypeid == 2,
                                    province.contactinformation.isnot(None),
                                    province.dataformat == 'province'),
                                isouter=True
                            ).join(
                                country,
                                and_(
                                    country.foirequest_id == FOIRequest.foirequestid,
                                    country.foirequestversion_id == FOIRequest.version,
                                    country.contacttypeid == 2,
                                    country.contactinformation.isnot(None),
                                    country.dataformat == 'country'),
                                isouter=True
                            ).join(
                                postal,
                                and_(
                                    postal.foirequest_id == FOIRequest.foirequestid,
                                    postal.foirequestversion_id == FOIRequest.version,
                                    postal.contacttypeid == 2,
                                    postal.contactinformation.isnot(None),
                                    postal.dataformat == 'postal'),
                                isouter=True
                            ).join(
                                personalemployeenumber,
                                and_(
                                    personalemployeenumber.foirequest_id == FOIRequest.foirequestid,
                                    personalemployeenumber.foirequestversion_id == FOIRequest.version,
                                    personalemployeenumber.personalattributeid == 1,
                                    personalemployeenumber.attributevalue.isnot(None)),
                                isouter=True
                            ).join(
                                personalcorrectionnumber,
                                and_(
                                    personalcorrectionnumber.foirequest_id == FOIRequest.foirequestid,
                                    personalcorrectionnumber.foirequestversion_id == FOIRequest.version,
                                    personalcorrectionnumber.personalattributeid == 2,
                                    personalcorrectionnumber.attributevalue.isnot(None)),
                                isouter=True
                            ).join(
                                personalhealthnumber,
                                and_(
                                    personalhealthnumber.foirequest_id == FOIRequest.foirequestid,
                                    personalhealthnumber.foirequestversion_id == FOIRequest.version,
                                    personalhealthnumber.personalattributeid == 3,
                                    personalhealthnumber.attributevalue.isnot(None)),
                                isouter=True
                            ).filter(
                                FOIRequest.isactive == True
                            ).order_by(FOIRequestApplicantMapping.created_at.desc())


        applicantprofile_schema = ApplicantProfileCompositeSchema(many=True)
        return applicantprofile_schema.dump(query_all.all())

    @classmethod
    def getapplicantrequests(cls, applicantid, applicanttype="all"):
        primary_applicant_requests = FOIRequestApplicantMapping.requestortypeid == 1
        onbehalfof_applicant_requests = FOIRequestApplicantMapping.requestortypeid == 2
        all_applicant_requests = or_(primary_applicant_requests, onbehalfof_applicant_requests)
        applicant_join_statement = all_applicant_requests

        if applicanttype == "applicant":
            applicant_join_statement = primary_applicant_requests
        elif applicanttype == "onbehalfof":
            applicant_join_statement = onbehalfof_applicant_requests

        from .FOIMinistryRequests import FOIMinistryRequest

        _session = db.session

        # Get the applicantprofileid for the given applicantid
        profile_id = _session.query(
            FOIRequestApplicant.applicantprofileid
        ).filter(
            FOIRequestApplicant.foirequestapplicantid == applicantid
        ).limit(1).scalar()

        # Get all foirequestapplicantids sharing the same profile
        # Fall back to just the given applicantid if no applicantprofileid assigned
        if profile_id is None:
            profile_subquery = _session.query(
                FOIRequestApplicant.foirequestapplicantid
            ).filter(
                FOIRequestApplicant.foirequestapplicantid == applicantid
            ).subquery()
        else:
            profile_subquery = _session.query(
                FOIRequestApplicant.foirequestapplicantid
            ).filter(
                FOIRequestApplicant.applicantprofileid == profile_id
            ).subquery()

        # # Determine if this applicant is a master or a duplicate
        # merged_into_id = _session.query(
        #     FOIRequestApplicant.merged_into_id
        # ).filter(
        #     FOIRequestApplicant.foirequestapplicantid == applicantid
        # ).scalar()

        # # If merged_into_id is None, this applicant is the master (or unmerged)
        # master_id = merged_into_id if merged_into_id is not None else applicantid

        # # Get all applicant ids in the merge group
        # applicantids = _session.query(
        #     FOIRequestApplicant.foirequestapplicantid
        # ).filter(
        #     or_(
        #         (FOIRequestApplicant.foirequestapplicantid == master_id),
        #         (FOIRequestApplicant.merged_into_id == master_id)
        #     )
        # ).all()

        # # applicantids = [row.foirequestapplicantid for row in applicantids]
        # applicantids = cls.get_all_merged_ids(applicantid)
        # print('\n\n\n***applicantids: ', applicantids)

        # # # Get all profile_ids for the given applicant ids (excluding nulls)
        # # profile_ids = _session.query(
        # #     FOIRequestApplicant.applicantprofileid
        # # ).filter(
        # #     FOIRequestApplicant.foirequestapplicantid.in_(applicantids),
        # #     FOIRequestApplicant.applicantprofileid.isnot(None)
        # # ).distinct().all()

        # # profile_ids = [row.applicantprofileid for row in profile_ids]
        # # print('\n\n\n****profile_ids: ', profile_ids)

        # # Build the subquery
        # profile_ids = cls.get_all_applicantprofileids(applicantids)
        # print('\n\n\n****profile_ids: ', profile_ids)

        # if not profile_ids:
        #     # No profiles found, fall back to just the given applicant ids
        #     profile_subquery = _session.query(
        #         FOIRequestApplicant.foirequestapplicantid
        #     ).filter(
        #         FOIRequestApplicant.foirequestapplicantid.in_(applicantids)
        #     ).subquery()
        # else:
        #     # Get all foirequestapplicantids sharing any of the found profiles
        #     profile_subquery = _session.query(
        #         FOIRequestApplicant.foirequestapplicantid
        #     ).filter(
        #         FOIRequestApplicant.applicantprofileid.in_(profile_ids)
        #     ).subquery()
        # Get the latest mapping version per foirequest to exclude stale applicant assignments
        subquery_latest_mapping = _session.query(
            FOIRequestApplicantMapping.foirequest_id,
            func.max(FOIRequestApplicantMapping.foirequestversion_id).label('max_version')
        ).group_by(
            FOIRequestApplicantMapping.foirequest_id
        ).subquery()

        # Get the latest FOIRequest version per foirequestid
        subquery_latest_foirequest_maxversion = _session.query(
            FOIRequest.foirequestid,
            func.max(FOIRequest.version).label('max_version')
        ).group_by(
            FOIRequest.foirequestid
        ).subquery()

        # Get the latest FOIMinistryRequest version per foiministryrequestid
        subquery_ministry_maxversion = _session.query(
            FOIMinistryRequest.foiministryrequestid,
            func.max(FOIMinistryRequest.version).label('max_version')
        ).group_by(
            FOIMinistryRequest.foiministryrequestid
        ).subquery()

        selectedcolumns = [
            FOIRequestApplicant.applicantprofileid.label('applicantprofileid'),
            FOIRequestApplicant.foirequestapplicantid.label('foirequestapplicantid'),
            FOIMinistryRequest.axisrequestid,
            FOIMinistryRequest.filenumber,
            FOIMinistryRequest.foirequest_id,
            FOIMinistryRequest.foiministryrequestid,
            FOIRequestStatus.name.label('requeststatus'),
            func.to_char(FOIRequest.receiveddate, 'MON DD YYYY').label('receiveddate'),
            FOIMinistryRequest.description
        ]

        query_all = _session.query(
            *selectedcolumns
        ).filter(
            # Only include applicants sharing the current profile
            FOIRequestApplicant.foirequestapplicantid.in_(profile_subquery)
        ).join(
            FOIRequestApplicantMapping,
            and_(
                applicant_join_statement,
                FOIRequestApplicantMapping.foirequestapplicantid == FOIRequestApplicant.foirequestapplicantid
            )
        ).join(
            # Only consider the latest mapping version per request
            subquery_latest_mapping,
            and_(
                subquery_latest_mapping.c.foirequest_id == FOIRequestApplicantMapping.foirequest_id,
                subquery_latest_mapping.c.max_version == FOIRequestApplicantMapping.foirequestversion_id
            )
        ).join(
            FOIRequest,
            and_(
                FOIRequest.foirequestid == FOIRequestApplicantMapping.foirequest_id,
                FOIRequest.version == FOIRequestApplicantMapping.foirequestversion_id,
                FOIRequest.isactive == True
            )
        ).join(
            subquery_latest_foirequest_maxversion,
            and_(
                subquery_latest_foirequest_maxversion.c.foirequestid == FOIRequest.foirequestid,
                subquery_latest_foirequest_maxversion.c.max_version == FOIRequest.version
            )
        ).join(
            FOIMinistryRequest,
            and_(
                FOIMinistryRequest.foirequest_id == FOIRequest.foirequestid,
                FOIMinistryRequest.isactive == True
            )
        ).join(
            subquery_ministry_maxversion,
            and_(
                subquery_ministry_maxversion.c.foiministryrequestid == FOIMinistryRequest.foiministryrequestid,
                subquery_ministry_maxversion.c.max_version == FOIMinistryRequest.version
            )
        ).join(
            FOIRequestStatus,
            FOIRequestStatus.requeststatusid == FOIMinistryRequest.requeststatusid
        ).order_by(FOIRequest.foirequestid.desc())

        applicantrequest_schema = ApplicantRequestSchema(many=True)
        print('\n\nQUERY: \n')
        print(query_all.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))

        return applicantrequest_schema.dump(query_all.all())

    @classmethod
    def get_applicant_profile_by_id(cls, foirequestapplicantid):
        query = db.session.query(FOIRequestApplicant).filter_by(foirequestapplicantid=foirequestapplicantid).order_by(FOIRequestApplicant.foirequestapplicantid.desc())
        applicantrequest_schema = ApplicantProfileBaseSchema(many=False)
        return applicantrequest_schema.dump(query.first())

    @classmethod
    def applicants_differ(cls, newapplicant, applicantfromdb, exclude=[]):
        exclude.extend(["foirequestapplicantid", "created_at", "updated_at", "createdby", "updatedby", "applicantprofileid",
                        "request_history", "category", "other_contact_info"])
        exclude = set(exclude or [])
        include = ["firstname", "middlename", "lastname", "alsoknownas",
                   "dob", "email", "businessname", "axisapplicantid", "address", "address_secondary",
                   "city", "province", "postal", "country", "home_phone", "mobile_phone", "work_phone",
                   "alternative_phone", "personal_health_number", "employee_number", "correction_number",
                   "other_notes"]

        mapper = inspect(newapplicant).mapper
        for column in mapper.column_attrs:
            key = column.key
            if key in exclude or key not in include:
                continue
            if getattr(newapplicant, key) != getattr(applicantfromdb, key):
                return True
        return False

    @classmethod
    def get_merged_into_ids(cls, foirequestapplicantids):
        _session = db.session
        result = _session.query(
            FOIRequestApplicant.merged_into_id
        ).filter(
            FOIRequestApplicant.foirequestapplicantid.in_(foirequestapplicantids)
        ).all()
        merged_into_ids = list(set([row[0] for row in result]))
        print('merged_into_ids: ', merged_into_ids)
        return merged_into_ids

    
    @classmethod
    def get_all_merged_ids(cls, applicantid):
        _session = db.session
        # merged_into_id = _session.query(
        #     FOIRequestApplicant.merged_into_id
        # ).filter(
        #     FOIRequestApplicant.foirequestapplicantid == applicantid
        # ).scalar()

        # # If merged_into_id is None, this applicant is the master (or unmerged)
        # master_id = merged_into_id if merged_into_id is not None else applicantid

        # cte = text("""
        #     WITH RECURSIVE merge_group AS (
        #         -- Base case: start with the given applicant
        #         SELECT foirequestapplicantid, merged_into_id
        #         FROM "FOIRequestApplicants"
        #         WHERE foirequestapplicantid = :applicantid

        #         UNION ALL

        #         -- Recursive case: follow merged_into_id up to the master
        #         SELECT a.foirequestapplicantid, a.merged_into_id
        #         FROM "FOIRequestApplicants" a
        #         INNER JOIN merge_group m ON a.foirequestapplicantid = m.merged_into_id
        #     )
        #     SELECT foirequestapplicantid FROM merge_group
        # """)
        applicantprofileid = cls.get_applicantprofileid_from_foirequestapplicantid(applicantid)
        print('applicantprofileid: ', applicantprofileid)
        cte = text("""
            SELECT applicantprofileid
            FROM "FOIRequestApplicants"
            WHERE merged_into_id = COALESCE(
                (SELECT merged_into_id 
                FROM "FOIRequestApplicants" 
                WHERE applicantprofileid = :applicantprofileid
                ORDER BY foirequestapplicantid DESC
                LIMIT 1),
                :applicantprofileid
            )
            OR applicantprofileid = COALESCE(
                (SELECT merged_into_id 
                FROM "FOIRequestApplicants" 
                WHERE applicantprofileid = :applicantprofileid
                ORDER BY foirequestapplicantid DESC
                LIMIT 1),
                :applicantprofileid
            )
        """)

        result = _session.execute(cte, {"applicantprofileid": applicantprofileid}).fetchall()
        all_applicant_ids = list(set([row[0] for row in result]))
        print('all_applicant_ids: ', all_applicant_ids)
        return all_applicant_ids

        # Get all applicant ids in the merge group
        applicantids = _session.query(
            FOIRequestApplicant.foirequestapplicantid
        ).filter(
            or_(
                (FOIRequestApplicant.foirequestapplicantid.in_(all_applicant_ids)),
                (FOIRequestApplicant.merged_into_id.in_(all_applicant_ids))
            )
        ).all()

        applicantids = [row.foirequestapplicantid for row in applicantids]
        return applicantids
    
    @classmethod
    def get_all_applicantprofileids(cls, foirequestapplicantids):
        _session = db.session
        # Get all profile_ids for the given applicant ids (excluding nulls)
        profile_ids = _session.query(
            FOIRequestApplicant.applicantprofileid
        ).filter(
            FOIRequestApplicant.foirequestapplicantid.in_(foirequestapplicantids),
            FOIRequestApplicant.applicantprofileid.isnot(None)
        ).distinct().all()

        profile_ids = [row.applicantprofileid for row in profile_ids]
        return profile_ids

    @classmethod
    def merge_applicant_profiles(cls, primaryid, foirequestapplicantids):
        _session = db.session
        applicant_profile_ids = cls.get_all_applicantprofileids(foirequestapplicantids)
        primary_applicantprofileid = cls.get_all_applicantprofileids([primaryid])
        merged_into_ids = cls.get_merged_into_ids(foirequestapplicantids)

        print('\napplicant_profile_ids: ', applicant_profile_ids)
        print('\nprimary_applicantprofileid: ', primary_applicantprofileid)
        print('\nprimary_applicantprofileid[0]: ', primary_applicantprofileid[0])
        print('\nmerged_into_ids in merge_applicant_profiles: ', merged_into_ids)

        # Merge selected profiles
        merged_profile_count = _session.query(FOIRequestApplicant).filter(
            FOIRequestApplicant.foirequestapplicantid.in_(foirequestapplicantids)
        ).update(
            {"merged_into_id": primary_applicantprofileid[0], "is_active": False}, 
            synchronize_session=False
        )
        print('merged_profile_count: ', merged_profile_count)

        # Update the profiles for retrieved merged_into_ids
        # First get the highest foirequestapplicantid for each applicantprofileid from merged_into_ids
        applicantprofileids_subquery = _session.query(
            func.max(FOIRequestApplicant.foirequestapplicantid)
        ).filter(
            FOIRequestApplicant.applicantprofileid.in_(merged_into_ids)
        ).group_by(
            FOIRequestApplicant.applicantprofileid
        ).subquery()

        # Then update the relevant profiles
        merged_into_ids_update_count = _session.query(FOIRequestApplicant).filter(
            FOIRequestApplicant.foirequestapplicantid.in_(applicantprofileids_subquery)
        ).update(
            {"merged_into_id": primary_applicantprofileid[0], "is_active": False}, 
            synchronize_session=False
        )
        print('merged_into_ids_update_count: ', merged_into_ids_update_count)

        # Deactivate all applicantprofileids that have been merged
        all_applicantprofileids = applicant_profile_ids + merged_into_ids
        id_subquery = _session.query(
            FOIRequestApplicant.foirequestapplicantid
        ).filter(
            FOIRequestApplicant.applicantprofileid.in_(all_applicantprofileids)
        ).subquery()

        deactivated_profile_count = _session.query(FOIRequestApplicant).filter(
            FOIRequestApplicant.foirequestapplicantid.in_(id_subquery)
        ).update(
            {"is_active": False}, 
            synchronize_session=False
        )
        print('deactivated_profile_count: ', deactivated_profile_count)
        
        _session.commit()
        return all_applicantprofileids

class FOIRequestApplicantSchema(ma.Schema):
    class Meta:
        fields = ('foirequestapplicantid','firstname','middlename','lastname','alsoknownas','dob','businessname','applicantprofileid',
                  'axisapplicantid', 'email', 'category', 'address', 'address_secondary', 'city', 'province', 'postal', 'country',
                  'home_phone', 'mobile_phone', 'work_phone', 'alternative_phone', 'other_contact_info', 'personal_health_number',
                  'employee_number', 'correction_number', 'other_notes', 'section43_info', 'request_history')

class ApplicantProfileCompositeSchema(ma.Schema): # For profiles with data derived from multiple tables
    class Meta:
        fields = ('applicantprofileid','updatedat','createdby','foirequestapplicantid','firstname','middlename','lastname',
                  'alsoknownas','dob','businessname','foirequestid','foirequestversion','requesttype','applicantcategory',
                  'email','address','address2','city','province','postal','country','homephone','workphone',
                  'workphone2','mobilephone','othercontactinfo','employeenumber','correctionnumber','phn','axisapplicantid','other_notes')

class ApplicantRequestSchema(ma.Schema):
    class Meta:
        fields = ('applicantprofileid','foirequestapplicantid','axisrequestid','foirequest_id','foiministryrequestid','filenumber', 'requeststatus','receiveddate','description')

class ApplicantProfileBaseSchema(ma.Schema): # For profiles with data solely from FOIRequestApplicants table
    address2 = fields.String(attribute="address_secondary")
    foirequestapplicantid = fields.Integer(attribute="foirequestapplicantid")
    homephone = fields.String(attribute="home_phone")
    mobilephone = fields.String(attribute="mobile_phone")
    workphone = fields.String(attribute="work_phone")
    workphone2 = fields.String(attribute="alternative_phone")
    othercontactinfo = fields.String(attribute="other_contact_info")
    phn = fields.String(attribute="personal_health_number")
    employeenumber = fields.String(attribute="employee_number")
    correctionnumber = fields.String(attribute="correction_number")
    section43_info = fields.String(attribute="section43_info")
    requestHistory = fields.Dict(attribute="request_history")
    applicantcategory = fields.String(attribute="category")
    dob = fields.Date(format="%Y-%m-%d")

    class Meta:
        fields = (
            "applicantprofileid",
            "foirequestapplicantid",
            "axisapplicantid",
            "applicantcategory",
            "lastname",
            "firstname",
            "middlename",
            "address",
            "address2",
            "city",
            "province",
            "country",
            "postal",
            "homephone",
            "mobilephone",
            "workphone",
            "workphone2",
            "othercontactinfo",
            "email",
            "businessname",
            "dob",
            "phn",
            "alsoknownas",
            "employeenumber",
            "correctionnumber",
            "other_notes",
            "section43_info",
            "requestHistory"
        )