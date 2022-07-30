from email import message
from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.libs.exceptions import FyleError
from core.models.assignments import Assignment, GradeEnum, AssignmentStateEnum
from marshmallow.exceptions import ValidationError

from .schema import AssignmentSchema, GradeSubmitSchema
teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)


@teacher_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.auth_principal
def list_assignments(p):
    """Returns list of assignments per Teacher"""
    teachers_assignments = Assignment.get_assignments_by_teacher(p.teacher_id)
    teachers_assignments_dump = AssignmentSchema().dump(teachers_assignments, many=True)
    return APIResponse.respond(data=teachers_assignments_dump)

@teacher_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.auth_principal
def grade_assignment(p, incoming_payload):
    """Grade ASsignement By ID"""
    payload = GradeSubmitSchema().load(incoming_payload)

    teacher_id = p.teacher_id

    id = str(payload.id)

    try:
        grade = GradeEnum(payload.grade).name
    except:
        raise ValidationError(
            message = "Invalid Grade"
        )

    assignment = Assignment.get_assignments_by_id(id)

    assignment_dump = AssignmentSchema().dump(assignment, many=True)

    if not assignment_dump:

        raise FyleError(
            status_code=404,
            message="Assignment Not found")

    assignment_dump = assignment_dump[0]

    assignment_dump['grade'] = grade

    if assignment_dump["state"] is AssignmentStateEnum.DRAFT:

        raise FyleError(
            status_code=400,
            message="Only Draft Assignments can be submitted")

    if assignment_dump["teacher_id"] is not teacher_id:

        raise FyleError(
            status_code=400,
            message="Only the Correct Teacher can Grade the Assignment")

    Assignment.grade_assignment(_id = id, grade=grade)

    db.session.commit()

    return APIResponse.respond(data=assignment_dump)