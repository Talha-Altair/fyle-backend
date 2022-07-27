from flask import Blueprint, jsonify
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, GradeEnum, AssignmentStateEnum

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
        return jsonify(error="ValidationError"
        ), 400

    assignment = Assignment.get_assignments_by_id(id)

    assignment_dump = AssignmentSchema().dump(assignment, many=True)

    if not assignment_dump:

        return jsonify(error="FyleError"), 404

    assignment_dump = assignment_dump[0]

    if assignment_dump["state"] is AssignmentStateEnum.DRAFT:

        return jsonify(error="FyleError"), 400

    if assignment_dump["teacher_id"] is not teacher_id:

        return jsonify(error="FyleError"), 400

    Assignment.grade_assignment(_id = id, grade=grade)

    db.session.commit()

    return APIResponse.respond(data=assignment_dump)