from flask import make_response, abort
from config import db
from models import Person, PersonSchema

def read_all():
    """
    creates list of all people
    """
    people = Person.query.order_by(Person.lname).all()

    # serialize data for response
    person_schema = PersonSchema(many=True)
    return person_schema.dump(people).data
        

def read_one(person_id):
    """
    searches through list of people based on name
    """
    person = Person.query.filter(Person.person_id == person_id).one_or_none()

    # if person exists, serialize
    if person is not None:
        person_schema = PersonSchema()
        return person_schema.dump(person).data

    else:
        abort(404, 'Person with id {person_id} not found'.format(person_id=person_id))

def create(person):
    """
    creates a new person object in the PEOPLE structure based on data that is passed in
    """

    lname = person.get('lname')
    fname = person.get('fname')

    # checks if person already exists
    existing_person = Person.query.filter(Person.fname == fname).filter(Person.lname == lname).one_or_none()

    if existing_person is None:
        
        schema = PersonSchema
        new_person = schema.load(person, session=db.session).data

        db.session.add(new_person)
        db.session.commit()

        return schema.dump(new_person).data, 201

    else:
        abort(
            409,
            'Person with last name {lname} already exists'.format(lname=lname)
        )

def update(person_id, person):
    """
    updates an existing person
    """
    update_person = Person.query.filter(
        Person.person_id == person_id
    ).one_or_none()

    fname = person.get('fname')
    lname = person.get('lname')

    existing_person = (
        Person.query.filter(Person.fname == fname)
        .filter(Person.lname == lname)
        .one_or_none()
    )

    if update_person is None:
        abort(
            404,
            "Person with name {lname} not found".format(lname=lname)
        )

    elif existing_person is not None and existing_person.person_id != person_id:
        abort(
            409,
            'Person with name {fname} {lname} already exists'.format(fname=fname, lname=lname),
        )
    # update!
    else:
        schema = PersonSchema()
        update = schema.load(person, session=db.session).data

        update.person_id = update_person.person_id

        db.session.merge(update)
        db.session.commit()

        data = schema.dump(update_person).data

        return data, 200

def delete(person_id):
    """
    yeets a person from the structure
    """
    person = Person.query.filter(Person.person_id == person_id).one_or_none()

    if person is not None:
        db.session.delete(person)
        db.session.commit()
        return make_response('Person {person_id} deleted').format(person_id=person_id), 200

    else:
        abort(
            404,
            "Person with id {person_id} not found".format(person_id=person_id),
        )