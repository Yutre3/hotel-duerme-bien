
await figma.loadFontAsync({family:'Inter',style:'Regular'});
await figma.loadFontAsync({family:'Inter',style:'Semi Bold'});
await figma.loadFontAsync({family:'Inter',style:'Bold'});
const page=figma.currentPage;page.name='Demo · Hotel Duerme Bien';
const bs=await figma.importComponentSetByKeyAsync('cc8b558dc7d9684011b6b99ce8e6509399bc836b');
const ins=await figma.importComponentSetByKeyAsync('c28150b04d333d34ed9d2b77abd9f2f54e1a878a');
const surface=await figma.variables.importVariableByKeyAsync('3fe6117980bb52e96ac3ed63a40765746e689874');
const bodyStyle=await figma.importStyleByKeyAsync('cebee1b62ea594fa8f97b0b247fd163730736f2a');
const blue={r:.086,g:.231,b:.314}, white={r:1,g:1,b:1}, ink={r:.145,g:.216,b:.278};
const frames={}, links=[];
function layout(parent,name,mode,w){const n=figma.createAutoLayout(mode);n.name=name;n.resize(w,60);n.itemSpacing=16;n.paddingLeft=24;n.paddingRight=24;n.paddingTop=20;n.paddingBottom=20;n.fills=[];parent.appendChild(n);n.layoutSizingHorizontal='FIXED';n.layoutSizingVertical='HUG';return n;}
function text(parent,str,size=16,bold=false,color=ink){const n=figma.createText();n.fontName={family:'Inter',style:bold?'Semi Bold':'Regular'};n.characters=str;n.fontSize=size;n.fills=[{type:'SOLID',color}];parent.appendChild(n);n.textAutoResize='HEIGHT';n.resize(parent.width-48,30);return n;}
async function button(parent,label,to,neutral=false){const variant=bs.children.find(n=>n.name==='Variant='+ (neutral?'Neutral':'Primary')+', State=Default, Size=Medium');const n=variant.createInstance();for(const t of n.findAllWithCriteria({types:['TEXT']})){for(const seg of t.getStyledTextSegments(['fontName']))await figma.loadFontAsync(seg.fontName);}parent.appendChild(n);n.setProperties({'Label#2:0':label});n.name=label;n.resize(neutral?194:240,44);links.push({node:n,to});return n;}
async function field(parent,label,value){const variant=ins.children.find(n=>n.name==='State=Default, Value Type=Default');const n=variant.createInstance();for(const t of n.findAllWithCriteria({types:['TEXT']})){for(const seg of t.getStyledTextSegments(['fontName']))await figma.loadFontAsync(seg.fontName);}parent.appendChild(n);n.setProperties({'Label#280:41':label,'Value#630:14':value});n.resize(430,82);return n;}
const screens=[
['acceso','Acceso',[['Usuario','admin_demo'],['Perfil','Administrador']],'Entrar','disponibilidad',[]],
['disponibilidad','Disponibilidad',[['Entrada','01/10/2026'],['Salida','03/10/2026'],['Pasajeros','2']],'Consultar disponibilidad','disponible',[]],
['disponible','Habitaciones disponibles',[],'Reservar habitación 201','reservas',['Habitación 201 · Capacidad 2 · Norte · Disponible','Habitación 305 · Capacidad 3 · Este · Disponible']],
['habitaciones','Habitaciones',[['Número','201'],['Capacidad','2'],['Orientación','Norte']],'Guardar habitación','habitacion-guardada',['201 · 2 pasajeros · Norte','305 · 3 pasajeros · Este']],
['habitacion-guardada','Habitación guardada',[],'Volver a habitaciones','habitaciones',['Habitación 201 guardada correctamente.']],
['huespedes','Huéspedes',[['Identificación','DEMO-01'],['Nombres','Ana'],['Apellidos','Ejemplo']],'Guardar huésped','huesped-guardado',['DEMO-01 · Ana Ejemplo','DEMO-02 · Luis Ejemplo']],
['huesped-guardado','Huésped guardado',[],'Ir a reservas','reservas',['Ana Ejemplo ya está registrada.']],
['reservas','Reservas',[['Titular','Ana Ejemplo'],['Habitación','201'],['Entrada','01/10/2026'],['Salida','03/10/2026'],['Pasajeros','2']],'Guardar reserva','reserva-guardada',[]],
['reserva-guardada','Reserva registrada',[],'Hacer check-in','checkin',['Reserva #1 · Ana Ejemplo · Habitación 201','01/10/2026 al 03/10/2026 · 2 pasajeros · REGISTRADA']],
['modificar','Modificar reserva',[['Entrada','02/10/2026'],['Salida','04/10/2026'],['Pasajeros','2']],'Guardar cambios','reserva-modificada',[]],
['reserva-modificada','Reserva modificada',[],'Volver a reservas','reservas',['Fechas actualizadas: 02/10/2026 al 04/10/2026.']],
['cancelar','Cancelar reserva',[],'Confirmar cancelación','cancelada',['¿Cancelar la reserva #1 de Ana Ejemplo?']],
['cancelada','Reserva cancelada',[],'Volver a reservas','reservas',['Reserva #1 CANCELADA. Disponibilidad liberada.']],
['checkin','Check-in',[['Origen','Reserva #1'],['Habitación','201'],['Entrada','01/10/2026'],['Salida prevista','03/10/2026'],['Huéspedes','Ana Ejemplo / Luis Ejemplo']],'Confirmar check-in','estadia',[]],
['estadia','Estadía activa',[],'Realizar check-out','checkout',['Estadía #1 · Habitación 201 · ACTIVA','Ana Ejemplo y Luis Ejemplo · Entrada 01/10/2026','Habitación ocupada.']],
['checkout','Check-out',[['Estadía','Estadía #1 · Habitación 201'],['Salida real','03/10/2026'],['Tarifa por pasajero/noche','10.000 CLP']],'Calcular cuenta','cuenta',[]],
['cuenta','Cuenta por pasajero',[],'Confirmar check-out','finalizada',['Ana Ejemplo · 2 noches · $10.000 · $20.000 CLP','Luis Ejemplo · 2 noches · $10.000 · $20.000 CLP','TOTAL: $40.000 CLP · Tarifa ficticia de demostración.']],
['finalizada','Check-out registrado',[],'Consultar informes','informes',['Estadía FINALIZADA. Costos guardados.','Habitación 201 disponible nuevamente.']],
['informes','Informes',[['Desde','01/10/2026'],['Hasta','04/10/2026']],'Generar informe','reporte',[]],
['reporte','Informe del período',[],'Volver a informes','informes',['Estadía #1 · Habitación 201 · 2 pasajeros · FINALIZADA','Reserva #1 · FINALIZADA · Cuenta $40.000 CLP']],
['usuarios','Usuarios',[['Nombre de usuario','encargado_demo'],['Perfil','Encargado'],['Estado','Activo']],'Guardar usuario','usuario-guardado',['admin_demo · Administrador · Activo','encargado_demo · Encargado · Activo']],
['usuario-guardado','Usuario guardado',[],'Volver a usuarios','usuarios',['Usuario encargado_demo guardado correctamente.']]
];
for(let i=0;i<screens.length;i++){
const [key,title,fields,action,next,rows]=screens[i];
const f=figma.createAutoLayout('VERTICAL');f.name=key+' · '+title;f.resize(1200,900);f.primaryAxisSizingMode='FIXED';f.counterAxisSizingMode='FIXED';f.itemSpacing=0;f.fills=[{type:'SOLID',color:white}];f.x=200+(i%4)*1400;f.y=200+Math.floor(i/4)*1100;frames[key]=f;
const header=layout(f,'Cabecera','HORIZONTAL',1200);header.fills=[{type:'SOLID',color:blue}];text(header,'Hotel Duerme Bien · Sistema de pasajeros',24,true,white);
const shell=layout(f,'Contenido','HORIZONTAL',1200);shell.paddingTop=24;shell.itemSpacing=24;
const nav=layout(shell,'Navegación','VERTICAL',242);nav.paddingLeft=0;nav.paddingRight=0;nav.itemSpacing=8;
for(const [nk,nm] of [['disponibilidad','Disponibilidad'],['habitaciones','Habitaciones'],['huespedes','Huéspedes'],['reservas','Reservas'],['checkin','Check-in'],['checkout','Check-out'],['informes','Informes'],['usuarios','Usuarios'],['acceso','Salir']]) await button(nav,nm,nk,true);
const main=layout(shell,'Área de trabajo','VERTICAL',860);main.paddingLeft=0;main.paddingRight=0;main.paddingTop=0;text(main,title,30,true);
const card=layout(main,'Formulario y resultados','VERTICAL',850);card.cornerRadius=12;card.fills=[figma.variables.setBoundVariableForPaint({type:'SOLID',color:white},'color',surface)];card.itemSpacing=12;
for(let j=0;j<fields.length;j+=2){const row=layout(card,'Campos','HORIZONTAL',800);row.paddingLeft=0;row.paddingRight=0;row.paddingTop=0;row.paddingBottom=0;for(const [lab,val] of fields.slice(j,j+2)){const n=await field(row,lab,val);n.resize(365,82);}}
for(const r of rows)text(card,r,18);
await button(card,action,next);
if(key==='reserva-guardada'){await button(card,'Modificar reserva','modificar',true);await button(card,'Cancelar reserva','cancelar',true);}
text(main,'Datos ficticios para recorrer el prototipo.',14);
}
for(const {node,to} of links){let top=node;while(top.parent&&top.parent.type!=='PAGE')top=top.parent;if(top.id===frames[to].id)continue;await node.setReactionsAsync([{trigger:{type:'ON_CLICK'},actions:[{type:'NODE',destinationId:frames[to].id,navigation:'NAVIGATE',transition:null,resetScrollPosition:true}]}]);}
page.flowStartingPoints=[{nodeId:frames.acceso.id,name:'Demo · Reserva, check-in y check-out'}];
return {frames:Object.fromEntries(Object.entries(frames).map(([k,n])=>[k,n.id])),interactionCount:links.length,createdNodeIds:screens.flatMap(s=>{const f=frames[s[0]];return [f.id,...f.findAll(()=>true).map(n=>n.id)]}),mutatedNodeIds:[page.id]};
