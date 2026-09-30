// Interfaz del modelo de demostración. Sin autenticación productiva ni servidor.
'use strict';
const KEY='hotelDuermeBienTema6V4';
let data=JSON.parse(localStorage.getItem(KEY)||'null')||Hotel.seed(),currentUser=null,view='acceso',editRoom=null,editReservation=null,editUser=null,quoteSignature=null;
const titles={acceso:'Acceso',disponibilidad:'Disponibilidad',habitaciones:'Habitaciones',huespedes:'Huéspedes',reservas:'Reservas',checkin:'Check-in',checkout:'Check-out',informes:'Informes',usuarios:'Usuarios'};
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money=n=>'$'+Number(n).toLocaleString('es-CL')+' CLP';
const today=()=>new Date().toLocaleDateString('sv-SE');
const tomorrow=()=>{let d=new Date();d.setDate(d.getDate()+1);return d.toLocaleDateString('sv-SE')};
const full=h=>h?h.nombres+' '+h.apellidos:'—';
const roomName=id=>data.habitaciones.find(h=>h.id===id)?.numero||'—';
const guestName=id=>full(data.huespedes.find(h=>h.id===id));
const opt=(a,value,label,selected)=>a.map(x=>`<option value="${esc(value(x))}" ${String(value(x))===String(selected)?'selected':''}>${esc(label(x))}</option>`).join('');
const field=(label,name,type='text',value='',extra='')=>`<label>${label}<input name="${name}" type="${type}" value="${esc(value)}" ${extra} required></label>`;
const select=(label,name,options,extra='')=>`<label>${label}<select name="${name}" ${extra}>${options}</select></label>`;
const form=(id,heading,fields,submit)=>`<form id="${id}" class="card form-card"><h3>${heading}</h3>${fields}<button class="primary-btn">${submit}</button><p role="status" class="message" id="${id}Message"></p></form>`;
const table=(heads,rows)=>`<div class="table-wrap"><table><thead><tr>${heads.map(h=>`<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.length?rows.map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join('')}</tr>`).join(''):`<tr><td colspan="${heads.length}">Sin registros</td></tr>`}</tbody></table></div>`;
const btn=(label,action,id)=>`<button type="button" data-action="${action}" data-id="${id}">${label}</button>`;
const span=s=>`<span class="status">${esc(s)}</span>`;
function save(){localStorage.setItem(KEY,JSON.stringify(data))}
function feedback(id,t,ok=false){let e=document.querySelector('#'+id+'Message')||document.querySelector('#globalMessage');e.textContent=t;e.className='message '+(ok?'ok':'error')}
function role(){return data.roles.find(r=>r.id===data.usuarios.find(u=>u.id===currentUser)?.rolId)?.nombre}
function allowed(v){return v==='acceso'||Hotel.perms[role()]?.includes(v)}
function render(){
 quoteSignature=null;
 if(!allowed(view))view='acceso';
 document.querySelector('#nav').innerHTML=Object.entries(titles).filter(([key])=>allowed(key)).map(([key,t])=>`<button class="nav-btn ${view===key?'active':''}" data-view="${key}">${t}</button>`).join('');
 document.querySelector('#session').textContent=currentUser?data.usuarios.find(u=>u.id===currentUser)?.nombre+' · '+role():'Sin sesión';
 document.querySelector('#pageTitle').textContent=titles[view];let content='';
 if(view==='acceso')content=form('loginForm','Sesión de demostración',select('Usuario de ejemplo','userId',opt(data.usuarios.filter(u=>u.activo),u=>u.id,u=>u.nombre+' · '+data.roles.find(r=>r.id===u.rolId).nombre,currentUser)),'Entrar');
 if(view==='disponibilidad'){
  let occupied=data.habitaciones.filter(h=>Hotel.occupied(data,h.id)).length;
  content=`<div class="stats"><article class="stat-card"><span>Habitaciones</span><strong>${data.habitaciones.length}</strong></article><article class="stat-card"><span>Ocupadas ahora</span><strong>${occupied}</strong></article><article class="stat-card"><span>Disponibles ahora</span><strong>${data.habitaciones.length-occupied}</strong></article><article class="stat-card"><span>Reservas vigentes</span><strong>${data.reservas.filter(r=>r.estado==='REGISTRADA').length}</strong></article></div>`+form('availabilityForm','Consultar por fechas y capacidad',field('Entrada','entrada','date',today())+field('Salida','salida','date',tomorrow())+field('Pasajeros','cantidad','number',1,'min="1" step="1"'),'Consultar')+'<section class="card" id="availableResult">'+table(['Habitación','Capacidad','Orientación','Ocupación actual'],data.habitaciones.map(h=>[esc(h.numero),h.capacidad,esc(h.orientacion),span(Hotel.occupied(data,h.id)?'OCUPADA':'DISPONIBLE')]))+'</section>';
 }
 if(view==='habitaciones'){
  const h=data.habitaciones.find(h=>h.id===editRoom);
  content='<div class="two-col">'+form('roomForm',h?'Editar habitación':'Registrar habitación',field('Número','numero','text',h?.numero||'')+field('Capacidad','capacidad','number',h?.capacidad||2,'min="1" step="1"')+field('Orientación','orientacion','text',h?.orientacion||'Norte'),'Guardar')+'<section class="card">'+table(['Número','Capacidad','Orientación','Acción'],data.habitaciones.map(h=>[esc(h.numero),h.capacidad,esc(h.orientacion),btn('Editar','edit-room',h.id)]))+'</section></div>';
 }
 if(view==='huespedes')content='<div class="two-col">'+form('guestForm','Registrar huésped',field('Identificación','identificacion')+field('Nombres','nombres')+field('Apellidos','apellidos'),'Guardar huésped')+'<section class="card">'+table(['Identificación','Nombres','Apellidos'],data.huespedes.map(h=>[esc(h.identificacion),esc(h.nombres),esc(h.apellidos)]))+'</section></div>';
 if(view==='reservas'){
  const r=data.reservas.find(r=>r.id===editReservation);
  content=form('reservationForm',r?'Modificar reserva #'+r.id:'Registrar reserva',select('Titular','titularId',opt(data.huespedes,h=>h.id,h=>full(h),r?.titularId))+select('Habitación','habitacionId',opt(data.habitaciones,h=>h.id,h=>'Habitación '+h.numero+' · '+h.capacidad+' pasajeros',r?.habitacionId))+field('Entrada','entrada','date',r?.entrada||today())+field('Salida','salida','date',r?.salida||tomorrow())+field('Cantidad de pasajeros','cantidad','number',r?.cantidad||1,'min="1" step="1"'),'Guardar reserva')+'<section class="card">'+table(['Reserva','Titular','Hab.','Fechas','Pasajeros','Estado','Acciones'],data.reservas.map(r=>['#'+r.id,esc(guestName(r.titularId)),esc(roomName(r.habitacionId)),esc(r.entrada)+' → '+esc(r.salida),r.cantidad,span(r.estado),r.estado==='REGISTRADA'?btn('Modificar','edit-reservation',r.id)+' '+btn('Cancelar','cancel-reservation',r.id):'—']))+'</section>';
 }
 if(view==='checkin')content=form('checkinForm','Asignar habitación y pasajeros',select('Origen','reservaId','<option value="">Sin reserva</option>'+opt(data.reservas.filter(r=>r.estado==='REGISTRADA'),r=>r.id,r=>'Reserva #'+r.id+' · Hab. '+roomName(r.habitacionId)+' · '+r.cantidad+' pasajeros'))+select('Habitación','habitacionId',opt(data.habitaciones,h=>h.id,h=>'Hab. '+h.numero+' · Capacidad '+h.capacidad))+field('Entrada','entrada','date',today())+field('Salida prevista','salida','date',tomorrow())+`<fieldset><legend>Identificar a todos los pasajeros</legend>${data.huespedes.map(h=>`<label class="check"><input type="checkbox" name="huespedIds" value="${h.id}">${esc(full(h))} · ${esc(h.identificacion)}</label>`).join('')}</fieldset>`,'Confirmar check-in')+'<section class="card">'+table(['Estadía','Habitación','Pasajeros','Entrada','Salida prevista'],data.estadias.filter(s=>s.estado==='ACTIVA').map(s=>['#'+s.id,esc(roomName(s.habitacionId)),data.participaciones.filter(p=>p.estadiaId===s.id).map(p=>esc(guestName(p.huespedId))).join('<br>'),esc(s.entrada),esc(s.salidaPrevista)]))+'</section>';
 if(view==='checkout')content=form('checkoutForm','Calcular cuenta y confirmar salida',select('Estadía activa','estadiaId',opt(data.estadias.filter(s=>s.estado==='ACTIVA'),s=>s.id,s=>'Estadía #'+s.id+' · Hab. '+roomName(s.habitacionId)))+field('Fecha de salida','salida','date',tomorrow())+field('Tarifa de demostración por pasajero y noche (CLP)','tarifaCLP','number','','min="0" step="1"')+'<button type="button" data-action="quote">Calcular cuenta</button><div id="quoteResult" aria-live="polite"></div><label class="check"><input name="confirmado" type="checkbox" required>Revisé la cuenta y confirmo la salida</label>','Confirmar check-out')+'<section class="card"><h3>Historial de cuentas</h3>'+table(['Estadía','Pasajero','Tarifa CLP','Noches','Costo CLP'],data.participaciones.filter(p=>p.costoCLP!==null).map(p=>['#'+p.estadiaId,esc(guestName(p.huespedId)),money(p.tarifaCLP),data.estadias.find(s=>s.id===p.estadiaId).nochesCobradas,money(p.costoCLP)]))+'</section>';
 if(view==='usuarios'){
  const u=data.usuarios.find(u=>u.id===editUser);
  content='<div class="two-col">'+form('userForm',u?'Editar usuario':'Registrar usuario',field('Nombre de usuario','nombre','text',u?.nombre||'')+select('Perfil','rolId',opt(data.roles,r=>r.id,r=>r.nombre,u?.rolId))+(u?'<label class="check"><input type="checkbox" name="activo" '+(u.activo?'checked':'')+'>Activo</label>':''),'Guardar usuario')+'<section class="card">'+table(['Usuario','Perfil','Estado','Acción'],data.usuarios.map(u=>[esc(u.nombre),esc(data.roles.find(r=>r.id===u.rolId).nombre),u.activo?'Activo':'Inactivo',btn('Editar','edit-user',u.id)]))+'</section></div>';
 }
 if(view==='informes')content=form('reportForm','Ocupación y reservas por período',field('Desde','entrada','date',today())+field('Hasta (exclusiva)','salida','date',tomorrow()),'Generar informes')+'<div id="reportResult"></div>';
 document.querySelector('#view').innerHTML=content;
}
function quote(){const f=document.querySelector('#checkoutForm');const v=Object.fromEntries(new FormData(f));const q=Hotel.quote(data,v.estadiaId,v.salida,v.tarifaCLP);document.querySelector('#quoteResult').innerHTML=table(['Pasajero','Noches','Costo CLP'],q.filas.map(p=>[esc(guestName(p.huespedId)),q.noches,money(p.costoCLP)]))+`<p><strong>Total: ${money(q.total)}</strong></p>`;quoteSignature=JSON.stringify([v.estadiaId,v.salida,v.tarifaCLP]);return q}
document.addEventListener('click',e=>{
 const nav=e.target.closest('[data-view]');if(nav){view=nav.dataset.view;editRoom=editReservation=editUser=null;render();return}
 const b=e.target.closest('[data-action]');if(!b)return;try{
  const id=Number(b.dataset.id);switch(b.dataset.action){
   case 'edit-room':Hotel.authorize(data,currentUser,'habitaciones');editRoom=id;render();break;
   case 'edit-reservation':Hotel.authorize(data,currentUser,'reservas');editReservation=id;render();break;
   case 'edit-user':Hotel.authorize(data,currentUser,'usuarios');editUser=id;render();break;
   case 'cancel-reservation':if(!window.confirm('¿Cancelar la reserva #'+id+'? Se conservará su historial.'))break;Hotel.cancel(data,currentUser,id);save();render();feedback('global','Reserva cancelada. Se liberó su disponibilidad.',true);break;
   case 'quote':quote();break;
  }
 }catch(err){feedback(b.dataset.action==='quote'?'checkoutForm':'global',err.message)}
});
document.addEventListener('input',e=>{if(e.target.form?.id==='checkoutForm'&&e.target.name!=='confirmado'){quoteSignature=null;document.querySelector('#quoteResult').innerHTML='';e.target.form.elements.confirmado.checked=false}});
document.addEventListener('change',e=>{
 if(e.target.form?.id==='checkoutForm'&&e.target.name!=='confirmado'){quoteSignature=null;document.querySelector('#quoteResult').innerHTML='';e.target.form.elements.confirmado.checked=false}
 if(e.target.name==='reservaId'){
  const r=data.reservas.find(r=>r.id===Number(e.target.value));const f=e.target.form;
  ['habitacionId','entrada','salida'].forEach(k=>{if(r)f.elements[k].value=k==='salida'?r.salida:r[k];f.elements[k].disabled=!!r});
 }
});
document.addEventListener('submit',e=>{
 e.preventDefault();const id=e.target.id;let v=Object.fromEntries(new FormData(e.target));try{
  if(id==='loginForm'){const u=data.usuarios.find(u=>u.id===Number(v.userId)&&u.activo);if(!u)throw Error('Seleccione un usuario activo.');currentUser=u.id;view='disponibilidad';render();return}
  if(id==='availabilityForm'){Hotel.authorize(data,currentUser,'disponibilidad');const rooms=Hotel.available(data,v.entrada,v.salida,v.cantidad);document.querySelector('#availableResult').innerHTML=table(['Habitación','Capacidad','Orientación'],rooms.map(h=>[esc(h.numero),h.capacidad,esc(h.orientacion)]));feedback(id,rooms.length+' habitación(es) disponibles.',true);return}
  if(id==='roomForm'){Hotel.room(data,currentUser,{...v,id:editRoom});editRoom=null}
  if(id==='guestForm')Hotel.guest(data,currentUser,v);
  if(id==='reservationForm'){Hotel.reservation(data,currentUser,{...v,id:editReservation});editReservation=null}
  if(id==='checkinForm')Hotel.checkin(data,currentUser,{...v,huespedIds:new FormData(e.target).getAll('huespedIds')});
  if(id==='checkoutForm'){if(quoteSignature!==JSON.stringify([v.estadiaId,v.salida,v.tarifaCLP]))throw Error('Calcule y revise la cuenta antes de confirmar la salida.');Hotel.checkout(data,currentUser,{...v,confirmado:v.confirmado==='on'})}
  if(id==='userForm'){Hotel.user(data,currentUser,{...v,id:editUser,activo:editUser?v.activo==='on':true});editUser=null}
  if(id==='reportForm'){
   Hotel.authorize(data,currentUser,'informes');const result=Hotel.reports(data,v.entrada,v.salida);
   document.querySelector('#reportResult').innerHTML='<section class="card"><h3>Ocupación durante el período</h3>'+table(['Estadía','Hab.','Entrada','Salida','Pasajeros','Estado'],result.estadias.map(s=>['#'+s.id,esc(roomName(s.habitacionId)),s.entrada,s.salidaReal||s.salidaPrevista,data.participaciones.filter(p=>p.estadiaId===s.id).length,span(s.estado)]))+'</section><section class="card"><h3>Reservas durante el período</h3>'+table(['Reserva','Titular','Habitación','Entrada','Salida','Estado'],result.reservas.map(r=>['#'+r.id,esc(guestName(r.titularId)),esc(roomName(r.habitacionId)),r.entrada,r.salida,span(r.estado)]))+'</section>';return
  }
  save();render();feedback(id,'Operación guardada correctamente.',true);
 }catch(err){feedback(id,err.message)}
});
save();render();
