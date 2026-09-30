const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');

// Pruebas de operaciones y validación. La inspección visual se realiza por separado.
const nodes=new Map(),storage=new Map();
function node(selector){
  if(!nodes.has(selector))nodes.set(selector,{value:'',innerHTML:'',textContent:'',className:'',dataset:{},classList:{add(){},remove(){},toggle(){}},handlers:{},addEventListener(type,fn){this.handlers[type]=fn},reset(){}});
  return nodes.get(selector);
}
const context=vm.createContext({document:{querySelector:node,querySelectorAll:()=>[]},localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},Date,console});
vm.runInContext(fs.readFileSync(path.join(__dirname,'../prototipo/app.js'),'utf8'),context);
const data=()=>JSON.parse(vm.runInContext('JSON.stringify(db())',context));
const value=(id,v)=>node(id).value=String(v);
const submit=id=>node(id).handlers.submit({preventDefault(){},target:node(id)});

value('#roomNumber','400');value('#roomCapacity','2.5');value('#roomOrientation','Norte');submit('#roomForm');
assert.equal(data().habitaciones.length,3,'Rechaza capacidades decimales');
value('#roomCapacity',2);submit('#roomForm');assert.equal(data().habitaciones.length,4);
submit('#roomForm');assert.equal(data().habitaciones.length,4,'Rechaza número duplicado');

value('#reservationGuest',1);value('#reservationRoom',1);value('#reservationEntry','2026-10-01');value('#reservationExit','2026-10-03');value('#reservationCount',3);submit('#reservationForm');assert.equal(data().reservas.length,0,'Rechaza exceso de capacidad');
value('#reservationCount',2);submit('#reservationForm');assert.equal(data().reservas.length,1);
value('#reservationRoom',1);value('#reservationCount',1);submit('#reservationForm');assert.equal(data().reservas.length,1,'Rechaza reserva superpuesta');
value('#reservationEntry','2026-10-03');value('#reservationExit','2026-10-05');submit('#reservationForm');assert.equal(data().reservas.length,2,'Permite intervalos contiguos');

value('#checkinReservation',1);submit('#checkinForm');assert.equal(data().estadias.length,1);assert.equal(data().habitaciones[0].estado,'OCUPADA');
submit('#checkinForm');assert.equal(data().estadias.length,1,'Rechaza doble check-in');
value('#checkoutStay',1);value('#costPerGuest','');value('#checkoutNights',2);submit('#checkoutForm');assert.equal(data().estadias[0].estado,'ACTIVA','No confirma sin tarifa de prueba');
value('#costPerGuest',-1);submit('#checkoutForm');assert.equal(data().estadias[0].estado,'ACTIVA','Rechaza tarifa negativa');
value('#costPerGuest',10000);submit('#checkoutForm');assert.equal(data().estadias[0].total,40000);assert.equal(data().estadias[0].costoPorPasajero,20000);assert.equal(data().habitaciones[0].estado,'DISPONIBLE');
submit('#checkoutForm');assert.equal(data().estadias[0].total,40000,'Rechaza segundo check-out');
console.log('Validaciones de capacidad, fechas, reserva, check-in y check-out: correctas.');
