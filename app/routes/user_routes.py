from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.models.incident_model import IncidentModel
from app.models.evidence_model import EvidenceModel
from app.models.audit_model import AuditModel

user_bp  =  Blueprint('user', __name__, url_prefix = '/user')

@user_bp.route('/')
@role_required('user')
def dashboard():
    incidents  =  IncidentModel.list_all(filters = {"created_by": current_user.username})
    return render_template('user/dashboard.html', incidents = incidents)

@user_bp.route('/incident/new', methods = ['GET', 'POST'])
@role_required('user')
def incident_new():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        severity = request.form.get('severity')
        description = request.form.get('description')

        if not title or not description:
            flash("El título y la descripción son obligatorios.", "error")
            return redirect(url_for('user.incident_new'))

        incident_id = IncidentModel.create(
            title = title,
            category = category,
            severity = severity,
            description = description,
            created_by = current_user.username
        )

        AuditModel.log(actor = current_user.username, action = "create_incident",
                       target_type = "incident", target_id = incident_id,
                       detail = f"User created new incident: {title}")

        flash("Incidente reportado exitosamente.", "success")
        return redirect(url_for('user.dashboard'))

    return render_template('user/create_incident.html')

@user_bp.route('/incident/<incident_id>')
@role_required('user')
def incident_view(incident_id):
    incident = IncidentModel.get_by_id(incident_id)
    if not incident or incident.get("created_by") !=  current_user.username:
        flash("No tienes acceso a este incidente.", "error")
        return redirect(url_for('user.dashboard'))

    evidences = EvidenceModel.list_all(incident_id = incident_id)
    return render_template('user/view_incident.html', incident = incident, evidences = evidences)

@user_bp.route('/incident/<incident_id>/evidence/add', methods = ['POST'])
@role_required('user')
def evidence_add(incident_id):
    filename = request.form.get('filename')
    url = request.form.get('url')

    if not filename and not url:
        flash("Debes proporcionar un nombre de archivo o una URL.", "error")
        return redirect(url_for('user.incident_view', incident_id = incident_id))

    eid = EvidenceModel.add(
        incident_id = incident_id,
        filename = filename or url.split("/")[-1],
        url = url or "",
        uploaded_by = current_user.username
    )

    AuditModel.log(actor = current_user.username, action = "add_evidence",
                   target_type = "evidence", target_id = eid,
                   detail = f"User added evidence")

    flash("Evidencia añadida correctamente.", "success")
    return redirect(url_for('user.incident_view', incident_id = incident_id))
