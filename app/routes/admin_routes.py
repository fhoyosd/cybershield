from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from app.utils.decorators import role_required
from app.models.user_model import UserModel
from app.models.incident_model import IncidentModel
from app.models.audit_model import AuditModel
from app.models.evidence_model import EvidenceModel

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@role_required('admin')
def dashboard():
    incidents = IncidentModel.list_all(limit=5)
    users = UserModel.list_users(limit=5)
    audits = AuditModel.list_all(limit=5)
    return render_template('admin/dashboard.html', incidents=incidents, users=users, audits=audits)

@admin_bp.route('/users')
@role_required('admin')
def users():
    users = UserModel.list_users(limit=1000)
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@role_required('admin')
def users_create():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        phone = request.form.get('phone')
        role = request.form.get('role') or 'user'

        ok, msg = UserModel.create_user(username=username, email=email, password=password, fullname=fullname, phone=phone, role=role)
        AuditModel.log(actor=session.get('username'), action="create_user", target_type="user", target_id=username, detail=msg)
        flash(msg, 'success' if ok else 'error')
        return redirect(url_for('admin.users'))
    return render_template('admin/create_user.html')

@admin_bp.route('/users/change-role', methods=['POST'])
@role_required('admin')
def users_change_role():
    username = request.form.get('username')
    new_role = request.form.get('role')
    ok, msg = UserModel.change_role(username, new_role)
    AuditModel.log(actor=session.get('username'), action="change_role", target_type="user", target_id=username, detail=new_role)
    flash(msg, 'success' if ok else 'error')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/delete', methods=['POST'])
@role_required('admin')
def users_delete():
    username = request.form.get('username')
    col = UserModel.collection()
    res = col.delete_one({"username": username})
    msg = "Usuario eliminado correctamente." if res.deleted_count else "Usuario no encontrado."
    AuditModel.log(actor=session.get('username'), action="delete_user", target_type="user", target_id=username, detail=msg)
    flash(msg, 'success' if res.deleted_count else 'error')
    return redirect(url_for('admin.users'))

@admin_bp.route('/incidents')
@role_required('admin')
def incidents():
    f_type = request.args.get('category')
    f_status = request.args.get('status')
    query = {}
    if f_type:
        query['category'] = f_type
    if f_status:
        query['status'] = f_status
    incidents = IncidentModel.list_all(filters=query if query else None)
    return render_template('admin/incidents.html', incidents=incidents)

@admin_bp.route('/incidents/create', methods=['GET','POST'])
@role_required('admin')
def incidents_create():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        severity = request.form.get('severity')
        creator = session.get('username')
        inc_id = IncidentModel.create(title, description, category, severity, creator)
        AuditModel.log(actor=creator, action="create_incident", target_type="incident", target_id=inc_id, detail=title)
        flash("Incidente creado correctamente.", 'success')
        return redirect(url_for('admin.incidents'))
    return render_template('admin/create_incident.html')

@admin_bp.route('/incidents/view/<id>')
@role_required('admin')
def incidents_view(id):
    inc = IncidentModel.get_by_id(id)
    evidences = EvidenceModel.list_all(incident_id=id)
    return render_template('admin/view_incident.html', incident=inc, evidences=evidences)

@admin_bp.route('/incidents/edit/<id>', methods=['GET','POST'])
@role_required('admin')
def incidents_edit(id):
    inc = IncidentModel.get_by_id(id)
    if not inc:
        flash("Incidente no encontrado.", 'error')
        return redirect(url_for('admin.incidents'))
    if request.method == 'POST':
        updates = {}
        title = request.form.get('title')
        description = request.form.get('description')
        assigned_to = request.form.get('assigned_to')
        status = request.form.get('status')
        if title: updates['title'] = title
        if description: updates['description'] = description
        if assigned_to is not None: updates['assigned_to'] = assigned_to
        if status: updates['status'] = status
        ok = IncidentModel.update(id, updates, actor=session.get('username'), note="Actualización desde el panel admin")
        AuditModel.log(actor=session.get('username'), action="edit_incident", target_type="incident", target_id=id, detail=str(updates))
        flash("Incidente actualizado." if ok else "No se pudo actualizar.", 'success' if ok else 'error')
        return redirect(url_for('admin.incidents_view', id=id))
    return render_template('admin/edit_incident.html', incident=inc)

@admin_bp.route('/incidents/delete/<id>', methods=['POST'])
@role_required('admin')
def incidents_delete(id):
    ok = IncidentModel.delete(id)
    AuditModel.log(actor=session.get('username'), action="delete_incident", target_type="incident", target_id=id, detail="deleted" if ok else "not found")
    flash("Incidente eliminado." if ok else "No se pudo eliminar.", 'success' if ok else 'error')
    return redirect(url_for('admin.incidents'))

@admin_bp.route('/evidences')
@role_required('admin')
def evidences():
    inc_id = request.args.get('incident_id')
    evids = EvidenceModel.list_all(incident_id=inc_id)
    return render_template('admin/evidences.html', evidences=evids)

@admin_bp.route('/evidences/add', methods=['POST'])
@role_required('admin')
def evidences_add():
    incident_id = request.form.get('incident_id')
    filename = request.form.get('filename')
    url = request.form.get('url')
    uploader = session.get('username')
    eid = EvidenceModel.add(incident_id, filename, url, uploader)
    AuditModel.log(actor=uploader, action="add_evidence", target_type="evidence", target_id=eid, detail=filename)
    flash("Evidencia agregada.", 'success')
    return redirect(url_for('admin.evidences', incident_id=incident_id))

@admin_bp.route('/evidences/delete', methods=['POST'])
@role_required('admin')
def evidences_delete():
    evidence_id = request.form.get('evidence_id')
    ok = EvidenceModel.delete(evidence_id)
    AuditModel.log(actor=session.get('username'), action="delete_evidence", target_type="evidence", target_id=evidence_id, detail="deleted" if ok else "not found")
    flash("Evidencia eliminada." if ok else "No se pudo eliminar.", 'success' if ok else 'error')
    return redirect(request.referrer or url_for('admin.evidences'))

@admin_bp.route('/audits')
@role_required('admin')
def audits():
    audits = AuditModel.list_all(limit=1000)
    return render_template('admin/audits.html', audits=audits)
