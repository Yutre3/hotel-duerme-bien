// Adaptado de Yutre3/diego para el nuevo proyecto académico.
// Demostración local: los perfiles y tarifas de prueba no son reglas confirmadas del hotel.
const KEY='hotelDuermeBienTema6V3';
const $=s=>document.querySelector(s);
const $$=s=>[...document.querySelectorAll(s)];
const uid=a=>a.length?Math.max(...a.map(x=>x.id))+1:1;

function seed(){
  if(localStorage.getItem(KEY)) return;
  localStorage.setItem(KEY,JSON.stringify({
    habitaciones:[
      {id:1,numero:'201',capacidad:2,orientacion:'Norte',estado:'DISPONIBLE'},
      {id:2,numero:'202',capacidad:2,orientacion:'Sur',estado:'DISPONIBLE'},
      {id:3,numero:'305',capacidad:3,orientacion:'Este',estado:'DISPONIBLE'}
    ],
    huespedes:[{id:1,nombre:'Huésped de prueba'}],
    usuarios:[
      {id:1,nombre:'Administrador demo',rol:'Administrador'},
      {id:2,nombre:'Encargado demo',rol:'Encargado de hotel'}
    ],
    reservas:[],
    estadias:[]
  }));
}
function db(){
  seed();
  const data=JSON.parse(localStorage.getItem(KEY))||{};
  data.habitaciones=Array.isArray(data.habitaciones)?data.habitaciones:[];
  data.huespedes=Array.isArray(data.huespedes)?data.huespedes:[];
  data.usuarios=Array.isArray(data.usuarios)?data.usuarios:[];
  data.reservas=Array.isArray(data.reservas)?data.reservas:[];
  data.estadias=Array.isArray(data.estadias)?data.estadias:[];
  save(data);
  return data;
}
function save(data){localStorage.setItem(KEY,JSON.stringify(data))}
function esc(v=''){return String(v).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function message(id,text,ok=true){
  const e=$(id); if(!e) return;
  e.textContent=text;
  e.className='message '+(ok?'ok':'error');
}
function localISO(date){
  const y=date.getFullYear(),m=String(date.getMonth()+1).padStart(2,'0'),d=String(date.getDate()).padStart(2,'0');
  return y+'-'+m+'-'+d;
}
function setDefaultDates(){
  const a=$('#searchEntry'),b=$('#searchExit');
  if(!a||!b||a.value||b.value) return;
  const today=new Date(),tomorrow=new Date(today);
  tomorrow.setDate(today.getDate()+1);
  a.value=localISO(today); b.value=localISO(tomorrow);
}
function setReservationStep(n){
  [1,2,3].forEach(i=>$('#step'+i)?.classList.toggle('active',i<=n));
}
function setView(name){
  $$('.view').forEach(v=>v.classList.remove('active'));
  $$('.nav-btn').forEach(b=>b.classList.remove('active'));
  $('#view-'+name)?.classList.add('active');
  $('.nav-btn[data-view="'+name+'"]')?.classList.add('active');
  renderAll();
}
$$('.nav-btn').forEach(b=>b.addEventListener('click',()=>setView(b.dataset.view)));
$('#resetDemo').addEventListener('click',()=>{
  localStorage.removeItem(KEY);
  seed();
  setDefaultDates();
  setReservationStep(1);
  renderAll();
  setView('inicio');
});

function roomCard(r,selectable=false){
  const stateClass=r.estado==='OCUPADA'?'occupied':'';
  return '<div class="room-row"><div><strong>Habitación '+esc(r.numero)+'</strong>'+
    '<span class="small">Capacidad: '+r.capacidad+' · Orientación: '+esc(r.orientacion)+'</span></div>'+
    (selectable
      ?'<button type="button" data-select-room="'+r.id+'">Seleccionar</button>'
      :'<span class="status '+stateClass+'">'+esc(r.estado)+'</span>')+
    '</div>';
}

function renderHome(){
  const d=db();
  const available=d.habitaciones.filter(x=>x.estado==='DISPONIBLE').length;
  const occupied=d.habitaciones.filter(x=>x.estado==='OCUPADA').length;
  $('#statDisponibles').textContent=available;
  $('#statOcupadas').textContent=occupied;
  $('#statReservas').textContent=d.reservas.filter(r=>r.estado!=='FINALIZADA').length;
  $('#statHuespedes').textContent=d.huespedes.length;
  $('#homeRooms').innerHTML=d.habitaciones.length?d.habitaciones.map(r=>roomCard(r)).join(''):'<div class="empty">No hay habitaciones registradas.</div>';
}

function renderRooms(){
  const d=db();
  $('#roomsList').innerHTML=d.habitaciones.length?d.habitaciones.map(r=>roomCard(r)).join(''):'<div class="empty">No hay habitaciones registradas.</div>';
}
$('#roomForm').addEventListener('submit',e=>{
  e.preventDefault();
  const d=db(),num=$('#roomNumber').value.trim(),capacity=+$('#roomCapacity').value;
  if(!num) return message('#roomMessage','Ingrese un número de habitación.',false);
  if(!Number.isSafeInteger(capacity)||capacity<1) return message('#roomMessage','La capacidad debe ser un número entero mayor que cero.',false);
  if(d.habitaciones.some(r=>r.numero.toLowerCase()===num.toLowerCase())) return message('#roomMessage','Ese número ya está registrado.',false);
  d.habitaciones.push({id:uid(d.habitaciones),numero:num,capacidad:capacity,orientacion:$('#roomOrientation').value,estado:'DISPONIBLE'});
  save(d); e.target.reset(); $('#roomCapacity').value=2;
  message('#roomMessage','Habitación registrada correctamente.'); renderAll();
});

function renderGuests(){
  const d=db();
  $('#guestsList').innerHTML=d.huespedes.length?d.huespedes.map(h=>
    '<div class="data-row"><div><strong>'+esc(h.nombre)+'</strong><span class="small">Huésped registrado · ID '+h.id+'</span></div></div>'
  ).join(''):'<div class="empty">No hay huéspedes registrados.</div>';
}
$('#guestForm').addEventListener('submit',e=>{
  e.preventDefault();
  const d=db(),name=$('#guestName').value.trim();
  if(name.length<3) return message('#guestMessage','Ingrese un nombre válido.',false);
  d.huespedes.push({id:uid(d.huespedes),nombre:name});
  save(d); e.target.reset();
  message('#guestMessage','Huésped registrado correctamente.'); renderAll();
});

function availableForDates(entry,exit){
  const d=db();
  return d.habitaciones.filter(room=>{
    if(room.estado==='OCUPADA') return false;
    return !d.reservas.some(r=>r.habitacionId===room.id && r.estado!=='FINALIZADA' && entry<r.salida && exit>r.entrada);
  });
}
function renderAvailable(entry=$('#searchEntry').value,exit=$('#searchExit').value){
  if(!entry||!exit){
    $('#availableRooms').innerHTML='<div class="empty">Seleccione las fechas y consulte la disponibilidad.</div>';
    return;
  }
  if(exit<=entry){
    $('#availableRooms').innerHTML='<div class="empty">La fecha de salida debe ser posterior a la entrada.</div>';
    return;
  }
  const rooms=availableForDates(entry,exit);
  $('#availableRooms').innerHTML=rooms.length?rooms.map(r=>roomCard(r,true)).join(''):'<div class="empty">No hay habitaciones disponibles para ese período.</div>';
  $$('[data-select-room]').forEach(b=>b.addEventListener('click',()=>{
    const d=db(),room=d.habitaciones.find(r=>r.id===+b.dataset.selectRoom);
    if(!room) return;
    $('#reservationRoom').value=room.id;
    $('#reservationRoomLabel').value='Habitación '+room.numero;
    $('#reservationEntry').value=$('#searchEntry').value;
    $('#reservationExit').value=$('#searchExit').value;
    setReservationStep(3);
    message('#reservationMessage','Habitación '+room.numero+' seleccionada.');
  }));
}
$('#availabilityForm').addEventListener('submit',e=>{
  e.preventDefault();
  const a=$('#searchEntry').value,b=$('#searchExit').value;
  if(!a||!b||b<=a) return message('#availabilityMessage','Revise las fechas: la salida debe ser posterior a la entrada.',false);
  renderAvailable(a,b);
  setReservationStep(2);
  message('#availabilityMessage','Disponibilidad consultada.');
});

function renderReservations(){
  const d=db();
  $('#reservationGuest').innerHTML=d.huespedes.length
    ?d.huespedes.map(h=>'<option value="'+h.id+'">'+esc(h.nombre)+'</option>').join('')
    :'<option value="">Primero registre un huésped</option>';
  $('#reservationsList').innerHTML=d.reservas.length?d.reservas.map(r=>{
    const h=d.huespedes.find(x=>x.id===r.huespedId);
    const room=d.habitaciones.find(x=>x.id===r.habitacionId);
    return '<div class="data-row"><div><strong>Reserva #'+r.id+' · '+esc(h?.nombre||'—')+'</strong>'+
      '<span class="small">Habitación '+esc(room?.numero||'—')+' · '+esc(r.entrada)+' → '+esc(r.salida)+' · '+r.cantidad+' huésped(es)</span></div>'+
      '<span class="status '+(r.estado==='FINALIZADA'?'finished':'')+'">'+esc(r.estado)+'</span></div>';
  }).join(''):'<div class="empty">Todavía no hay reservas registradas.</div>';
}
$('#reservationForm').addEventListener('submit',e=>{
  e.preventDefault();
  const d=db();
  const guestId=+$('#reservationGuest').value,roomId=+$('#reservationRoom').value;
  const entry=$('#reservationEntry').value,exit=$('#reservationExit').value,count=+$('#reservationCount').value;
  const room=d.habitaciones.find(r=>r.id===roomId);
  if(!guestId) return message('#reservationMessage','Primero registre o seleccione un huésped.',false);
  if(!room) return message('#reservationMessage','Primero seleccione una habitación disponible.',false);
  if(!entry||!exit||exit<=entry) return message('#reservationMessage','Revise las fechas de la reserva.',false);
  if(!Number.isSafeInteger(count)||count<1||count>room.capacidad) return message('#reservationMessage','La cantidad de huéspedes debe ser entera y no superar la capacidad.',false);
  if(!availableForDates(entry,exit).some(r=>r.id===roomId)) return message('#reservationMessage','La habitación ya no está disponible para esas fechas.',false);
  d.reservas.push({id:uid(d.reservas),huespedId:guestId,habitacionId:roomId,entrada:entry,salida:exit,cantidad:count,estado:'REGISTRADA'});
  save(d);
  $('#reservationRoom').value=''; $('#reservationRoomLabel').value='';
  $('#reservationCount').value=1;
  setReservationStep(1);
  message('#reservationMessage','Reserva guardada correctamente.');
  renderAll();
});

function renderCheckin(){
  const d=db();
  const eligible=d.reservas.filter(r=>r.estado==='REGISTRADA'&&d.habitaciones.find(x=>x.id===r.habitacionId)?.estado==='DISPONIBLE');
  $('#checkinReservation').innerHTML=eligible.length?eligible.map(r=>{
    const h=d.huespedes.find(x=>x.id===r.huespedId),room=d.habitaciones.find(x=>x.id===r.habitacionId);
    return '<option value="'+r.id+'">Reserva #'+r.id+' · '+esc(h?.nombre||'—')+' · Hab. '+esc(room?.numero||'—')+'</option>';
  }).join(''):'<option value="">No hay reservas disponibles para check-in</option>';
  const active=d.estadias.filter(s=>s.estado==='ACTIVA');
  $('#activeStays').innerHTML=active.length?active.map(s=>{
    const room=d.habitaciones.find(x=>x.id===s.habitacionId),h=d.huespedes.find(x=>x.id===s.huespedId);
    return '<div class="data-row"><div><strong>'+esc(h?.nombre||'—')+'</strong><span class="small">Habitación '+esc(room?.numero||'—')+' · Estadía activa</span></div><span class="status occupied">OCUPADA</span></div>';
  }).join(''):'<div class="empty">No hay estadías activas.</div>';
}
$('#checkinForm').addEventListener('submit',e=>{
  e.preventDefault();
  const d=db(),reservation=d.reservas.find(x=>x.id===+$('#checkinReservation').value);
  if(!reservation||reservation.estado!=='REGISTRADA') return message('#checkinMessage','Seleccione una reserva registrada que no tenga check-in.',false);
  const room=d.habitaciones.find(x=>x.id===reservation.habitacionId);
  if(!room||room.estado!=='DISPONIBLE') return message('#checkinMessage','La habitación no está disponible.',false);
  room.estado='OCUPADA';
  reservation.estado='CHECK-IN';
  d.estadias.push({id:uid(d.estadias),reservaId:reservation.id,huespedId:reservation.huespedId,habitacionId:reservation.habitacionId,cantidad:reservation.cantidad,checkin:new Date().toISOString(),checkout:null,total:null,estado:'ACTIVA'});
  save(d);
  message('#checkinMessage','Check-in registrado. La habitación ahora está ocupada.');
  renderAll();
});

function renderCheckout(){
  const d=db(),active=d.estadias.filter(s=>s.estado==='ACTIVA');
  $('#checkoutStay').innerHTML=active.length?active.map(s=>{
    const room=d.habitaciones.find(x=>x.id===s.habitacionId),h=d.huespedes.find(x=>x.id===s.huespedId);
    return '<option value="'+s.id+'">'+esc(h?.nombre||'—')+' · Hab. '+esc(room?.numero||'—')+'</option>';
  }).join(''):'<option value="">No hay estadías activas</option>';
  const finished=d.estadias.filter(s=>s.estado==='FINALIZADA');
  $('#finishedStays').innerHTML=finished.length?finished.map(s=>{
    const room=d.habitaciones.find(x=>x.id===s.habitacionId),h=d.huespedes.find(x=>x.id===s.huespedId);
    return '<div class="data-row"><div><strong>'+esc(h?.nombre||'—')+'</strong><span class="small">Habitación '+esc(room?.numero||'—')+' · Total demostrativo: $'+Number(s.total||0).toLocaleString('es-CL')+'</span></div><span class="status finished">FINALIZADA</span></div>';
  }).join(''):'<div class="empty">No hay check-outs registrados.</div>';
  calcCheckout();
}
function calcCheckout(){
  const d=db(),stay=d.estadias.find(x=>x.id===+$('#checkoutStay').value),rate=+$('#costPerGuest').value,nights=+$('#checkoutNights').value;
  $('#checkoutTotal').value=stay&&$('#costPerGuest').value!==''&&Number.isSafeInteger(rate)&&rate>=0&&Number.isSafeInteger(nights)&&nights>0?'$'+(stay.cantidad*rate*nights).toLocaleString('es-CL')+' CLP':'Pendiente de tarifa de prueba';
}
$('#checkoutStay').addEventListener('change',calcCheckout);
$('#costPerGuest').addEventListener('input',calcCheckout);
$('#checkoutNights').addEventListener('input',calcCheckout);
$('#checkoutForm').addEventListener('submit',e=>{
  e.preventDefault();
  const d=db(),stay=d.estadias.find(x=>x.id===+$('#checkoutStay').value),rate=+$('#costPerGuest').value,nights=+$('#checkoutNights').value;
  if(!stay||stay.estado!=='ACTIVA') return message('#checkoutMessage','Seleccione una estadía activa.',false);
  if($('#costPerGuest').value===''||!Number.isSafeInteger(rate)||rate<0||!Number.isSafeInteger(nights)||nights<1) return message('#checkoutMessage','Ingrese una tarifa de prueba válida en pesos chilenos y noches enteras positivas.',false);
  if(!Number.isSafeInteger(stay.cantidad*rate*nights)) return message('#checkoutMessage','El costo calculado supera el rango admitido.',false);
  stay.costoPorPasajero=rate*nights;
  stay.nochesDePrueba=nights;
  stay.total=stay.cantidad*rate*nights;
  stay.checkout=new Date().toISOString();
  stay.estado='FINALIZADA';
  const room=d.habitaciones.find(x=>x.id===stay.habitacionId);
  if(room) room.estado='DISPONIBLE';
  const reservation=d.reservas.find(x=>x.id===stay.reservaId);
  if(reservation) reservation.estado='FINALIZADA';
  save(d);
  message('#checkoutMessage','Check-out registrado. La habitación volvió a estar disponible.');
  renderAll();
});

function renderUsers(){
  const d=db();
  $('#usersList').innerHTML=d.usuarios.length?d.usuarios.map(u=>
    '<div class="data-row"><div><strong>'+esc(u.nombre)+'</strong><span class="small">'+esc(u.rol)+'</span></div></div>'
  ).join(''):'<div class="empty">No hay usuarios registrados.</div>';
}
$('#userForm').addEventListener('submit',e=>{
  e.preventDefault();
  const d=db(),name=$('#userName').value.trim();
  if(name.length<3) return message('#userMessage','Ingrese un nombre válido.',false);
  d.usuarios.push({id:uid(d.usuarios),nombre:name,rol:$('#userRole').value});
  save(d); e.target.reset();
  message('#userMessage','Usuario registrado correctamente.');
  renderAll();
});

function renderReports(){
  const d=db();
  const occupied=d.habitaciones.filter(x=>x.estado==='OCUPADA').length;
  const available=d.habitaciones.filter(x=>x.estado==='DISPONIBLE').length;
  const total=d.habitaciones.length;
  $('#reportOccupied').textContent=occupied;
  $('#reportAvailable').textContent=available;
  $('#reportReservations').textContent=d.reservas.length;
  $('#reportOccupancy').textContent=total?Math.round(occupied/total*100)+'%':'0%';
  $('#reportList').innerHTML=d.reservas.length?d.reservas.map(r=>{
    const room=d.habitaciones.find(x=>x.id===r.habitacionId),guest=d.huespedes.find(x=>x.id===r.huespedId);
    return '<div class="data-row"><div><strong>Reserva #'+r.id+' · '+esc(guest?.nombre||'—')+'</strong><span class="small">Habitación '+esc(room?.numero||'—')+' · '+esc(r.entrada)+' → '+esc(r.salida)+'</span></div><span class="status '+(r.estado==='FINALIZADA'?'finished':'')+'">'+esc(r.estado)+'</span></div>';
  }).join(''):'<div class="empty">No hay reservas para informar.</div>';
}

function renderAll(){
  seed();
  renderHome();
  renderRooms();
  renderGuests();
  renderReservations();
  renderAvailable();
  renderCheckin();
  renderCheckout();
  renderUsers();
  renderReports();
}
seed();
setDefaultDates();
setReservationStep(1);
renderAll();
