from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.models.incident_model import IncidentModel
from app.models.evidence_model import EvidenceModel
from app.models.audit_model import AuditModel

analyst_bp = Blueprint('analyst', __name__, url_prefix = '/analyst')

@analyst_bp.route('/')
@role_required('analyst', 'admin')
def dashboard():
    username = current_user.username
    assigned = IncidentModel.list_all(filters = {"assigned_to": username}, limit = 10)
    recent = IncidentModel.list_all(limit = 10)
    audits = AuditModel.list_all(limit = 5)
    return render_template('analyst/dash.html', assigned = assigned, recent = recent, audits = audits)

@analyst_bp.route('/incidents')
@role_required('analyst', 'admin')
def incidents():
    view = request.args.get('view', 'assigned')
    username = current_user.username
    if view == 'all':
        incidents = IncidentModel.list_all()
    else:
        incidents = IncidentModel.list_all(filters = {"assigned_to": username})
    return render_template('analyst/incidents.html', incidents = incidents, view = view)

@analyst_bp.route('/incidents/<incident_id>')
@role_required('analyst', 'admin')
def incident_view(incident_id):
    inc = IncidentModel.get_by_id(incident_id)
    if not inc:
        flash("Incidente no encontrado.", "error")
        return redirect(url_for('analyst.incidents'))
    evidences = EvidenceModel.list_all(incident_id = incident_id)
    return render_template('analyst/view_incident.html', incident = inc, evidences = evidences)

@analyst_bp.route('/incidents/<incident_id>/edit', methods = ['GET', 'POST'])
@role_required('analyst', 'admin')
def incident_edit(incident_id):
    inc = IncidentModel.get_by_id(incident_id)
    if not inc:
        flash("Incidente no encontrado.", "error")
        return redirect(url_for('analyst.incidents'))

    if request.method == 'POST':
        new_status = request.form.get('status')
        note = request.form.get('note')
        assign_self = request.form.get('assign_self') == 'on'

        updates = {}
        if new_status:
            updates['status'] = new_status
        if assign_self:
            updates['assigned_to'] = current_user.username

        ok = IncidentModel.update(incident_id, updates, actor=current_user.username, note = note if note else "Actualizado por analista")
        AuditModel.log(actor = current_user.username, action = "edit_incident", target_type = "incident", target_id = incident_id, detail = str(updates) + ("; note: " + (note or "")))
        flash("Incidente actualizado correctamente." if ok else "No se pudo actualizar el incidente.", "success" if ok else "error")
        return redirect(url_for('analyst.incident_view', incident_id = incident_id))

    return render_template('analyst/edit_incident.html', incident = inc)

@analyst_bp.route('/incidents/<incident_id>/evidence/add', methods = ['POST'])
@role_required('analyst', 'admin')
def evidence_add(incident_id):
    filename = request.form.get('filename')
    url = request.form.get('url')
    uploader = current_user.username

    if not filename and not url:
        flash("Debes proporcionar un nombre de archivo o una URL.", "error")
        return redirect(url_for('analyst.incident_view', incident_id = incident_id))

    eid = EvidenceModel.add(incident_id, filename or url.split('/')[-1], url or "", uploader)
    AuditModel.log(actor = uploader, action = "add_evidence", target_type = "evidence", target_id = eid, detail = f"Added by {uploader}")
    flash("Evidencia agregada correctamente.", "success")
    return redirect(url_for('analyst.incident_view', incident_id = incident_id))

@analyst_bp.route('/evidences')
@role_required('analyst', 'admin')
def evidences():
    incident_id = request.args.get('incident_id')
    evids = EvidenceModel.list_all(incident_id = incident_id) if incident_id else EvidenceModel.list_all()
    return render_template('analyst/evidences.html', evidences = evids)
