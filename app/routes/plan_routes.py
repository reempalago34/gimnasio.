from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models.plan import Plan
from app import db

bp = Blueprint('plan_routes', __name__, url_prefix='/planes')

@bp.route('/')
@login_required
def index():
    planes = Plan.query.all()
    return render_template('planes/index.html', planes=planes)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    from flask_login import current_user
    if current_user.rol not in ['admin', 'recepcionista']:
        flash('No tienes permisos para agregar planes.', 'danger')
        return redirect(url_for('plan_routes.index'))
    if request.method == 'POST':
        nombrePlan = request.form['nombrePlan']
        precio = request.form['precio']
        duracionMeses = request.form['duracionMeses']
        
        nuevo_plan = Plan(nombrePlan=nombrePlan, precio=precio, duracionMeses=duracionMeses)
        nuevo_plan.save()
        flash('Plan registrado con éxito', 'success')
        return redirect(url_for('plan_routes.index'))
        
    return render_template('planes/add.html')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    from flask_login import current_user
    if current_user.rol not in ['admin', 'recepcionista']:
        flash('No tienes permisos para editar planes.', 'danger')
        return redirect(url_for('plan_routes.index'))
    plan = Plan.query.get_or_404(id)
    if request.method == 'POST':
        plan.nombrePlan = request.form['nombrePlan']
        plan.precio = request.form['precio']
        plan.duracionMeses = request.form['duracionMeses']
        db.session.commit()
        flash('Plan actualizado con éxito', 'success')
        return redirect(url_for('plan_routes.index'))
        
    return render_template('planes/edit.html', plan=plan)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    from flask_login import current_user
    if current_user.rol not in ['admin', 'recepcionista']:
        flash('No tienes permisos para borrar planes.', 'danger')
        return redirect(url_for('plan_routes.index'))
    plan = Plan.query.get_or_404(id)
    db.session.delete(plan)
    db.session.commit()
    flash('Plan eliminado con éxito', 'success')
    return redirect(url_for('plan_routes.index'))
