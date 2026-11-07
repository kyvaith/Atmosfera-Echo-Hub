/* Host tests with a mocked HA WebSocket API. No Home Assistant or firmware is exercised. */
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const crypto = require("node:crypto");
const source = fs.readFileSync(path.resolve(__dirname,"../../custom_components/atmosfera_echo_hub/www/tile-editor.js"),"utf8");
const clone = value => JSON.parse(JSON.stringify(value));
const emptyRoot = () => ({innerHTML:"",activeElement:null,addEventListener(){},querySelector(){return null;},querySelectorAll(){return [];},contains(){return false;}});
class HostElement {
  constructor(){this.isConnected=true;}
  attachShadow(){this.shadowRoot=emptyRoot();}
}
const context = vm.createContext({
  HTMLElement:HostElement,customElements:{get(){return false;},define(){}},
  window:{addEventListener(){},removeEventListener(){},clearInterval(){},clearTimeout(){},setTimeout,clearTimeout,setInterval},
  crypto,TextEncoder,Blob,URL,console,
});
vm.runInContext(source+"\nglobalThis.TestEditor = AtmosferaTileEditor;",context);
const profile = {
  id:"echo-hub-m3-v1",version:1,wire_version:1,width:800,height:800,max_cards:16,max_document_bytes:32768,
  pages:[{id:"home-1",title:"Home",order:0},{id:"home-2",title:"Security",order:1},{id:"home-3",title:"Apps",order:2},{id:"home-4",title:"Controls",order:3}],
  slots:[
    {slot:0,page_id:"home-1",x:0,y:0,width:0,height:0,editable:false,hidden:true,types:["entity","sensor","action"]},
    {slot:2,page_id:"home-2",x:55,y:176,width:220,height:248,radius:110,editable:true,hidden:false,types:["entity","sensor","action"]},
    {slot:3,page_id:"home-2",x:290,y:176,width:220,height:248,radius:72,editable:true,hidden:false,types:["entity","sensor","action"]},
    {slot:11,page_id:"home-2",x:410,y:462,width:296,height:116,radius:58,editable:true,hidden:false,types:["entity","sensor","action"]},
    {slot:13,page_id:"home-4",x:112,y:548,width:276,height:112,radius:56,editable:true,hidden:false,types:["entity","sensor","action"]},
  ],
  features:{move:true,resize:false,custom_pages:false,native_controls:false,applied_ack:false},
};
function card(id,slot,entity="light.room") {
  return {id,slot,type:"entity",entity_id:entity,title:id,icon:"light",palette:"primary",visible:true,action:{kind:"default"}};
}
function makeEditor(callWS=async() => {throw new Error("Unexpected API call");}) {
  const editor = new context.TestEditor();
  editor._hass={callWS,locale:{language:"en"},states:{"light.room":{state:"on",attributes:{}}}};
  const layout={version:2,profile:"echo-hub-m3-v1",revision:4,cards:[{...card("reserved",0),visible:false},card("first",2),card("second",3,"switch.pump")]};
  editor._data={version:2,entries:[{entry_id:"screen-a",title:"A",layout:clone(layout),profile:clone(profile),status:{saved_revision:4,sent_revision:3,applied_revision:null,device_available:true,pending:true},accent_color:"36BCF0"},{entry_id:"screen-b",title:"B",layout:clone(layout),profile:clone(profile),status:{}}],icons:["light","switch","action"],palettes:["primary","surface"]};
  editor._entryId="screen-a";editor._saved=clone(layout);editor._draft=clone(layout);editor._pageId="home-2";editor._status=clone(editor.entry.status);
  editor.fetchCatalogue=async()=>{};
  return editor;
}

function cameraPreviewEditor() {
  const e=makeEditor();e._selectedSlot=2;e.profile.schema_camera_preview=true;e.profile.layout_versions=[2,3];
  e._data.icons.push("camera");e._status={...e._status,sent_revision:4,context_press_version:1,press_enabled_version:1,
    camera_preview_supported:true,camera_catalog_generation:7,camera_preview_entities:["camera.door"]};
  const entity={entity_id:"camera.door",name:"Door",domain:"camera",state:"idle",available:true,actions:[],camera_preview:{allowlisted:true,min_duration:15,max_duration:90}};
  e._entityIndex.set(entity.entity_id,entity);e._hass.states[entity.entity_id]={state:"idle",attributes:{friendly_name:"Door"}};
  e._draft.cards[1]=e.newCard(entity,2);e._saved=clone(e._draft);return e;
}
function cameraStoredDraft(e,draft=e._draft) {
  const layout=clone(draft);delete layout.revision;
  return {version:1,profile:e.profile.id,base_revision:4,updated_at:1,layout};
}

test("camera launcher uses explicit review to draft, normal Save and Undo; no service or preview call",()=>{
  const e=cameraPreviewEditor(),before=clone(e._draft);
  assert.deepEqual(clone(e.cardAt(2).action),{kind:"none"});assert.equal(e.cardAt(2).icon,"camera");
  assert.equal(e.requestCameraPreview(),true);assert.deepEqual(clone(e._draft),before);
  assert.match(e.modalMarkup(),/data-camera-duration/);e._pending.duration=50;
  assert.equal(e.confirmCameraPreview(),true);assert.equal(e._draft.version,3);
  assert.deepEqual(clone(e.cardAt(2).action),{kind:"camera_preview",duration_seconds:50});
  e.validateStoredDraft(cameraStoredDraft(e));assert.deepEqual(clone(e._saved),before);
  assert.match(e.inspectorMarkup(),/camera-preview-configure/);assert.equal(e.stateText(e.cardAt(2)),"Open");
  e.history("undo");assert.deepEqual(clone(e._draft),before);e.history("redo");assert.equal(e.cardAt(2).action.duration_seconds,50);
});

test("camera launcher rejects closed-schema extras, wrong target and duration coercion",()=>{
  const e=cameraPreviewEditor();e.requestCameraPreview();e.confirmCameraPreview();
  for(const mutate of [c=>{c.action.duration_seconds=true;},c=>{c.action.duration_seconds=14;},c=>{c.action.duration_seconds=91;},
    c=>{c.action.duration_seconds="35";},c=>{c.action.url="https://arbitrary";},c=>{c.action.service="camera.turn_on";},
    c=>{c.type="action";},c=>{c.entity_id="light.room";}]) {
    const draft=clone(e._draft);mutate(draft.cards[1]);assert.throws(()=>e.validateStoredDraft(cameraStoredDraft(e,draft)),/invalid|limit/);
  }
  const legacy=clone(e._draft);legacy.version=2;assert.throws(()=>e.validateStoredDraft(cameraStoredDraft(e,legacy)),/invalid|limit/);
});

test("camera launcher fresh metadata, capabilities and review identity gates",()=>{
  for(const mutate of [e=>{e._status.camera_preview_supported=false;},e=>{e._status.camera_preview_entities=[];},
    e=>{e._status.press_enabled_version=0;},e=>{e._status.context_press_version=0;},e=>{e._status.device_available=false;},
    e=>{e._status.sent_revision=3;},e=>{e.entityFor("camera.door").camera_preview.allowlisted=false;},
    e=>{e._hass.states["camera.door"].state="unavailable";},e=>{e.cardAt(2).visible=false;}]) {
    const e=cameraPreviewEditor();mutate(e);assert.equal(e.requestCameraPreview(),false);
  }
  for(const mutate of [e=>{e._status.camera_catalog_generation++;},e=>{e._saved.revision++;},e=>{e._selectionEpoch++;},
    e=>{e._hass.states["camera.door"]={state:"idle",attributes:{}};},e=>{e.cardAt(2).title="changed";},
    e=>{e._hass.user={id:"other"};},e=>{e._status.camera_preview_entities=[];}]) {
    const e=cameraPreviewEditor();e.requestCameraPreview();mutate(e);assert.equal(e.confirmCameraPreview(),false);assert.equal(e.cardAt(2).action.kind,"none");
  }
});

test("camera launcher cancelled review and invalid duration stay passive",()=>{
  const e=cameraPreviewEditor(),before=clone(e._draft);e.requestCameraPreview();e._pending=null;assert.deepEqual(clone(e._draft),before);
  for(const value of ["", "15.5", "1e2", "100", "14"]) {
    e.requestCameraPreview();e.onInput({target:{dataset:{cameraDuration:""},value}});
    assert.equal(e.cameraPreviewDurationValid(),false);assert.equal(e.confirmCameraPreview(),false);assert.deepEqual(clone(e._draft),before);
  }
});

test("camera launcher fetches saved visible metadata with filtered library and no selection",async()=>{
  const e=cameraPreviewEditor();e.requestCameraPreview();e.confirmCameraPreview();e._saved=clone(e._draft);
  const metadata=clone(e.entityFor("camera.door"));e._entityIndex.clear();e._selectedSlot=null;e._catalogue=[];e._domain="light";
  const calls=[];e._hass.callWS=async request=>{calls.push(request);return {entities:[metadata]};};
  assert.equal(e.stateText(e.cardAt(2)),"Unavailable");
  await Promise.all(e.fetchPreviewEntities());
  assert.equal(calls.length,1);assert.equal(calls[0].type,"atmosfera_echo_hub/catalogue/get");assert.equal(calls[0].query,"camera.door");
  assert.equal(e.stateText(e.cardAt(2)),"Open");assert.equal(e._selectedSlot,null);assert.equal(e._domain,"light");
  await Promise.all(e.fetchPreviewEntities());assert.equal(calls.length,1);
  assert.deepEqual(clone(e._draft),clone(e._saved));
});
test("carousel edits preserve card slots, protect Home and Apps, and support undo",()=>{
  const editor=makeEditor();
  const before=clone(editor._draft.cards);
  editor.profile.pages.push({id:"home-5",title:"Tools",order:4});
  editor.profile.carousel_order=editor.profile.pages.map(page=>page.id);
  editor.editCarousel("carousel-up","home-5");
  assert.deepEqual(clone(editor._draft.home_order),["home-1","home-2","home-3","home-5","home-4"]);
  editor.editCarousel("carousel-toggle","home-3");
  editor.editCarousel("carousel-toggle","home-5");
  assert.deepEqual(clone(editor._draft.home_order),["home-1","home-2","home-3","home-4"]);
  assert.deepEqual(clone(editor._draft.cards),before);
  editor.history("undo");
  assert.deepEqual(clone(editor._draft.home_order),["home-1","home-2","home-3","home-5","home-4"]);
});
test("moving swaps occupied slots while preserving identities; reserved and absent places are refused",()=>{
  const editor=makeEditor();
  assert.equal(editor.moveCard(2,3),true);
  assert.equal(editor.cardAt(3).id,"first");
  assert.equal(editor.cardAt(2).id,"second");
  assert.equal(editor._draft.cards.find(item=>item.id==="reserved").slot,0);
  assert.equal(editor.moveCard(3,0),false);
  assert.equal(editor.moveCard(3,99),false);
  assert.equal(editor.dirty,true);
  editor.history("undo");
  assert.equal(editor.cardAt(2).id,"first");assert.equal(editor.dirty,false);
  editor.history("redo");assert.equal(editor.cardAt(3).id,"first");
});
test("a destination's capabilities reject an incompatible swap without changing the draft",()=>{
  const editor=makeEditor();
  editor.profile.slots.find(slot=>slot.slot===3).types=["sensor"];
  const before=clone(editor._draft);
  assert.equal(editor.moveCard(2,3),false);
  assert.deepEqual(clone(editor._draft),before);
  assert.equal(editor._undo.length,0);
});
test("entity assignment fills an empty place, generates one stable ID and makes information cards passive",()=>{
  const editor=makeEditor();
  editor._entityIndex.set("sensor.room",{entity_id:"sensor.room",name:"Room temperature",domain:"sensor",state:"21.8",available:true,actions:[]});
  assert.equal(editor.assignEntity("sensor.room",11),true);
  const assigned=clone(editor.cardAt(11));
  assert.match(assigned.id,/^card-[a-f0-9-]+$/);
  assert.equal(assigned.type,"sensor");assert.deepEqual(assigned.action,{kind:"none"});
  editor.history("undo");assert.equal(editor.cardAt(11),undefined);
  editor.history("redo");assert.equal(editor.cardAt(11).id,assigned.id);
});
test("new cards cannot exceed the backend title bound",()=>{
  const editor=makeEditor();
  const result=editor.newCard({entity_id:"sensor.room",name:"x".repeat(200)},11);
  assert.equal(result.title.length,40);
});

test("LAN HTTP without randomUUID supports assignment, copy and undo with distinct IDs",()=>{
  const originalCrypto=context.crypto;
  context.crypto={getRandomValues:bytes=>crypto.webcrypto.getRandomValues(bytes)};
  try {
    const editor=makeEditor();
    editor._entityIndex.set("sensor.room",{entity_id:"sensor.room",name:"Room temperature",domain:"sensor",state:"21.8",available:true,actions:[]});
    assert.equal(editor.assignEntity("sensor.room",11),true);
    const source=clone(editor.cardAt(11));
    assert.match(source.id,/^card-[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/);
    assert.equal(editor.copyCard(11),true);
    assert.equal(editor.pasteCard(13),true);
    assert.notEqual(editor.cardAt(13).id,source.id);
    assert.equal(editor.cardAt(13).entity_id,source.entity_id);
    editor.history("undo");
    assert.equal(editor.cardAt(13),undefined);
    assert.equal(editor.cardAt(11).id,source.id);
  } finally {context.crypto=originalCrypto;}
});
test("save sends the expected revision and preserves draft after a revision conflict",async()=>{
  let request;
  const editor=makeEditor(async message=>{request=message;throw {code:"revision_conflict",message:"Expected revision 5"};});
  editor.mutate(layout=>{layout.cards[1].title="My draft";});
  assert.equal(await editor.save(),false);
  assert.equal(request.type,"atmosfera_echo_hub/layout/save");
  assert.equal(request.expected_revision,4);
  assert.equal(editor._draft.cards[1].title,"My draft");
  assert.equal(editor._saved.revision,4);
  assert.equal(editor._conflict,true);assert.equal(editor.dirty,true);assert.equal(editor._busy,false);
});
test("successful save reports storage and transport separately and never invents applied confirmation",async()=>{
  const editor=makeEditor(async message=>({layout:{...clone(message.layout),revision:5},status:{saved_revision:5,sent_revision:4,applied_revision:null,device_available:false,pending:true}}));
  editor.mutate(layout=>{layout.cards[1].title="Saved";});
  assert.equal(await editor.save(),true);
  assert.equal(editor._saved.revision,5);assert.equal(editor.dirty,false);
  const status=editor.statusMarkup();
  assert.match(status,/Saved <b>v5<\/b>/);
  assert.match(status,/Sent <b>v4<\/b>/);
  assert.match(status,/Applied <b>Not confirmed<\/b>/);
  assert.doesNotMatch(status,/Applied <b>v5/);
});
test("device switches do not discard dirty work without a choice",()=>{
  const editor=makeEditor();
  editor.mutate(layout=>{layout.cards[1].title="Keep me";});
  editor.requestSwitch("screen-b");
  assert.equal(editor._entryId,"screen-a");
  assert.equal(editor._pending.kind,"switch");assert.equal(editor._pending.entryId,"screen-b");
  assert.equal(editor._draft.cards[1].title,"Keep me");
});
test("valid import is a backend dry run until the user accepts it, then becomes one undoable draft",async()=>{
  let request;
  const editor=makeEditor(async message=>{
    request=message;
    return {layout:{version:2,profile:"echo-hub-m3-v1",revision:4,cards:[card("imported",11)]},status:{},dry_run:true,warnings:[]};
  });
  const backup={format:"atmosfera-layout",version:1,layout:{version:2,profile:"echo-hub-m3-v1",cards:[card("imported",11)]}};
  assert.equal(await editor.importText(JSON.stringify(backup)),true);
  assert.equal(request.type,"atmosfera_echo_hub/layout/import");assert.equal(request.dry_run,true);
  assert.equal(request.expected_revision,4);
  assert.equal(editor.cardAt(2).id,"first");assert.equal(editor.dirty,false);
  editor.useImported();assert.equal(editor.cardAt(11).id,"imported");assert.equal(editor.dirty,true);
  editor.history("undo");assert.equal(editor.cardAt(2).id,"first");assert.equal(editor.dirty,false);
});
test("malformed, unsupported and oversized imports never reach the API or alter the document",async()=>{
  let calls=0;const editor=makeEditor(async()=>{calls++;});
  const before=clone(editor._draft);
  await assert.rejects(editor.importText("{bad"));
  await assert.rejects(editor.importText(JSON.stringify({format:"unknown",version:1})));
  await assert.rejects(editor.importText("x".repeat(32769)));
  assert.equal(calls,0);assert.deepEqual(clone(editor._draft),before);
});
test("backend import rejection preserves saved and dirty drafts",async()=>{
  const editor=makeEditor(async()=>{throw {code:"incompatible_profile",message:"Wrong profile"};});
  editor.mutate(layout=>{layout.cards[1].title="Untouched";});
  const before=clone(editor._draft);
  await assert.rejects(editor.importText(JSON.stringify({format:"atmosfera-layout",version:1,layout:{}})));
  assert.deepEqual(clone(editor._draft),before);assert.equal(editor._pending,null);
});
test("remote save detection preserves local work and reload keeps an explicit recovery copy",async()=>{
  let latest;
  const editor=makeEditor(async()=>({version:2,entries:[latest]}));
  latest={...clone(editor.entry),layout:{...clone(editor.entry.layout),revision:5}};
  latest.layout.cards[1].title="Other user's layout";
  editor.mutate(layout=>{layout.cards[1].title="My draft";});
  await editor.refreshStatus();assert.equal(editor._conflict,true);assert.equal(editor._draft.cards[1].title,"My draft");
  await editor.reloadSaved();assert.equal(editor._draft.cards[1].title,"Other user's layout");assert.equal(editor._recovery.cards[1].title,"My draft");assert.equal(editor.dirty,false);
  editor.restoreDraft();assert.equal(editor._draft.cards[1].title,"My draft");assert.equal(editor._saved.revision,5);assert.equal(editor._draft.revision,5);assert.equal(editor.dirty,true);
});
test("a catalogue response for the previous device cannot replace the new device library",async()=>{
  let resolve;const editor=makeEditor(()=>new Promise(done=>{resolve=done;}));
  editor.fetchCatalogue=context.TestEditor.prototype.fetchCatalogue;
  const pending=editor.fetchCatalogue();
  editor._entryId="screen-b";
  resolve({entities:[{entity_id:"sensor.private",name:"Private",domain:"sensor",state:"1",actions:[]}],total:1});
  await pending;assert.equal(editor._catalogue.length,0);assert.equal(editor._entityIndex.has("sensor.private"),false);
});
test("typed fields validate numbers, RGB and boolean input without evaluating text",()=>{
  const editor=makeEditor();
  assert.equal(editor.parseFieldValue({value:"50"},{type:"number",min:0,max:100}),50);
  assert.throws(()=>editor.parseFieldValue({value:"101"},{type:"number",min:0,max:100}));
  assert.throws(()=>editor.parseFieldValue({value:"NaN"},{type:"number"}));
  assert.deepEqual(clone(editor.parseFieldValue({value:"255, 0, 100"},{type:"rgb"})),[255,0,100]);
  assert.throws(()=>editor.parseFieldValue({value:"255,,100"},{type:"rgb"}));
  assert.throws(()=>editor.parseFieldValue({value:"-1,0,256"},{type:"rgb"}));
  assert.equal(editor.parseFieldValue({value:"false"},{type:"boolean"}),false);
  assert.throws(()=>editor.parseFieldValue({value:"anything"},{type:"boolean"}));
});
test("untrusted entity titles and values are escaped in all generated markup",()=>{
  const editor=makeEditor();editor.cardAt(2).title='<img src=x onerror="bad">';
  editor._catalogue=[{entity_id:"sensor.test",name:"<script>bad</script>",domain:"sensor",state:"<img>",actions:[]}];
  assert.doesNotMatch(editor.previewMarkup(),/<img src=x/);assert.match(editor.previewMarkup(),/&lt;img/);
  assert.doesNotMatch(editor.libraryMarkup(),/<script>/);assert.match(editor.libraryMarkup(),/&lt;script&gt;/);
  assert.doesNotMatch(editor.inspectorMarkup(),/<img src=x/);
  assert.doesNotMatch(source,/onsubmit=|onclick=|eval\s*\(|new Function\s*\(/);
});
test("keyboard Enter selects an empty place and Space/Enter moves an existing card",()=>{
  const editor=makeEditor();
  const tile={dataset:{slot:"11"},closest(selector){return selector===".preview-card"?this:null;},tagName:"DIV"};
  editor.onKeyDown({target:tile,key:"Enter",code:"Enter",preventDefault(){}});
  assert.equal(editor._selectedSlot,11);
  editor._carry={kind:"card",from:2};
  editor.onKeyDown({target:tile,key:"Enter",code:"Enter",preventDefault(){}});
  assert.equal(editor.cardAt(11).id,"first");assert.equal(editor._carry,null);
});
test("preview obeys server geometry and does not expose reserved slots as editable cards",()=>{
  const editor=makeEditor();const markup=editor.previewMarkup();
  assert.match(markup,/left:6.875%;top:22%;width:27.5%;height:31%/);
  assert.doesNotMatch(markup,/data-slot="0"/);
  assert.equal(editor.pages.length,2);
});


test("the circular viewport contains every actual profile tile's rounded outline without moving geometry",()=>{
  const model=fs.readFileSync(path.resolve(__dirname,"../../custom_components/atmosfera_echo_hub/layout.py"),"utf8");
  const block=model.match(/_SLOT_GEOMETRY = \{([\s\S]*?)\n\}/)?.[1];
  assert.ok(block,"The profile must expose its fixed slot geometry");
  const slots=[...block.matchAll(/(\d+): \("home-\d", (\d+), (\d+), (\d+), (\d+)\)/g)].map(match=>match.slice(1).map(Number)).filter(item=>item[0]>=2);
  assert.equal(slots.length,14);
  for(const [slot,x,y,width,height] of slots){
    const radius=slot===3?72:slot===7?62:Math.min(width,height)/2;
    const centers=[[x+radius,y+radius,180],[x+width-radius,y+radius,270],[x+width-radius,y+height-radius,0],[x+radius,y+height-radius,90]];
    for(const [cx,cy,start] of centers) for(let degree=start;degree<=start+90;degree+=3){
      const angle=degree*Math.PI/180,px=cx+radius*Math.cos(angle),py=cy+radius*Math.sin(angle);
      assert.ok(Math.hypot(px-400,py-400)<=400.01,`Slot ${slot} escapes the physical circular viewport`);
    }
  }
  const editor=makeEditor();
  assert.match(editor.styles(),/\.screen\{[^}]*border-radius:50%/);
  assert.match(editor.styles(),/\.device-stage\{[^}]*border-radius:50%/);
});
test("live HA state formatting is used when available without repainting the inspector",()=>{
  const editor=makeEditor();
  editor._hass.formatEntityState=()=> "Włączone";
  assert.equal(editor.stateText(editor.cardAt(2)),"Włączone");
  let repainted=false;
  editor.paintInspector=()=>{repainted=true;};
  editor.hass=editor._hass;
  assert.equal(repainted,false);
});


class BrowserStorage {
  constructor(){this.values=new Map();}
  get length(){return this.values.size;}
  key(index){return [...this.values.keys()][index]??null;}
  getItem(key){return this.values.get(key)??null;}
  setItem(key,value){this.values.set(String(key),String(value));}
  removeItem(key){this.values.delete(key);}
}
function enableDraft(editor,storage,user="alice") {
  context.window.localStorage=storage;editor._hass.user={id:user};
  editor._draftOwner=user;editor._draftBaseRevision=editor._saved.revision;
  return editor;
}
function flushDraft(editor) {clearTimeout(editor._draftTimer);return editor.persistDraft();}
test("dirty browser drafts are scoped by user, display and profile and never auto-apply",()=>{
  const storage=new BrowserStorage(), editor=enableDraft(makeEditor(),storage);
  editor.mutate(layout=>{layout.cards[1].title="Browser draft";});assert.equal(flushDraft(editor),true);
  const key=editor.draftKey(), stored=JSON.parse(storage.getItem(key));
  assert.equal(stored.base_revision,4);assert.equal(stored.layout.cards[1].title,"Browser draft");
  assert.equal(stored.layout.revision,undefined);assert.ok(new TextEncoder().encode(storage.getItem(key)).length<=32768);
  const same=enableDraft(makeEditor(),storage);same.offerStoredDraft();
  assert.equal(same._pending.kind,"restore");assert.equal(same._draft.cards[1].title,"first");assert.equal(same.dirty,false);
  const otherUser=enableDraft(makeEditor(),storage,"bob");otherUser.offerStoredDraft();assert.equal(otherUser._pending,null);
  const otherDisplay=enableDraft(makeEditor(),storage);otherDisplay._entryId="screen-b";otherDisplay.offerStoredDraft();assert.equal(otherDisplay._pending,null);
  const otherProfile=enableDraft(makeEditor(),storage);otherProfile.profile.id="future-profile";otherProfile.offerStoredDraft();assert.equal(otherProfile._pending,null);
  same.persistDraft();assert.ok(storage.getItem(key),"Leaving a restore prompt must not discard the stored draft");
});
test("restore validates through backend import dry-run and stale bases require explicit review before saving",async()=>{
  const storage=new BrowserStorage(), first=enableDraft(makeEditor(),storage);
  first.mutate(layout=>{layout.cards[1].title="Older draft";});flushDraft(first);
  const calls=[], editor=enableDraft(makeEditor(async message=>{
    calls.push(clone(message));
    if(message.type.endsWith("/layout/import"))return {layout:{...clone(message.backup.layout),revision:5},status:{},dry_run:true};
    return {layout:{...clone(message.layout),revision:6},status:{saved_revision:6,sent_revision:5,applied_revision:null}};
  }),storage);
  editor._saved.revision=5;editor._draft.revision=5;editor.entry.layout.revision=5;
  editor.offerStoredDraft();assert.equal(await editor.restoreStoredDraft(),true);clearTimeout(editor._draftTimer);
  assert.equal(calls[0].type,"atmosfera_echo_hub/layout/import");assert.equal(calls[0].dry_run,true);assert.equal(calls[0].expected_revision,5);
  assert.equal(editor._draft.cards[1].title,"Older draft");assert.equal(editor._draftBaseRevision,4);assert.equal(editor._conflict,true);
  assert.equal(await editor.save(),false);assert.equal(calls.length,1);
  editor.reviewRestoredDraft();assert.equal(editor._draftBaseRevision,5);assert.equal(editor._conflict,false);
  assert.equal(JSON.parse(storage.getItem(editor.draftKey())).base_revision,5);
  assert.equal(await editor.save(),true);assert.equal(calls[1].expected_revision,5);assert.equal(storage.getItem(editor.draftKey()),null);
});
test("restoring a draft does not mutate anything when the backend rejects it",async()=>{
  const storage=new BrowserStorage(), first=enableDraft(makeEditor(),storage);
  first.mutate(layout=>{layout.cards[1].title="Preserve me";});flushDraft(first);
  const editor=enableDraft(makeEditor(async()=>{throw {code:"unsupported_action",message:"Changed capabilities"};}),storage);
  editor.offerStoredDraft();const before=clone(editor._draft);
  assert.equal(await editor.restoreStoredDraft(),false);
  assert.deepEqual(clone(editor._draft),before);assert.equal(editor.dirty,false);assert.equal(editor._pending.kind,"restore");
  assert.ok(storage.getItem(editor.draftKey()));assert.match(editor.modalMarkup(),/Changed capabilities/);
});
test("only whitelisted configuration is stored; invalid or oversized local records are never sent for restore",()=>{
  const storage=new BrowserStorage(), editor=enableDraft(makeEditor(),storage);
  editor.mutate(layout=>{layout.cards[1].camera_token="not-configuration";});assert.equal(flushDraft(editor),false);assert.equal(storage.length,0);
  delete editor._draft.cards[1].camera_token;editor._draft.cards[1].title="Valid draft";assert.equal(flushDraft(editor),true);
  assert.doesNotMatch(storage.getItem(editor.draftKey()),/camera_token|access_token|api_key|camera_url/);
  const clean=enableDraft(makeEditor(),storage);
  storage.setItem(clean.draftKey(),"x".repeat(32769));clean.offerStoredDraft();assert.equal(clean._pending,null);assert.equal(clean.dirty,false);
  storage.setItem(clean.draftKey(),JSON.stringify({version:1,profile:"echo-hub-m3-v1",base_revision:4,updated_at:1,layout:{version:2,profile:"echo-hub-m3-v1",cards:[],secret:"bad"}}));
  clean.offerStoredDraft();assert.equal(clean._pending,null);assert.equal(clean.dirty,false);
});
test("clean undo and explicit discard remove drafts; per-user storage is capped at eight",()=>{
  const storage=new BrowserStorage(), editor=enableDraft(makeEditor(),storage);
  editor.mutate(layout=>{layout.cards[1].title="Changed";});flushDraft(editor);assert.ok(storage.getItem(editor.draftKey()));
  editor.history("undo");flushDraft(editor);assert.equal(storage.getItem(editor.draftKey()),null);
  editor.history("redo");flushDraft(editor);
  const reloaded=enableDraft(makeEditor(),storage);reloaded.offerStoredDraft();reloaded.discardStoredDraft();assert.equal(storage.getItem(editor.draftKey()),null);
  for(let index=0;index<12;index++)storage.setItem(editor.draftPrefix()+`other-${index}:echo-hub-m3-v1`,JSON.stringify({updated_at:index}));
  storage.setItem("atmosfera-layout-draft:v1:bob:other:echo-hub-m3-v1","keep");
  flushDraft(editor);
  assert.equal([...storage.values.keys()].filter(key=>key.startsWith(editor.draftPrefix())).length,8);
  assert.equal(storage.getItem("atmosfera-layout-draft:v1:bob:other:echo-hub-m3-v1"),"keep");
});
test("local storage failures do not block editing or a normal HA save",async()=>{
  const storage={getItem(){throw new Error("Blocked");},setItem(){throw new Error("Quota");},removeItem(){throw new Error("Blocked");},length:0};
  const editor=enableDraft(makeEditor(async message=>({layout:{...clone(message.layout),revision:5},status:{saved_revision:5,sent_revision:null,applied_revision:null}})),storage);
  editor.mutate(layout=>{layout.cards[1].title="Can still save";});assert.equal(flushDraft(editor),false);assert.equal(editor._storageError,true);assert.equal(editor.dirty,true);
  assert.equal(await editor.save(),true);assert.equal(editor.dirty,false);assert.equal(editor._saved.revision,5);
});
test("drafts are disabled without a HA user identity",()=>{
  const storage=new BrowserStorage(),editor=makeEditor();context.window.localStorage=storage;
  editor.mutate(layout=>{layout.cards[1].title="No user";});assert.equal(flushDraft(editor),false);assert.equal(storage.length,0);
});
test("changing HA users keeps the old user's draft and ignores outstanding old-context responses",async()=>{
  const storage=new BrowserStorage(),editor=enableDraft(makeEditor(),storage);
  const data=clone(editor._data);let reply;
  editor._hass.callWS=()=>new Promise(resolve=>{reply=resolve;});
  editor.mutate(layout=>{layout.cards[1].title="Alice only";});flushDraft(editor);
  const aliceKey=editor.draftKey(), pending=editor.refreshStatus();
  editor.hass={user:{id:"bob"},locale:{language:"en"},states:{},callWS:async()=>clone(data)};
  await new Promise(resolve=>setImmediate(resolve));
  reply({entries:[{...clone(data.entries[0]),layout:{...clone(data.entries[0].layout),revision:9}}]});
  await pending;
  assert.equal(editor._hass.user.id,"bob");assert.equal(editor._draft.cards[1].title,"first");assert.equal(editor._saved.revision,4);
  assert.equal(JSON.parse(storage.getItem(aliceKey)).layout.cards[1].title,"Alice only");
  assert.equal(editor._pending,null);assert.equal(editor.dirty,false);
  clearTimeout(editor._draftTimer);
});

// A small DOM setter/focus shim verifies mutation contracts, not browser rendering.
function trackedEditorDOM(editor) {
  const root=emptyRoot(), regions=new Map();
  root.htmlWrites=0;
  Object.defineProperty(root,"innerHTML",{get(){return "";},set(){root.htmlWrites++;}});
  function region(markup="") {
    let html="";
    const node={writes:0,buttons:[],contains(child){return !!child && child.region===this;},querySelectorAll(){return this.buttons;}};
    function apply(value) {
      // Browser serialization need not retain source escaping in text nodes.
      html=value.replaceAll("&quot;",'"');
      if(node.contains(root.activeElement))root.activeElement=null;
      node.buttons=[...value.matchAll(/<button\b[^>]*data-action="([^"]+)"/g)].map(match=>({tagName:"BUTTON",dataset:{action:match[1]},region:node,focuses:0,focus(){this.focuses++;root.activeElement=this;}}));
    }
    Object.defineProperty(node,"innerHTML",{get(){return html;},set(value){node.writes++;apply(value);}});
    apply(markup);return node;
  }
  function text(value,dataset={}) {
    let current=value;
    const node={writes:0,dataset};
    Object.defineProperty(node,"textContent",{get(){return current;},set(value){node.writes++;current=value;}});
    return node;
  }
  regions.set("#delivery-status",region(editor.statusMarkup()));
  regions.set("#feedback",region(editor.feedbackMarkup()));
  regions.set("#modal-host",region());
  regions.set("#inspector",region("existing inspector"));
  const live=text(editor.stateText(editor.cardAt(2)),{liveSlot:"2"});
  root.querySelector=selector=>selector===".modal button"?regions.get("#modal-host").buttons[0]||null:regions.get(selector)||null;
  root.querySelectorAll=selector=>selector==="[data-live-slot]"?[live]:[];
  editor.shadowRoot=root;
  return {root,regions,live,region};
}

test("unchanged status polls preserve the conflict action DOM and focused button",async()=>{
  const editor=makeEditor();
  const latest=clone(editor.entry);latest.layout.revision=5;
  latest.status={...latest.status,saved_revision:5,sent_revision:4};
  editor._hass.callWS=async()=>({entries:[clone(latest)]});
  editor._draft.cards[1].title="Keep draft";
  const dom=trackedEditorDOM(editor),feedback=dom.regions.get("#feedback"),status=dom.regions.get("#delivery-status");
  await editor.refreshStatus();
  assert.equal(editor._conflict,true);assert.equal(feedback.writes,1);assert.equal(status.writes,1);
  const reload=feedback.buttons.find(button=>button.dataset.action==="reload");reload.focus();
  await editor.refreshStatus();await editor.refreshStatus();
  assert.equal(feedback.writes,1,"Unchanged conflict must not replace its buttons");
  assert.equal(status.writes,1,"Unchanged delivery status must not replace its children");
  assert.equal(dom.root.activeElement,reload);assert.equal(reload.focuses,1);
  assert.equal(dom.regions.get("#inspector").writes,0);assert.equal(dom.root.htmlWrites,0);
  latest.status.sent_revision=5;
  await editor.refreshStatus();
  assert.equal(status.writes,2,"A real transport change still updates the status");
  assert.equal(feedback.writes,1);assert.equal(dom.root.activeElement,reload);
});

test("real feedback changes retain the focused action and normalized identical markup is not rewritten",()=>{
  const editor=makeEditor();editor._conflict=true;
  const dom=trackedEditorDOM(editor),feedback=dom.regions.get("#feedback");
  const before=feedback.buttons[0];before.focus();
  editor._error='Try "later"';editor.paintFeedback();
  const after=feedback.buttons[0];
  assert.notEqual(after,before);assert.equal(dom.root.activeElement,after);assert.equal(after.dataset.action,"reload");
  assert.equal(feedback.writes,1);
  editor.paintFeedback();editor.paintFeedback();
  assert.equal(feedback.writes,1,"Serialized quotes must not cause repeated writes");assert.equal(after.focuses,1);
  editor.render();
  const writes=feedback.writes;
  editor.paintFeedback();editor.paintStatus();
  assert.equal(feedback.writes,writes,"Full render must seed the new regions' source markup");
  assert.equal(dom.regions.get("#delivery-status").writes,0);
});

test("unchanged modal feedback does not replace buttons or move the user's focus",()=>{
  const editor=makeEditor();editor._pending={kind:"switch",entryId:"screen-b"};
  const dom=trackedEditorDOM(editor),modal=dom.regions.get("#modal-host");
  editor.renderModal();assert.equal(modal.writes,1);assert.equal(dom.root.activeElement,modal.buttons[0]);
  const discard=modal.buttons.find(button=>button.dataset.action==="modal-discard");discard.focus();
  editor.paintFeedback();editor.renderModal();
  assert.equal(modal.writes,1);assert.equal(dom.root.activeElement,discard);assert.equal(discard.focuses,1);
  editor._error="Save failed";editor.paintFeedback();
  const current=modal.buttons.find(button=>button.dataset.action==="modal-discard");
  assert.equal(modal.writes,2);assert.equal(dom.root.activeElement,current);
  assert.equal(modal.buttons[0].focuses,0,"A genuine update must not move focus to the first modal action");
});

test("HA state updates patch live text only when changed and leave conflict and inspector untouched",()=>{
  const editor=makeEditor();editor._conflict=true;
  const dom=trackedEditorDOM(editor),inspector=dom.regions.get("#inspector");
  const field={tagName:"INPUT",region:inspector};dom.root.activeElement=field;
  editor.hass={...editor._hass};editor.hass={...editor._hass};
  assert.equal(dom.live.writes,0);
  editor.hass={...editor._hass,states:{"light.room":{state:"off",attributes:{}}}};
  assert.equal(dom.live.writes,1);assert.equal(dom.live.textContent,"off");
  editor.hass={...editor._hass};assert.equal(dom.live.writes,1);
  for(const region of dom.regions.values())assert.equal(region.writes,0);
  assert.equal(dom.root.htmlWrites,0);assert.equal(dom.root.activeElement,field);
});

function areaEntity(id="light.kitchen",area_id="kitchen",area_name="Kitchen") {
  return {entity_id:id,name:id,domain:id.split(".")[0],state:"on",available:true,actions:[],area_id,area_name};
}
function useCatalogue(editor) {editor.fetchCatalogue=context.TestEditor.prototype.fetchCatalogue;return editor;}

test("area search combines query and domain on the server before the catalogue limit",async()=>{
  const calls=[],editor=useCatalogue(makeEditor(async message=>{
    calls.push(clone(message));return {entities:[areaEntity()],total:250,truncated:true,areas:[{area_id:"kitchen",area_name:"Kitchen"}],area_total:1,areas_truncated:false};
  }));
  editor._query="ceiling";editor._domain="light";editor._area="area:kitchen";
  const before=clone(editor._draft);
  await editor.fetchCatalogue();
  assert.deepEqual(calls[0],{type:"atmosfera_echo_hub/catalogue/get",entry_id:"screen-a",query:"ceiling",limit:200,domains:["light"],area_id:"kitchen"});
  assert.equal(editor._catalogueTotal,250);assert.equal(editor._truncated,true);assert.equal(editor._area,"area:kitchen");
  assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
});

test("All areas omits the filter; No area sends empty ID and cannot collide with an actual area named none",async()=>{
  const calls=[],editor=useCatalogue(makeEditor(async message=>{calls.push(clone(message));return {entities:[],total:0,areas:[{area_id:"none",area_name:"A real area"}],areas_truncated:false};}));
  await editor.onChange({target:{id:"area",value:"none"}});
  assert.equal(calls[0].area_id,"");assert.equal(editor._area,"none");
  await editor.onChange({target:{id:"area",value:"area:none"}});
  assert.equal(calls[1].area_id,"none");
  await editor.onChange({target:{id:"area",value:""}});
  assert.equal(Object.hasOwn(calls[2],"area_id"),false);
  assert.match(editor.areaOptionsMarkup(),/value="none"/);assert.match(editor.areaOptionsMarkup(),/value="area:none"/);
});

test("partial area metadata is optional, deduplicated, bounded and escaped; empty assignments stay selectable as No area",async()=>{
  const editor=useCatalogue(makeEditor(async()=>({entities:[areaEntity("light.legacy",null,null),{entity_id:"sensor.yaml",name:"YAML sensor",domain:"sensor",state:"1",actions:[]},areaEntity("light.one","salon","Salon Żółty"),areaEntity("light.two","salon",null),areaEntity("switch.partial","office",null)],total:5,truncated:false})));
  await editor.fetchCatalogue();
  assert.deepEqual(clone(editor._areas),[{area_id:"office",area_name:"office"},{area_id:"salon",area_name:"Salon Żółty"}]);
  assert.equal(editor._catalogue.length,5);assert.match(editor.areaOptionsMarkup(),/No area/);
  editor._areas=editor.catalogueAreas([{area_id:'x"<',area_name:'<img src=x onerror="bad">'},{area_id:"",area_name:"Invalid"},{area_name:"Missing ID"},{area_id:"x".repeat(257),area_name:"Too long"}]);
  const markup=editor.areaOptionsMarkup();assert.equal(editor._areas.length,1);
  assert.doesNotMatch(markup,/<img/);assert.match(markup,/&lt;img/);assert.match(markup,/area:x&quot;&lt;/);
  editor._hass.locale.language="pl";
  assert.match(editor.areaOptionsMarkup(),/Wszystkie obszary/);assert.match(editor.areaOptionsMarkup(),/Bez obszaru/);assert.equal(editor.t("area"),"Obszar / pomieszczenie");
});

test("an authoritatively removed selected area resets and refetches All without losing query, domain or draft",async()=>{
  const calls=[],editor=useCatalogue(makeEditor(async message=>{calls.push(clone(message));return {entities:message.area_id?[]:[areaEntity()],total:message.area_id?0:1,areas:[{area_id:"kitchen",area_name:"Kitchen"}],areas_truncated:false};}));
  editor._query="room";editor._domain="light";editor._area="area:deleted";editor._draft.cards[1].title="Unsaved";
  const before=clone(editor._draft);
  await editor.fetchCatalogue();
  assert.equal(calls.length,2);assert.equal(calls[0].area_id,"deleted");assert.equal(Object.hasOwn(calls[1],"area_id"),false);
  assert.equal(calls[1].query,"room");assert.deepEqual(calls[1].domains,["light"]);assert.equal(editor._area,"");
  assert.equal(editor._catalogue.length,1);assert.deepEqual(clone(editor._draft),before);assert.equal(editor.dirty,true);
});

test("truncated area facets retain the selected area and report the limit in both locales",async()=>{
  let calls=0;const editor=useCatalogue(makeEditor(async()=>{calls++;return {entities:[],total:0,areas:[{area_id:"first",area_name:"First"}],area_total:501,areas_truncated:true};}));
  editor._area="area:last";editor._areas=[{area_id:"last",area_name:"Last known area"}];
  await editor.fetchCatalogue();
  assert.equal(calls,1);assert.equal(editor._area,"area:last");assert.match(editor.areaOptionsMarkup(),/Last known area/);
  assert.match(editor.libraryMarkup(),/Some areas are not listed/);
  editor._hass.locale.language="pl";assert.match(editor.libraryMarkup(),/Nie wszystkie obszary są na liście/);
});

test("device switching resets room filters only after the dirty-switch choice",()=>{
  const editor=makeEditor();editor._area="area:kitchen";editor._areas=[{area_id:"kitchen",area_name:"Kitchen"}];editor._areasTruncated=true;
  editor._query="lamp";editor._domain="light";editor._draft.cards[1].title="Keep draft";
  editor.requestSwitch("screen-b");
  assert.equal(editor._entryId,"screen-a");assert.equal(editor._area,"area:kitchen");assert.equal(editor._draft.cards[1].title,"Keep draft");
  editor.selectEntry("screen-b");
  assert.equal(editor._area,"");assert.equal(editor._areas.length,0);assert.equal(editor._areasTruncated,false);assert.equal(editor._query,"");assert.equal(editor._domain,"");
});

test("unchanged library/filter paints keep the focused select and never rebuild conflict or inspector",async()=>{
  const editor=useCatalogue(makeEditor(async()=>({entities:[areaEntity()],total:1,areas:[{area_id:"kitchen",area_name:"Kitchen"}],areas_truncated:false})));
  const dom=trackedEditorDOM(editor),library=dom.region(),domain=dom.region(),area=dom.region(),inspector=dom.regions.get("#inspector");
  dom.regions.set("#library-results",library);dom.regions.set("#domain",domain);dom.regions.set("#area",area);
  const query=dom.root.querySelector;dom.root.querySelector=selector=>selector===".inspector"?inspector:query(selector);
  dom.root.activeElement={tagName:"INPUT",region:inspector};
  await editor.fetchCatalogue();
  const writes=[library.writes,domain.writes,area.writes];
  area.tagName="SELECT";dom.root.activeElement=area;
  editor.paintLibrary();editor.paintLibrary();
  assert.deepEqual([library.writes,domain.writes,area.writes],writes);assert.equal(dom.root.activeElement,area);
  assert.equal(inspector.writes,0);assert.equal(dom.regions.get("#feedback").writes,0);assert.equal(dom.root.htmlWrites,0);
});

test("a late previous-area response cannot replace the current filtered catalogue",async()=>{
  const replies=[],editor=useCatalogue(makeEditor(()=>new Promise(resolve=>replies.push(resolve))));
  editor._area="area:kitchen";const first=editor.fetchCatalogue();
  editor._area="area:office";const second=editor.fetchCatalogue();
  const areas=[{area_id:"kitchen",area_name:"Kitchen"},{area_id:"office",area_name:"Office"}];
  replies[1]({entities:[areaEntity("light.office","office","Office")],total:1,areas,areas_truncated:false});await second;
  replies[0]({entities:[areaEntity()],total:1,areas,areas_truncated:false});await first;
  assert.equal(editor._area,"area:office");assert.equal(editor._catalogue[0].entity_id,"light.office");assert.equal(editor._entityIndex.has("light.kitchen"),false);
});

test("area-only metadata does not rewrite an unfocused inspector; genuine capability changes still do",async()=>{
  let actions=[];
  const editor=useCatalogue(makeEditor(async()=>({entities:[{...areaEntity("light.room","office","Office"),actions}],total:1,areas:[{area_id:"office",area_name:"Office"}],areas_truncated:false})));
  editor._selectedSlot=2;editor.cardAt(2).action={kind:"service",service:"light.turn_on",data:{}};
  editor._entityIndex.set("light.room",{...areaEntity("light.room","kitchen","Kitchen"),actions:[]});
  const dom=trackedEditorDOM(editor),inspector=dom.region(editor.inspectorMarkup());dom.regions.set("#inspector",inspector);
  const query=dom.root.querySelector;dom.root.querySelector=selector=>selector===".inspector"?inspector:query(selector);
  dom.root.activeElement={tagName:"SELECT"};
  await editor.fetchCatalogue();assert.equal(inspector.writes,0);
  actions=[{service:"light.turn_on",fields:{brightness_pct:{type:"number",min:0,max:100,required:false}}}];
  await editor.fetchCatalogue();assert.equal(inspector.writes,1);assert.match(inspector.innerHTML,/data:brightness_pct/);
  await editor.fetchCatalogue();assert.equal(inspector.writes,1);
});

test("copy snapshots one card without changing the layout; cross-page paste clones data with a new identity and one undo",()=>{
  const editor=makeEditor();
  editor.cardAt(2).action={kind:"service",service:"light.turn_on",data:{brightness_pct:35,rgb_color:[10,20,30]}};
  editor._saved=clone(editor._draft);
  const original=clone(editor.cardAt(2));
  assert.equal(editor.copyCard(2),true);
  assert.equal(editor.dirty,false);assert.equal(editor._undo.length,0);
  editor.cardAt(2).action.data.rgb_color[0]=99;
  assert.equal(editor.pasteCard(13),true);
  const pasted=clone(editor.cardAt(13));
  assert.notEqual(pasted.id,original.id);assert.match(pasted.id,/^card-[a-f0-9-]+$/);
  assert.deepEqual(pasted,{...original,id:pasted.id,slot:13});
  assert.equal(editor._pageId,"home-4");assert.equal(editor._selectedSlot,13);assert.equal(editor._undo.length,1);
  editor.history("undo");assert.equal(editor.cardAt(13),undefined);
  editor.history("redo");assert.equal(editor.cardAt(13).id,pasted.id);
  editor.cardAt(13).action.data.rgb_color[1]=88;
  assert.equal(editor.pasteCard(11),true);
  assert.notEqual(editor.cardAt(11).id,pasted.id);
  assert.deepEqual(clone(editor.cardAt(11).action.data.rgb_color),[10,20,30]);
});

test("paste refuses occupied hidden cards, reserved, missing and incompatible places atomically",()=>{
  const editor=makeEditor();editor.cardAt(3).visible=false;
  editor.profile.slots.find(slot=>slot.slot===13).types=["sensor"];
  editor.copyCard(2);const before=clone(editor._draft);
  for(const slot of [3,0,99,13])assert.equal(editor.pasteCard(slot),false);
  assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
  assert.equal(editor.copyCard(0),false);assert.equal(editor.copyCard(99),false);
});

test("hidden read-only card copies preserve visibility, presentation and passive action exactly",()=>{
  const editor=makeEditor(),sourceCard=editor.cardAt(2);
  Object.assign(sourceCard,{type:"sensor",entity_id:"binary_sensor.window",visible:false,icon:"action",palette:"surface",action:{kind:"none"}});
  editor.copyCard(2);assert.equal(editor.pasteCard(11),true);
  assert.deepEqual(clone(editor.cardAt(11)),{...clone(sourceCard),id:editor.cardAt(11).id,slot:11});
});

test("copy and paste respect busy, modal, active gesture, invalid fields and document limits",()=>{
  for(const [key,value] of [["_busy",true],["_pending",{kind:"switch"}],["_drag",{}],["_carry",{}],["_fieldErrors",{title:"Invalid"}]]){
    const editor=makeEditor();editor.copyCard(2);editor[key]=value;
    assert.equal(editor.copyCard(2),false,key);assert.equal(editor.pasteCard(11),false,key);
    assert.equal(editor._undo.length,0);
  }
  const full=makeEditor();full.copyCard(2);full.profile.max_cards=full._draft.cards.length;
  // A profile change clears the previous copy; copy again under the new limit.
  full.copyCard(2);assert.equal(full.pasteCard(11),false);
  const bounded=makeEditor();bounded.profile.max_document_bytes=100;bounded.copyCard(2);
  const before=clone(bounded._draft);assert.equal(bounded.pasteCard(11),false);
  assert.deepEqual(clone(bounded._draft),before);assert.equal(bounded._undo.length,0);assert.match(bounded._error,/limit/);
});

test("copy never saves, dispatches actions, or persists its clipboard to browser storage",()=>{
  const storage=new BrowserStorage(),editor=enableDraft(makeEditor(),storage);
  editor.copyCard(2);assert.equal(storage.length,0);assert.equal(editor.dirty,false);
  assert.equal(editor.pasteCard(11),true);flushDraft(editor);
  assert.equal(storage.length,1);
  const record=JSON.parse(storage.getItem(editor.draftKey()));
  assert.equal(record.layout.cards.length,4);assert.equal(Object.hasOwn(record,"clipboard"),false);
  assert.equal(Object.hasOwn(record,"_cardClipboard"),false);
});

test("the clipboard is invalidated on device, profile, user and component lifecycle changes",()=>{
  const entry=makeEditor();entry.copyCard(2);entry.selectEntry("screen-b");assert.equal(entry.clipboardCard(),undefined);
  for(const change of [editor=>{editor.profile.id="other";},editor=>{editor.profile.version++;},editor=>{editor.profile.slots[1].types=["sensor"];},editor=>{editor._hass.user={id:"other"};}]){
    const editor=makeEditor();editor.copyCard(2);change(editor);
    assert.equal(editor.pasteCard(11),false);assert.equal(editor._cardClipboard,null);
  }
  const user=makeEditor();user._hass.user={id:"alice"};user.copyCard(2);user.isConnected=false;
  user.hass={...user._hass,user:{id:"bob"}};assert.equal(user._cardClipboard,null);
  const detached=makeEditor();detached.copyCard(2);detached.disconnectedCallback();assert.equal(detached._cardClipboard,null);
});

test("a status poll reporting a changed server profile invalidates the copy without migrating the active draft",async()=>{
  const editor=makeEditor();editor.copyCard(2);
  const latest=clone(editor.entry);latest.profile.version=2;
  editor._hass.callWS=async()=>({entries:[latest]});
  const before=clone(editor._draft);await editor.refreshStatus();
  assert.equal(editor._cardClipboard,null);assert.deepEqual(clone(editor._draft),before);
  assert.equal(editor.profile.version,1);assert.equal(editor.dirty,false);
});

function keyboardTarget(slot,tagName="DIV") {
  return {dataset:{slot:String(slot)},tagName,closest(selector){return selector===".preview-card"?this:null;}};
}
function shortcut(editor,target,key,modifiers={ctrlKey:true}) {
  const event={target,key,code:`Key${key.toUpperCase()}`,prevented:false,preventDefault(){this.prevented=true;},...modifiers};
  editor.onKeyDown(event);return event;
}
test("Ctrl and Cmd copy/paste use focused places and leave text controls and contenteditable to the browser",()=>{
  const editor=makeEditor();editor._selectedSlot=3;
  assert.equal(shortcut(editor,keyboardTarget(2),"c").prevented,true);
  assert.equal(shortcut(editor,keyboardTarget(13),"v",{metaKey:true}).prevented,true);
  assert.equal(editor.cardAt(13).entity_id,"light.room");
  for(const tag of ["INPUT","SELECT","TEXTAREA"]){
    assert.equal(shortcut(editor,keyboardTarget(11,tag),"v").prevented,false);
  }
  const editable=keyboardTarget(11);editable.isContentEditable=true;
  assert.equal(shortcut(editor,editable,"v").prevented,false);
  assert.equal(editor.cardAt(11),undefined);
});

test("copy menu and empty-place paste are localized, escaped and clearable",async()=>{
  const editor=makeEditor();editor._selectedSlot=2;editor.cardAt(2).title="<img onerror=bad>";
  assert.match(editor.inspectorMarkup(),/data-action="copy-card"/);
  await editor.onClick({target:{closest(){return {dataset:{action:"copy-card"}};}}});
  assert.match(editor.clipboardMarkup(),/&lt;img onerror=bad&gt;/);assert.doesNotMatch(editor.clipboardMarkup(),/<img/);
  editor._selectedSlot=11;assert.match(editor.inspectorMarkup(),/data-action="paste-card"/);
  editor._hass.locale.language="pl";assert.match(editor.inspectorMarkup(),/Wklej kopię tutaj/);assert.match(editor.clipboardMarkup(),/Wyczyść kopię/);
  await editor.onClick({target:{closest(){return {dataset:{action:"paste-card"}};}}});assert.ok(editor.cardAt(11));
  editor.clearCardClipboard();assert.equal(editor.clipboardMarkup(),"");assert.equal(editor.pasteMarkup(),"");
});

function nativeStatus(overrides={}) {
  return {saved_revision:4,sent_revision:4,accepted_revision:4,snapshot_ready:true,pending_slots:0,context_press_version:1,applied_revision:null,device_available:true,...overrides};
}
test("received revision zero is valid and readiness requires the matching saved revision; applied is independent",()=>{
  const editor=makeEditor();editor._status=nativeStatus({saved_revision:0,sent_revision:0,accepted_revision:0});
  let markup=editor.statusMarkup();assert.match(markup,/Received <b>v0<\/b>/);assert.match(markup,/data-snapshot-state="ready"/);
  assert.match(markup,/Applied <b>Not confirmed<\/b>/);
  editor._status=nativeStatus({accepted_revision:3});markup=editor.statusMarkup();
  assert.match(markup,/Received <b>v3 · Older layout/);assert.match(markup,/data-snapshot-state="stale"/);
  assert.doesNotMatch(markup,/Snapshot cache <b>Ready/);
  editor._status=nativeStatus({accepted_revision:5});assert.match(editor.statusMarkup(),/Different layout/);
});

test("off-screen pending masks are counted without error semantics, including unsigned bit31",()=>{
  const editor=makeEditor();editor._status=nativeStatus({snapshot_ready:false,pending_slots:65532});
  let markup=editor.statusMarkup();assert.match(markup,/14 places waiting/);assert.match(markup,/data-snapshot-state="pending"/);
  assert.doesNotMatch(markup,/status-warning/);
  editor._status.pending_slots=0x80000001;assert.match(editor.statusMarkup(),/2 places waiting/);
  editor._status.pending_slots=0;assert.match(editor.statusMarkup(),/Snapshot cache <b>Waiting/);
  editor._hass.locale.language="pl";editor._status.pending_slots=6;assert.match(editor.statusMarkup(),/Oczekujące miejsca: 2/);
});

test("offline and failed refreshes retain received history but cannot claim current snapshot readiness",()=>{
  const editor=makeEditor();editor._status=nativeStatus({device_available:false});
  let markup=editor.statusMarkup();assert.match(markup,/v4 · Last known/);assert.match(markup,/data-snapshot-state="offline"/);
  assert.doesNotMatch(markup,/Snapshot cache <b>Ready/);
  editor._status.device_available=true;editor._statusError=true;markup=editor.statusMarkup();
  assert.match(markup,/v4 · Last known/);assert.match(markup,/could not be refreshed/);
  assert.match(markup,/data-snapshot-state="unknown"/);
});

test("legacy, malformed and missing reports remain unknown rather than confirming snapshots",()=>{
  const editor=makeEditor();
  for(const status of [{},{context_press_version:0},{accepted_revision:null},{accepted_revision:true},{accepted_revision:-1},{accepted_revision:"4"},{accepted_revision:Number.MAX_SAFE_INTEGER+1},{snapshot_ready:"true"},{pending_slots:true},{pending_slots:-1},{pending_slots:0x100000000},{snapshot_ready:true,pending_slots:1}]){
    editor._status=Object.keys(status).length?nativeStatus(status):{};
    const markup=editor.statusMarkup();assert.match(markup,/data-snapshot-state="unknown"/);
    assert.doesNotMatch(markup,/Snapshot cache <b>Ready/);
  }
  editor._status=nativeStatus({snapshot_ready:false});delete editor._status.pending_slots;
  assert.match(editor.statusMarkup(),/data-snapshot-state="pending"/);
});

test("status readouts escape no unvalidated revision values and only an explicit actual acknowledgement enables Applied",()=>{
  const editor=makeEditor();editor._status=nativeStatus({saved_revision:"<img>",sent_revision:"<script>",accepted_revision:"<img>",applied_revision:4});
  assert.doesNotMatch(editor.statusMarkup(),/<img>|<script>|Applied <b>v4/);
  editor.profile.features.applied_ack=true;assert.match(editor.statusMarkup(),/Applied <b>v4<\/b>/);
  editor._status.applied_revision=true;assert.match(editor.statusMarkup(),/Applied <b>Not confirmed/);
});

test("an older same-device status response cannot replace a newer completed poll",async()=>{
  const replies=[],editor=makeEditor(()=>new Promise(resolve=>replies.push(resolve)));
  const first=editor.refreshStatus(),second=editor.refreshStatus();
  replies[1]({entries:[{...clone(editor.entry),status:nativeStatus()}]});await second;
  replies[0]({entries:[{...clone(editor.entry),status:nativeStatus({accepted_revision:2})}]});await first;
  assert.equal(editor._status.accepted_revision,4);assert.equal(editor._statusError,false);
});

test("a poll begun before Save cannot rewind the saved layout after Save completes",async()=>{
  let reply;const editor=makeEditor(async message=>{
    if(message.type.endsWith("/layout/get"))return new Promise(resolve=>{reply=resolve;});
    return {layout:{...clone(message.layout),revision:5},status:nativeStatus({saved_revision:5,sent_revision:5,accepted_revision:5})};
  });
  const stale=clone(editor.entry),poll=editor.refreshStatus();
  editor.mutate(layout=>{layout.cards[1].title="New saved title";});assert.equal(await editor.save(),true);
  reply({entries:[stale]});await poll;
  assert.equal(editor._saved.revision,5);assert.equal(editor._draft.revision,5);
  assert.equal(editor.cardAt(2).title,"New saved title");assert.equal(editor.dirty,false);assert.equal(editor._conflict,false);
  assert.equal(editor._status.accepted_revision,5);
});

test("a failed pre-transaction poll cannot mark a completed Save or Reload as stale",async()=>{
  for(const operation of ["save","reloadSaved"]){
    let fail,calls=0;const editor=makeEditor(async message=>{
      if(calls++===0)return new Promise((_resolve,reject)=>{fail=reject;});
      const layout=message.layout?clone(message.layout):clone(editor._saved);layout.revision=5;
      return operation==="save"?{layout,status:nativeStatus({saved_revision:5})}:{entries:[{...clone(editor.entry),layout,status:nativeStatus({saved_revision:5})}]};
    });
    const poll=editor.refreshStatus();
    if(operation==="save")editor.mutate(layout=>{layout.cards[1].title="Saved";});
    await editor[operation]();fail(new Error("Previous status request"));await poll;
    assert.equal(editor._statusError,false,operation);assert.equal(editor._saved.revision,5,operation);
  }
});

test("a pre-reload poll cannot undo the explicit newer saved layout",async()=>{
  let reply,calls=0;const editor=makeEditor(async()=>{
    if(calls++===0)return new Promise(resolve=>{reply=resolve;});
    const latest=clone(editor.entry);latest.layout.revision=5;latest.layout.cards[1].title="Explicit reload";
    return {entries:[latest]};
  });
  const stale=clone(editor.entry),poll=editor.refreshStatus();await editor.reloadSaved();
  reply({entries:[stale]});await poll;
  assert.equal(editor._saved.revision,5);assert.equal(editor.cardAt(2).title,"Explicit reload");assert.equal(editor.dirty,false);
});

test("stale poll errors after a device switch or newer response cannot taint current status",async()=>{
  let reject;const editor=makeEditor(()=>new Promise((_resolve,fail)=>{reject=fail;}));
  const old=editor.refreshStatus();editor.selectEntry("screen-b");reject(new Error("Old connection"));await old;
  assert.equal(editor._statusError,false);
  const replies=[],same=makeEditor(()=>new Promise((resolve,fail)=>replies.push({resolve,fail})));
  const first=same.refreshStatus(),second=same.refreshStatus();
  replies[1].resolve({entries:[{...clone(same.entry),status:nativeStatus()}]});await second;
  replies[0].fail(new Error("Old poll"));await first;assert.equal(same._statusError,false);
});

test("unchanged new delivery fields preserve status DOM; a changed pending count updates only status",()=>{
  const editor=makeEditor();editor._status=nativeStatus({snapshot_ready:false,pending_slots:6});
  const dom=trackedEditorDOM(editor),status=dom.regions.get("#delivery-status");
  editor.paintStatus();const before=status.writes;
  editor.paintStatus();assert.equal(status.writes,before);
  editor._status.pending_slots=4;editor.paintStatus();assert.equal(status.writes,before+1);
  assert.equal(dom.regions.get("#inspector").writes,0);assert.equal(dom.root.htmlWrites,0);
});

test("the collapsed layout profile readout distinguishes total, editable and reserved capacity without firmware claims",()=>{
  const editor=makeEditor();
  editor.profile.slots=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15].map(slot=>({slot,page_id:slot<2?"home-1":slot<6||slot===11||slot===12?"home-2":"home-4",editable:slot>=2,hidden:slot<2,types:["entity"]}));
  const markup=editor.capabilitiesMarkup();
  assert.match(markup,/echo-hub-m3-v1/);assert.match(markup,/800 × 800/);
  assert.match(markup,/16 · 14 editable · 2 reserved \/ hidden/);assert.match(markup,/4 · 2 editable · 2 built-in/);
  assert.match(markup,/Move \/ swap<\/dt><dd>Supported/);assert.match(markup,/Native controls<\/dt><dd>Not supported/);
  assert.match(markup,/not a detected firmware version/);
  editor.render();assert.match(editor.shadowRoot.innerHTML,/<details class="device-capabilities" id="device-capabilities"><summary>/);
  assert.doesNotMatch(editor.shadowRoot.innerHTML,/<details[^>]*\bopen\b/);
});

test("partial profile metadata stays unknown; profile names are escaped and both locales are complete",()=>{
  const editor=makeEditor();editor.entry.profile={id:"<img onerror=bad>"};
  let markup=editor.capabilitiesMarkup();assert.match(markup,/&lt;img onerror=bad&gt;/);assert.doesNotMatch(markup,/<img/);
  assert.match(markup,/Native controls<\/dt><dd>Unknown/);assert.match(markup,/Resolution<\/dt><dd>Unknown/);
  assert.doesNotMatch(markup,/0 editable|0 reserved/);
  editor._hass.locale.language="pl";markup=editor.capabilitiesMarkup();assert.match(markup,/Rozdzielczość/);assert.match(markup,/Nieznany/);
  assert.equal(editor.t("capabilities"),"Profil ekranu i ograniczenia");
});

function lightEditor(callWS) {
  const editor=makeEditor(callWS);editor._selectedSlot=2;
  editor.profile.layout_versions=[2,3];editor.profile.schema_control_types=["light"];
  editor._status={...editor._status,device_available:true,light_control_status:"ready",native_control_types:["light_brightness_v1"]};
  editor._hass.states["light.room"]={state:"on",attributes:{supported_color_modes:["brightness"],brightness:null}};
  editor._entityIndex.set("light.room",{entity_id:"light.room",domain:"light",name:"Room",state:"on",available:true,actions:[
    {service:"light.turn_on",fields:{brightness_pct:{type:"number",min:0,max:100}}},{service:"light.turn_off",fields:{}}
  ]});
  return editor;
}
const actionInput=value=>({dataset:{field:"action-kind"},value,removeAttribute(){},setAttribute(){}});
const clickAction=(editor,action)=>editor.onClick({target:{closest:()=>({dataset:{action}})}});

function numberEditor(callWS) {
  const editor=lightEditor(callWS), card=editor.cardAt(2);
  card.entity_id="input_number.helper";
  editor.profile.schema_control_types=["light","number"];
  editor._status={...editor._status,entity_control_status:"ready",native_control_types:["entity_control_v1"],control_kinds:["light","number"]};
  editor._hass.states[card.entity_id]={state:"0",attributes:{min:-1,max:1,step:0.25,unit_of_measurement:"°C"}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"input_number",name:"Helper",state:"0",available:true,
    actions:[{service:"input_number.set_value",fields:{value:{type:"number",min:-1,max:1,step:0.25}}}],
    number_control:{domain:{schema:"numeric_steps_v1",min:"-1",max:"1",step:"0.25",unit:"°C",max_index:8},index:4}});
  return editor;
}

function deviceNumberEditor() {
  const editor=numberEditor(),card=editor.cardAt(2),old=card.entity_id;
  const metadata=editor._entityIndex.get(old);card.entity_id="number.provider";
  editor._hass.states[card.entity_id]=editor._hass.states[old];delete editor._hass.states[old];editor._entityIndex.delete(old);
  editor._entityIndex.set(card.entity_id,{...metadata,entity_id:card.entity_id,domain:"number",actions:[{service:"number.set_value",fields:metadata.actions[0].fields}]});
  return editor;
}

function coverEditor() {
  const editor=lightEditor(),card=editor.cardAt(2);card.entity_id="cover.blind";
  editor.profile.schema_control_types=["light","number","choice","cover"];
  editor._status={...editor._status,entity_control_status:"ready",native_control_types:["entity_control_v1"],control_kinds:["light","number","choice","cover"],cover_stop_version:1};
  editor._hass.states[card.entity_id]={state:"open",attributes:{supported_features:11,current_position:40}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"cover",name:"Roleta",state:"open",available:true,
    actions:["open","stop","close"].map(operation=>({service:`cover.${operation}_cover`,fields:{}})),
    cover_control:{caps:{open:true,stop:true,close:true},state:"open",position:40,available:true}});
  return editor;
}

function fanPanelEditor() {
  const editor=lightEditor(),card=editor.cardAt(2);card.entity_id="fan.office";
  editor.profile.schema_control_types=["light","number","choice","cover","fan"];
  editor._status={...editor._status,entity_control_status:"ready",native_control_types:["entity_control_v1"],control_kinds:["light","number","choice","cover","fan"]};
  editor._hass.states[card.entity_id]={state:"on",attributes:{supported_features:63,percentage:66,percentage_step:100/3,preset_modes:["Eco","Sleep"]}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"fan",available:true,
    actions:["turn_on","turn_off","set_percentage","set_preset_mode","oscillate","set_direction"].map(name=>({service:`fan.${name}`,fields:{}})),
    fan_control:{caps:{turn_on:true,turn_off:true,oscillate:true,direction:true,speeds:[0,33,66,100],presets:["Eco","Sleep"]}}});
  return editor;
}

function coverPanelEditor() {
  const editor=coverEditor();editor.profile.schema_cover_panel=true;editor._status.cover_panel_version=1;
  const entity=editor._entityIndex.get("cover.blind"),state=editor._hass.states["cover.blind"];
  state.attributes={...state.attributes,supported_features:255,current_tilt_position:50,device_class:"blind"};
  entity.actions=["open_cover","stop_cover","close_cover","set_cover_position","open_cover_tilt","close_cover_tilt","stop_cover_tilt","set_cover_tilt_position"].map(service=>({service:`cover.${service}`,fields:{}}));
  entity.cover_panel={version:1,device_class:"blind",caps:{open:true,stop:true,close:true,set_position:true,open_tilt:true,close_tilt:true,stop_tilt:true,set_tilt_position:true},state:{available:true,cover_state:"open",position:40,tilt_position:50}};
  return editor;
}

test("negotiated cover panel keeps the existing reviewed launcher and advertises separate axes",()=>{
  const editor=coverPanelEditor(),before=clone(editor._draft);
  assert.equal(editor.coverControlAvailability().ready,true);
  assert.equal(editor.coverControlAvailability().reason,"coverPanelHint");
  assert.match(editor.inspectorMarkup(),/Open cover panel/);
  assert.equal(editor.requestLightControl("cover"),true);
  assert.match(editor.modalMarkup(),/Each Stop acts on its own section/);
  assert.deepEqual(clone(editor._draft),before);
  assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(editor.cardAt(2).action),{kind:"control",control:"cover"});
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);
});

test("tilt-only cover admission requires the detailed panel and exact service",()=>{
  const editor=coverPanelEditor(),entity=editor._entityIndex.get("cover.blind");
  entity.cover_control=null;
  for(const key of Object.keys(entity.cover_panel.caps)) entity.cover_panel.caps[key]=key==="set_tilt_position";
  entity.actions=[{service:"cover.set_cover_tilt_position",fields:{}}];
  editor._hass.states["cover.blind"].attributes.supported_features=128;
  assert.equal(editor.coverControlAvailability().ready,true);
  editor._status.cover_panel_version=0;
  assert.equal(editor.coverControlAvailability().ready,false);
  editor._status.cover_panel_version=1;entity.actions=[];
  assert.equal(editor.coverControlAvailability().ready,false);
});

test("cover panel review tolerates position feedback and rejects changed class or capabilities",()=>{
  const fresh=coverPanelEditor();fresh.requestLightControl("cover");
  fresh._hass.states["cover.blind"].state="opening";
  fresh._hass.states["cover.blind"].attributes.current_position=47;
  fresh._hass.states["cover.blind"].attributes.current_tilt_position=70;
  assert.equal(fresh.confirmLightControl(),true);
  for(const change of [e=>{e.profile.schema_cover_panel=false;},e=>{e._status.cover_panel_version=0;},e=>{e._status.cover_stop_version=0;},e=>{e._entityIndex.get("cover.blind").cover_panel.device_class="garage";},e=>{e._hass.states["cover.blind"].attributes.device_class="garage";},e=>{e._entityIndex.get("cover.blind").actions=[];},e=>{e._entityIndex.get("cover.blind").cover_panel.caps.stop_tilt=false;}]) {
    const editor=coverPanelEditor(),before=clone(editor._draft);editor.requestLightControl("cover");change(editor);
    assert.equal(editor.confirmLightControl(),false);assert.deepEqual(clone(editor._draft),before);
  }
});

test("malformed detail metadata does not silently offer an incomplete cover panel",()=>{
  for(const change of [e=>{e._entityIndex.get("cover.blind").cover_panel.version=true;},e=>{e._entityIndex.get("cover.blind").cover_panel.device_class="guess";},e=>{e._entityIndex.get("cover.blind").cover_panel.caps.set_position=1;},e=>{delete e._entityIndex.get("cover.blind").cover_panel.caps.open_tilt;},e=>{e._hass.states["cover.blind"].attributes.supported_features=11;}]) {
    const editor=coverPanelEditor();change(editor);assert.equal(editor.coverControlAvailability().ready,false);
  }
});

function detailedPanelEditor(family="light") {
 const e=lightEditor(),card=e.cardAt(2);card.entity_id=family+".office";
 Object.assign(e.profile,{schema_light_detail:true,schema_climate_panel:true,schema_control_types:["light","number","choice","panel"]});
 Object.assign(e._status,{entity_control_status:"ready",native_control_types:["entity_control_v1"],control_kinds:["light","number","choice","panel"],detail_version:1,light_detail_version:1,climate_panel_version:1,panel_version:1,panel_types:["timer","remote","power"]});
 const attrs=family==="light"?{brightness:128,supported_features:4,supported_color_modes:["color_temp"],min_color_temp_kelvin:2000,max_color_temp_kelvin:6500,effect_list:["None","Rainbow"]}:
   {supported_features:17,min_temp:7,max_temp:35,target_temp_step:.5,temperature:21,current_temperature:20.5,hvac_modes:["off","heat"],preset_modes:["eco","comfort"]};
 e._hass.states[card.entity_id]={state:family==="light"?"on":"heat",attributes:attrs};
 e._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:family,available:true,actions:[],
   [family==="light"?"light_detail":"climate_panel"]:{version:1,facets:family==="light"?3:13,fingerprint:"d".repeat(64),facet_reasons:{},
     state:family==="light"?{on:true,brightness_pct:50,caps:{turn_on:true,turn_off:true,brightness:true}}:{mode:"heat",unit:"°C",target:"21",current:"20.5",editable:true}}});
 return e;
}

test("Light detail and full Climate are explicit reviewed actions, never service previews",()=>{
 for(const [family,kind,action] of [["light","lightdetail",{kind:"control",control:"light",detail:1}],["climate","climatepanel",{kind:"control",control:"panel",property:"climate"}]]) {
  const e=detailedPanelEditor(family),before=clone(e._draft);
  assert.equal(e.detailControlAvailability().ready,true);assert.match(e.inspectorMarkup(),new RegExp(`value="control-${kind}"`));
  e.editField(actionInput("control-"+kind));assert.deepEqual(clone(e._draft),before);
  assert.match(e.modalMarkup(),/full device view/);assert.equal(e.confirmLightControl(),true);assert.deepEqual(clone(e.cardAt(2).action),action);
  assert.equal(e.cardControlKind(e.cardAt(2)),kind);e.history("undo");assert.deepEqual(clone(e._draft),before);
 }
});

test("A supported detail profile keeps the existing Light binding selected until explicit migration",()=>{
 const e=detailedPanelEditor();e._draft.version=3;e.cardAt(2).action={kind:"control",control:"light"};
 const html=e.inspectorMarkup();assert.match(html,/<option value="control" selected/);assert.match(html,/<option value="control-lightdetail">/);
 assert.equal(e.cardControlKind(e.cardAt(2)),"light");assert.equal(e.requestLightControl("lightdetail"),true);assert.equal(e.confirmLightControl(),true);
 assert.deepEqual(clone(e.cardAt(2).action),{kind:"control",control:"light",detail:1});
 assert.equal(e.requestLightControl("lightdetail"),false);
});

test("Detail review tolerates live target and state changes without requiring a refreshed catalogue",()=>{
 for(const [family,kind] of [["light","lightdetail"],["climate","climatepanel"]]) {
  const e=detailedPanelEditor(family);e.requestLightControl(kind);const state=e._hass.states[e.cardAt(2).entity_id];
  state.state="off";state.attributes[family==="light"?"brightness":"current_temperature"]=family==="light"?70:20.9;
  assert.equal(e.confirmLightControl(),true);
 }
 for(const change of [e=>e._status.light_detail_version=0,e=>e._status.detail_version=0,e=>e.profile.schema_light_detail=false,e=>e._entityIndex.get("light.office").light_detail.fingerprint="e".repeat(64),e=>e._hass.states["light.office"].attributes.effect_list.reverse(),e=>e._hass.states["light.office"].state="unavailable"]) {
  const e=detailedPanelEditor(),before=clone(e._draft);e.requestLightControl("lightdetail");change(e);assert.equal(e.confirmLightControl(),false);assert.deepEqual(clone(e._draft),before);
 }
});

test("Climate may open as a read-only range or offline view without inventing a single target",()=>{
 for(const observed of ["heat_cool","auto","unknown","unavailable"]) {
  const e=detailedPanelEditor("climate"),entity=e.entityFor("climate.office"),meta=entity.climate_panel;
  e._hass.states["climate.office"].state=observed;entity.available=false;meta.facets=0;
  meta.state={mode:observed,unit:null,target:"",current:"",low:"18",high:"24",domain:null,index:null,editable:false};
  meta.facet_reasons={temperature:"unsupported_metadata",hvac_mode:"unsupported_service"};
  assert.equal(e.detailControlAvailability().ready,true);assert.equal(e.requestLightControl("climatepanel"),true);assert.equal(e.confirmLightControl(),true);
 }
 const bad=detailedPanelEditor("climate");delete bad._hass.states["climate.office"];assert.equal(bad.detailControlAvailability().ready,false);
});

test("Detail bindings survive loss of negotiation but stored actions reject malformed profile fields",()=>{
 for(const [family,kind] of [["light","lightdetail"],["climate","climatepanel"]]) {
  const e=detailedPanelEditor(family);e.requestLightControl(kind);e.confirmLightControl();
  const record={version:1,profile:e.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:e.profile.id,cards:clone(e._draft.cards)}};
  assert.doesNotThrow(()=>e.validateStoredDraft(record));e._status.detail_version=0;
  assert.match(e.inspectorMarkup(),new RegExp(`value="control-${kind}" selected disabled`));assert.doesNotThrow(()=>e.validateStoredDraft(record));
  for(const patch of [{detail:true},{detail:2},{detail:"1"},{initial_duration:120},{service:"light.turn_on"}]) {
   const bad=clone(record);Object.assign(bad.layout.cards.find(c=>c.slot===2).action,patch);assert.throws(()=>e.validateStoredDraft(bad));
  }
  const bad=clone(record);bad.layout.cards.find(c=>c.slot===2).entity_id="switch.office";assert.throws(()=>e.validateStoredDraft(bad));
 }
});

test("Detail metadata masks and reason maps remain closed and bounded",()=>{
 for(const family of ["light","climate"]) {
  for(const change of [m=>m.version=true,m=>m.facets=family==="light"?4:128,m=>m.facets=-1,m=>m.fingerprint="short",m=>m.facet_reasons={arbitrary:"unsupported_service"},m=>m.facet_reasons={temperature:"future_reason"},m=>m.facet_reasons=[]]) {
   const e=detailedPanelEditor(family);change(e.entityFor(family+".office")[family==="light"?"light_detail":"climate_panel"]);assert.equal(e.detailControlAvailability().ready,false);
  }
 }
});

function familyPanelEditor(family="timer",domain=family==="power"?"switch":family) {
 const e=lightEditor(),card=e.cardAt(2);card.entity_id=`${domain}.office`;
 e.profile.schema_control_types.push("panel");e.profile.schema_panel_control=true;e.profile.schema_panel_types=["timer","remote","power"];
 Object.assign(e._status,{entity_control_status:"ready",native_control_types:["entity_control_v1"],control_kinds:["light","panel"],panel_version:1,panel_types:["timer","remote","power"]});
 const caps=family==="timer"?{start:true,pause:true,cancel:true,initial_duration:null}:family==="remote"?{turn_on:true,turn_off:true,activities:["Music","Cinema"]}:{turn_on:true,turn_off:true,device_class:"outlet"};
 const state=family==="timer"?{phase:"idle",duration_seconds:120,remaining_seconds:null,finishes_at_utc_s:null,sampled_at_utc_s:1793790000}:family==="remote"?{power:"off",activity_index:null}:{power:"off"};
 e._hass.states[card.entity_id]={state:family==="timer"?"idle":"off",attributes:family==="remote"?{supported_features:4,activity_list:["Music","Cinema"],current_activity:"Music"}:family==="power"?{device_class:"outlet"}:{duration:"0:02:00"}};
 e._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain,available:true,panel_control:{version:1,panel_type:family,caps,state,available:true,eligible_actions:family==="timer"?17:1},actions:(family==="timer"?["start","pause","cancel"]:["turn_on","turn_off"]).map(name=>({service:`${domain}.${name}`,fields:{}}))});
 return e;
}

test("Timer Remote and Power panels require explicit draft review without live commands",()=>{
 for(const [family,domain] of [["timer","timer"],["remote","remote"],["power","switch"],["power","input_boolean"]]) {
  const e=familyPanelEditor(family,domain),before=clone(e._draft);
  assert.equal(e.panelControlAvailability().ready,true);assert.match(e.inspectorMarkup(),new RegExp(`value="control-${family}panel"`));
  e.editField(actionInput(`control-${family}panel`));assert.deepEqual(clone(e._draft),before);
  assert.match(e.modalMarkup(),/Use the device panel/);assert.equal(e.confirmLightControl(),true);
  assert.deepEqual(clone(e.cardAt(2).action),{kind:"control",control:"panel",property:family});
  assert.equal(e.cardControlKind(e.cardAt(2)),family+"panel");e.history("undo");assert.deepEqual(clone(e._draft),before);
 }
});

test("Timer migration preserves a deliberate duration and local editing never starts it",()=>{
 const e=familyPanelEditor();e.cardAt(2).action={kind:"service",service:"timer.start",data:{duration:120}};
 e.requestLightControl("timerpanel");assert.equal(e.confirmLightControl(),true);assert.equal(e.cardAt(2).action.initial_duration,120);
 assert.match(e.inspectorMarkup(),/data-field="panel-duration"/);assert.match(e.inspectorMarkup(),/value="120"/);
 const input=value=>({dataset:{field:"panel-duration"},value,removeAttribute(){},setAttribute(){}});
 e.editField(input("3600"));assert.equal(e.cardAt(2).action.initial_duration,3600);
 for(const value of ["0","86401","1.5","-1","NaN"," 12","1e2"]) {e.editField(input(value));assert.equal(e.cardAt(2).action.initial_duration,3600);}
 e.editField(input(""));assert.equal(Object.hasOwn(e.cardAt(2).action,"initial_duration"),false);
 assert.equal(e._hass.states["timer.office"].state,"idle");
});

test("Panel reviews track capabilities and negotiated families but tolerate countdown telemetry",()=>{
 const ok=familyPanelEditor();ok.requestLightControl("timerpanel");const meta=ok.entityFor("timer.office").panel_control;
 // A normal hass update does not refresh the catalogue while review is open.
 ok._hass.states["timer.office"].state="active";
 ok._hass.states["timer.office"].attributes.remaining="0:01:27";
 assert.equal(ok.confirmLightControl(),true);
 for(const family of ["remote","power"]) {
  const e=familyPanelEditor(family);assert.equal(e.requestLightControl(family+"panel"),true);
  e._hass.states[e.cardAt(2).entity_id].state="on";
  assert.equal(e.confirmLightControl(),true);
 }
 for(const change of [e=>e._status.panel_types=["remote"],e=>e._status.panel_version=0,e=>e.profile.schema_panel_types=["power"],e=>e._status.control_kinds=["light"],e=>e.entityFor("timer.office").panel_control.caps.cancel=false,e=>e.entityFor("timer.office").actions=[],e=>e._hass.states["timer.office"].state="unavailable"]) {
  const e=familyPanelEditor(),before=clone(e._draft);assert.equal(e.requestLightControl("timerpanel"),true);change(e);assert.equal(e.confirmLightControl(),false);assert.deepEqual(clone(e._draft),before);
 }
});

test("Panel stored drafts retain offline intent and enforce exact family and duration boundaries",()=>{
 for(const family of ["timer","remote","power"]) {
  const e=familyPanelEditor(family);e.requestLightControl(family+"panel");e.confirmLightControl();
  const record={version:1,profile:e.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:e.profile.id,cards:clone(e._draft.cards)}};
  assert.doesNotThrow(()=>e.validateStoredDraft(record));e._status.panel_version=0;
  assert.match(e.inspectorMarkup(),new RegExp(`value="control-${family}panel" selected disabled`));assert.doesNotThrow(()=>e.validateStoredDraft(record));
  for(const patch of [{property:"info"},{service:"switch.turn_on"},{initial_duration:family==="timer"?0:120},{initial_duration:true},{initial_duration:null},{initial_duration:"120"}]) {
   const invalid=clone(record);Object.assign(invalid.layout.cards.find(c=>c.slot===2).action,patch);assert.throws(()=>e.validateStoredDraft(invalid));
  }
  const invalid=clone(record);invalid.layout.cards.find(c=>c.slot===2).entity_id="light.room";assert.throws(()=>e.validateStoredDraft(invalid));
 }
});

test("Remote panel accepts off with retained activity and rejects malformed or changed catalogues",()=>{
 const e=familyPanelEditor("remote");assert.equal(e.panelControlAvailability().ready,true);
 e.requestLightControl("remotepanel");e._hass.states["remote.office"].attributes.activity_list.reverse();assert.equal(e.confirmLightControl(),false);
 for(const change of [m=>m.caps.activities=["same","same"],m=>m.caps.activities=Array(9).fill("x"),m=>m.caps.activities=["x".repeat(33)],m=>m.caps.activities=["unknown"],m=>m.caps.turn_on=1,m=>m.caps.extra=true,m=>m.panel_type="power"]) {
  const v=familyPanelEditor("remote");change(v.entityFor("remote.office").panel_control);assert.equal(v.panelControlAvailability().ready,false);
 }
 const partial=familyPanelEditor("remote"),m=partial.entityFor("remote.office").panel_control;
 m.caps.activities=[];delete partial._hass.states["remote.office"].attributes.supported_features;assert.equal(partial.panelControlAvailability().ready,true);
});

test("Power panel preserves partial service support and never offers a toggle fallback",()=>{
 const e=familyPanelEditor("power"),entity=e.entityFor("switch.office");entity.panel_control.caps.turn_off=false;entity.actions=[{service:"switch.turn_on"}];
 assert.equal(e.panelControlAvailability().ready,true);entity.actions=[{service:"switch.toggle"}];assert.equal(e.panelControlAvailability().ready,false);
 for(const change of [m=>m.caps.device_class="guessed",m=>m.caps.turn_on="true",m=>m.available=false,m=>m.eligible_actions=4]) {
  const v=familyPanelEditor("power");change(v.entityFor("switch.office").panel_control);assert.equal(v.panelControlAvailability().ready,false);
 }
});

function robotPanelEditor(type="vacuum") {
  const editor=lightEditor(),card=editor.cardAt(2),mower=type==="lawn_mower";
  card.entity_id=`${type}.office`;
  editor.profile.schema_control_types=["light","number","choice","cover","robot"];
  editor.profile.schema_robot_control=true;
  editor._status={...editor._status,entity_control_status:"ready",robot_control_supported:true,
    native_control_types:["entity_control_v1"],control_kinds:["light","number","choice","cover","robot"]};
  editor._hass.states[card.entity_id]={state:"docked",attributes:{supported_features:mower?7:32700,
    ...(mower?{}:{fan_speed_list:["min","medium","max"],fan_speed:"min"})}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:type,available:true,
    actions:(mower?["start_mowing","pause","dock"]:["start","pause","stop","return_to_base","locate","clean_spot","set_fan_speed","clean_area"])
      .map(name=>({service:`${type}.${name}`,fields:{}})),
    robot_control:{version:1,robot_type:type,catalogue_fingerprint:"a".repeat(64),area_reason:mower?"unsupported":null,
      caps:{actions:mower?11:63,speeds:mower?[]:["min","medium","max"],areas:mower?[]:["Salon","Kuchnia"]},
      state:{activity:"docked",available:true,speed_index:mower?null:0,battery_percent:null,eligible_actions:mower?1:49,area_enabled:!mower}}});
  return editor;
}

test("robot and mower launchers are reviewed drafts with Undo and no service preview",()=>{
  for(const type of ["vacuum","lawn_mower"]){
    const editor=robotPanelEditor(type),before=clone(editor._draft);
    assert.equal(editor.robotPanelAvailability().ready,true);
    assert.match(editor.inspectorMarkup(),/value="control-robot"/);
    editor.editField(actionInput("control-robot"));
    assert.equal(editor._pending.controlKind,"robot");assert.deepEqual(clone(editor._draft),before);
    assert.match(editor.modalMarkup(),/Use the device panel/);
    assert.equal(editor.confirmLightControl(),true);
    assert.deepEqual(clone(editor.cardAt(2).action),{kind:"control",control:"robot"});
    editor.history("undo");assert.deepEqual(clone(editor._draft),before);
  }
});

test("robot review tolerates telemetry but rejects new private room mappings and lost capabilities",()=>{
  const current=robotPanelEditor();current.requestLightControl("robot");
  current._hass.states["vacuum.office"].state="cleaning";
  current._entityIndex.get("vacuum.office").robot_control.state.battery_percent=84;
  assert.equal(current.confirmLightControl(),true);
  for(const change of [e=>{e._status.robot_control_supported=false;},e=>{e.profile.schema_robot_control=false;},
    e=>{e._status.control_kinds=[];},e=>{e._entityIndex.get("vacuum.office").actions=[];},
    e=>{e._entityIndex.get("vacuum.office").robot_control.catalogue_fingerprint="b".repeat(64);},
    e=>{e._hass.states["vacuum.office"].state="unavailable";},
    e=>{e._hass.states["vacuum.office"].attributes.fan_speed_list=["Eco"];}
  ]){
    const editor=robotPanelEditor(),before=clone(editor._draft);editor.requestLightControl("robot");change(editor);
    assert.equal(editor.confirmLightControl(),false);assert.deepEqual(clone(editor._draft),before);
  }
});

test("robot catalogue validation rejects truncation and unsupported mower facets independently",()=>{
  for(const mutate of [m=>m.caps.areas=Array.from({length:9},(_,i)=>String(i)),m=>m.caps.speeds=["same","same"],
    m=>m.caps.areas=["x".repeat(33)],m=>m.catalogue_fingerprint="bad",m=>m.caps.actions=64,m=>m.robot_type="lawn_mower"]){
    const editor=robotPanelEditor();mutate(editor._entityIndex.get("vacuum.office").robot_control);
    assert.equal(editor.robotPanelAvailability().ready,false);
  }
  const missing=robotPanelEditor(),meta=missing._entityIndex.get("vacuum.office").robot_control;
  meta.caps.areas=[];meta.area_reason="too_many_areas";meta.state.speed_index=null;meta.state.battery_percent=null;
  assert.equal(missing.robotPanelAvailability().ready,true);
  for(const [mask,feature,service] of [[1,1,"start_mowing"],[2,2,"pause"],[8,4,"dock"]]){
    const editor=robotPanelEditor("lawn_mower"),entity=editor._entityIndex.get("lawn_mower.office");
    entity.robot_control.caps.actions=mask;entity.actions=[{service:`lawn_mower.${service}`}];
    editor._hass.states["lawn_mower.office"].attributes.supported_features=feature;
    assert.equal(editor.robotPanelAvailability().ready,true);
    editor._hass.states["lawn_mower.office"].attributes.supported_features=0;
    assert.equal(editor.robotPanelAvailability().ready,false);
  }
  const mower=robotPanelEditor("lawn_mower");mower._entityIndex.get("lawn_mower.office").robot_control.caps.actions|=4;
  assert.equal(mower.robotPanelAvailability().ready,false);
});

test("unavailable robot rooms explain the missing facet without hiding remaining controls",()=>{
  for(const [reason,text] of [["too_many_areas",/up to eight/],["no_mapped_areas",/No rooms are mapped/],
    ["area_labels_unsupported",/too long or ambiguous/],["unsupported",/does not expose a supported room selector/]]){
    const editor=robotPanelEditor(),meta=editor._entityIndex.get("vacuum.office").robot_control;
    meta.caps.areas=[];meta.area_reason=reason;
    assert.equal(editor.robotPanelAvailability().ready,true);
    assert.match(editor.inspectorMarkup(),text);
    editor.requestLightControl("robot");assert.match(editor.modalMarkup(),text);
    assert.equal(editor.confirmLightControl(),true);
  }
  const mower=robotPanelEditor("lawn_mower");
  assert.match(mower.inspectorMarkup(),/supported mowing, pause and dock controls/);
  assert.doesNotMatch(mower.t(mower.robotPanelAvailability().reason),/suction|rooms/);
});

test("robot stored binding survives offline recovery and legacy suction can migrate explicitly",()=>{
  const editor=robotPanelEditor();editor.cardAt(2).action={kind:"control",control:"choice",property:"fan_speed"};editor._draft.version=3;
  assert.match(editor.inspectorMarkup(),/value="control-robot"/);
  editor.requestLightControl("robot");assert.equal(editor.confirmLightControl(),true);
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}};
  assert.doesNotThrow(()=>editor.validateStoredDraft(record));
  const wrong=clone(record);wrong.layout.cards[1].entity_id="switch.robot";
  assert.throws(()=>editor.validateStoredDraft(wrong));
  editor._status.control_kinds=["light"];
  assert.match(editor.inspectorMarkup(),/value="control-robot" selected disabled/);
});

function humidityPanelEditor() {
  const editor=lightEditor(),card=editor.cardAt(2);card.entity_id="humidifier.office";
  editor.profile.schema_control_types=["light","number","choice","cover","fan","humidifier"];
  editor._status={...editor._status,entity_control_status:"ready",native_control_types:["entity_control_v1"],control_kinds:["light","number","choice","cover","fan","humidifier"]};
  editor._hass.states[card.entity_id]={state:"on",attributes:{supported_features:1,humidity:55,current_humidity:44.5,min_humidity:30,max_humidity:80,available_modes:["Normal","Eco"],mode:"Normal",device_class:"humidifier"}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"humidifier",available:true,
    actions:["turn_on","turn_off","set_humidity","set_mode"].map(name=>({service:`humidifier.${name}`,fields:{}})),
    humidifier_control:{caps:{turn_on:true,turn_off:true,modes:["Normal","Eco"]},device_class:"humidifier",
      humidity_domain:{schema:"numeric_steps_v1",min:"30",max:"80",step:"1",unit:"%",max_index:50}}});
  return editor;
}

test("humidity panel is a reviewed launcher distinct from legacy mode selection",()=>{
  const editor=humidityPanelEditor(),before=clone(editor._draft);
  assert.equal(editor.humidityPanelAvailability().ready,true);
  assert.match(editor.inspectorMarkup(),/value="control-humiditypanel"/);
  editor.editField(actionInput("control-humiditypanel"));
  assert.equal(editor._pending.controlKind,"humiditypanel");assert.deepEqual(clone(editor._draft),before);
  assert.match(editor.modalMarkup(),/Use the humidity panel/);
  assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(editor.cardAt(2).action),{kind:"control",control:"humidifier"});
  assert.match(editor.inspectorMarkup(),/value="control-humiditypanel" selected/);
  assert.equal(editor.requestLightControl("humiditypanel"),false);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);
});

test("humidity panel remains available with power only and missing measurements",()=>{
  const editor=humidityPanelEditor(),meta=editor._entityIndex.get("humidifier.office");
  meta.humidifier_control.humidity_domain=null;meta.humidifier_control.caps.modes=[];
  meta.actions=meta.actions.filter(action=>action.service.includes("turn_"));
  delete editor._hass.states["humidifier.office"].attributes.humidity;
  delete editor._hass.states["humidifier.office"].attributes.current_humidity;
  assert.equal(editor.humidityPanelAvailability().ready,true);
  assert.equal(editor.requestLightControl("humiditypanel"),true);
  assert.equal(editor.confirmLightControl(),true);
  const fixed=humidityPanelEditor();
  fixed._entityIndex.get("humidifier.office").humidifier_control.humidity_domain={schema:"numeric_steps_v1",min:"50",max:"50",step:"1",unit:"%",max_index:0};
  assert.equal(fixed.humidityPanelAvailability().ready,true);
});

test("humidity panel review ignores measurement updates but rejects changed limits and negotiation",()=>{
  const fresh=humidityPanelEditor();fresh.requestLightControl("humiditypanel");
  fresh._hass.states["humidifier.office"].attributes.current_humidity=49.2;
  assert.equal(fresh.confirmLightControl(),true);
  for(const change of [e=>{e._status.control_kinds=["light"];},e=>{e._entityIndex.get("humidifier.office").actions=[];},e=>{e._hass.states["humidifier.office"].attributes.min_humidity=40;},e=>{e._entityIndex.get("humidifier.office").humidifier_control.caps.modes=["Normal"];},e=>{e._hass.states["humidifier.office"].state="unavailable";}]) {
    const editor=humidityPanelEditor(),before=clone(editor._draft);editor.requestLightControl("humiditypanel");change(editor);
    assert.equal(editor.confirmLightControl(),false);assert.deepEqual(clone(editor._draft),before);
  }
});

test("humidity panel draft recovery preserves typed binding and offline guidance",()=>{
  const editor=humidityPanelEditor();editor.requestLightControl("humiditypanel");editor.confirmLightControl();
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}};
  assert.doesNotThrow(()=>editor.validateStoredDraft(record));
  const wrong=clone(record);wrong.layout.cards[1].entity_id="climate.office";
  assert.throws(()=>editor.validateStoredDraft(wrong));
  editor._status.control_kinds=["light","number","choice","cover","fan"];
  assert.match(editor.inspectorMarkup(),/value="control-humiditypanel" selected disabled/);
});

test("fan panel opens through an explicit draft action, preserves Undo and sends no device command",()=>{
  const editor=fanPanelEditor(),before=clone(editor._draft);
  assert.equal(editor.fanControlAvailability().ready,true);
  assert.match(editor.inspectorMarkup(),/value="control-fan"/);
  editor.editField(actionInput("control-fan"));
  assert.equal(editor._pending.controlKind,"fan");assert.deepEqual(clone(editor._draft),before);
  assert.match(editor.modalMarkup(),/Use the fan panel/);
  assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(editor.cardAt(2).action),{kind:"control",control:"fan"});
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);
});

test("fan panel review rejects lost negotiation or capabilities and does not replace the draft",()=>{
  for(const change of [e=>{e._status.control_kinds=["light","number"];},e=>{e.profile.schema_control_types=["light"];},e=>{e._entityIndex.get("fan.office").actions=[];},e=>{e._hass.states["fan.office"].state="unavailable";},e=>{e.cardAt(2).visible=false;}]) {
    const editor=fanPanelEditor();editor.requestLightControl("fan");change(editor);const before=clone(editor._draft);
    assert.equal(editor.confirmLightControl(),false);assert.deepEqual(clone(editor._draft),before);
  }
  const editor=fanPanelEditor(),before=clone(editor._draft);editor.requestLightControl("fan");
  editor._entityIndex.get("fan.office").fan_control.caps.presets=["Eco"];
  assert.equal(editor.confirmLightControl(),false);assert.deepEqual(clone(editor._draft),before);
});

test("fan panel drafts retain kind and reject a different entity domain",()=>{
  const editor=fanPanelEditor();editor.requestLightControl("fan");editor.confirmLightControl();
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}};
  assert.doesNotThrow(()=>editor.validateStoredDraft(record));
  const wrong=clone(record);wrong.layout.cards[1].entity_id="switch.fan";
  assert.throws(()=>editor.validateStoredDraft(wrong));
  editor._status.control_kinds=["light","number","choice","cover"];
  assert.match(editor.inspectorMarkup(),/value="control-fan" selected disabled/);
});

test("cover controls are an explicit reviewed v3 choice with one undo and no preview action",()=>{
  const editor=coverEditor(),before=clone(editor._draft);assert.equal(editor.coverControlAvailability().ready,true);assert.match(editor.inspectorMarkup(),/value="control-cover"/);
  editor.editField(actionInput("control-cover"));assert.equal(editor._pending.controlKind,"cover");assert.match(editor.modalMarkup(),/Use cover controls/);assert.deepEqual(clone(editor._draft),before);
  assert.equal(editor.confirmLightControl(),true);assert.deepEqual(clone(editor.cardAt(2).action),{kind:"control",control:"cover"});assert.equal(editor._draft.version,3);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);
});

test("cover readiness requires the separately echoed priority Stop version",()=>{
  for(const value of [undefined,0,2,true,"1"]) {
    const editor=coverEditor();editor._status.cover_stop_version=value;
    assert.equal(editor.coverControlAvailability().ready,false);assert.equal(editor.requestLightControl("cover"),false);
  }
});

test("cover admission requires complete matching negotiation and current supported entity actions",()=>{
  for(const change of [e=>{e._status.control_kinds=["light","number","choice"];},e=>{e._status.device_available=false;},e=>{e._entityIndex.get("cover.blind").cover_control.caps.stop=1;},e=>{e._entityIndex.get("cover.blind").cover_control.caps.extra=true;},e=>{e._entityIndex.get("cover.blind").actions=[];},e=>{e._hass.states["cover.blind"].state="unknown";},e=>{e._hass.states["cover.blind"].attributes.supported_features=0;},e=>{e.cardAt(2).type="sensor";}]) {
    const editor=coverEditor();change(editor);assert.equal(editor.coverControlAvailability().ready,false);assert.equal(editor.requestLightControl("cover"),false);
  }
});

test("cover review survives valid motion and position changes but refuses changed capabilities",()=>{
  const editor=coverEditor();editor.requestLightControl("cover");editor._hass.states["cover.blind"].state="opening";editor._hass.states["cover.blind"].attributes.current_position=45;
  assert.equal(editor.confirmLightControl(),true);
  const stale=coverEditor(),before=clone(stale._draft);stale.requestLightControl("cover");stale._entityIndex.get("cover.blind").cover_control.caps.stop=false;
  assert.equal(stale.confirmLightControl(),false);assert.deepEqual(clone(stale._draft),before);
});

test("cover drafts, copy and recovery preserve the explicit kind with old-native passive guidance",()=>{
  const editor=coverEditor();editor.requestLightControl("cover");editor.confirmLightControl();
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}};
  assert.doesNotThrow(()=>editor.validateStoredDraft(record));assert.equal(editor.copyCard(2),true);assert.equal(editor.pasteCard(13),true);assert.deepEqual(clone(editor.cardAt(13).action),{kind:"control",control:"cover"});
  editor._selectedSlot=2;editor._status.control_kinds=["light","number","choice"];assert.match(editor.inspectorMarkup(),/value="control-cover" selected disabled/);
  const bad=clone(record);bad.layout.cards[1].entity_id="light.room";assert.throws(()=>editor.validateStoredDraft(bad));
});

test("selected-cover readiness repaints when a live source becomes available even though Light readiness stays false",()=>{
  const editor=coverEditor();editor._hass.states["cover.blind"].state="unknown";let paints=0;editor.paintControlAvailability=()=>{paints++;};
  const next={...editor._hass,states:{...editor._hass.states,"cover.blind":{state:"closed",attributes:{supported_features:11,current_position:0}}}};
  assert.equal(editor.lightControlAvailability().ready,false);editor.hass=next;assert.equal(paints,1);assert.equal(editor.coverControlAvailability().ready,true);
});

function stateLabelEditor() {
  const editor=makeEditor();editor.profile.schema_state_labels=true;editor._selectedSlot=2;
  Object.assign(editor.cardAt(2),{type:"sensor",entity_id:"input_select.mode",action:{kind:"none"}});
  editor._hass.states["input_select.mode"]={state:"Eco",attributes:{options:["Eco","Comfort","Boost"]}};
  return editor;
}

test("text helper assignment creates a passive information card and keeps user text verbatim",()=>{
  const editor=makeEditor(),entity={entity_id:"input_text.note",name:"Notatka",domain:"input_text",available:true,actions:[]};
  editor._entityIndex.set(entity.entity_id,entity);editor._hass.states[entity.entity_id]={state:"Kurier o 15:30",attributes:{mode:"text"}};
  assert.equal(editor.assignEntity(entity.entity_id,13),true);assert.equal(editor.cardAt(13).type,"sensor");assert.deepEqual(clone(editor.cardAt(13).action),{kind:"none"});
  editor._hass.formatEntityState=()=>"Should not translate user content";assert.equal(editor.stateText(editor.cardAt(13)),"Kurier o 15:30");
  editor._hass.states[entity.entity_id].state="  <b>Notatka</b>\n  domowa  ";assert.equal(editor.stateText(editor.cardAt(13)),"<b>Notatka</b> domowa");
  editor._hass.states[entity.entity_id].state="x".repeat(200);assert.equal(editor.stateText(editor.cardAt(13)).length,40);
});

test("changing a selected helper to password masks card, mapping and already cached library values",()=>{
  const editor=stateLabelEditor(),card=editor.cardAt(2);card.entity_id="input_text.note";card.state_labels={"QA-value":"Exposed"};
  const entity={entity_id:card.entity_id,state:"old plain text",available:true};editor._hass.states[card.entity_id]={state:"QA-value",attributes:{mode:"password"}};
  assert.equal(editor.stateText(card),"Hidden text");assert.deepEqual(clone(editor.libraryState(entity)),{state:"Hidden text",available:false});
  delete editor._hass.states[card.entity_id].attributes.mode;assert.equal(editor.stateText(card),"Hidden text");
  editor._hass.states[card.entity_id].attributes.mode="text";assert.equal(editor.stateText(card),"Exposed");
});

test("information cards do not advertise unrelated actuator controls",()=>{
  const editor=stateLabelEditor();assert.doesNotMatch(editor.inspectorMarkup(),/Choose a visible Entity card|slider on the device/);
});

test("state label editing is a reviewed local transaction with one undo and no preview service",()=>{
  const editor=stateLabelEditor(),before=clone(editor._draft);assert.match(editor.inspectorMarkup(),/data-action="state-labels"/);
  assert.equal(editor.requestStateLabels(),true);assert.equal(editor.addStateLabel(),true);
  editor.editStateLabel(0,"key","Eco");editor.editStateLabel(0,"label","Oszczędny");
  assert.deepEqual(clone(editor._draft),before);assert.match(editor.modalMarkup(),/Source state/);
  assert.equal(editor.confirmStateLabels(),true);assert.equal(editor._undo.length,1);assert.equal(editor.stateText(editor.cardAt(2)),"Oszczędny");
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).state_labels.Eco,"Oszczędny");
});

test("label validation rejects reserved states, duplicates, unprintable text and byte overflow",()=>{
  const editor=stateLabelEditor();
  for(const rows of [[{key:"unknown",label:"OK"}],[{key:"unavailable",label:"OK"}],[{key:"Eco",label:" "}],[{key:"Eco",label:"a\nb"}],[{key:"Eco",label:"a\u202eb"}],[{key:"Eco",label:"ą".repeat(17)}],[{key:"x".repeat(33),label:"Long"}],[{key:"Eco",label:"A"},{key:"Eco",label:"B"}],Array.from({length:9},(_,i)=>({key:String(i),label:"Label"}))])assert.equal(editor.labelsFromRows(rows),null);
  assert.deepEqual(clone(editor.labelsFromRows([{key:" Eco ",label:"literal <&>"}])),{" Eco ":"literal <&>"});
  editor.requestStateLabels();editor.addStateLabel();assert.equal(editor.confirmStateLabels(),false);assert.equal(editor._undo.length,0);
});

test("label review refuses changed entry, user, card, draft, profile and saved revision",()=>{
  for(const change of [e=>{e._entryId="other";},e=>{e._selectionEpoch++;},e=>{e._hass.user={id:"other"};},e=>{e._selectedSlot=3;},e=>{e._saved.revision++;},e=>{e.cardAt(2).title="Changed";},e=>{e.profile.width++;},e=>{e._conflict=true;},e=>{e._profileStale=true;}]) {
    const editor=stateLabelEditor();editor.requestStateLabels();editor.addStateLabel();editor.editStateLabel(0,"key","Eco");editor.editStateLabel(0,"label","Oszczędny");change(editor);
    const before=clone(editor._draft);assert.equal(editor.confirmStateLabels(),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
  }
});

test("exact mappings preserve outage messages and normal HA fallback, including literal prototype keys",()=>{
  const editor=stateLabelEditor(),card=editor.cardAt(2);card.state_labels=Object.fromEntries([["Eco","Oszczędny"],["__proto__","Literal"],["unknown","Forged"]]);
  editor._hass.formatEntityState=state=>`HA ${state.state}`;
  for(const [state,expected] of [["Eco","Oszczędny"],["eco","HA eco"],["Boost","HA Boost"],["__proto__","Literal"],["constructor","HA constructor"],["unknown","HA unknown"],["unavailable",editor.t("offline")]]) {
    editor._hass.states[card.entity_id].state=state;assert.equal(editor.stateText(card),expected);
  }
});

test("label rows keep the focused input during typing and a bounded add button cannot be reenabled by paint",()=>{
  const editor=stateLabelEditor();editor.requestStateLabels();for(let i=0;i<8;i++)assert.equal(editor.addStateLabel(),true);
  assert.equal(editor.addStateLabel(),false);const focused={},add={dataset:{action:"state-label-add"},disabled:false},apply={dataset:{action:"modal-state-labels"},disabled:false};
  editor.shadowRoot.activeElement=focused;editor.shadowRoot.querySelectorAll=selector=>selector===".modal button"?[add,apply]:[];
  editor.editStateLabel(0,"key","Eco");editor.editStateLabel(0,"label","Short");assert.equal(editor.shadowRoot.activeElement,focused);assert.equal(add.disabled,true);assert.equal(apply.disabled,true);
  assert.equal(editor.removeStateLabel(0),true);assert.equal(editor._pending.rows.length,7);
});

test("labels roundtrip with copy and clear in one edit while incompatible card types discard them",()=>{
  const editor=stateLabelEditor();editor.cardAt(2).state_labels={Eco:"Oszczędny"};
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:2,profile:editor.profile.id,cards:clone(editor._draft.cards)}};
  assert.doesNotThrow(()=>editor.validateStoredDraft(record));const bad=clone(record);bad.layout.cards[1].type="entity";assert.throws(()=>editor.validateStoredDraft(bad));
  assert.equal(editor.copyCard(2),true);assert.equal(editor.pasteCard(13),true);assert.equal(editor.cardAt(13).state_labels.Eco,"Oszczędny");editor.history("undo");
  editor._selectedSlot=2;editor.requestStateLabels();editor.removeStateLabel(0);assert.equal(editor.confirmStateLabels(),true);assert.equal(editor.cardAt(2).state_labels,undefined);editor.history("undo");
  editor.editField({dataset:{field:"type"},value:"entity",removeAttribute(){},setAttribute(){}});assert.equal(editor.cardAt(2).state_labels,undefined);
});

test("label previews and form values escape literal HTML and the Polish description explains fallback",()=>{
  const editor=stateLabelEditor();editor._hass.locale.language="pl";editor.cardAt(2).state_labels={Eco:'<b>"Eco"</b>'};editor.requestStateLabels();
  const markup=editor.modalMarkup();assert.match(markup,/Opisy stanów/);assert.match(markup,/&lt;b&gt;/);assert.doesNotMatch(markup,/<b>/);
});

test("a device Number uses the existing reviewed stepper without a preview command",()=>{
  const editor=deviceNumberEditor();assert.equal(editor.numberControlAvailability().ready,true);assert.match(editor.inspectorMarkup(),/value="control-number"/);
  assert.equal(editor.requestLightControl("number"),true);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(editor.cardAt(2).action),{kind:"control",control:"number"});assert.equal(editor.cardAt(2).entity_id,"number.provider");
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}};
  assert.doesNotThrow(()=>editor.validateStoredDraft(record));assert.equal(editor.copyCard(2),true);assert.equal(editor.pasteCard(13),true);
  assert.equal(editor.cardAt(13).entity_id,"number.provider");assert.deepEqual(clone(editor.cardAt(13).action),{kind:"control",control:"number"});
});

test("provider Number admission requires its own service, live metadata and negotiated support",()=>{
  for(const change of [e=>{e._entityIndex.get("number.provider").actions[0].service="input_number.set_value";},e=>{e._entityIndex.get("number.provider").domain="input_number";},e=>{e._status.control_kinds=["light"];},e=>{e._hass.states["number.provider"].state="unknown";},e=>{delete e._entityIndex.get("number.provider").number_control;}]) {
    const editor=deviceNumberEditor();change(editor);assert.equal(editor.numberControlAvailability().ready,false);assert.equal(editor.requestLightControl("number"),false);
  }
});

test("provider Number review is invalidated when its exact step metadata changes",()=>{
  const editor=deviceNumberEditor(),before=clone(editor._draft);editor.requestLightControl("number");editor._hass.states["number.provider"].attributes.step=.5;
  assert.equal(editor.confirmLightControl(),false);assert.deepEqual(clone(editor._draft),before);
});

for (const language of ["en","pl"]) test(`selected Number inspector renders only Number hints and retains Light hints (${language})`,()=>{
  let calls=0;
  const editor=numberEditor(async()=>{calls++;throw Error("No request allowed");});
  editor._hass.locale.language=language;
  editor._draft.version=3;
  editor.cardAt(2).action={kind:"control",control:"number"};
  Object.assign(editor.cardAt(3),{entity_id:"light.room",type:"entity",action:{kind:"control",control:"light"}});
  editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);
  editor.fetchSelectedEntity=async()=>{};
  const select=slot=>{
    editor.onClick({target:{closest:()=>({dataset:{action:"slot",slot:String(slot)}})}});
    assert.equal(editor._selectedSlot,slot);
    const rendered=/<aside class="inspector" id="inspector">([\s\S]*?)<\/aside>/.exec(editor.shadowRoot.innerHTML);
    assert.ok(rendered,"actual selection renders the inspector region");
    return rendered[1];
  };
  const hints=markup=>[...markup.matchAll(/<p class="hint"[^>]*>([\s\S]*?)<\/p>/g)].map(match=>match[1]);
  const noLightTerms=language==="pl"?/światł|Włącz|Wyłącz|jasnoś/iu:/light|On\/Off|brightness/i;
  let markup=select(2);
  assert.match(markup,/class="entity-reference">input_number\.helper/);
  assert.match(markup,/<option value="control-number" selected/);
  assert.deepEqual(hints(markup),[editor.t("numberHint")]);
  assert.doesNotMatch(hints(markup).join(" "),noLightTerms);
  editor._status.entity_control_status="unconfirmed";
  markup=select(2);
  assert.deepEqual(hints(markup),[editor.t("numberUnsupported")]);
  assert.doesNotMatch(hints(markup).join(" "),noLightTerms);
  editor._status.entity_control_status="ready";
  markup=select(3);
  assert.match(markup,/class="entity-reference">light\.room/);
  assert.match(markup,/<option value="control" selected/);
  assert.deepEqual(hints(markup),[editor.t("stateColorHint"),editor.t("controlBrightness"),editor.t("controlHint")]);
  markup=select(2);
  assert.deepEqual(hints(markup),[editor.t("numberHint")]);
  assert.doesNotMatch(hints(markup).join(" "),noLightTerms);
  assert.equal(calls,0);assert.equal(editor.dirty,false);assert.equal(editor._undo.length,0);
});

test("Number explicit choice requires generic negotiation and canonical server metadata",()=>{
  const editor=numberEditor();assert.equal(editor.numberControlAvailability().ready,true);
  assert.match(editor.inspectorMarkup(),/value="control-number"/);
  for(const mutate of [e=>{e._status.native_control_types=["light_brightness_v1"];},e=>{e._status.control_kinds=["light"];},
    e=>{e._status.entity_control_status="unconfirmed";},e=>{e._entityIndex.get("input_number.helper").number_control=null;},
    e=>{e.cardAt(2).entity_id="number.provider";},e=>{e._hass.states["input_number.helper"].state="unknown";}]) {
    const candidate=numberEditor();mutate(candidate);assert.equal(candidate.numberControlAvailability().ready,false);
    assert.equal(candidate.requestLightControl("number"),false);
  }
});

test("Number and generic Light reject malformed capability profile and action collection types without throwing",()=>{
  for(const value of ["entity_control_v1",0,false,{},null]) {
    const editor=numberEditor();editor._status.native_control_types=value;
    assert.doesNotThrow(()=>editor.numberControlAvailability());assert.equal(editor.numberControlAvailability().ready,false);
  }
  for(const value of ["number",0,false,{},null]) {
    const editor=numberEditor();editor._status.control_kinds=value;
    assert.doesNotThrow(()=>editor.numberControlAvailability());assert.equal(editor.numberControlAvailability().ready,false);
    const light=lightEditor();light._status.native_control_types=["entity_control_v1"];light._status.entity_control_status="ready";light._status.control_kinds=value;
    assert.doesNotThrow(()=>light.lightControlAvailability());assert.equal(light.lightControlAvailability().ready,false);
  }
  for(const field of ["layout_versions","schema_control_types"]) for(const value of ["number,3",0,false,{},null]) {
    const editor=numberEditor();editor.profile[field]=value;
    assert.doesNotThrow(()=>editor.numberControlAvailability());assert.equal(editor.numberControlAvailability().ready,false);
  }
  for(const value of ["input_number.set_value",0,false,{},null,[null,0,"input_number.set_value"]]) {
    const editor=numberEditor();editor._entityIndex.get("input_number.helper").actions=value;
    assert.doesNotThrow(()=>editor.numberControlAvailability());assert.equal(editor.numberControlAvailability().ready,false);
  }
});

test("Number review is explicit one undoable v3 change with no service request",()=>{
  let requests=0;const editor=numberEditor(async()=>{requests++;throw Error("unexpected");});
  const before=clone(editor._draft);
  editor.editField(actionInput("control-number"));assert.equal(editor._pending.controlKind,"number");
  assert.match(editor.modalMarkup(),/Use Number controls/);assert.deepEqual(clone(editor._draft),before);
  assert.equal(editor.confirmLightControl(),true);
  assert.equal(editor._draft.version,3);assert.deepEqual(clone(editor.cardAt(2).action),{kind:"control",control:"number"});
  assert.equal(requests,0);assert.equal(editor._undo.length,1);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);
});

test("Number consent refuses metadata kind entry and profile changes and does not follow numeric state churn",()=>{
  for(const mutate of [e=>{e._hass.states["input_number.helper"].attributes.step=0.5;},e=>{e._hass.states["input_number.helper"].attributes.unit_of_measurement="W";},
    e=>{e._status.control_kinds=["light"];},e=>{e._entryId="screen-b";},e=>{e.profile.schema_control_types=["light"];},e=>{e.cardAt(2).visible=false;}]) {
    const editor=numberEditor();assert.equal(editor.requestLightControl("number"),true);mutate(editor);
    assert.equal(editor.lightControlReviewCurrent(),false);assert.equal(editor.confirmLightControl(),false);
    assert.deepEqual(clone(editor.cardAt(2).action),{kind:"default"});
  }
  const editor=numberEditor();editor.requestLightControl("number");editor._hass.states["input_number.helper"].state="0.25";
  assert.equal(editor.lightControlReviewCurrent(),true);
});

test("saved Number survives unsupported firmware and unrelated Save without default or service fallback",async()=>{
  const requests=[],editor=numberEditor(async request=>{requests.push(clone(request));return {layout:{...clone(request.layout),revision:5},status:{device_available:false}};});
  editor._draft.version=editor._saved.version=3;editor.cardAt(2).action={kind:"control",control:"number"};
  editor._saved.cards[1]=clone(editor.cardAt(2));editor._status={device_available:false};
  assert.match(editor.inspectorMarkup(),/value="control-number" selected disabled/);
  assert.equal(editor.requestLightControl("number"),false);
  editor.mutate(()=>{editor.cardAt(2).title="Retained Number";});assert.equal(await editor.save(),true);
  assert.equal(requests.length,1);assert.equal(requests[0].type,"atmosfera_echo_hub/layout/save");
  assert.deepEqual(requests[0].layout.cards[1].action,{kind:"control",control:"number"});
});

test("Number local recovery is exact and copied v3 controls retain kind through undo",()=>{
  const editor=numberEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"number"};
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}};
  assert.doesNotThrow(()=>editor.validateStoredDraft(clone(record)));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="sensor.provider";},r=>{r.layout.cards[1].action.token="private";}]) {
    const bad=clone(record);mutate(bad);assert.throws(()=>editor.validateStoredDraft(bad));
  }
  assert.equal(editor.copyCard(2),true);assert.equal(editor.pasteCard(13),true);
  assert.deepEqual(clone(editor.cardAt(13).action),{kind:"control",control:"number"});
  editor.history("undo");assert.equal(editor.cardAt(13),undefined);
});

test("generic-only Light remains eligible with its unchanged Light policy",()=>{
  const editor=lightEditor();editor._status.native_control_types=["entity_control_v1"];
  editor._status.entity_control_status="ready";editor._status.control_kinds=["light","number"];
  assert.equal(editor.lightControlAvailability().ready,true);assert.equal(editor.requestLightControl(),true);
  assert.equal(editor.confirmLightControl(),true);assert.deepEqual(clone(editor.cardAt(2).action),{kind:"control",control:"light"});
  editor._status.control_kinds=["number"];assert.equal(editor.lightControlAvailability().ready,false);
});

test("Number PL review escapes untrusted titles and uses no locale numeric command",()=>{
  const editor=numberEditor();editor._hass.locale.language="pl";editor.cardAt(2).title="<img onerror=bad>";
  editor.requestLightControl("number");const markup=editor.modalMarkup();
  assert.match(markup,/Użyć sterowania liczbą/);assert.match(markup,/&lt;img/);assert.doesNotMatch(markup,/<img/);
  assert.equal(editor._pending.controlKind,"number");
});

test("Number export/import keeps exact typed action through backend dry-run and explicit draft acceptance",async()=>{
  const requests=[],saved={version:3,profile:profile.id,revision:4,cards:[card("helper",2,"input_number.helper")]};
  saved.cards[0].action={kind:"control",control:"number"};
  const backup={format:"atmosfera-layout",version:1,layout:{version:3,profile:profile.id,cards:clone(saved.cards)}};
  const editor=numberEditor(async request=>{requests.push(clone(request));
    if(request.type.endsWith("/export")) return {backup:clone(backup)};
    if(request.type.endsWith("/import")) return {layout:clone(saved),warnings:[]};
    throw Error("unexpected service");
  });
  let clicked=0,downloaded;
  const oldDocument=context.document,oldTimeout=context.window.setTimeout,oldURL=context.URL;
  context.document={createElement(){return {click(){clicked++;},remove(){}};},body:{append(){}}};
  context.URL={createObjectURL(blob){downloaded=blob;return "blob:test";},revokeObjectURL(){}};
  context.window.setTimeout=callback=>callback();
  try {
    await editor.exportSaved();assert.equal(clicked,1);assert.deepEqual(JSON.parse(await downloaded.text()),backup);
    assert.equal(await editor.importText(JSON.stringify(backup)),true);
    assert.equal(requests[1].dry_run,true);assert.equal(editor._draft.version,2);
    editor.useImported();assert.deepEqual(clone(editor.cardAt(2).action),{kind:"control",control:"number"});
    assert.equal(requests.length,2);assert.equal(requests.every(r=>r.type.endsWith("/export")||r.type.endsWith("/import")),true);
  } finally {context.document=oldDocument;context.window.setTimeout=oldTimeout;context.URL=oldURL;}
});

test("light controls require exact live negotiation, not the static profile or a generic support boolean",()=>{
  const editor=lightEditor();assert.equal(editor.lightControlAvailability().ready,true);
  assert.match(editor.inspectorMarkup(),/<option value="control"/);
  const baseline=clone(editor._status);
  for(const patch of [{native_control_types:[]},{native_control_types:["light_brightness_v2"]},{native_control_types:"light_brightness_v1"},
    {light_control_status:"unconfirmed"},{light_control_status:"unsupported"},{light_control_status:"negotiating"},{device_available:false},{device_available:1}]) {
    editor._status={...baseline,...patch};editor.profile.features.native_controls=true;
    assert.equal(editor.lightControlAvailability().ready,false,JSON.stringify(patch));
    assert.doesNotMatch(editor.inspectorMarkup(),/<option value="control"/);
    assert.equal(editor.requestLightControl(),false);assert.equal(editor.dirty,false);
  }
  editor._status=baseline;editor._statusError=true;assert.equal(editor.lightControlAvailability().ready,false);
  editor._statusError=false;editor.isConnected=false;assert.equal(editor.lightControlAvailability().ready,false);
  editor.isConnected=true;editor.profile.layout_versions=[2];assert.equal(editor.lightControlAvailability().ready,false);
});

test("the editor only offers controls for a visible editable entity light with live power capability",()=>{
  for(const mutate of [editor=>{editor.cardAt(2).visible=false;},editor=>{editor.cardAt(2).type="sensor";},editor=>{editor.cardAt(2).type="action";},
    editor=>{editor.profile.slots.find(slot=>slot.slot===2).editable=false;},editor=>{editor.cardAt(2).entity_id="switch.pump";},
    editor=>{editor._entityIndex.get("light.room").available=false;},editor=>{editor._entityIndex.get("light.room").state="unknown";},
    editor=>{editor._hass.states["light.room"].state="unavailable";},editor=>{delete editor._hass.states["light.room"];},
    editor=>{editor._entityIndex.get("light.room").actions=[];}]) {
    const editor=lightEditor();mutate(editor);const before=clone(editor._draft);
    assert.equal(editor.lightControlAvailability().ready,false);assert.equal(editor.requestLightControl(),false);
    assert.deepEqual(clone(editor._draft),before);assert.equal(editor._pending,null);
  }
});

test("selecting light controls reviews v3 without saving; confirmation is one reversible migration preserving all other configuration",async()=>{
  let calls=0;const editor=lightEditor(async()=>{calls++;throw Error("No API call expected");});
  editor.cardAt(3).action={kind:"service",service:"switch.turn_off",data:{}};
  editor._saved=clone(editor._draft);
  const before=clone(editor._draft);editor.editField(actionInput("control"));await editor.onChange({target:actionInput("control")});
  assert.equal(editor._pending.kind,"light-control");assert.equal(editor.dirty,false);assert.equal(editor._undo.length,0);
  assert.match(editor.modalMarkup(),/layout v3/);assert.match(editor.modalMarkup(),/Nothing is saved yet/);
  assert.deepEqual(clone(editor._draft),before);
  await clickAction(editor,"modal-light-control");
  const expected=clone(before);expected.version=3;expected.cards[1].action={kind:"control",control:"light"};
  assert.deepEqual(clone(editor._draft),expected);assert.equal(calls,0);assert.equal(editor._undo.length,1);assert.equal(editor._saved.version,2);
  assert.equal(editor.confirmLightControl(),false);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);
  editor.history("redo");assert.deepEqual(clone(editor._draft),expected);
});

test("cancelling the review and ordinary light assignment preserve v2 default taps",async()=>{
  const editor=lightEditor(),before=clone(editor._draft);
  assert.equal(editor.requestLightControl(),true);await clickAction(editor,"modal-cancel");
  assert.equal(editor._pending,null);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
  assert.equal(editor.assignEntity("light.room",11),true);
  assert.equal(editor._draft.version,2);assert.deepEqual(clone(editor.cardAt(11).action),{kind:"default"});
});

test("review confirmation cannot cross changed entry, user, context, profile, draft or capability",()=>{
  for(const mutate of [editor=>{editor._entryId="screen-b";},editor=>{editor._selectionEpoch++;},editor=>{editor._hass.user={id:"other"};},
    editor=>{editor.profile.width=801;},editor=>{editor.cardAt(2).entity_id="light.other";},editor=>{editor.cardAt(2).id="replaced";},
    editor=>{editor.cardAt(3).title="changed elsewhere";},editor=>{editor._saved.revision++;},editor=>{editor._draft.revision++;},editor=>{editor._status.light_control_status="offline";},editor=>{editor._statusError=true;},
    editor=>{editor._hass.states["light.room"].state="unknown";},editor=>{editor.isConnected=false;}]) {
    const editor=lightEditor();assert.equal(editor.requestLightControl(),true);mutate(editor);const before=clone(editor._draft);
    assert.equal(editor.lightControlReviewCurrent(),false);assert.equal(editor.confirmLightControl(),false);
    assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);assert.equal(editor._pending,null);
    assert.match(editor._error,/changed/);
  }
});

test("a polled server profile change blocks pending and new opt-ins until an explicit reload, preserving the local draft",async()=>{
  const editor=lightEditor();assert.equal(editor.requestLightControl(),true);
  const latest=clone(editor.entry);latest.profile.width=801;latest.status=clone(editor._status);
  editor._hass.callWS=async()=>({entries:[clone(latest)]});const before=clone(editor._draft);
  await editor.refreshStatus();assert.equal(editor.profile.width,800);assert.equal(editor._profileStale,true);
  assert.equal(editor.lightControlReviewCurrent(),false);assert.match(editor.inspectorMarkup(),/Reload the saved layout/);
  assert.equal(editor.confirmLightControl(),false);assert.equal(editor.requestLightControl(),false);assert.deepEqual(clone(editor._draft),before);
  await editor.reloadSaved();assert.equal(editor.profile.width,801);assert.equal(editor._profileStale,false);
  assert.equal(editor.requestLightControl(),true);assert.equal(editor.dirty,false);
});

test("a real remote-save poll over a dirty draft invalidates consent even while local saved and draft revisions stay unchanged",async()=>{
  const editor=lightEditor();editor.mutate(()=>{editor.cardAt(3).title="Keep local edit";});
  assert.equal(editor.requestLightControl(),true);const before=clone(editor._draft);
  const latest=clone(editor.entry);latest.layout.revision=5;latest.status={...clone(editor._status),saved_revision:5};
  editor._hass.callWS=async()=>({entries:[clone(latest)]});await editor.refreshStatus();
  assert.equal(editor._saved.revision,4);assert.equal(editor._draft.revision,4);assert.equal(editor._conflict,true);
  assert.equal(editor.lightControlReviewCurrent(),false);assert.equal(editor.confirmLightControl(),false);
  assert.equal(editor.requestLightControl(),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,1);
});

test("consent fingerprints exposed power and brightness capabilities while ordinary brightness changes remain admissible",()=>{
  const editor=lightEditor();assert.equal(editor.requestLightControl(),true);
  editor._hass.states["light.room"].attributes.brightness=100;assert.equal(editor.lightControlReviewCurrent(),true);
  editor._hass.states["light.room"].attributes.supported_color_modes=["onoff"];
  delete editor._entityIndex.get("light.room").actions[0].fields.brightness_pct;
  assert.equal(editor.lightControlAvailability().ready,true);assert.equal(editor.lightControlReviewCurrent(),false);
  assert.equal(editor.confirmLightControl(),false);assert.equal(editor.dirty,false);
  assert.equal(editor.requestLightControl(),true);editor._entityIndex.get("light.room").actions.shift();
  assert.equal(editor.lightControlAvailability().ready,true);assert.equal(editor.lightControlReviewCurrent(),false);
});

test("onoff-only lights offer supported power controls without inventing a brightness value",()=>{
  const editor=lightEditor();editor._hass.states["light.room"].attributes={supported_color_modes:["onoff"]};
  delete editor._entityIndex.get("light.room").actions[0].fields.brightness_pct;
  assert.equal(editor.lightControlAvailability().ready,true);assert.equal(editor.lightControlAvailability().brightness,false);
  assert.match(editor.inspectorMarkup(),/Brightness unavailable/);assert.equal(editor.requestLightControl(),true);
  assert.match(editor.modalMarkup(),/Brightness unavailable/);assert.doesNotMatch(editor.modalMarkup(),/50%/);
  editor._hass.locale.language="pl";assert.match(editor.modalMarkup(),/Jasność niedostępna/);
});

test("brightness capability with null brightness remains eligible and describes an unknown value as --",()=>{
  const editor=lightEditor();assert.equal(editor.lightControlAvailability().brightness,true);
  assert.match(editor.inspectorMarkup(),/unknown value is shown as --/);assert.doesNotMatch(editor.inspectorMarkup(),/50%/);
  editor._hass.states["light.room"].attributes.supported_color_modes=["bogus"];
  assert.equal(editor.lightControlAvailability().brightness,false);
});

test("saved v3 controls survive unsupported or offline devices and unrelated saves without becoming default actions",async()=>{
  const requests=[];const editor=lightEditor(async request=>{requests.push(clone(request));return {layout:{...clone(request.layout),revision:5},status:{device_available:false}};});
  editor._saved.version=3;editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"light"};editor._saved.cards[1].action=clone(editor.cardAt(2).action);
  editor._status={device_available:false};
  assert.match(editor.inspectorMarkup(),/<option value="control" selected disabled>/);
  assert.match(editor.inspectorMarkup(),/matching firmware/);assert.equal(editor.requestLightControl(),false);
  editor.mutate(()=>{editor.cardAt(2).title="Keep my control";});assert.equal(await editor.save(),true);
  assert.equal(requests.length,1);assert.equal(requests[0].type,"atmosfera_echo_hub/layout/save");assert.equal(requests[0].layout.version,3);
  assert.deepEqual(requests[0].layout.cards[1].action,{kind:"control",control:"light"});
});

test("changing a control card to Action or Information makes it passive, while undo restores its explicit control",()=>{
  for(const type of ["action","sensor"]) {
    const editor=lightEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"light"};
    editor.editField({...actionInput(type),dataset:{field:"type"}});editor.finishField();
    assert.deepEqual(clone(editor.cardAt(2).action),{kind:"none"});assert.equal(editor._draft.version,3);
    editor.history("undo");assert.deepEqual(clone(editor.cardAt(2).action),{kind:"control",control:"light"});
  }
});

test("local recovery accepts only exact v3 light-control configuration and never runtime session data",()=>{
  const editor=lightEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"light"};
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}};
  assert.doesNotThrow(()=>editor.validateStoredDraft(clone(record)));
  for(const mutate of [record=>{record.layout.version=2;},record=>{record.layout.cards[1].action.token="secret";},record=>{record.layout.cards[1].action.service="light.turn_on";},
    record=>{record.layout.cards[1].action.control="climate";},record=>{record.layout.cards[1].type="action";},record=>{record.layout.cards[1].entity_id="switch.pump";},
    record=>{record.layout.cards[1].action={kind:"default",control:"light"};}]) {
    const bad=clone(record);mutate(bad);assert.throws(()=>editor.validateStoredDraft(bad));
  }
  editor.profile.layout_versions="2,3";assert.throws(()=>editor.validateStoredDraft(clone(record)));
});

test("v3 control copies preserve the reviewed schema and gain new card identity in one paste transaction",()=>{
  const editor=lightEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"light"};
  assert.equal(editor.copyCard(2),true);assert.equal(editor.pasteCard(13),true);
  assert.equal(editor._draft.version,3);assert.notEqual(editor.cardAt(13).id,editor.cardAt(2).id);
  assert.deepEqual(clone(editor.cardAt(13).action),{kind:"control",control:"light"});
  editor.history("undo");assert.equal(editor.cardAt(13),undefined);assert.equal(editor._draft.version,3);
  editor._draft.version=2;assert.equal(editor.canPasteCard(13),false);assert.equal(editor.pasteCard(13),false);
  assert.equal(editor._draft.version,2);assert.equal(editor.cardAt(13),undefined);
});

test("light opt-in refuses active edits with invalid fields, gestures, an existing dialog or a busy transaction",()=>{
  for(const mutate of [editor=>{editor._busy=true;},editor=>{editor._drag={};},editor=>{editor._carry={};},editor=>{editor._pending={kind:"import"};},editor=>{editor._fieldErrors.title="Invalid";}]) {
    const editor=lightEditor();mutate(editor);const before=clone(editor._draft);
    assert.equal(editor.requestLightControl(),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
  }
});

test("live negotiation changes repaint only a changed unfocused inspector and never mutate a layout",async()=>{
  const editor=lightEditor();editor._status.native_control_types=[];
  const latest=clone(editor.entry);latest.status={...editor._status,native_control_types:["light_brightness_v1"]};
  const dom=trackedEditorDOM(editor),inspector=dom.region(editor.inspectorMarkup());dom.regions.set("#inspector",inspector);
  const before=clone(editor._draft);editor._hass.callWS=async()=>({entries:[clone(latest)]});
  await editor.refreshStatus();assert.equal(inspector.writes,1);assert.match(inspector.innerHTML,/<option value="control"/);
  await editor.refreshStatus();assert.equal(inspector.writes,1);assert.deepEqual(clone(editor._draft),before);
  editor._hass.callWS=async()=>{throw Error("offline");};await editor.refreshStatus();
  assert.equal(inspector.writes,2);assert.doesNotMatch(inspector.innerHTML,/<option value="control"/);assert.deepEqual(clone(editor._draft),before);
});

test("a focused inspector is not replaced by negotiation changes, but stale selection is still denied",async()=>{
  const editor=lightEditor(),dom=trackedEditorDOM(editor),inspector=dom.regions.get("#inspector");
  const query=dom.root.querySelector;dom.root.querySelector=selector=>selector===".inspector"?inspector:query(selector);
  dom.root.activeElement={tagName:"SELECT",region:inspector};
  const latest=clone(editor.entry);latest.status={...editor._status,native_control_types:[]};editor._hass.callWS=async()=>({entries:[clone(latest)]});
  await editor.refreshStatus();assert.equal(inspector.writes,0);assert.equal(editor.requestLightControl(),false);assert.equal(editor._pending,null);
});

test("HA availability changes withdraw the light option without rebuilding an inspector for ordinary brightness updates",()=>{
  const editor=lightEditor(),dom=trackedEditorDOM(editor),inspector=dom.region(editor.inspectorMarkup());dom.regions.set("#inspector",inspector);
  const state=clone(editor._hass.states["light.room"]);state.attributes.brightness=100;
  editor.hass={...editor._hass,states:{"light.room":state}};assert.equal(inspector.writes,0);
  editor.hass={...editor._hass,states:{"light.room":{...state,state:"unavailable"}}};
  assert.equal(inspector.writes,1);assert.doesNotMatch(inspector.innerHTML,/<option value="control"/);assert.equal(editor.dirty,false);
});

test("imported v3 controls stay a backend-validated reviewed draft without action dispatch or implicit saving",async()=>{
  const calls=[],editor=lightEditor(async request=>{calls.push(clone(request));return {layout:{...clone(request.backup.layout),revision:4},warnings:[]};});
  const imported=clone(editor._draft);imported.version=3;imported.cards[1].action={kind:"control",control:"light"};
  assert.equal(await editor.importText(JSON.stringify({format:"atmosfera-layout",version:1,layout:imported})),true);
  assert.equal(editor._draft.version,2);assert.equal(editor._pending.kind,"import");editor.useImported();
  assert.equal(editor._draft.version,3);assert.deepEqual(clone(editor.cardAt(2).action),{kind:"control",control:"light"});
  assert.equal(calls.length,1);assert.equal(calls[0].type,"atmosfera_echo_hub/layout/import");assert.equal(calls[0].dry_run,true);
  editor.history("undo");assert.equal(editor._draft.version,2);assert.deepEqual(clone(editor.cardAt(2).action),{kind:"default"});
});

test("review text is localized and untrusted titles are escaped",()=>{
  const editor=lightEditor();editor.cardAt(2).title='<img src=x onerror="bad">';assert.equal(editor.requestLightControl(),true);
  assert.doesNotMatch(editor.modalMarkup(),/<img src=x/);assert.match(editor.modalMarkup(),/&lt;img/);
  editor._hass.locale.language="pl";assert.match(editor.modalMarkup(),/układ v3/);assert.match(editor.modalMarkup(),/Jeszcze nic nie zapisano/);
});

function renderedPageTabs(markup) {
  return [...markup.matchAll(/<(button|span)\b([^>]*\bclass="(?:page-tab|reserved-page)[^"]*"[^>]*)>([\s\S]*?)<\/\1>/g)].map(([,tag,attributes,body])=>({
    tag,attributes,label:body.replace(/<[^>]*>/g,"").replaceAll("&amp;","&").replaceAll("&lt;","<").replaceAll("&gt;",">").replaceAll("&quot;",'"'),
    page:attributes.match(/\bdata-page="([^"]*)"/)?.[1],
  }));
}

test("page navigation follows the complete native profile order, including built-in Apps before Controls",()=>{
  const editor=makeEditor(),before=clone(editor.profile.pages);
  const tabs=renderedPageTabs(editor.pageMarkup());
  assert.deepEqual(tabs.map(tab=>tab.label),["Clock & weather","Security","Applications","Controls"]);
  assert.deepEqual(tabs.map(tab=>tab.tag),["span","button","span","button"]);
  assert.deepEqual(tabs.filter(tab=>tab.tag==="button").map(tab=>tab.page),["home-2","home-4"]);
  assert.deepEqual(clone(editor.profile.pages),before);
});

test("profile order is authoritative even when page metadata arrives out of order, without mutating the response",()=>{
  const editor=makeEditor(),pages=editor.profile.pages;
  editor.profile.pages=[pages[3],pages[1],pages[0],pages[2]];
  const before=clone(editor.profile.pages);
  assert.deepEqual(renderedPageTabs(editor.pageMarkup()).map(tab=>tab.label),["Clock & weather","Security","Applications","Controls"]);
  assert.deepEqual(clone(editor.profile.pages),before);
  pages[3].order=-10;pages[0].order=30;
  assert.deepEqual(renderedPageTabs(editor.pageMarkup()).map(tab=>tab.label),["Controls","Security","Applications","Clock & weather"]);
});

test("reserved page labels remain localized and unknown read-only pages use escaped supplied metadata",()=>{
  const editor=makeEditor();editor._hass.locale.language="pl";
  let markup=editor.pageMarkup();
  assert.deepEqual(renderedPageTabs(markup).map(tab=>tab.label),["Zegar i pogoda","Bezpieczeństwo","Aplikacje","Sterowanie"]);
  assert.equal((markup.match(/title="Strona wbudowana"/g)||[]).length,2);
  editor.entry.profile={id:"unrecognized-profile",pages:[{id:"custom",title:'Remote <img onerror="bad">',order:7}],slots:[]};
  markup=editor.pageMarkup();
  assert.equal(renderedPageTabs(markup)[0].label,'Remote <img onerror="bad">');
  assert.match(markup,/&lt;img onerror=&quot;bad&quot;&gt;/);assert.doesNotMatch(markup,/<img|data-action="page"|Zegar i pogoda|Aplikacje|Strona wbudowana/);
  editor.profile.pages=[{id:"unknown-page",order:0}];
  assert.equal(renderedPageTabs(editor.pageMarkup())[0].label,"unknown-page");
});

test("missing page metadata never invents Home or Apps and pages without editable bindings stay read-only",()=>{
  const editor=makeEditor();editor.entry.profile={id:"partial"};
  assert.equal(editor.pageMarkup(),"");
  editor.profile.pages=[];assert.equal(editor.pageMarkup(),"");
  editor.entry.profile=clone(profile);editor.profile.slots=[];
  const tabs=renderedPageTabs(editor.pageMarkup());
  assert.equal(tabs.length,4);assert.equal(tabs.every(tab=>tab.tag==="span"&&!tab.page),true);
  assert.doesNotMatch(editor.pageMarkup(),/data-action="page"|role="tab"/);
});

test("editable page tabs preserve ARIA selection and click routing after the noneditable Apps entry",async()=>{
  const editor=makeEditor(),before=clone(editor._draft);
  let tabs=renderedPageTabs(editor.pageMarkup());
  assert.match(tabs[1].attributes,/role="tab" aria-selected="true"/);
  assert.match(tabs[3].attributes,/role="tab" aria-selected="false"/);
  assert.doesNotMatch(tabs[0].attributes+tabs[2].attributes,/data-action|role="tab"/);
  let renders=0;editor.render=()=>{renders++;};editor._selectedSlot=2;
  const controls={dataset:{action:"page",page:tabs[3].page}};
  await editor.onClick({target:{closest:()=>controls},preventDefault(){}});
  assert.equal(editor._pageId,"home-4");assert.equal(editor._selectedSlot,null);assert.equal(renders,1);
  assert.deepEqual(clone(editor._draft),before);assert.equal(editor.dirty,false);
  tabs=renderedPageTabs(editor.pageMarkup());assert.match(tabs[3].attributes,/aria-selected="true"/);
});

test("drag hover ignores built-in Apps while the following Controls tab still switches the preview",()=>{
  const editor=makeEditor(),tabs=renderedPageTabs(editor.pageMarkup()),before=clone(editor._draft);
  const node=tab=>({dataset:{page:tab.page},disabled:false,closest(selector){return selector==='[data-action="page"]'&&tab.tag==="button"?this:null;}});
  let under=node(tabs[2]),scheduled=[];const previousTimeout=context.window.setTimeout,previousClear=context.window.clearTimeout;
  context.window.setTimeout=(callback,delay)=>{scheduled.push({callback,delay});return scheduled.length;};
  context.window.clearTimeout=()=>{};
  try {
    editor.shadowRoot.elementFromPoint=()=>under;editor._ghost={style:{}};
    editor._drag={pointer:9,active:true,kind:"card",from:2};
    const painted=[];editor.paintPages=()=>painted.push("pages");editor.paintPreview=()=>painted.push("preview");editor.paintInspector=()=>painted.push("inspector");
    const event={pointerId:9,clientX:30,clientY:40,preventDefault(){}};
    editor.onPointerMove(event);assert.equal(scheduled.length,0);assert.equal(editor._drag.hoverPage,null);
    under=node(tabs[3]);editor.onPointerMove(event);
    assert.equal(scheduled.length,1);assert.equal(scheduled[0].delay,500);assert.equal(editor._pageId,"home-2");
    scheduled[0].callback();assert.equal(editor._pageId,"home-4");
    assert.deepEqual(painted,["pages","preview","inspector"]);assert.equal(editor._drag.from,2);
    assert.deepEqual(clone(editor._draft),before);assert.equal(editor.dirty,false);
  } finally {context.window.setTimeout=previousTimeout;context.window.clearTimeout=previousClear;}
});

function storedIdentity(values={}) {
  return {source:"home_assistant_device_registry",registry_entry_present:true,name:"Kitchen display",manufacturer:"Maker",model:"Panel",software_version:"stored-build",...values};
}
test("stored identity is distinct from the trusted layout profile and never offers an identify action",()=>{
  const editor=makeEditor(),before=clone(editor._draft);editor.entry.device_identity=storedIdentity();
  const markup=editor.capabilitiesMarkup();
  for(const value of ["Kitchen display","Maker","Panel","stored-build","echo-hub-m3-v1"])assert.ok(markup.includes(value));
  assert.match(markup,/Last details stored in Home Assistant\./);assert.match(markup,/Software version \(stored\)/);assert.doesNotMatch(markup,/firmware or identity probe/);
  assert.doesNotMatch(editor.deviceIdentityMarkup(),/<button|data-action/);assert.deepEqual(clone(editor._draft),before);
  editor._hass.locale.language="pl";const pl=editor.deviceIdentityMarkup();assert.match(pl,/Dane urządzenia/);assert.match(pl,/Ostatnie dane zapisane w Home Assistant\./);assert.match(pl,/Producent/);assert.match(pl,/Wersja oprogramowania \(zapisana\)/);
});
test("offline or failed status keeps stored identity with explicit retained-data qualification",()=>{
  const editor=makeEditor();editor.entry.device_identity=storedIdentity();editor._status.device_available=false;
  let markup=editor.deviceIdentityMarkup();assert.match(markup,/stored-build/);assert.match(markup,/The device’s current status cannot be confirmed\./);
  editor._status.device_available=true;editor._statusError=true;assert.match(editor.deviceIdentityMarkup(),/The device’s current status cannot be confirmed\./);
  editor._statusError=false;assert.doesNotMatch(editor.deviceIdentityMarkup(),/The device’s current status cannot be confirmed\./);
});
test("missing partial and hostile metadata stay unknown or escaped without inventing firmware facts",()=>{
  const editor=makeEditor();let markup=editor.deviceIdentityMarkup();assert.match(markup,/No stored details are available for this device\./);assert.match(markup,/Unknown/);
  editor.entry.device_identity=storedIdentity({name:'<img onerror="bad">',model:null,manufacturer:12});
  markup=editor.deviceIdentityMarkup();assert.match(markup,/&lt;img onerror=&quot;bad&quot;&gt;/);assert.doesNotMatch(markup,/<img/);assert.match(markup,/Model<\/dt><dd>Unknown/);assert.match(markup,/Manufacturer<\/dt><dd>Unknown/);
  editor.entry.device_identity=storedIdentity({source:"native-live",name:"Untrusted claim"});assert.doesNotMatch(editor.deviceIdentityMarkup(),/Untrusted claim/);
  editor.entry.device_identity=storedIdentity({name:"x".repeat(500)});assert.equal((editor.deviceIdentityMarkup().match(/x/g)||[]).length,80);
});
test("metadata-only polls patch only the identity region once and preserve draft inspector conflict and focus",async()=>{
  let editor;editor=makeEditor(async()=>({entries:[{...clone(editor.entry),device_identity:storedIdentity({software_version:"new-stored"})}]}));
  editor.entry.device_identity=storedIdentity();editor.mutate(layout=>{layout.cards[1].title="Draft title";});
  const before=clone(editor._draft),dom=trackedEditorDOM(editor),identity=dom.region(editor.deviceIdentityMarkup());dom.regions.set("#device-identity",identity);
  const inspector=dom.regions.get("#inspector"),feedback=dom.regions.get("#feedback");dom.root.activeElement={tagName:"INPUT",region:inspector};const focused=dom.root.activeElement;
  editor.paintStatus();assert.equal(identity.writes,0);
  await editor.refreshStatus();assert.equal(identity.writes,1);assert.match(identity.innerHTML,/new-stored/);
  await editor.refreshStatus();assert.equal(identity.writes,1);
  assert.equal(inspector.writes,0);assert.equal(feedback.writes,0);assert.equal(dom.root.htmlWrites,0);assert.equal(dom.root.activeElement,focused);assert.deepEqual(clone(editor._draft),before);
});
test("device switches and stale asynchronous responses cannot leak another display's identity",async()=>{
  let release;const editor=makeEditor(()=>new Promise(resolve=>{release=resolve;}));editor.entry.device_identity=storedIdentity({name:"Display A"});
  editor._data.entries[1].device_identity=storedIdentity({name:"Display B"});
  const request=editor.refreshStatus();const previous=clone(editor.entry);editor._entryId="screen-b";editor._selectionEpoch++;
  release({entries:[{...previous,device_identity:storedIdentity({name:"Stale A"})}]});await request;
  assert.match(editor.deviceIdentityMarkup(),/Display B/);assert.doesNotMatch(editor.deviceIdentityMarkup(),/Stale A|Display A/);
});


// CUT remains a local intent until one validated call to the existing move kernel.
test("cut across pages retains source until paste, preserves stable identity and creates one undoable move",()=>{
  const editor=makeEditor();editor._selectedSlot=2;
  Object.assign(editor.cardAt(2),{title:"Long stored source title",visible:false,action:{kind:"service",service:"light.turn_on",data:{brightness_pct:61,rgb_color:[10,20,30]}}});
  editor._saved=clone(editor._draft);const before=clone(editor._draft),sourceCard=clone(editor.cardAt(2));
  let calls=0;const move=editor.moveCard;editor.moveCard=function(from,to){calls++;return move.call(this,from,to);};
  assert.equal(editor.cutCard(),true);assert.deepEqual(clone(editor._draft),before);assert.equal(editor.dirty,false);assert.equal(editor._undo.length,0);
  assert.equal(editor._cardClipboard.mode,"cut");assert.notEqual(editor._cardClipboard.card,editor.cardAt(2));
  assert.equal(editor.pasteCard(13),true);assert.equal(calls,1);assert.equal(editor.cardAt(2),undefined);
  assert.deepEqual(clone(editor.cardAt(13)),{...sourceCard,slot:13});assert.equal(editor._draft.cards.length,before.cards.length);
  assert.equal(editor._pageId,"home-4");assert.equal(editor._selectedSlot,13);assert.equal(editor._undo.length,1);assert.equal(editor._cardClipboard,null);
  const moved=clone(editor._draft);editor.history("undo");assert.deepEqual(clone(editor._draft),before);assert.equal(editor.dirty,false);
  editor.history("redo");assert.deepEqual(clone(editor._draft),moved);assert.equal(editor.cardAt(13).id,sourceCard.id);
});

test("a cut move works at card capacity while independent copies still require capacity",()=>{
  const editor=makeEditor();editor.profile.max_cards=editor._draft.cards.length;
  assert.equal(editor.copyCard(2),true);assert.equal(editor.canPasteCard(13),false);
  assert.equal(editor.cutCard(2),true);assert.equal(editor.canPasteCard(13),true);assert.equal(editor.pasteCard(13),true);
  assert.equal(editor._draft.cards.length,editor.profile.max_cards);assert.equal(editor.cardAt(13).id,"first");
});

test("edited moved deleted replaced or ambiguously duplicated cut sources cannot overwrite later work",()=>{
  const changes=[editor=>{editor.cardAt(2).title="New title";},editor=>{editor.cardAt(2).action={kind:"none"};},
    editor=>{editor.cardAt(2).visible=false;},editor=>{editor.cardAt(2).type="action";},editor=>{editor.cardAt(2).id="replacement";},
    editor=>{editor.moveCard(2,11);},editor=>{editor._draft.cards=editor._draft.cards.filter(card=>card.slot!==2);},
    editor=>{editor._draft.cards.push({...clone(editor.cardAt(2)),slot:11});}];
  for(const change of changes){
    const editor=makeEditor();assert.equal(editor.cutCard(2),true);change(editor);const before=clone(editor._draft),history=editor._undo.length;
    assert.equal(editor.canPasteCard(13),false);assert.equal(editor.pasteCard(13),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,history);
    assert.equal(editor.cardAt(13),undefined);assert.match(editor.clipboardMarkup(),/source card changed/);
  }
  const nested=makeEditor();nested.cardAt(2).action={kind:"service",service:"light.turn_on",data:{rgb_color:[10,20,30]}};
  nested.cutCard(2);nested.cardAt(2).action.data.rgb_color[0]=99;assert.equal(nested.pasteCard(13),false);assert.equal(nested.cardAt(2).action.data.rgb_color[0],99);
});

test("unrelated card edits remain intact through cut paste and its single undo",()=>{
  const editor=makeEditor();editor.cutCard(2);editor.mutate(layout=>{layout.cards.find(card=>card.slot===3).title="Keep later edit";});
  const beforePaste=clone(editor._draft);assert.equal(editor.pasteCard(13),true);assert.equal(editor._undo.length,2);
  assert.equal(editor.cardAt(3).title,"Keep later edit");editor.history("undo");assert.deepEqual(clone(editor._draft),beforePaste);
  assert.equal(editor.cardAt(2).id,"first");assert.equal(editor.cardAt(3).title,"Keep later edit");
});

test("cut refuses reserved sources and occupied hidden reserved absent or incompatible destinations without swapping",()=>{
  const editor=makeEditor();editor.cardAt(3).visible=false;editor.profile.slots.find(slot=>slot.slot===13).types=["sensor"];
  assert.equal(editor.cutCard(0),false);assert.equal(editor.cutCard(99),false);assert.equal(editor.cutCard(2),true);
  const before=clone(editor._draft);for(const target of [2,3,0,99,13])assert.equal(editor.pasteCard(target),false,String(target));
  assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);assert.equal(editor._cardClipboard.mode,"cut");
});

test("cut preserves passive sensor and existing v3 control semantics without negotiation or migration",()=>{
  const sensor=makeEditor();Object.assign(sensor.cardAt(2),{type:"sensor",visible:false,entity_id:"sensor.room",action:{kind:"none"}});
  sensor.cutCard(2);assert.equal(sensor.pasteCard(13),true);assert.equal(sensor.cardAt(13).type,"sensor");assert.equal(sensor.cardAt(13).visible,false);assert.deepEqual(clone(sensor.cardAt(13).action),{kind:"none"});
  const control=makeEditor();control._draft.version=3;control.cardAt(2).action={kind:"control",control:"light"};control._status.device_available=false;
  control.cutCard(2);assert.equal(control.pasteCard(13),true);assert.equal(control._draft.version,3);assert.deepEqual(clone(control.cardAt(13).action),{kind:"control",control:"light"});
  const invalid=makeEditor();invalid.cardAt(2).action={kind:"control",control:"light"};invalid.cutCard(2);assert.equal(invalid.pasteCard(13),false);assert.equal(invalid._draft.version,2);
});

test("cut and paste respect busy modal pointer keyboard invalid-field and stale-profile boundaries",()=>{
  for(const [key,value] of [["_busy",true],["_pending",{kind:"switch"}],["_drag",{}],["_carry",{}],["_fieldErrors",{title:"Invalid"}],["_profileStale",true]]){
    const editor=makeEditor();editor.cutCard(2);editor[key]=value;const before=clone(editor._draft);
    assert.equal(editor.cutCard(2),false,key);assert.equal(editor.pasteCard(13),false,key);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
  }
});

test("a cut move's final document bound is checked before moving, and a failed kernel retains the source and intent",()=>{
  const bounded=makeEditor();const bytes=new TextEncoder().encode(JSON.stringify(bounded._draft)).length;
  bounded.profile.max_document_bytes=bytes;assert.equal(bounded.cutCard(2),true);const before=clone(bounded._draft);
  assert.equal(bounded.pasteCard(13),false);assert.deepEqual(clone(bounded._draft),before);assert.equal(bounded._undo.length,0);assert.equal(bounded._cardClipboard.mode,"cut");assert.match(bounded._error,/limit/);
  const capture=makeEditor();capture.profile.max_document_bytes=10;assert.equal(capture.cutCard(2),false);assert.equal(capture._cardClipboard,null);
  const rejected=makeEditor();rejected.cutCard(2);const original=clone(rejected._draft);let calls=0;rejected.moveCard=()=>{calls++;return false;};
  assert.equal(rejected.pasteCard(13),false);assert.equal(calls,1);assert.deepEqual(clone(rejected._draft),original);assert.equal(rejected._cardClipboard.mode,"cut");
});

test("one memory clipboard switches between copy and cut without changing independent copy identities",()=>{
  const editor=makeEditor();editor.cutCard(2);editor.copyCard(3);assert.equal(editor._cardClipboard.mode,"copy");
  assert.equal(editor.pasteCard(11),true);const copied=editor.cardAt(11).id;assert.notEqual(copied,"second");assert.equal(editor.cardAt(3).id,"second");
  assert.equal(editor.pasteCard(13),true);assert.notEqual(editor.cardAt(13).id,copied);assert.notEqual(editor.cardAt(13).id,"second");
  editor.history("undo");editor.cutCard(2);assert.equal(editor._cardClipboard.mode,"cut");assert.equal(editor.pasteCard(13),true);assert.equal(editor.cardAt(13).id,"first");assert.equal(editor._cardClipboard,null);
});

test("device offline status preserves cut and editing, while explicit HA disconnect clears both clipboard modes",()=>{
  const offline=makeEditor();offline.cutCard(2);offline._status.device_available=false;offline.paintValues();
  assert.equal(offline._cardClipboard.mode,"cut");assert.equal(offline.pasteCard(13),true);assert.equal(offline.cardAt(13).id,"first");
  for(const mode of ["copyCard","cutCard"])for(const disconnect of [editor=>{editor._hass.connected=false;},editor=>{editor._hass.connection={connected:false};},editor=>{editor.isConnected=false;}]){
    const editor=makeEditor();editor[mode](2);disconnect(editor);editor.paintValues();const before=clone(editor._draft);
    assert.equal(editor._cardClipboard,null);assert.equal(editor[mode](2),false);assert.equal(editor.pasteCard(13),false);assert.deepEqual(clone(editor._draft),before);
  }
});

test("cut context cannot cross entry profile user detach or a server-profile invalidation",async()=>{
  for(const change of [editor=>{editor.selectEntry("screen-b");},editor=>{editor.profile.id="other";},editor=>{editor.profile.slots[1].editable=false;},editor=>{editor._hass.user={id:"other"};},editor=>{editor.disconnectedCallback();}]){
    const editor=makeEditor();editor.cutCard(2);change(editor);const before=clone(editor._draft);assert.equal(editor.pasteCard(13),false);assert.equal(editor._cardClipboard,null);assert.deepEqual(clone(editor._draft),before);
  }
  const editor=makeEditor();editor.cutCard(2);const latest=clone(editor.entry);latest.profile.version++;
  editor._hass.callWS=async()=>({entries:[latest]});const before=clone(editor._draft);await editor.refreshStatus();
  assert.equal(editor._cardClipboard,null);assert.equal(editor._profileStale,true);assert.deepEqual(clone(editor._draft),before);assert.equal(editor.cutCard(2),false);
});

test("Ctrl and Cmd cut/paste route focused slots while native text selection and Alt shortcuts remain untouched",()=>{
  const editor=makeEditor();editor._selectedSlot=3;
  assert.equal(shortcut(editor,keyboardTarget(2),"x").prevented,true);assert.equal(editor.cardAt(2).id,"first");
  assert.equal(shortcut(editor,keyboardTarget(13),"v",{metaKey:true}).prevented,true);assert.equal(editor.cardAt(13).id,"first");assert.equal(editor.cardAt(3).id,"second");
  for(const tag of ["INPUT","SELECT","TEXTAREA"]){const field=makeEditor();assert.equal(shortcut(field,keyboardTarget(2,tag),"x").prevented,false);assert.equal(field._cardClipboard,null);}
  const editable=keyboardTarget(2);editable.isContentEditable=true;const field=makeEditor();assert.equal(shortcut(field,editable,"x").prevented,false);assert.equal(field._cardClipboard,null);
  const nested={tagName:"SPAN",closest:selector=>selector==='[contenteditable="true"]'?{}:null};assert.equal(shortcut(field,nested,"x").prevented,false);
  assert.equal(shortcut(field,keyboardTarget(2),"x",{ctrlKey:true,altKey:true}).prevented,false);assert.equal(field._cardClipboard,null);
});

test("Escape clears cut or copy even in a field or modal and never changes the draft",()=>{
  for(const mode of ["cutCard","copyCard"]){
    const editor=makeEditor();editor[mode](2);const before=clone(editor._draft);shortcut(editor,keyboardTarget(2,"INPUT"),"Escape",{});
    assert.equal(editor._cardClipboard,null);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
    editor[mode](2);editor._pending={kind:"switch"};shortcut(editor,keyboardTarget(2),"Escape",{});assert.equal(editor._cardClipboard,null);assert.equal(editor._pending,null);
  }
});

test("cut and paste controls are localized escaped and click-routed without changing stored titles",async()=>{
  const editor=makeEditor();editor._selectedSlot=2;editor.cardAt(2).title='<img onerror="bad">';const title=editor.cardAt(2).title;
  assert.match(editor.inspectorMarkup(),/data-action="cut-card"/);assert.match(editor.inspectorMarkup(),/Ctrl\/Cmd\+X/);
  await clickAction(editor,"cut-card");assert.match(editor.clipboardMarkup(),/To move:/);assert.match(editor.clipboardMarkup(),/&lt;img/);assert.doesNotMatch(editor.clipboardMarkup(),/<img/);
  editor._hass.locale.language="pl";editor._selectedSlot=13;assert.match(editor.clipboardMarkup(),/Do przeniesienia:/);assert.match(editor.clipboardMarkup(),/Anuluj przenoszenie/);assert.match(editor.inspectorMarkup(),/Przenieś kartę tutaj/);
  await clickAction(editor,"paste-card");assert.equal(editor.cardAt(13).title,title);assert.equal(editor.cardAt(13).id,"first");assert.equal(editor._cardClipboard,null);
});

test("cut intent is never persisted or sent; an accepted move only stores the ordinary bounded layout draft",()=>{
  let calls=0;const storage=new BrowserStorage(),editor=enableDraft(makeEditor(async()=>{calls++;throw Error("No API expected");}),storage);
  const before=clone(editor._draft);assert.equal(editor.cutCard(2),true);assert.equal(storage.length,0);assert.deepEqual(clone(editor._draft),before);
  editor.persistDraft();assert.equal(storage.length,0);assert.equal(editor.pasteCard(13),true);flushDraft(editor);assert.equal(calls,0);
  const record=JSON.parse(storage.getItem(editor.draftKey()));assert.equal(record.layout.cards.find(card=>card.id==="first").slot,13);
  assert.equal(Object.hasOwn(record,"clipboard"),false);assert.equal(Object.hasOwn(record,"_cardClipboard"),false);assert.equal(Object.hasOwn(record.layout,"clipboard"),false);
  assert.doesNotMatch(source,/navigator\.clipboard|clipboardData|execCommand\(["'](?:cut|copy)/);
});

test("ordinary HA updates and unchanged polls preserve cut banner inspector conflict DOM and focus",async()=>{
  const editor=makeEditor();editor.cutCard(2);const dom=trackedEditorDOM(editor),banner=dom.region(editor.clipboardMarkup());dom.regions.set("#card-clipboard",banner);
  const inspector=dom.regions.get("#inspector"),feedback=dom.regions.get("#feedback"),focused={tagName:"INPUT",region:inspector};dom.root.activeElement=focused;
  const before=clone(editor._draft);editor.hass={...editor._hass,states:{"light.room":{state:"off",attributes:{}}}};
  editor._hass.callWS=async()=>({entries:[clone(editor.entry)]});await editor.refreshStatus();editor.paintValues();
  assert.equal(banner.writes,0);assert.equal(inspector.writes,0);assert.equal(feedback.writes,0);assert.equal(dom.root.htmlWrites,0);assert.equal(dom.root.activeElement,focused);assert.deepEqual(clone(editor._draft),before);
  assert.equal(editor._cardClipboard.mode,"cut");
});

test("disconnect and Escape clear the banner without rebuilding a focused property field",()=>{
  for(const operation of [editor=>{editor.hass={...editor._hass,connected:false};},editor=>{shortcut(editor,keyboardTarget(2,"INPUT"),"Escape",{});}]){
    const editor=makeEditor();editor.cutCard(2);const dom=trackedEditorDOM(editor),banner=dom.region(editor.clipboardMarkup());dom.regions.set("#card-clipboard",banner);
    const inspector=dom.regions.get("#inspector"),focused={tagName:"INPUT",region:inspector};dom.root.activeElement=focused;const before=clone(editor._draft);
    operation(editor);assert.equal(editor._cardClipboard,null);assert.equal(banner.writes,1);assert.equal(banner.innerHTML,"");assert.equal(inspector.writes,0);assert.equal(dom.root.activeElement,focused);assert.deepEqual(clone(editor._draft),before);
  }
});


test("typing after cut marks the intent stale without replacing the focused field, and paste preserves the edit",()=>{
  const editor=makeEditor();editor._selectedSlot=2;editor.cutCard(2);
  const dom=trackedEditorDOM(editor),banner=dom.region(editor.clipboardMarkup());dom.regions.set("#card-clipboard",banner);
  const inspector=dom.regions.get("#inspector"),input={tagName:"INPUT",region:inspector,dataset:{field:"title"},value:"My later edit",removeAttribute(){},setAttribute(){}};
  dom.root.activeElement=input;editor.editField(input);
  assert.equal(banner.writes,1);assert.match(banner.innerHTML,/source card changed/);assert.equal(inspector.writes,0);assert.equal(dom.root.activeElement,input);
  input.value="My continued edit";editor.editField(input);assert.equal(banner.writes,1);
  assert.equal(editor.pasteCard(13),false);assert.equal(editor.cardAt(2).title,"My continued edit");assert.equal(editor.cardAt(13),undefined);
  assert.equal(editor._undo.length,1);editor.history("undo");assert.equal(editor.cardAt(2).title,"first");
});


// Completion feedback follows the history transaction, including two-step CUT undo.
test("successful undo and redo replace stale cut feedback before render, including the return to a clean layout",()=>{
  for(const [locale,undone,redone] of [["en","Change undone.","Change redone."],["pl","Cofnięto zmianę.","Przywrócono zmianę."]]){
    const calls=[];const editor=makeEditor(async request=>{calls.push(clone(request));return {entities:[]};});editor._hass.locale.language=locale;
    const clean=clone(editor._draft);editor._selectedSlot=3;editor.removeCard();const deleted=clone(editor._draft);
    editor.cutCard(2);assert.equal(editor.pasteCard(3),true);const moved=clone(editor._draft);assert.equal(editor._notice,editor.t("pasteMoved"));
    const renders=[];editor.render=()=>renders.push({notice:editor._notice,error:editor._error,draft:clone(editor._draft)});
    editor._error="Old error";editor.history("undo");assert.deepEqual(clone(editor._draft),deleted);assert.equal(editor._notice,undone);assert.equal(editor._error,"");assert.equal(editor.dirty,true);
    assert.deepEqual(renders.at(-1),{notice:undone,error:"",draft:deleted});assert.doesNotMatch(editor.feedbackMarkup(),/Old error|Save when ready|Zapisz układ/);
    editor.history("undo");assert.deepEqual(clone(editor._draft),clean);assert.equal(editor._notice,undone);assert.equal(editor.dirty,false);
    editor.history("redo");assert.deepEqual(clone(editor._draft),deleted);assert.equal(editor._notice,redone);assert.equal(renders.at(-1).notice,redone);
    editor.history("redo");assert.deepEqual(clone(editor._draft),moved);assert.equal(editor._notice,redone);assert.equal(editor.cardAt(3).id,"first");assert.equal(editor._saved.revision,4);assert.ok(calls.every(request=>request.type==="atmosfera_echo_hub/catalogue/get"));
  }
});

test("history clears an actual later copy-size error without reviving stale copied-card feedback",()=>{
  const editor=makeEditor();editor.copyCard(2);assert.equal(editor.pasteCard(11),true);
  editor.profile.max_document_bytes=new TextEncoder().encode(JSON.stringify(editor._draft)).length;
  editor.copyCard(2);assert.equal(editor.pasteCard(13),false);assert.match(editor._error,/limit/);assert.equal(editor._notice,editor.t("copied"));
  editor.history("undo");assert.equal(editor.cardAt(11),undefined);assert.equal(editor.dirty,false);assert.equal(editor._notice,"Change undone.");assert.equal(editor._error,"");
  assert.match(editor.feedbackMarkup(),/Change undone\./);assert.doesNotMatch(editor.feedbackMarkup(),/exceeds|Card copied/);
  editor._error="Another stale error";editor.history("redo");assert.ok(editor.cardAt(11));assert.equal(editor._notice,"Change redone.");assert.equal(editor._error,"");
});

test("empty or busy history preserves feedback and stacks after the existing field-finalization boundary",()=>{
  for(const direction of ["undo","redo"])for(const busy of [false,true]){
    const editor=makeEditor();if(busy)editor.mutate(layout=>{layout.cards[1].title="Pending work";});
    editor._busy=busy;editor._notice="Keep notice";editor._error="Keep error";const before=clone(editor._draft),undo=clone(editor._undo),redo=clone(editor._redo);
    let finishes=0,renders=0,fetches=0,schedules=0;const finish=editor.finishField;
    editor.finishField=function(){finishes++;return finish.call(this);};editor.render=()=>{renders++;};editor.fetchSelectedEntity=()=>{fetches++;};editor.scheduleDraft=()=>{schedules++;};
    editor.history(direction);assert.equal(finishes,1);assert.equal(editor._notice,"Keep notice");assert.equal(editor._error,"Keep error");
    assert.deepEqual(clone(editor._draft),before);assert.deepEqual(clone(editor._undo),undo);assert.deepEqual(clone(editor._redo),redo);assert.equal(renders,0);assert.equal(fetches,0);assert.equal(schedules,0);
  }
});


function multiEditor(callWS) {
  const editor=makeEditor(callWS);
  editor._draft.version=3;editor.profile.layout_versions=[2,3];
  editor.cardAt(2).action={kind:"control",control:"light"};
  editor._draft.cards.push({...card("third",13,"sensor.humidity"),type:"sensor",visible:false,action:{kind:"none"}});
  editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);
  return editor;
}
function selectGroup(editor,slots=[2,3]) {
  assert.equal(editor.startCardSelection(),true);
  for(const slot of slots)assert.equal(editor.toggleCardSelection(slot),true);
}

test("multi-selection is ephemeral and hidden cards remain selectable across the existing pages",async()=>{
  let calls=0;const editor=multiEditor(async()=>{calls++;throw Error("No request expected");}),before=clone(editor._draft);
  assert.equal(editor.startCardSelection(),true);assert.equal(editor.toggleCardSelection(2),true);
  for(const slot of [0,11,99])assert.equal(editor.toggleCardSelection(slot),false);
  await editor.onClick({target:{closest:()=>({dataset:{action:"page",page:"home-4"}})},preventDefault(){}});
  assert.equal(editor.toggleCardSelection(13),true);assert.deepEqual([...editor._selectedCardIds],["first","third"]);
  assert.match(editor.cardSelectionMarkup(),/Selected: 2 · on this page: 1/);
  assert.match(editor.previewMarkup(),/hidden-card[^>]*aria-pressed="true"/);
  assert.doesNotMatch(editor.previewMarkup(),/class="tile-drag"/);
  assert.equal(editor._selectedSlot,null);assert.equal(editor.dirty,false);assert.equal(editor._undo.length,0);
  assert.deepEqual(clone(editor._draft),before);assert.equal(calls,0);
});

test("selecting a page adds only eligible occupied cards and clear keeps the explicit mode",()=>{
  const editor=multiEditor();editor.cardAt(3).visible=false;editor.profile.slots.find(slot=>slot.slot===3).types=["sensor"];
  assert.equal(editor.startCardSelection(),true);assert.equal(editor.selectPageCards(),true);assert.deepEqual([...editor._selectedCardIds],["first"]);
  editor._pageId="home-4";assert.equal(editor.selectPageCards(),true);assert.deepEqual([...editor._selectedCardIds],["first","third"]);
  assert.equal(editor.clearCardSelection(),true);assert.equal(editor._selectedCardIds.size,0);assert.equal(editor._selectingCards,true);assert.equal(editor.dirty,true);
  assert.equal(editor._undo.length,0);
});

test("the selection limit is14 and page selection refuses an over-capacity set atomically",()=>{
  const editor=makeEditor();editor.profile.slots=Array.from({length:15},(_,i)=>({slot:i+2,page_id:"home-2",editable:true,hidden:false,types:["entity"],x:0,y:i*20,width:20,height:20}));
  editor._draft.cards=Array.from({length:15},(_,i)=>card(`bounded-${i}`,i+2));editor._saved=clone(editor._draft);
  editor.startCardSelection();assert.equal(editor.selectPageCards(),false);assert.equal(editor._selectedCardIds.size,0);
  for(let slot=2;slot<16;slot++)assert.equal(editor.toggleCardSelection(slot),true);
  assert.equal(editor.toggleCardSelection(16),false);assert.equal(editor._selectedCardIds.size,14);assert.equal(editor.dirty,false);
});

test("a bulk visibility operation keeps all typed fields, uses one transaction and is exactly undoable",()=>{
  const editor=multiEditor();editor.cardAt(3).action={kind:"service",service:"switch.turn_on",data:{nested:{keep:[1,2,3]}}};
  editor._saved=clone(editor._draft);const before=clone(editor._draft);selectGroup(editor,[2,13]);
  let mutations=0;const mutate=editor.mutate;editor.mutate=function(change){mutations++;return mutate.call(this,change);};
  assert.equal(editor.setSelectedVisibility(false),true);assert.equal(mutations,1);assert.equal(editor._undo.length,1);
  const hidden=clone(editor._draft);assert.deepEqual(hidden.cards,before.cards.map(card=>["first","third"].includes(card.id)?{...card,visible:false}:card));
  assert.equal(editor._selectedCardIds.size,2);assert.equal(editor._selectingCards,true);assert.match(editor._notice,/Cards hidden/);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);assert.equal(editor._selectingCards,false);assert.equal(editor._selectedCardIds.size,0);
  editor.history("redo");assert.deepEqual(clone(editor._draft),hidden);assert.equal(editor._selectedCardIds.size,0);
});

test("idempotent Show and Hide create no history and preserve the chosen IDs",()=>{
  const editor=multiEditor();selectGroup(editor);
  assert.equal(editor.setSelectedVisibility(true),false);assert.equal(editor._undo.length,0);assert.equal(editor.dirty,false);
  assert.equal(editor.setSelectedVisibility(false),true);assert.equal(editor._undo.length,1);
  assert.equal(editor.setSelectedVisibility(false),false);assert.equal(editor._undo.length,1);assert.equal(editor._selectedCardIds.size,2);
  assert.equal(editor.setSelectedVisibility(true),true);assert.equal(editor._undo.length,2);assert.equal(editor.dirty,false);
});

test("Hide checks the full byte limit before true-to-false expansion and never mutates a partial group",()=>{
  const editor=multiEditor();editor.profile.max_document_bytes=new TextEncoder().encode(JSON.stringify(editor._draft)).length;
  const before=clone(editor._draft);selectGroup(editor);
  assert.equal(editor.setSelectedVisibility(false),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
  assert.equal(editor._selectedCardIds.size,2);assert.match(editor._error,/limit/);
});

test("bulk delete reviews escaped titles/count then cancel leaves the draft and selection untouched",async()=>{
  const editor=multiEditor();editor.cardAt(2).title='<img onerror="bad">';const before=clone(editor._draft);selectGroup(editor,[2,13]);
  assert.equal(editor.requestSelectedDelete(),true);assert.equal(editor._pending.kind,"bulk-delete");assert.equal(editor._undo.length,0);
  let markup=editor.modalMarkup();assert.match(markup,/Delete 2 cards/);assert.match(markup,/&lt;img/);assert.doesNotMatch(markup,/<img/);assert.match(markup,/third/);assert.match(markup,/Place 14/);
  editor._hass.locale.language="pl";markup=editor.modalMarkup();assert.match(markup,/Usunąć ze szkicu: 2/);assert.match(markup,/Cofnij odtwarza całą grupę/);
  await clickAction(editor,"modal-cancel");assert.equal(editor._pending,null);assert.equal(editor._selectingCards,true);assert.equal(editor._selectedCardIds.size,2);
  assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);assert.doesNotMatch(editor.cardSelectionMarkup(),/data-action="batch-delete" disabled/);
});

test("confirmed bulk delete is one reversible filter and never deletes reserved or unrelated cards",()=>{
  const editor=multiEditor();const before=clone(editor._draft);selectGroup(editor,[2,13]);editor.requestSelectedDelete();
  let mutations=0;const mutate=editor.mutate;editor.mutate=function(change){mutations++;return mutate.call(this,change);};
  assert.equal(editor.confirmSelectedDelete(),true);assert.equal(mutations,1);assert.equal(editor._undo.length,1);
  assert.deepEqual(clone(editor._draft.cards),before.cards.filter(card=>!["first","third"].includes(card.id)));
  assert.equal(editor._selectedCardIds.size,0);assert.equal(editor._selectingCards,true);assert.equal(editor._pending,null);assert.match(editor._notice,/removed from the draft: 2/);
  const deleted=clone(editor._draft);editor.history("undo");assert.deepEqual(clone(editor._draft),before);assert.equal(editor.dirty,false);assert.equal(editor._selectedCardIds.size,0);
  editor.history("redo");assert.deepEqual(clone(editor._draft),deleted);
});

test("delete rejects changed selected snapshots, identity, slot, duplicate ID and revision without partial work",()=>{
  const edits=[editor=>{editor.cardAt(2).title="Later title";},editor=>{editor.cardAt(2).action={kind:"service",service:"light.turn_on",data:{brightness_pct:12}};},
    editor=>{editor.cardAt(2).visible=false;},editor=>{editor.cardAt(2).id="new identity";},editor=>{editor.cardAt(2).slot=11;},
    editor=>{editor._draft.cards.push({...clone(editor.cardAt(2)),slot:11});},editor=>{editor._draft.cards=editor._draft.cards.filter(card=>card.slot!==2);},
    editor=>{editor._saved.revision++;},editor=>{editor.entry.layout.revision++;},editor=>{editor._draft.version=2;}];
  for(const edit of edits){const editor=multiEditor();selectGroup(editor);editor.requestSelectedDelete();edit(editor);const before=clone(editor._draft),history=editor._undo.length;
    assert.equal(editor.confirmSelectedDelete(),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,history);assert.ok(editor.cardAt(3));}
});

test("delete revalidates nested selected data and preserves later unrelated edits",()=>{
  const changed=multiEditor();changed.cardAt(2).action={kind:"service",service:"light.turn_on",data:{rgb_color:[1,2,3]}};selectGroup(changed);changed.requestSelectedDelete();
  changed.cardAt(2).action.data.rgb_color[0]=99;assert.equal(changed.confirmSelectedDelete(),false);assert.equal(changed.cardAt(2).action.data.rgb_color[0],99);
  const editor=multiEditor();selectGroup(editor);editor.requestSelectedDelete();editor.mutate(layout=>{layout.cards.find(card=>card.slot===13).title="Keep unrelated work";});
  const beforeDelete=clone(editor._draft);assert.equal(editor.confirmSelectedDelete(),true);assert.equal(editor.cardAt(13).title,"Keep unrelated work");assert.equal(editor._undo.length,2);
  editor.history("undo");assert.deepEqual(clone(editor._draft),beforeDelete);
});

test("selection mode guards legacy assign/move/remove/copy/cut/paste/edit and pointer or keyboard carry entrypoints",async()=>{
  let calls=0;const editor=multiEditor(async()=>{calls++;});editor._entityIndex.set("light.room",{entity_id:"light.room",domain:"light",name:"Lamp"});selectGroup(editor);
  const before=clone(editor._draft);editor._selectedSlot=2;
  for(const [name,args] of [["assignEntity",["light.room",11]],["moveCard",[2,11]],["removeCard",[]],["copyCard",[2]],["cutCard",[2]],["pasteCard",[11]],["requestLightControl",[]]])assert.equal(editor[name](...args),false,name);
  editor.editField({dataset:{field:"title"},value:"Wrong single-card edit"});editor.startCarry({dataset:{dragKind:"card",from:"2"}});
  editor.onPointerDown({button:0,target:{closest:()=>({dataset:{dragKind:"card",from:"2"}})}});
  assert.equal(await editor.importText("not a file"),false);assert.equal(editor._drag,null);assert.equal(editor._carry,null);
  assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);assert.equal(calls,0);
});

test("busy modal drag carry invalid-field conflict and explicit disconnect block bulk operations",()=>{
  for(const [key,value] of [["_busy",true],["_pending",{kind:"switch"}],["_drag",{}],["_carry",{}],["_fieldErrors",{title:"invalid"}],["_conflict",true]]){
    const editor=multiEditor();selectGroup(editor);editor[key]=value;const before=clone(editor._draft);
    assert.equal(editor.toggleCardSelection(13),false,key);assert.equal(editor.setSelectedVisibility(false),false,key);assert.equal(editor.requestSelectedDelete(),false,key);assert.deepEqual(clone(editor._draft),before);
  }
  for(const [key,value] of [["_busy",true],["_pending",{}],["_drag",{}],["_carry",{}],["_fieldErrors",{title:"invalid"}],["_profileStale",true]]){
    const editor=multiEditor();editor[key]=value;assert.equal(editor.startCardSelection(),false,key);assert.equal(editor._selectingCards,false);
  }
});

test("selection context clears on entry user profile detach and explicit HA disconnect while device offline is editable",()=>{
  for(const change of [editor=>{editor.selectEntry("screen-b");},editor=>{editor._hass.user={id:"another"};editor.paintValues();},editor=>{editor.profile.width++;editor.paintValues();},
    editor=>{editor.disconnectedCallback();},editor=>{editor.hass={...editor._hass,connected:false};},editor=>{editor.hass={...editor._hass,connection:{connected:false}};}]){
    const editor=multiEditor();selectGroup(editor);change(editor);assert.equal(editor._selectingCards,false);assert.equal(editor._selectedCardIds.size,0);assert.equal(editor.confirmSelectedDelete(),false);
  }
  const offline=multiEditor();selectGroup(offline);offline._status.device_available=false;offline.paintValues();assert.equal(offline._selectedCardIds.size,2);assert.equal(offline.setSelectedVisibility(false),true);
});

test("real status profile invalidation and clean remote replacement clear selection without applying it",async()=>{
  for(const change of [latest=>{latest.profile.width++;},latest=>{latest.layout.revision++;}]){
    const editor=multiEditor();selectGroup(editor);const latest=clone(editor.entry);change(latest);editor._hass.callWS=async()=>({entries:[latest]});await editor.refreshStatus();
    assert.equal(editor._selectingCards,false);assert.equal(editor._selectedCardIds.size,0);assert.equal(editor._undo.length,0);
  }
});

test("selection is not persisted and bulk drafts still use explicit Save and revision CAS",async()=>{
  const requests=[],storage=new BrowserStorage();const editor=enableDraft(multiEditor(async request=>{requests.push(clone(request));throw {code:"revision_conflict"};}),storage);
  selectGroup(editor);editor.persistDraft();assert.equal(storage.length,0);assert.equal(editor.setSelectedVisibility(false),true);flushDraft(editor);
  assert.equal(requests.length,0);const record=JSON.parse(storage.getItem(editor.draftKey()));
  assert.deepEqual(Object.keys(record.layout).sort(),["cards","profile","version"]);assert.doesNotMatch(JSON.stringify(record),/_selectedCardIds|_selectingCards|bulk-delete/);
  const before=clone(editor._draft);assert.equal(await editor.save(),false);assert.equal(requests.length,1);assert.equal(requests[0].type,"atmosfera_echo_hub/layout/save");assert.equal(requests[0].expected_revision,4);
  assert.deepEqual(clone(editor._draft),before);assert.equal(editor._conflict,true);
});

test("Space and Enter toggle the focused card, Delete only reviews, Escape clears without mutation and fields retain native keys",()=>{
  const editor=multiEditor();editor.startCardSelection();const before=clone(editor._draft);
  shortcut(editor,keyboardTarget(2)," ",{ctrlKey:false,code:"Space"});assert.deepEqual([...editor._selectedCardIds],["first"]);assert.equal(editor._carry,null);
  shortcut(editor,keyboardTarget(3),"Enter",{ctrlKey:false});assert.equal(editor._selectedCardIds.size,2);
  for(const tag of ["INPUT","SELECT","TEXTAREA"]){assert.equal(shortcut(editor,keyboardTarget(13,tag),"x").prevented,false);assert.equal(shortcut(editor,keyboardTarget(13,tag),"Delete",{ctrlKey:false}).prevented,false);}
  const editable=keyboardTarget(13);editable.isContentEditable=true;assert.equal(shortcut(editor,editable,"v").prevented,false);
  shortcut(editor,keyboardTarget(2),"Delete",{ctrlKey:false});assert.equal(editor._pending.kind,"bulk-delete");assert.deepEqual(clone(editor._draft),before);
  shortcut(editor,keyboardTarget(2),"Escape",{ctrlKey:false});assert.equal(editor._pending,null);assert.equal(editor._selectingCards,false);assert.equal(editor._selectedCardIds.size,0);assert.deepEqual(clone(editor._draft),before);
});

test("selection UI buttons are localized click-routed and aria-pressed follows stable IDs",async()=>{
  const editor=multiEditor();editor._hass.locale.language="pl";await clickAction(editor,"selection-start");await clickAction(editor,"selection-page");
  assert.match(editor.cardSelectionMarkup(),/Zaznaczono: 2 · na tej stronie: 2/);assert.match(editor.cardSelectionMarkup(),/Ukryj zaznaczone/);
  assert.match(editor.inspectorMarkup(),/Zaznaczanie kart/);assert.doesNotMatch(editor.inspectorMarkup(),/id="properties"/);
  assert.match(editor.previewMarkup(),/data-slot="2"[^>]*aria-pressed="true"/);assert.match(editor.previewMarkup(),/data-slot="11"[^>]*tabindex="-1"[^>]*aria-disabled="true"/);
  await clickAction(editor,"batch-hide");assert.equal(editor.cardAt(2).visible,false);await clickAction(editor,"selection-clear");assert.equal(editor._selectedCardIds.size,0);
  await clickAction(editor,"selection-exit");assert.equal(editor._selectingCards,false);
});

test("ordinary HA updates and unchanged status polls preserve selection toolbar inspector and search focus",async()=>{
  const editor=multiEditor();selectGroup(editor);const dom=trackedEditorDOM(editor),toolbar=dom.region(editor.cardSelectionMarkup());dom.regions.set("#card-selection",toolbar);
  const inspector=dom.regions.get("#inspector"),feedback=dom.regions.get("#feedback"),searchRegion=dom.region(),focused={tagName:"INPUT",region:searchRegion};dom.root.activeElement=focused;
  const before=clone(editor._draft);editor.hass={...editor._hass,states:{"light.room":{state:"off",attributes:{}}}};
  editor._hass.callWS=async()=>({entries:[clone(editor.entry)]});await editor.refreshStatus();editor.paintToolbar();editor.paintToolbar();
  assert.equal(toolbar.writes,0);assert.equal(inspector.writes,0);assert.equal(feedback.writes,0);assert.equal(dom.root.htmlWrites,0);assert.equal(dom.root.activeElement,focused);
  assert.equal(editor._selectedCardIds.size,2);assert.deepEqual(clone(editor._draft),before);
});

test("finishing a valid field edit is a prior undo boundary; the following group is exactly one further undo",()=>{
  const editor=multiEditor(),original=clone(editor._draft);editor._fieldBefore=clone(editor._draft);editor.cardAt(2).title="Prior field edit";
  selectGroup(editor);assert.equal(editor._undo.length,1);const beforeGroup=clone(editor._draft);editor.setSelectedVisibility(false);assert.equal(editor._undo.length,2);
  editor.history("undo");assert.deepEqual(clone(editor._draft),beforeGroup);editor.history("undo");assert.deepEqual(clone(editor._draft),original);
});

test("successful Save Reload import restore and undo never resurrect ephemeral selection",async()=>{
  const saved=multiEditor(async request=>({layout:{...clone(request.layout),revision:5},status:{saved_revision:5}}));selectGroup(saved);saved.setSelectedVisibility(false);
  assert.equal(await saved.save(),true);assert.equal(saved._selectingCards,false);assert.equal(saved._selectedCardIds.size,0);
  const reload=multiEditor();selectGroup(reload);reload._hass.callWS=async()=>({entries:[clone(reload.entry)]});await reload.reloadSaved();assert.equal(reload._selectingCards,false);
  const imported=multiEditor();selectGroup(imported);imported._pending={kind:"import",layout:clone(imported._draft),warnings:[]};imported.useImported();assert.equal(imported._selectingCards,false);
  const restored=multiEditor();selectGroup(restored);restored._recovery=clone(restored._draft);restored._recovery.cards[1].title="Recovered";restored.restoreDraft();assert.equal(restored._selectingCards,false);
});


test("selection entry exit and completed group actions restore an explicit keyboard focus target",()=>{
  const editor=multiEditor(),focused=[];
  editor.focusSlot=slot=>focused.push(`slot:${slot}`);
  editor.shadowRoot.querySelector=selector=>selector.startsWith('[data-action=')?{focus(){focused.push(selector);}}:null;
  assert.equal(editor.startCardSelection(),true);assert.equal(focused.at(-1),"slot:2");
  editor.toggleCardSelection(2);assert.equal(editor.setSelectedVisibility(false),true);assert.equal(focused.at(-1),'[data-action="batch-hide"]');
  editor.requestSelectedDelete();assert.equal(editor.confirmSelectedDelete(),true);assert.equal(focused.at(-1),'[data-action="selection-page"]');
  editor.endCardSelection();assert.equal(focused.at(-1),'[data-action="selection-start"]');
});

test("context invalidation removes an obsolete delete dialog instead of leaving an orphaned confirmation",()=>{
  const editor=multiEditor();selectGroup(editor);editor.requestSelectedDelete();editor.profile.width++;
  assert.equal(editor.modalMarkup(),"");assert.equal(editor._pending,null);assert.equal(editor._selectingCards,false);assert.ok(editor.cardAt(2));
  const direct=multiEditor();selectGroup(direct);direct.requestSelectedDelete();direct._hass.connected=false;
  const before=clone(direct._draft);assert.equal(direct.confirmSelectedDelete(),false);assert.equal(direct._pending,null);assert.deepEqual(clone(direct._draft),before);
});

test("a known remote revision conflict blocks and repaints bulk actions without replacing the dirty draft",async()=>{
  const editor=multiEditor();selectGroup(editor);editor.setSelectedVisibility(false);const draft=clone(editor._draft);
  const dom=trackedEditorDOM(editor),toolbar=dom.region(editor.cardSelectionMarkup());dom.regions.set("#card-selection",toolbar);
  const latest=clone(editor.entry);latest.layout.revision++;editor._hass.callWS=async()=>({entries:[latest]});await editor.refreshStatus();
  assert.equal(editor._conflict,true);assert.equal(toolbar.writes,1);assert.match(toolbar.innerHTML,/data-action="batch-show" disabled/);
  assert.equal(editor.setSelectedVisibility(true),false);assert.equal(editor.requestSelectedDelete(),false);assert.deepEqual(clone(editor._draft),draft);
  editor.endCardSelection();assert.equal(editor.startCardSelection(),false);
});


function groupEditor(callWS) {
  const editor=multiEditor(callWS);
  editor.profile.slots.push(...[12,14,15].map(slot=>({slot,page_id:slot===12?"home-2":"home-4",editable:true,hidden:false,types:["entity","sensor","action"],x:20,y:20,width:100,height:100})));
  return editor;
}
function copyGroup(editor,slots=[2,13]) {selectGroup(editor,slots);assert.equal(editor.copySelectedCards(),true);}
function reviewGroup(editor,slots=[11,14]) {assert.equal(editor.requestGroupPaste(),true);slots.forEach((slot,index)=>assert.equal(editor.setGroupTarget(index,String(slot)),true));}
function withUUIDs(values,run) {
  const original=context.crypto;let calls=0;
  context.crypto={randomUUID(){const value=values[Math.min(calls++,values.length-1)];if(value instanceof Error)throw value;return value;}};
  try{return run(()=>calls);}finally{context.crypto=original;}
}

test("group copy snapshots14-or-fewer cards in source-page/slot order and ends selection without history or requests",()=>{
  let requests=0;const editor=groupEditor(async()=>{requests++;throw Error("No request expected");});
  const original=clone(editor._draft);copyGroup(editor,[13,2]);
  assert.equal(editor._cardClipboard.mode,"group-copy");assert.deepEqual(clone(editor.clipboardGroup()).map(card=>card.id),["first","third"]);
  assert.equal(editor._selectingCards,false);assert.equal(editor._selectedCardIds.size,0);assert.equal(editor.dirty,false);assert.equal(editor._undo.length,0);
  assert.deepEqual(clone(editor._draft),original);assert.equal(editor.clipboardCard(),undefined);assert.equal(requests,0);
  editor.cardAt(2).title="Edited source";assert.equal(editor.clipboardGroup()[0].title,"first");
});

test("group review has escaped per-card labels, both destination page optgroups and no default mapping",()=>{
  const editor=groupEditor();editor.cardAt(2).title='<img onerror="x">';copyGroup(editor);assert.equal(editor.requestGroupPaste(),true);
  assert.deepEqual(clone(editor._pending.targets),[null,null]);assert.equal(editor.groupPasteReady(),false);
  let markup=editor.modalMarkup();assert.match(markup,/&lt;img/);assert.doesNotMatch(markup,/<img/);assert.match(markup,/<optgroup label="Security">/);assert.match(markup,/<optgroup label="Controls">/);
  assert.equal((markup.match(/value="" selected/g)||[]).length,2);assert.match(markup,/data-action="modal-paste-group" disabled/);
  editor._hass.locale.language="pl";markup=editor.modalMarkup();assert.match(markup,/Wklej skopiowane karty: 2/);assert.match(editor.clipboardMarkup(),/Skopiowana grupa: 2/);
});

test("mapped targets must be distinct empty compatible editable places and clearing never maps to reserved0",()=>{
  const editor=groupEditor();copyGroup(editor);editor.requestGroupPaste();
  for(const value of ["0","2","13","-1","11x","1e1"])assert.equal(editor.setGroupTarget(0,value),false,value);
  assert.equal(editor.setGroupTarget(0,"11"),true);assert.equal(editor.setGroupTarget(1,"11"),false);assert.deepEqual(clone(editor._pending.targets),[11,null]);
  assert.equal(editor.setGroupTarget(1,"14"),true);assert.equal(editor.groupPasteReady(),true);
  assert.equal(editor.setGroupTarget(0,""),true);assert.deepEqual(clone(editor._pending.targets),[null,14]);assert.equal(editor.groupPasteReady(),false);
  assert.equal(editor.setGroupTarget(-1,"12"),false);assert.equal(editor.setGroupTarget(99,"12"),false);
});

test("one confirmed group preserves visibility actions and every typed field in one existing mutate/UndoRedo",()=>{
  const requests=[];const editor=groupEditor(async request=>{requests.push(clone(request));});editor.cardAt(2).action={kind:"service",service:"light.turn_on",data:{rgb_color:[1,2,3],brightness_pct:25}};
  const source=clone(editor._draft.cards.filter(card=>[2,13].includes(card.slot))),before=clone(editor._draft);copyGroup(editor);reviewGroup(editor);
  let mutations=0;const mutate=editor.mutate;editor.mutate=function(change){mutations++;return mutate.call(this,change);};
  assert.equal(editor.confirmGroupPaste(),true);assert.equal(mutations,1);assert.equal(editor._undo.length,1);assert.equal(editor._pending,null);
  const first=clone(editor.cardAt(11)),second=clone(editor.cardAt(14));assert.notEqual(first.id,source[0].id);assert.notEqual(second.id,source[1].id);assert.notEqual(first.id,second.id);
  assert.deepEqual({...first,id:source[0].id,slot:source[0].slot},source[0]);assert.deepEqual({...second,id:source[1].id,slot:source[1].slot},source[1]);
  assert.equal(requests.length,0);const pasted=clone(editor._draft);editor.cardAt(11).action.data.rgb_color[0]=99;assert.equal(editor.clipboardGroup()[0].action.data.rgb_color[0],1);
  editor._draft=clone(pasted);editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.deepEqual(clone(editor._draft),pasted);assert.deepEqual(requests.map(request=>request.type),["atmosfera_echo_hub/catalogue/get"]);
});

test("a second explicit paste gets fresh IDs while the immutable copied group survives the first paste and Undo",()=>{
  const editor=groupEditor();copyGroup(editor);reviewGroup(editor);assert.equal(editor.confirmGroupPaste(),true);const first=clone(editor.cardAt(11)),second=clone(editor.cardAt(14));
  reviewGroup(editor,[12,15]);assert.equal(editor.confirmGroupPaste(),true);
  const ids=[first.id,second.id,editor.cardAt(12).id,editor.cardAt(15).id];assert.equal(new Set(ids).size,4);assert.equal(editor._undo.length,2);
  editor.history("undo");assert.equal(editor.cardAt(12),undefined);assert.equal(editor.cardAt(15),undefined);assert.equal(editor.cardAt(11).id,first.id);assert.equal(editor.clipboardGroup().length,2);
});

test("current, deleted source and in-batch ID collisions abort the entire group with bounded generation",()=>{
  for(const mode of ["current","deleted-source","batch"]){
    const editor=groupEditor();editor.cardAt(2).id="card-source";copyGroup(editor);
    if(mode==="deleted-source")editor._draft.cards=editor._draft.cards.filter(card=>card.id!=="card-source");
    reviewGroup(editor);const before=clone(editor._draft);
    withUUIDs([mode==="batch"?"same":"source"],calls=>{assert.equal(editor.confirmGroupPaste(),false);assert.equal(calls(),mode==="batch"?2:1);});
    assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);assert.equal(editor.cardAt(11),undefined);assert.match(editor._error,/No cards were pasted/);
  }
});

test("invalid or unavailable UUID generation never partially inserts a group",()=>{
  for(const value of ["x".repeat(80),new Error("No secure random source")]){const editor=groupEditor();copyGroup(editor);reviewGroup(editor);const before=clone(editor._draft);
    withUUIDs([value],calls=>{assert.equal(editor.confirmGroupPaste(),false);assert.equal(calls(),1);});assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);}
});

test("the complete mapped UTF8 candidate is checked before any mutation",()=>{
  const editor=groupEditor();editor.cardAt(2).title="Żółć".repeat(8);editor.cardAt(13).title="Śnieg".repeat(6);
  const cards=clone(editor._draft.cards.filter(card=>[2,13].includes(card.slot))),expected=clone(editor._draft);
  expected.cards.push({...cards[0],id:"card-utf8-a",slot:11},{...cards[1],id:"card-utf8-b",slot:14});
  const text=JSON.stringify(expected);assert.ok(new TextEncoder().encode(text).length>text.length);editor.profile.max_document_bytes=text.length;
  copyGroup(editor);reviewGroup(editor);const before=clone(editor._draft);
  withUUIDs(["utf8-a","utf8-b"],()=>assert.equal(editor.confirmGroupPaste(),false));assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);assert.match(editor._error,/limit/);
});

test("card capacity is a whole-group bound with zero ID work when only one of two cards would fit",()=>{
  const editor=groupEditor();editor.profile.max_cards=editor._draft.cards.length+1;copyGroup(editor);reviewGroup(editor);
  withUUIDs([new Error("Must not generate")],calls=>{assert.equal(editor.groupPasteReady(),false);assert.equal(editor.confirmGroupPaste(),false);assert.equal(calls(),0);});
  assert.equal(editor._draft.cards.length,4);assert.equal(editor._undo.length,0);
});

test("later edits or deletion of copied sources do not change the snapshots, and unrelated review-time edits survive paste",()=>{
  const editor=groupEditor();copyGroup(editor);reviewGroup(editor);const snapshot=clone(editor.clipboardGroup());
  editor._draft.cards=editor._draft.cards.filter(card=>card.slot!==2);editor.cardAt(13).title="New original title";
  editor.mutate(layout=>{layout.cards.find(card=>card.slot===3).title="Unrelated work";});const beforePaste=clone(editor._draft);
  assert.equal(editor.confirmGroupPaste(),true);assert.equal(editor.cardAt(11).title,snapshot[0].title);assert.equal(editor.cardAt(14).title,snapshot[1].title);assert.equal(editor.cardAt(3).title,"Unrelated work");
  editor.history("undo");assert.deepEqual(clone(editor._draft),beforePaste);
});

test("late occupation including hidden cards refuses the whole group while keeping the original document intact",()=>{
  const editor=groupEditor();copyGroup(editor);reviewGroup(editor);editor._draft.cards.push({...card("late",14),visible:false});const before=clone(editor._draft);
  assert.equal(editor.groupPasteReady(),false);assert.equal(editor.confirmGroupPaste(),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);assert.equal(editor.cardAt(11),undefined);assert.match(editor.modalMarkup(),/Selected place is no longer available/);
});

test("saved/server revision, epoch, profile, version and clipboard review identity must all remain current",()=>{
  const changes=[editor=>editor._saved.revision++,editor=>editor.entry.layout.revision++,editor=>editor._selectionEpoch++,editor=>editor.profile.width++,editor=>editor._draft.version=2,
    editor=>{editor._cardClipboard={...editor._cardClipboard};},editor=>{editor._cardClipboard.cards[0].title="Altered buffer";}];
  for(const change of changes){const editor=groupEditor();copyGroup(editor);reviewGroup(editor);change(editor);const before=clone(editor._draft);
    assert.equal(editor.confirmGroupPaste(),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);}
});

test("group intent and pending review clear on user entry profile disconnect detach and Escape",()=>{
  const changes=[editor=>editor.selectEntry("screen-b"),editor=>{editor.hass={...editor._hass,user:{id:"new-user"}};},editor=>{editor.profile.width++;editor.paintValues();},
    editor=>{editor.hass={...editor._hass,connected:false};},editor=>editor.disconnectedCallback(),editor=>shortcut(editor,keyboardTarget(2),"Escape",{ctrlKey:false})];
  for(const change of changes){const editor=groupEditor();copyGroup(editor);reviewGroup(editor);change(editor);assert.equal(editor._cardClipboard,null);assert.equal(editor._pending,null);}
});

test("legacy clipboard helpers cannot read or singly paste group data and replacing an intent keeps one shared clipboard",()=>{
  const editor=groupEditor();copyGroup(editor);const before=clone(editor._draft);assert.equal(editor.clipboardCard(),undefined);assert.equal(editor.canPasteCard(11),false);assert.equal(editor.pasteCard(11),false);assert.equal(editor.pasteMarkup(11),"");
  assert.deepEqual(clone(editor._draft),before);assert.equal(editor.copyCard(3),true);assert.equal(editor.clipboardGroup(),undefined);assert.equal(editor.clipboardCard().id,"second");
  assert.equal(editor.pasteCard(11),true);assert.equal(editor.cardAt(11).entity_id,"switch.pump");
  assert.equal(editor.cutCard(13),true);assert.equal(editor._cardClipboard.mode,"cut");assert.equal(editor.clipboardGroup(),undefined);
});

test("group copy and review obey busy modal carry drag field conflict and profile guards",()=>{
  for(const [key,value] of [["_busy",true],["_pending",{kind:"switch"}],["_drag",{}],["_carry",{}],["_fieldErrors",{title:"invalid"}],["_conflict",true],["_profileStale",true]]){
    const copy=groupEditor();selectGroup(copy);copy[key]=value;assert.equal(copy.copySelectedCards(),false,key);assert.notEqual(copy._cardClipboard?.mode,"group-copy");
    const paste=groupEditor();copyGroup(paste);paste[key]=value;assert.equal(paste.requestGroupPaste(),false,key);
  }
});

test("CtrlCopy ends selection, CtrlPaste opens mapping, text controls keep native clipboard and Cancel retains the copied group",async()=>{
  const editor=groupEditor();selectGroup(editor);shortcut(editor,keyboardTarget(2),"c");assert.equal(editor._selectingCards,false);assert.equal(editor._cardClipboard.mode,"group-copy");
  for(const tag of ["INPUT","SELECT","TEXTAREA"])assert.equal(shortcut(editor,keyboardTarget(2,tag),"v").prevented,false);
  shortcut(editor,keyboardTarget(2),"v");assert.equal(editor._pending.kind,"group-paste");const intent=editor._cardClipboard;
  await clickAction(editor,"modal-cancel");assert.equal(editor._pending,null);assert.equal(editor._cardClipboard,intent);
});

test("mapping rows restore select focus and the modal traps Tab across selects and buttons",async()=>{
  const editor=groupEditor();copyGroup(editor);const focused=[];
  const controls=[{tagName:"SELECT",closest(){return null;},focus(){focused.push("first-select");}},{tagName:"SELECT",closest(){return null;},focus(){focused.push("second-select");}},{tagName:"BUTTON",closest(){return null;},focus(){focused.push("cancel");}}];
  editor.shadowRoot.querySelector=selector=>selector==='.modal select'?controls[0]:selector==='[data-group-target="1"]'?controls[1]:null;
  assert.equal(editor.requestGroupPaste(),true);editor.paintModalFocus();assert.equal(focused.at(-1),"first-select");
  await editor.onChange({target:{dataset:{groupTarget:"1"},value:"14"}});assert.equal(focused.at(-1),"second-select");
  editor.shadowRoot.querySelectorAll=selector=>selector==='.modal select:not([disabled]),.modal button:not([disabled])'?controls:[];
  let prevented=0;editor.onKeyDown({key:"Tab",target:controls[2],preventDefault(){prevented++;}});assert.equal(focused.at(-1),"first-select");
  editor.onKeyDown({key:"Tab",shiftKey:true,target:controls[0],preventDefault(){prevented++;}});assert.equal(focused.at(-1),"cancel");assert.equal(prevented,2);
});

test("poll and paint validity never generate IDs and never re-enable an unmapped or invalid group confirm",async()=>{
  const editor=groupEditor();copyGroup(editor);editor.requestGroupPaste();const button={dataset:{action:"modal-paste-group"},disabled:false};
  editor.shadowRoot.querySelectorAll=selector=>selector==='.modal button'?[button]:[];
  withUUIDs([new Error("Paint must be pure")],calls=>{editor.modalMarkup();editor.paintToolbar();assert.equal(button.disabled,true);assert.equal(calls(),0);});
  editor.setGroupTarget(0,"11");editor.setGroupTarget(1,"14");editor.paintToolbar();assert.equal(button.disabled,false);
  editor._draft.cards.push(card("late",14));editor.paintToolbar();assert.equal(button.disabled,true);assert.equal(editor._undo.length,0);
});

test("ordinary HA updates and unchanged status polls do not rebuild a group review or focused select",async()=>{
  const editor=groupEditor();copyGroup(editor);reviewGroup(editor);const dom=trackedEditorDOM(editor),banner=dom.region(editor.clipboardMarkup());dom.regions.set("#card-clipboard",banner);
  const modal=dom.regions.get("#modal-host"),select={tagName:"SELECT",region:modal};dom.root.activeElement=select;const before=clone(editor._draft);
  editor.hass={...editor._hass,states:{"light.room":{state:"off",attributes:{}}}};editor._hass.callWS=async()=>({entries:[clone(editor.entry)]});await editor.refreshStatus();editor.paintToolbar();
  assert.equal(modal.writes,0);assert.equal(banner.writes,0);assert.equal(dom.root.htmlWrites,0);assert.equal(dom.root.activeElement,select);assert.deepEqual(clone(editor._draft),before);
});

test("v2 stays v2 for ordinary cards and a copied control never silently upgrades it",()=>{
  const regular=groupEditor();regular._draft.version=2;regular.cardAt(2).action={kind:"default"};regular._saved=clone(regular._draft);regular.entry.layout=clone(regular._draft);
  copyGroup(regular);reviewGroup(regular);assert.equal(regular.confirmGroupPaste(),true);assert.equal(regular._draft.version,2);
  const controlled=groupEditor();copyGroup(controlled);controlled._draft.version=2;controlled.requestGroupPaste();assert.equal(controlled.setGroupTarget(0,"11"),false);assert.equal(controlled.groupPasteReady(),false);assert.equal(controlled.confirmGroupPaste(),false);assert.equal(controlled._draft.version,2);assert.equal(controlled._undo.length,0);
});

test("group intent/mappings are never stored while accepted copies use existing explicit Save revision CAS",async()=>{
  const storage=new BrowserStorage(),requests=[];const editor=enableDraft(groupEditor(async request=>{requests.push(clone(request));return {layout:{...clone(request.layout),revision:5},status:{saved_revision:5}};}),storage);
  copyGroup(editor);flushDraft(editor);assert.equal(storage.length,0);reviewGroup(editor);flushDraft(editor);assert.equal(storage.length,0);
  assert.equal(editor.confirmGroupPaste(),true);assert.equal(flushDraft(editor),true);const record=JSON.parse(storage.getItem(editor.draftKey()));assert.doesNotMatch(JSON.stringify(record),/group-copy|group-paste|targets|clipboard/);
  assert.equal(requests.length,0);assert.equal(await editor.save(),true);assert.equal(requests.length,1);assert.equal(requests[0].type,"atmosfera_echo_hub/layout/save");assert.equal(requests[0].expected_revision,4);assert.equal(requests[0].layout.cards.length,6);
});


test("all14 editable cards can be copied at full capacity without inventing destinations or partial paste",()=>{
  const editor=groupEditor();editor.profile.slots=Array.from({length:14},(_,index)=>({slot:index+2,page_id:index<7?"home-2":"home-4",editable:true,hidden:false,types:["entity"],x:0,y:0,width:20,height:20}));
  editor._draft.cards=Array.from({length:14},(_,index)=>card(`source-${index}`,index+2));editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);
  editor.startCardSelection();for(let slot=2;slot<16;slot++)editor.toggleCardSelection(slot);
  assert.equal(editor.copySelectedCards(),true);assert.equal(editor.clipboardGroup().length,14);assert.equal(editor.requestGroupPaste(),true);assert.equal(editor._pending.targets.length,14);
  assert.ok(editor._pending.targets.every(target=>target===null));assert.equal(editor.groupPasteReady(),false);assert.equal(editor.confirmGroupPaste(),false);assert.equal(editor._draft.cards.length,14);assert.equal(editor._undo.length,0);
});


function cutGroup(editor,slots=[2,13]) {selectGroup(editor,slots);assert.equal(editor.cutSelectedCards(),true);}

test("cut selected captures full ordered sources/context and leaves cards untouched until confirmation",()=>{
  const editor=groupEditor(),before=clone(editor._draft);cutGroup(editor,[13,2]);
  assert.equal(editor._cardClipboard.mode,"group-cut");assert.deepEqual(clone(editor.clipboardGroup()).map(card=>card.id),["first","third"]);
  assert.equal(editor._cardClipboard.revision,4);assert.equal(editor._cardClipboard.version,3);assert.equal(editor._cardClipboard.epoch,editor._selectionEpoch);
  assert.equal(editor._selectingCards,false);assert.equal(editor._selectedCardIds.size,0);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);assert.equal(editor.dirty,false);
});

test("a group move changes only slots, keeps array order/IDs/typed data, and uses exactly one undo transaction",()=>{
  const editor=groupEditor();editor.cardAt(2).action={kind:"service",service:"light.turn_on",data:{rgb_color:[3,4,5],brightness_pct:18}};const before=clone(editor._draft);
  cutGroup(editor);reviewGroup(editor);let mutations=0;const mutate=editor.mutate;editor.mutate=function(change){mutations++;return mutate.call(this,change);};
  withUUIDs([new Error("Move must not generate IDs")],calls=>{assert.equal(editor.confirmGroupPaste(),true);assert.equal(calls(),0);});
  const moved=clone(editor._draft),expected=clone(before);expected.cards.forEach(card=>{if(card.id==="first")card.slot=11;if(card.id==="third")card.slot=14;});
  assert.deepEqual(moved,expected);assert.equal(mutations,1);assert.equal(editor._undo.length,1);assert.equal(editor._cardClipboard,null);assert.equal(editor._pending,null);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);assert.equal(editor._cardClipboard,null);editor.history("redo");assert.deepEqual(clone(editor._draft),moved);assert.equal(editor._cardClipboard,null);
});

test("two-way swaps and three-way cycles are committed simultaneously rather than through sequential moves",()=>{
  for(const [sources,targets] of [[[2,13],[13,2]],[[2,3,13],[3,13,2]]]){
    const editor=groupEditor(),before=clone(editor._draft);cutGroup(editor,sources);reviewGroup(editor,targets);assert.equal(editor.groupPasteReady(),true);assert.equal(editor.confirmGroupPaste(),true);
    const expected=clone(before);expected.cards.forEach(card=>{const index=sources.indexOf(card.slot);if(index!==-1)card.slot=targets[index];});
    assert.deepEqual(clone(editor._draft),expected);assert.equal(new Set(editor._draft.cards.map(card=>card.slot)).size,editor._draft.cards.length);assert.equal(editor._undo.length,1);
  }
});

test("all14 editable cards can cycle at full16-card capacity without UUID work or an extra card",()=>{
  const editor=groupEditor();editor.profile.slots=Array.from({length:14},(_,index)=>({slot:index+2,page_id:index<7?"home-2":"home-4",editable:true,hidden:false,types:["entity"],x:0,y:0,width:20,height:20}));
  editor._draft.cards=[{...card("reserved0",0),visible:false},{...card("reserved1",1),visible:false},...Array.from({length:14},(_,index)=>card(`move-${index}`,index+2))];editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);
  const sources=Array.from({length:14},(_,index)=>index+2),targets=sources.slice(1).concat(2),before=clone(editor._draft);cutGroup(editor,sources);reviewGroup(editor,targets);
  withUUIDs([new Error("No IDs at capacity")],calls=>{assert.equal(editor.confirmGroupPaste(),true);assert.equal(calls(),0);});
  assert.equal(editor._draft.cards.length,16);assert.deepEqual(editor._draft.cards.map(card=>card.id),before.cards.map(card=>card.id));assert.equal(editor._undo.length,1);
  assert.deepEqual(clone(editor._draft.cards.slice(0,2)),before.cards.slice(0,2));assert.deepEqual(editor._draft.cards.slice(2).map(card=>card.slot),targets);
});

test("every changed selected-source snapshot, missing/moved card and duplicate source identity or slot refuses the entire move",()=>{
  const changes=[editor=>editor.cardAt(2).title="Changed",editor=>editor.cardAt(2).entity_id="light.other",editor=>editor.cardAt(2).visible=false,
    editor=>editor.cardAt(2).icon="switch",editor=>editor.cardAt(2).palette="surface",editor=>editor.cardAt(2).type="action",editor=>editor.cardAt(2).action={kind:"none"},
    editor=>editor.cardAt(2).slot=12,editor=>editor.cardAt(2).id="changed-id",editor=>editor._draft.cards=editor._draft.cards.filter(card=>card.slot!==2),
    editor=>editor._draft.cards.push({...clone(editor.cardAt(2)),slot:12}),editor=>editor._draft.cards.push({...card("different-id",2),visible:false})];
  for(const change of changes){const editor=groupEditor();cutGroup(editor);reviewGroup(editor);const intent=editor._cardClipboard;change(editor);const before=clone(editor._draft);
    assert.equal(editor.groupCutSourceSlots(),null);assert.equal(editor.confirmGroupPaste(),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);assert.equal(editor._cardClipboard,intent);assert.match(editor._error,/Cut the group again/);}
});

test("a nested source action change refuses review and keeps friendly recut feedback reachable",()=>{
  const editor=groupEditor();editor.cardAt(2).action={kind:"service",service:"light.turn_on",data:{rgb_color:[1,2,3]}};cutGroup(editor);const intent=editor._cardClipboard;
  editor.cardAt(2).action.data.rgb_color[1]=99;assert.equal(editor.requestGroupPaste(),false);assert.equal(editor._pending,null);assert.equal(editor._cardClipboard,intent);assert.match(editor._error,/Cut the group again/);
  assert.match(editor.clipboardMarkup(),/Cut the group again/);assert.match(editor.clipboardMarkup(),/data-action="paste-group" disabled/);assert.equal(editor._undo.length,0);
});

test("unrelated edits made after the move review survive and remain when the group transaction is undone",()=>{
  const editor=groupEditor();cutGroup(editor);reviewGroup(editor);editor.mutate(layout=>{layout.cards.find(card=>card.slot===3).title="Unrelated draft work";});const beforeMove=clone(editor._draft);
  assert.equal(editor.confirmGroupPaste(),true);assert.equal(editor.cardAt(3).title,"Unrelated draft work");assert.equal(editor._undo.length,2);editor.history("undo");assert.deepEqual(clone(editor._draft),beforeMove);
});

test("occupied unselected targets including hidden cards stay blocked and UI selection never grants an occupied-slot exception",()=>{
  for(const hidden of [false,true]){const editor=groupEditor();editor.cardAt(3).visible=!hidden;cutGroup(editor);editor._selectedCardIds.add("second");editor.requestGroupPaste();
    assert.equal(editor.groupTargetCompatible(editor.clipboardGroup()[0],3),false);assert.equal(editor.setGroupTarget(0,"3"),false);assert.equal(editor.cardAt(3).id,"second");assert.equal(editor._undo.length,0);}
  const copy=groupEditor();copyGroup(copy);copy.requestGroupPaste();assert.equal(copy.groupTargetCompatible(copy.clipboardGroup()[0],13),false);assert.equal(copy.setGroupTarget(0,"13"),false);assert.equal(copy._cardClipboard.mode,"group-copy");
});

test("mixed-type cut targets must accept the incoming card and controls retain the capturedv3 requirement",()=>{
  const editor=groupEditor();editor.profile.slots.find(slot=>slot.slot===13).types=["sensor"];editor.profile.slots.find(slot=>slot.slot===11).types=["entity"];editor.profile.slots.find(slot=>slot.slot===14).types=["sensor"];
  cutGroup(editor);editor.requestGroupPaste();assert.equal(editor.setGroupTarget(0,"13"),false);assert.equal(editor.setGroupTarget(0,"11"),true);assert.equal(editor.setGroupTarget(1,"14"),true);assert.equal(editor.confirmGroupPaste(),true);
  const version=groupEditor();cutGroup(version);reviewGroup(version);version._draft.version=2;const before=clone(version._draft);assert.equal(version.confirmGroupPaste(),false);assert.deepEqual(clone(version._draft),before);assert.equal(version._undo.length,0);
  const regular=groupEditor();regular._draft.version=2;regular.cardAt(2).action={kind:"default"};regular._saved=clone(regular._draft);regular.entry.layout=clone(regular._draft);cutGroup(regular);reviewGroup(regular);assert.equal(regular.confirmGroupPaste(),true);assert.equal(regular._draft.version,2);
});

test("the full UTF8 document bound rejects even one extra slot digit atomically and preserves the cut intent",()=>{
  const editor=groupEditor();editor.cardAt(2).title="Żółć i śnieg";editor.profile.max_document_bytes=new TextEncoder().encode(JSON.stringify(editor._draft)).length;
  cutGroup(editor);reviewGroup(editor);const before=clone(editor._draft),intent=editor._cardClipboard;
  assert.equal(editor.confirmGroupPaste(),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._cardClipboard,intent);assert.equal(editor._undo.length,0);assert.match(editor._error,/limit/);
});

test("explicit same-place mapping consumes cut successfully without changing clean/dirty history or retained redo",()=>{
  for(const dirty of [false,true]){const editor=groupEditor();
    if(dirty)editor.mutate(layout=>{layout.cards.find(card=>card.slot===3).title="Retained unrelated edit";});
    editor.mutate(layout=>{layout.cards.find(card=>card.slot===3).palette="surface";});editor.history("undo");
    const before=clone(editor._draft),undo=clone(editor._undo),redo=clone(editor._redo);cutGroup(editor);reviewGroup(editor,[2,13]);
    let mutations=0;editor.mutate=()=>{mutations++;throw Error("No-op must not mutate");};
    withUUIDs([new Error("No UUID for no-op")],calls=>{assert.equal(editor.confirmGroupPaste(),true);assert.equal(calls(),0);});
    assert.equal(mutations,0);assert.deepEqual(clone(editor._draft),before);assert.deepEqual(clone(editor._undo),undo);assert.deepEqual(clone(editor._redo),redo);assert.equal(editor.dirty,dirty);
    assert.equal(editor._cardClipboard,null);assert.equal(editor._pending,null);assert.match(editor._notice,/already in the selected places/);assert.equal(editor.clipboardMarkup(),"");assert.equal(editor.modalMarkup(),"");
  }
});

test("a refused mutation kernel does not consume the pending cut or its sources",()=>{
  const editor=groupEditor();cutGroup(editor);reviewGroup(editor);const intent=editor._cardClipboard,pending=editor._pending,before=clone(editor._draft);editor.mutate=()=>false;
  assert.equal(editor.confirmGroupPaste(),false);assert.equal(editor._cardClipboard,intent);assert.equal(editor._pending,pending);assert.deepEqual(clone(editor._draft),before);
});

test("cut captures saved/serverrevision version and epoch, and later changes require cutting again",()=>{
  for(const change of [editor=>editor._saved.revision++,editor=>editor.entry.layout.revision++,editor=>editor._selectionEpoch++,editor=>editor._draft.version=2]){
    const editor=groupEditor();cutGroup(editor);reviewGroup(editor);change(editor);const before=clone(editor._draft);assert.equal(editor.confirmGroupPaste(),false);assert.deepEqual(clone(editor._draft),before);assert.match(editor._error,/Cut the group again/);assert.equal(editor._undo.length,0);
  }
  const stale=groupEditor();selectGroup(stale);stale.entry.layout.revision++;assert.equal(stale.cutSelectedCards(),false);assert.equal(stale._cardClipboard,null);
});

test("group-cut shares context invalidation with other clipboard variants and cannot become an implicit group copy",()=>{
  const changes=[editor=>editor.selectEntry("screen-b"),editor=>{editor.hass={...editor._hass,user:{id:"another"}};},editor=>{editor.profile.width++;editor.paintValues();},editor=>{editor.hass={...editor._hass,connected:false};},editor=>editor.disconnectedCallback()];
  for(const change of changes){const editor=groupEditor();cutGroup(editor);reviewGroup(editor);change(editor);assert.equal(editor._cardClipboard,null);assert.equal(editor._pending,null);assert.equal(editor.confirmGroupPaste(),false);}
  const replaced=groupEditor();cutGroup(replaced);reviewGroup(replaced);replaced._cardClipboard={...replaced._cardClipboard,mode:"group-copy"};const before=clone(replaced._draft);assert.equal(replaced.confirmGroupPaste(),false);assert.deepEqual(clone(replaced._draft),before);
});

test("CtrlX in selection opens one group-cut intent, CtrlPaste reviews it, native fields keep Cut and Cancel retains sources",async()=>{
  const editor=groupEditor();selectGroup(editor);shortcut(editor,keyboardTarget(2),"x");assert.equal(editor._cardClipboard.mode,"group-cut");assert.equal(editor._selectingCards,false);
  const before=clone(editor._draft);for(const tag of ["INPUT","SELECT","TEXTAREA"])assert.equal(shortcut(editor,keyboardTarget(2,tag),"x").prevented,false);
  shortcut(editor,keyboardTarget(2),"v");assert.equal(editor._pending.kind,"group-paste");const intent=editor._cardClipboard;await clickAction(editor,"modal-cancel");assert.equal(editor._cardClipboard,intent);assert.equal(editor._pending,null);assert.deepEqual(clone(editor._draft),before);
  shortcut(editor,keyboardTarget(2),"Escape",{ctrlKey:false});assert.equal(editor._cardClipboard,null);
});

test("move labels and cancellation are distinct from copy in English and Polish",async()=>{
  const editor=groupEditor();selectGroup(editor);await clickAction(editor,"cut-selected");assert.match(editor.clipboardMarkup(),/data-clipboard-mode="group-cut"/);assert.match(editor.clipboardMarkup(),/Group to move/);assert.match(editor.clipboardMarkup(),/Cancel move/);
  editor.requestGroupPaste();assert.match(editor.modalMarkup(),/Move 2 selected cards/);assert.match(editor.modalMarkup(),/Move group/);assert.doesNotMatch(editor.modalMarkup(),/Paste 2 copied/);
  editor._hass.locale.language="pl";assert.match(editor.clipboardMarkup(),/Grupa do przeniesienia/);assert.match(editor.clipboardMarkup(),/Anuluj przenoszenie/);assert.match(editor.modalMarkup(),/Przenieś zaznaczone karty: 2/);
});

test("cut review validity/options/polls and a move never invoke UUID generation or a service request",async()=>{
  let requests=0;const editor=groupEditor(async()=>{requests++;throw Error("No group request");});cutGroup(editor);reviewGroup(editor);const before=clone(editor._draft);
  withUUIDs([new Error("No UUID anywhere in groupmove")],calls=>{editor.groupPasteReady();editor.groupTargetOptions(editor.clipboardGroup()[0],0);editor.modalMarkup();editor.paintToolbar();assert.equal(editor.confirmGroupPaste(),true);assert.equal(calls(),0);});
  assert.equal(requests,0);assert.equal(editor._draft.cards.length,before.cards.length);
});

test("unchanged HA state/status updates preserve a cut review and focused select",async()=>{
  const editor=groupEditor();cutGroup(editor);reviewGroup(editor);const dom=trackedEditorDOM(editor),banner=dom.region(editor.clipboardMarkup());dom.regions.set("#card-clipboard",banner);const modal=dom.regions.get("#modal-host"),select={tagName:"SELECT",region:modal};dom.root.activeElement=select;
  editor.hass={...editor._hass,states:{"light.room":{state:"off",attributes:{}}}};editor._hass.callWS=async()=>({entries:[clone(editor.entry)]});await editor.refreshStatus();editor.paintToolbar();
  assert.equal(banner.writes,0);assert.equal(modal.writes,0);assert.equal(dom.root.htmlWrites,0);assert.equal(dom.root.activeElement,select);assert.equal(editor.groupPasteReady(),true);
});

test("cut capture and move obey modal busy field conflict carry and drag guards",()=>{
  for(const [key,value] of [["_busy",true],["_pending",{kind:"switch"}],["_fieldErrors",{title:"invalid"}],["_conflict",true],["_carry",{}],["_drag",{}],["_profileStale",true]]){
    const start=groupEditor();selectGroup(start);start[key]=value;assert.equal(start.cutSelectedCards(),false,key);
    const move=groupEditor();cutGroup(move);reviewGroup(move);move[key]=value;const before=clone(move._draft);assert.equal(move.confirmGroupPaste(),false,key);assert.deepEqual(clone(move._draft),before);assert.equal(move._undo.length,0);
  }
});

test("cut intent and mapping never persist; moved slots use the existing explicit Save revision CAS",async()=>{
  const storage=new BrowserStorage(),requests=[];const editor=enableDraft(groupEditor(async request=>{requests.push(clone(request));return {layout:{...clone(request.layout),revision:5},status:{saved_revision:5}};}),storage);
  cutGroup(editor);reviewGroup(editor);flushDraft(editor);assert.equal(storage.length,0);assert.equal(editor.confirmGroupPaste(),true);assert.equal(flushDraft(editor),true);
  const record=JSON.parse(storage.getItem(editor.draftKey()));assert.doesNotMatch(JSON.stringify(record),/group-cut|group-paste|clipboard|targets/);assert.equal(record.layout.cards.length,4);assert.equal(requests.length,0);
  assert.equal(await editor.save(),true);assert.equal(requests.length,1);assert.equal(requests[0].type,"atmosfera_echo_hub/layout/save");assert.equal(requests[0].expected_revision,4);assert.equal(requests[0].layout.cards.length,4);
});

// Retain actual render/paint implementations; model only their two DOM regions
// and focusable preview cards, so stale rendered pages cannot pass as state-only.
function groupMovePageDOM(editor) {
  const root=emptyRoot(),tabs={innerHTML:""},preview={cards:[]};let previewHTML="",rootHTML="";
  Object.defineProperty(preview,"innerHTML",{get(){return previewHTML;},set(value){
    previewHTML=value;preview.cards=[...value.matchAll(/<div class="preview-card\b[^>]*data-slot="(\d+)"/g)].map(match=>({dataset:{slot:match[1]},focus(){root.activeElement=this;}}));
  }});
  Object.defineProperty(root,"innerHTML",{get(){return rootHTML;},set(value){
    rootHTML=value;root.activeElement=null;tabs.innerHTML=value.match(/id="page-tabs"[^>]*>([\s\S]*?)<\/nav>/)?.[1]||"";
    preview.innerHTML=value.match(/id="device-preview"[^>]*>([\s\S]*?)<p class="preview-caption">/)?.[1]||"";
  }});
  root.querySelector=selector=>selector==="#page-tabs"?tabs:selector==="#device-preview"?preview:
    preview.cards.find(card=>selector===`.preview-card[data-slot="${card.dataset.slot}"]`)||null;
  editor.shadowRoot=root;editor.render();return {root,tabs,preview};
}

test("changed group moves repaint the actual destination page/tab before focusing the mapped card",()=>{
  const editor=groupEditor();cutGroup(editor);reviewGroup(editor);editor._pageId="home-4";const dom=groupMovePageDOM(editor);
  assert.match(dom.preview.innerHTML,/aria-label="Controls"/);assert.equal(dom.preview.cards.some(card=>card.dataset.slot==="11"),false);
  assert.equal(editor.confirmGroupPaste(),true);
  assert.match(dom.tabs.innerHTML,/data-page="home-2" role="tab" aria-selected="true"/);assert.match(dom.preview.innerHTML,/aria-label="Security"/);
  assert.equal(dom.preview.cards.some(card=>card.dataset.slot==="11"),true);assert.equal(dom.preview.cards.some(card=>card.dataset.slot==="14"),false);
  assert.equal(dom.root.activeElement?.dataset.slot,"11");assert.equal(editor.cardAt(11).id,"first");
});

test("same-place group moves repaint the target page and focus without rendering a history transaction",()=>{
  const editor=groupEditor();cutGroup(editor);reviewGroup(editor,[2,13]);editor._pageId="home-4";const dom=groupMovePageDOM(editor),before=clone(editor._draft);
  editor.mutate=()=>{throw Error("No-op must not mutate or full-render through history");};
  assert.equal(editor.confirmGroupPaste(),true);
  assert.match(dom.tabs.innerHTML,/data-page="home-2" role="tab" aria-selected="true"/);assert.match(dom.preview.innerHTML,/aria-label="Security"/);
  assert.equal(dom.root.activeElement?.dataset.slot,"2");assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);assert.equal(editor.dirty,false);
});


function styleEditor(callWS) {
  const editor=multiEditor(callWS);
  editor._data.palettes=["primary","primary_container","secondary","surface","tertiary"];
  editor.cardAt(13).palette="surface";
  editor.cardAt(3).action={kind:"service",service:"light.turn_on",data:{brightness_pct:27,rgb_color:[2,3,4]}};
  editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);
  return editor;
}
function styleReview(editor,palette=null,slots=[2,13]) {
  selectGroup(editor,slots);assert.equal(editor.requestSelectedStyle(),true);
  if(palette!==null)assert.equal(editor.setSelectedStyle(palette),true);
}

test("selected style review starts unchanged and labels all five existing colors semantically in EN and PL",()=>{
  const names={en:["Accent","Accent container","Secondary","Neutral","Tertiary"],pl:["Akcent","Jasny akcent","Drugorzędny","Neutralny","Uzupełniający"]};
  for(const language of ["en","pl"]){const editor=styleEditor();editor._hass.locale.language=language;styleReview(editor);
    assert.equal(editor._pending.kind,"bulk-style");assert.equal(editor._pending.palette,null);assert.equal(editor.selectedStyleReady(),false);
    const markup=editor.modalMarkup(),options=[...markup.matchAll(/<option value="([^"]+)"[^>]*>([^<]+)<\/option>/g)];
    assert.deepEqual(options.map(match=>match[1]),editor._data.palettes);assert.deepEqual(options.map(match=>match[2]),names[language]);
    assert.match(markup,/data-action="modal-style-selected" disabled/);assert.match(markup,language==="en"?/Leave unchanged/:/Nie zmieniaj/);
    assert.match(markup,/Security|Bezpieczeństwo/);assert.match(markup,/Controls|Sterowanie/);
    assert.equal(editor._undo.length,0);assert.equal(editor.dirty,false);assert.equal(editor._selectedCardIds.size,2);
  }
});

test("a mixed visible and hidden group changes only palettes once and one Undo restores all typed cards and order",()=>{
  const editor=styleEditor(),before=clone(editor._draft);styleReview(editor,"tertiary");
  let mutations=0;const mutate=editor.mutate;editor.mutate=function(change){mutations++;return mutate.call(this,change);};
  withUUIDs([new Error("Style must not generate identities")],calls=>{assert.equal(editor.confirmSelectedStyle(),true);assert.equal(calls(),0);});
  const expected=clone(before);expected.cards.forEach(card=>{if(["first","third"].includes(card.id))card.palette="tertiary";});
  assert.deepEqual(clone(editor._draft),expected);assert.equal(editor.cardAt(13).visible,false);assert.equal(mutations,1);assert.equal(editor._undo.length,1);
  assert.equal(editor._pending,null);assert.equal(editor._selectingCards,true);assert.deepEqual([...editor._selectedCardIds],["first","third"]);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);assert.equal(editor._selectingCards,false);
  editor.history("redo");assert.deepEqual(clone(editor._draft),expected);
});

test("style apply uses the current draft and its one Undo retains unrelated edits made after review",()=>{
  const editor=styleEditor();styleReview(editor,"secondary");
  editor.mutate(layout=>{layout.cards.find(card=>card.id==="second").title="Unrelated title after review";});
  const beforeApply=clone(editor._draft);assert.equal(editor.selectedStyleCurrent(),true);assert.equal(editor.confirmSelectedStyle(),true);
  assert.equal(editor.cardAt(3).title,"Unrelated title after review");assert.equal(editor._undo.length,2);
  editor.history("undo");assert.deepEqual(clone(editor._draft),beforeApply);assert.equal(editor._undo.length,1);
});

test("every later selected-card field change or source identity ambiguity refuses the entire reviewed style",()=>{
  const changes=[
    editor=>{editor.cardAt(2).title="Changed title";},editor=>{editor.cardAt(2).palette="secondary";},
    editor=>{editor.cardAt(2).action={kind:"service",service:"light.turn_on",data:{brightness_pct:83}};},
    editor=>{editor.cardAt(2).slot=11;},editor=>{editor.cardAt(2).id="new-owner";},
    editor=>{editor.cardAt(2).entity_id="light.other";},editor=>{editor.cardAt(2).type="action";},
    editor=>{editor.cardAt(2).icon="switch";},editor=>{editor.cardAt(13).visible=true;},
    editor=>{editor._draft.cards=editor._draft.cards.filter(card=>card.id!=="first");},
    editor=>{editor._draft.cards.push({...clone(editor.cardAt(2)),slot:11});},
    editor=>{editor._draft.cards.push({...card("foreign",2),palette:"surface"});},
    editor=>{editor._selectedCardIds.delete("third");},editor=>{editor._selectedCardIds.add("second");}
  ];
  for(const change of changes){const editor=styleEditor();styleReview(editor,"secondary");change(editor);const current=clone(editor._draft);
    assert.equal(editor.confirmSelectedStyle(),false);assert.deepEqual(clone(editor._draft),current);assert.equal(editor._undo.length,0);
  }
});

test("style confirmation is fenced by complete context epoch revisions document version and admission",()=>{
  const changes=[editor=>{editor._hass.user={id:"different-user"};},editor=>{editor._entryId="screen-b";},
    editor=>{editor.profile.width++;},editor=>{editor._selectionEpoch++;},editor=>{editor._saved.revision++;},
    editor=>{editor.entry.layout.revision++;},editor=>{editor._draft.version=2;},editor=>{editor._conflict=true;},
    editor=>{editor._busy=true;},editor=>{editor._fieldErrors.title="Invalid";},editor=>{editor._drag={};},editor=>{editor._carry={};},
    editor=>{editor._hass.connected=false;},editor=>{editor._hass.connection={connected:false};}];
  for(const change of changes){const editor=styleEditor();styleReview(editor,"secondary");change(editor);const current=clone(editor._draft);
    assert.equal(editor.confirmSelectedStyle(),false);assert.deepEqual(clone(editor._draft),current);assert.equal(editor._undo.length,0);
  }
});

test("palette choices remain exactly the existing known tokens and late catalogue changes invalidate review",()=>{
  for(const value of ["#36BCF0","rgb(1,2,3)","unknown","__proto__",false,17,{},null]){
    const editor=styleEditor();styleReview(editor);assert.equal(editor.setSelectedStyle(value),false);assert.equal(editor.selectedStyleReady(),false);assert.equal(editor._pending.palette,null);assert.equal(editor._undo.length,0);
  }
  const editor=styleEditor();editor._data.palettes.push("__proto__","#123456","primary");styleReview(editor,"primary_container");
  assert.deepEqual(clone(editor._pending.palettes),["primary","primary_container","secondary","surface","tertiary"]);
  editor._data.palettes=editor._data.palettes.filter(value=>value!=="secondary");const before=clone(editor._draft);
  assert.equal(editor.confirmSelectedStyle(),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
});

test("unchanged choice is not confirmable and clearing a real choice restores disabled confirmation",()=>{
  const editor=styleEditor();styleReview(editor);const before=clone(editor._draft);
  assert.equal(editor.confirmSelectedStyle(),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
  assert.equal(editor.setSelectedStyle("primary"),true);assert.equal(editor.selectedStyleReady(),true);
  assert.equal(editor.setSelectedStyle(""),true);assert.equal(editor.selectedStyleReady(),false);assert.equal(editor.confirmSelectedStyle(),false);
  assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
});

test("same-value style success preserves clean or dirty state and an existing redo branch without calling mutate",()=>{
  for(const mode of ["clean","redo","dirty-redo"]){const editor=styleEditor();editor.cardAt(13).palette="primary";editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);
    if(mode!=="clean"){editor.mutate(layout=>{layout.cards.find(card=>card.id==="second").title="Keep A";});if(mode==="dirty-redo")editor.mutate(layout=>{layout.cards.find(card=>card.id==="second").title="Keep B";});editor.history("undo");}
    const before=clone(editor._draft),undo=clone(editor._undo),redo=clone(editor._redo),dirty=editor.dirty,reference=editor._draft;
    styleReview(editor,"primary");editor.mutate=()=>{throw Error("Same value must not mutate");};
    assert.equal(editor.confirmSelectedStyle(),true);assert.equal(editor._draft,reference);assert.deepEqual(clone(editor._draft),before);
    assert.deepEqual(clone(editor._undo),undo);assert.deepEqual(clone(editor._redo),redo);assert.equal(editor.dirty,dirty);assert.equal(editor._pending,null);
    assert.equal(editor._selectingCards,true);assert.equal(editor._selectedCardIds.size,2);assert.match(editor._notice,/already use/);
  }
});

test("repeat all-same palette is no new history and one Undo still reverses the actual prior group change",()=>{
  const editor=styleEditor(),before=clone(editor._draft);styleReview(editor,"primary");assert.equal(editor.confirmSelectedStyle(),true);assert.match(editor._notice,/changed: 1\./);
  assert.equal(editor._undo.length,1);assert.equal(editor.requestSelectedStyle(),true);assert.equal(editor.setSelectedStyle("primary"),true);assert.equal(editor.confirmSelectedStyle(),true);
  assert.equal(editor._undo.length,1);editor.history("undo");assert.deepEqual(clone(editor._draft),before);
});

test("full current UTF8 candidate is bounded before applying longer palette names with no partial update",()=>{
  const editor=styleEditor();editor.cardAt(2).title="Żółć".repeat(8);editor.cardAt(13).title="Śnieg".repeat(6);editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);
  const before=clone(editor._draft),candidate=clone(before);candidate.cards.forEach(card=>{if(["first","third"].includes(card.id))card.palette="primary_container";});
  const oldBytes=new TextEncoder().encode(JSON.stringify(before)).length,newBytes=new TextEncoder().encode(JSON.stringify(candidate)).length;
  editor.profile.max_document_bytes=oldBytes+1;assert.ok(JSON.stringify(candidate).length<editor.profile.max_document_bytes);assert.ok(newBytes>editor.profile.max_document_bytes);
  styleReview(editor,"primary_container");assert.equal(editor.confirmSelectedStyle(),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);assert.match(editor._error,/limit/);
  assert.equal(editor.setSelectedStyle("surface"),true);assert.equal(editor.confirmSelectedStyle(),true);assert.equal(editor._undo.length,1);
});

test("all14 selected cards can receive one existing palette without card allocation or identity work",()=>{
  const editor=styleEditor();editor.profile.slots=Array.from({length:14},(_,index)=>({slot:index+2,page_id:index<7?"home-2":"home-4",editable:true,hidden:false,types:["entity"],x:0,y:0,width:20,height:20}));
  editor._draft.cards=Array.from({length:14},(_,index)=>({...card(`bounded-style-${index}`,index+2),visible:index%2===0,palette:index%2?"surface":"primary"}));editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);
  const before=clone(editor._draft);styleReview(editor,"secondary",Array.from({length:14},(_,index)=>index+2));
  withUUIDs([new Error("No UUID")],calls=>{assert.equal(editor.confirmSelectedStyle(),true);assert.equal(calls(),0);});
  assert.equal(editor._draft.cards.length,14);assert.deepEqual(clone(editor._draft.cards).map(({palette,...rest})=>rest),before.cards.map(({palette,...rest})=>rest));assert.ok(editor._draft.cards.every(card=>card.palette==="secondary"));assert.equal(editor._undo.length,1);
});

test("Cancel keeps selection and restores its style action focus; Escape removes the review and selection",async()=>{
  const editor=styleEditor();styleReview(editor,"secondary");const before=clone(editor._draft),focused=[];
  editor.shadowRoot.querySelector=selector=>selector.startsWith('[data-action=')?{focus(){focused.push(selector);}}:null;
  await clickAction(editor,"modal-cancel");assert.equal(editor._pending,null);assert.equal(editor._selectingCards,true);assert.equal(editor._selectedCardIds.size,2);assert.equal(focused.at(-1),'[data-action="style-selected"]');
  assert.equal(editor.requestSelectedStyle(),true);shortcut(editor,keyboardTarget(2),"Escape",{ctrlKey:false});
  assert.equal(editor._pending,null);assert.equal(editor._selectingCards,false);assert.equal(editor._selectedCardIds.size,0);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
});

test("native style SELECT is change-routed, initially focused and participates in Tab wrapping without stealing copy keys",async()=>{
  const editor=styleEditor();styleReview(editor);const focused=[];
  const controls=[{tagName:"SELECT",dataset:{selectedStyle:""},value:"secondary",disabled:false},{tagName:"BUTTON",dataset:{action:"modal-cancel"},disabled:false},{tagName:"BUTTON",dataset:{action:"modal-style-selected"},disabled:false}];
  controls.forEach((control,index)=>{control.focus=()=>focused.push(index);control.closest=()=>null;});
  editor.shadowRoot.querySelector=selector=>selector===".modal select:not([disabled])"||selector==="[data-selected-style]"?controls[0]:null;
  editor.shadowRoot.querySelectorAll=selector=>selector==='.modal select:not([disabled]),.modal button:not([disabled])'?controls:selector==='.modal button'?controls.slice(1):selector==='[data-selected-style]'?[controls[0]]:[];
  editor.paintModalFocus();assert.equal(focused.at(-1),0);await editor.onChange({target:controls[0]});assert.equal(editor._pending.palette,"secondary");assert.equal(focused.at(-1),0);
  assert.equal(shortcut(editor,controls[2],"Tab",{ctrlKey:false}).prevented,true);assert.equal(focused.at(-1),0);
  assert.equal(shortcut(editor,controls[0],"Tab",{ctrlKey:false,shiftKey:true}).prevented,true);assert.equal(focused.at(-1),2);
  assert.equal(shortcut(editor,controls[0],"c").prevented,false);assert.equal(shortcut(editor,controls[0],"x").prevented,false);assert.equal(editor._undo.length,0);
});

test("style context resets clear the owned modal and Delete's own-review flag cannot admit it",()=>{
  for(const change of [editor=>editor.endCardSelection(),editor=>{editor.profile.width++;editor.paintValues();},editor=>{editor._hass.connected=false;editor.paintValues();},editor=>editor.disconnectedCallback()]){
    const editor=styleEditor();styleReview(editor,"secondary");change(editor);assert.equal(editor._pending,null);assert.equal(editor.modalMarkup(),"");assert.equal(editor.confirmSelectedStyle(),false);assert.equal(editor._undo.length,0);
  }
  const editor=styleEditor();styleReview(editor,"secondary");assert.equal(editor.cardSelectionAllowed(true),false);assert.equal(editor.cardSelectionAllowed(false,true),true);
});

test("ordinary HA updates and unchanged status polls keep the selected-style modal and its focused SELECT intact",async()=>{
  const editor=styleEditor();styleReview(editor,"secondary");const dom=trackedEditorDOM(editor),modal=dom.regions.get("#modal-host");
  modal.innerHTML=editor.modalMarkup();modal.writes=0;dom.regions.set("#card-selection",dom.region(editor.cardSelectionMarkup()));
  const select={tagName:"SELECT",region:modal};dom.root.activeElement=select;const before=clone(editor._draft);
  editor.hass={...editor._hass,states:{"light.room":{state:"off",attributes:{}}}};editor._hass.callWS=async()=>({entries:[clone(editor.entry)]});await editor.refreshStatus();editor.paintToolbar();
  assert.equal(modal.writes,0);assert.equal(dom.root.htmlWrites,0);assert.equal(dom.root.activeElement,select);assert.equal(editor._pending.palette,"secondary");assert.deepEqual(clone(editor._draft),before);
});

test("style operations dispatch no services or WS, allocate no IDs, and schedule only the existing changed-draft transaction",()=>{
  let calls=0,schedules=0;const editor=styleEditor(async()=>{calls++;throw Error("No request");});editor.scheduleDraft=()=>{schedules++;};
  withUUIDs([new Error("No ID")],ids=>{styleReview(editor,"secondary");editor.modalMarkup();editor.paintToolbar();assert.equal(calls,0);assert.equal(schedules,0);assert.equal(ids(),0);
    assert.equal(editor.confirmSelectedStyle(),true);assert.equal(schedules,1);assert.equal(editor.requestSelectedStyle(),true);assert.equal(editor.setSelectedStyle("secondary"),true);assert.equal(editor.confirmSelectedStyle(),true);assert.equal(schedules,1);assert.equal(ids(),0);});
  assert.equal(calls,0);assert.equal(editor._undo.length,1);
});

test("style review is unavailable without selected cards or supported colors and ordinary v2 documents stay v2",()=>{
  const empty=styleEditor();assert.equal(empty.requestSelectedStyle(),false);empty.startCardSelection();assert.equal(empty.requestSelectedStyle(),false);
  for(const palettes of [undefined,[],["#ffffff","unknown"]]){const editor=styleEditor();editor._data.palettes=palettes;selectGroup(editor);assert.equal(editor.requestSelectedStyle(),false);assert.match(editor.cardSelectionMarkup(),/data-action="style-selected" disabled/);}
  const editor=styleEditor();editor._draft.version=2;editor.cardAt(2).action={kind:"default"};editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);
  styleReview(editor,"secondary");assert.equal(editor.confirmSelectedStyle(),true);assert.equal(editor._draft.version,2);
});

test("style review and selected IDs are not persisted while accepted style uses only existing palette fields",()=>{
  const storage=new BrowserStorage(),editor=enableDraft(styleEditor(),storage);styleReview(editor,"secondary");flushDraft(editor);assert.equal(storage.length,0);
  assert.equal(editor.confirmSelectedStyle(),true);flushDraft(editor);const record=JSON.parse(storage.getItem(editor.draftKey()));
  assert.deepEqual(Object.keys(record.layout).sort(),["cards","profile","version"]);assert.doesNotMatch(JSON.stringify(record),/bulk-style|selectedStyle|palettes|_selectedCardIds/);
  assert.equal(record.layout.cards.find(card=>card.id==="first").palette,"secondary");
});


test("both changed and same-value style restore the action focus and an invalid review focuses Cancel rather than a disabled SELECT",()=>{
  for(const same of [false,true]){const editor=styleEditor();if(same){editor.cardAt(13).palette="primary";editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);}
    styleReview(editor,"primary");let focus=0;editor.shadowRoot.querySelector=selector=>selector==='[data-action="style-selected"]'?{focus(){focus++;}}:null;
    assert.equal(editor.confirmSelectedStyle(),true);assert.equal(focus,1);assert.equal(editor._pending,null);assert.equal(editor._selectingCards,true);
  }
  const editor=styleEditor();styleReview(editor,"secondary");editor.cardAt(2).title="Late selected change";const focused=[];
  editor.shadowRoot.querySelector=selector=>selector==='.modal select:not([disabled])'?null:selector==='.modal button'?{focus(){focused.push("cancel");}}:null;
  assert.equal(editor.selectedStyleCurrent(),false);editor.paintModalFocus();assert.deepEqual(focused,["cancel"]);assert.equal(editor._undo.length,0);
});


test("palette fallback and provided colors match the actual native C++ role oracle",()=>{
  const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,"fixtures/native_tile_palette.json"),"utf8"));
  const editor=makeEditor();
  for(const row of fixture.cases){
    editor.entry.accent_color=row.seed;delete editor.entry.colors;
    for(const [role,pair] of Object.entries(row.roles))assert.deepEqual(clone(editor.paletteColors(role)),{background:editor.hex(pair[0]),foreground:editor.hex(pair[1])});
    editor.entry.colors=Object.fromEntries(Object.entries(row.roles).map(([name,pair])=>[name,{background:pair[0],foreground:pair[1]}]));
    for(const [role,pair] of Object.entries(row.roles))assert.deepEqual(clone(editor.paletteColors(role)),{background:editor.hex(pair[0]),foreground:editor.hex(pair[1])});
  }
  editor.entry.accent_color="AEE2FF";editor.entry.colors={primary:{background:true,foreground:-1}};
  assert.deepEqual(clone(editor.paletteColors("primary")),{background:"#aee2ff",foreground:"#071018"});
  for(const name of ["unknown","__proto__","constructor"])assert.deepEqual(clone(editor.paletteColors(name)),{background:"#222d33",foreground:"#ffffff"});
});

test("appearance-only status refresh changes CSS without replacing focused DOM or draft history",async()=>{
  const editor=makeEditor();editor._draft.cards[1].title="My unsaved title";editor._undo=[{before:"kept"}];editor._redo=[{after:"kept"}];
  const before=clone({draft:editor._draft,saved:editor._saved,undo:editor._undo,redo:editor._redo});
  const styles={},tile={dataset:{slot:"2"},style:{setProperty:(name,value)=>{styles[name]=value;}}};
  const swatch={dataset:{palette:"secondary"},style:{}},focus={value:"unfinished text"};
  editor.shadowRoot.activeElement=focus;
  editor.shadowRoot.querySelectorAll=selector=>selector===".preview-card[data-slot]" ? [tile] : selector===".palette-swatches [data-palette]" ? [swatch] : [];
  editor.paintPreview=()=>assert.fail("Appearance must not replace preview DOM");editor.render=()=>assert.fail("Same-revision appearance must not render the document");
  const latest=clone(editor.entry);latest.accent_color="AEE2FF";latest.colors={primary:{background:0xAEE2FF,foreground:0x071018},secondary:{background:0xCAF6FF,foreground:0x071018}};
  const calls=[];editor._hass.callWS=async message=>{calls.push(message);return {entries:[clone(latest)]};};
  await editor.refreshStatus();
  assert.deepEqual(styles,{"--tile-bg":"#aee2ff","--tile-fg":"#071018"});assert.equal(swatch.style.background,"#caf6ff");
  assert.equal(editor.shadowRoot.activeElement,focus);assert.equal(focus.value,"unfinished text");
  assert.deepEqual(clone({draft:editor._draft,saved:editor._saved,undo:editor._undo,redo:editor._redo}),before);
  assert.equal(calls.length,1);assert.equal(calls[0].type,"atmosfera_echo_hub/layout/get");assert.equal(editor.dirty,true);
});


test("Sun assignment uses passive information and existing clock without changing other cards",()=>{
  const editor=makeEditor();editor._data.icons.push("clock");editor.profile.sun_text_slots=[2,3,11];
  editor._entityIndex.set("sun.sun",{entity_id:"sun.sun",name:"Sun",domain:"sun",state:"above_horizon",available:true,actions:[]});
  const before=clone(editor._draft.cards);
  assert.equal(editor.assignEntity("sun.sun",11),true);
  const assigned=clone(editor.cardAt(11));
  assert.equal(assigned.type,"sensor");assert.equal(assigned.icon,"clock");assert.equal(assigned.palette,"surface");
  assert.deepEqual(assigned.action,{kind:"none"});assert.equal(assigned.entity_id,"sun.sun");
  assert.deepEqual(clone(editor._draft.cards.filter(card=>card.slot!==11)),before);
  editor.history("undo");assert.equal(editor.cardAt(11),undefined);
  editor.history("redo");assert.equal(editor.cardAt(11).id,assigned.id);assert.deepEqual(clone(editor.cardAt(11).action),{kind:"none"});
});


function sunEditor(callWS) {
  const editor=makeEditor(callWS);editor._data.icons.push("clock");
  editor.profile.sun_text_slots=[2,3,4,5,6,7,8,9,10,11,12,15];
  for(const slot of [...editor.profile.sun_text_slots,14]) if(!editor.slotAt(slot)) editor.profile.slots.push({...clone(editor.slotAt(11)),slot,page_id:slot>=13 ? "home-4" : "home-2"});
  editor._entityIndex.set("sun.sun",{entity_id:"sun.sun",name:"Sun",domain:"sun",state:"above_horizon",available:true,actions:[]});
  return editor;
}

test("Sun placement and real pointer-drop path refuse both large value places and reciprocal swaps",()=>{
  for(const slot of [13,14]) {
    const editor=sunEditor(),before=clone(editor._draft);
    assert.equal(editor.assignEntity("sun.sun",slot),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
    assert.equal(editor._error,editor.t("sunPlacement"));
    assert.equal(editor.assignEntity("sun.sun",11),true);
    const placed=clone(editor._draft);
    assert.equal(editor.moveCard(11,slot),false);assert.deepEqual(clone(editor._draft),placed);
    editor._draft.cards.push(card("large",slot,"sensor.temperature"));
    assert.equal(editor.moveCard(slot,11),false);assert.equal(editor.cardAt(11).entity_id,"sun.sun");
    editor._drag={pointer:1,active:true,target:slot,kind:"card",from:11};editor.cancelMove=()=>{editor._drag=null;};
    const dragBefore=clone(editor._draft);editor.onPointerUp({pointerId:1});assert.deepEqual(clone(editor._draft),dragBefore);
    assert.equal(editor.moveCard(11,2),true);assert.equal(editor.cardAt(2).entity_id,"sun.sun");
  }
});

test("Sun clipboard copy and cut keep unsupported destinations disabled, including group mapping",()=>{
  for(const moving of [false,true]) {
    const editor=sunEditor();assert.equal(editor.assignEntity("sun.sun",11),true);
    assert.equal(moving ? editor.cutCard(11) : editor.copyCard(11),true);
    for(const slot of [13,14]) {assert.equal(!!editor.canPasteCard(slot),false);assert.equal(editor.pasteCard(slot),false);assert.equal(editor.cardAt(slot),undefined);}
    assert.equal(editor.pasteCard(15),true);assert.equal(editor.cardAt(15).entity_id,"sun.sun");
    const group=sunEditor();assert.equal(group.assignEntity("sun.sun",11),true);selectGroup(group,[11]);
    assert.equal(moving ? group.cutSelectedCards() : group.copySelectedCards(),true);assert.equal(group.requestGroupPaste(),true);
    for(const slot of [13,14]) assert.equal(group.setGroupTarget(0,String(slot)),false);
    assert.equal(group.setGroupTarget(0,"15"),true);assert.equal(group.confirmGroupPaste(),true);assert.equal(group.cardAt(15).entity_id,"sun.sun");
  }
});

test("Sun invalid import, restored draft and save are refused without a request or draft mutation",async()=>{
  let calls=0;const editor=sunEditor(async()=>{calls++;assert.fail("Invalid Sun must not send");});
  const sun=editor.newCard({entity_id:"sun.sun",name:"Sun"},13),backup={format:"atmosfera-layout",version:1,layout:{version:2,profile:editor.profile.id,cards:[sun]}};
  const before=clone(editor._draft);await assert.rejects(editor.importText(JSON.stringify(backup)),new RegExp(editor.t("sunPlacement")));
  assert.deepEqual(clone(editor._draft),before);
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:Date.now(),layout:clone(backup.layout)};
  assert.throws(()=>editor.validateStoredDraft(record),new RegExp(editor.t("sunPlacement")));
  editor._draft.cards.push(sun);const invalid=clone(editor._draft);
  assert.equal(await editor.save(),false);assert.deepEqual(clone(editor._draft),invalid);assert.equal(calls,0);assert.equal(editor._error,editor.t("sunPlacement"));
});

test("Sun import confirmation rechecks current capabilities and normal placement can save",async()=>{
  const calls=[];let editor;editor=sunEditor(async message=>{calls.push(message);return {layout:{...clone(message.backup?.layout || message.layout),revision:5},warnings:[],status:{}};});
  const sun=editor.newCard({entity_id:"sun.sun",name:"Sun"},15),backup={format:"atmosfera-layout",version:1,layout:{version:2,profile:editor.profile.id,cards:[sun]}};
  assert.equal(await editor.importText(JSON.stringify(backup)),true);const before=clone(editor._draft);
  editor.profile.sun_text_slots=[];editor.useImported();assert.deepEqual(clone(editor._draft),before);assert.equal(editor._pending.kind,"import");
  editor.profile.sun_text_slots=[2,3,11,15];editor.useImported();assert.equal(editor.cardAt(15).entity_id,"sun.sun");
  assert.equal(await editor.save(),true);assert.equal(calls.length,2);assert.equal(calls[0].type,"atmosfera_echo_hub/layout/import");assert.equal(calls[0].dry_run,true);assert.equal(calls[1].type,"atmosfera_echo_hub/layout/save");assert.equal(calls[1].layout.version,2);
});

test("Sun text capability, read-only inspector and missing-capability errors remain honest in both languages",()=>{
  for(const language of ["en","pl"]) {
    const editor=sunEditor();editor._hass.locale.language=language;assert.equal(editor.assignEntity("sun.sun",11),true);
    assert.match(editor.capabilitiesMarkup(),/data-sun-capability/);assert.match(editor.inspectorMarkup(),/data-sun-placement/);
    const typeSelect=editor.inspectorMarkup().match(/<select data-field="type">([\s\S]*?)<\/select>/)[1];
    assert.match(typeSelect,/value="sensor"/);assert.doesNotMatch(typeSelect,/value="entity"|value="action"/);
    assert.equal(editor.acceptsCard(editor.slotAt(13),editor.cardAt(11)),false);
    delete editor.profile.sun_text_slots;const before=clone(editor._draft);assert.equal(editor.moveCard(11,2),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._error,editor.t("sunPlacement"));
  }
});

function catalogueEntity(state="unknown") {
  return {entity_id:"light.room",name:"Room",domain:"light",state,available:state!=="unknown" && state!=="unavailable",actions:[]};
}
function trackCatalogue(editor,entity,live) {
  editor._catalogue=[entity];editor._entityIndex.set(entity.entity_id,entity);
  editor._hass.states={[entity.entity_id]:live};editor._entityStateRefs.set(entity,live);
}

test("library state uses live HA data while cached capability metadata is still unknown",()=>{
  const editor=makeEditor(),entity=catalogueEntity();editor._catalogue=[entity];
  assert.match(editor.libraryMarkup(),/data-live-entity-state="light.room" class="entity-state">on<\/span>/);
  assert.equal(entity.state,"unknown");assert.equal(entity.available,false);
  editor._hass.states["light.room"]={state:"<script>bad</script>",attributes:{}};
  assert.match(editor.libraryMarkup(),/&lt;script&gt;bad&lt;\/script&gt;/);
  assert.doesNotMatch(editor.libraryMarkup(),/<script>bad/);
});

test("live library updates retain row, focus, draft and history without network calls",()=>{
  let calls=0;const editor=makeEditor(async()=>{calls++;});
  const unavailable=new Set(["unavailable"]),label={dataset:{liveEntityState:"light.room"},textContent:"unknown",
    classList:{toggle(name,value){if(value)unavailable.add(name);else unavailable.delete(name);}}};
  const focused={value:"Unfinished title"},root=emptyRoot();
  root.activeElement=focused;root.querySelectorAll=selector=>selector==="[data-live-entity-state]"?[label]:[];
  Object.defineProperty(root,"innerHTML",{set(){throw Error("Live state must not replace rows");}});editor.shadowRoot=root;
  const before=clone(editor._draft);editor.paintValues();
  assert.equal(label.textContent,"on");assert.equal(unavailable.has("unavailable"),false);
  assert.equal(root.activeElement,focused);assert.deepEqual(clone(editor._draft),before);
  assert.equal(editor._undo.length,0);assert.equal(calls,0);
  editor._hass.states["light.room"]={state:"unavailable",attributes:{}};editor.paintValues();
  assert.equal(label.textContent,"unavailable");assert.equal(unavailable.has("unavailable"),true);
});

test("unknown, unavailable and removed library entities never retain a cached on state",()=>{
  const editor=makeEditor(),entity=catalogueEntity("on");
  for(const state of ["unknown","unavailable"]){
    editor._hass.states["light.room"]={state,attributes:{}};
    assert.equal(editor.libraryState(entity).state,state);assert.equal(editor.libraryState(entity).available,false);
  }
  delete editor._hass.states["light.room"];assert.equal(editor.libraryState(entity).state,"unavailable");
  delete editor._hass.states;assert.equal(editor.libraryState(entity).state,"on");
});

test("capability responses retain their request state epoch when HA changes during a fetch",async()=>{
  let reply;const editor=makeEditor(()=>new Promise(resolve=>{reply=resolve;}));
  const previous=editor._hass.states["light.room"];
  const pending=context.TestEditor.prototype.fetchCatalogue.call(editor);
  editor._hass.states={"light.room":{state:"on",attributes:{supported_features:8}}};
  reply({entities:[catalogueEntity("on")],total:1,truncated:false});await pending;
  const cached=editor.entityFor("light.room");assert.equal(editor._entityStateRefs.get(cached),previous);
  assert.equal(editor.entityMetadataStale(cached),true);assert.equal(editor._cataloguePending,null);
});

test("existing status cadence refreshes changed metadata once and ignores unrelated HA updates",async()=>{
  let reply,completed,calls=0;const editor=makeEditor(()=>{calls++;return new Promise(resolve=>{reply=resolve;});});
  const entity=catalogueEntity("on"),live=editor._hass.states["light.room"];
  trackCatalogue(editor,entity,live);editor.fetchCatalogue=()=>{completed=context.TestEditor.prototype.fetchCatalogue.call(editor);return completed;};
  editor._hass.states={...editor._hass.states,"sensor.unrelated":{state:"7",attributes:{}}};
  editor.refreshEntityMetadata();assert.equal(calls,0);
  editor._hass.states={...editor._hass.states,"light.room":{state:"on",attributes:{supported_features:8}}};
  editor.refreshEntityMetadata();editor.refreshEntityMetadata();assert.equal(calls,1);
  const fresh={...catalogueEntity("on"),actions:[{service:"light.turn_on",fields:{brightness_pct:{type:"number"}}}]};
  reply({entities:[fresh],total:1,truncated:false});await completed;
  assert.equal(editor.entityFor("light.room").actions[0].service,"light.turn_on");
  assert.equal(editor.entityMetadataStale(editor.entityFor("light.room")),false);
  assert.equal(editor._undo.length,0);assert.equal(editor.dirty,false);
});

test("metadata refresh defers during drag, review or save without adding another poller",()=>{
  const editor=makeEditor(),entity=catalogueEntity("on"),old=editor._hass.states["light.room"];
  trackCatalogue(editor,entity,old);editor._hass.states["light.room"]={state:"off",attributes:{}};
  let requests=0;editor.fetchCatalogue=async()=>{requests++;};
  for(const field of ["_drag","_carry","_pending","_busy"]){editor[field]={};editor.refreshEntityMetadata();editor[field]=null;}
  editor.shadowRoot.querySelector=selector=>selector===".entity-list"?{contains:()=>true}:null;
  editor.refreshEntityMetadata();assert.equal(requests,0);
  editor.shadowRoot.querySelector=()=>null;
  assert.equal(requests,0);editor.refreshEntityMetadata();assert.equal(requests,1);
});

test("selected entity outside the current search refreshes once and discards a removed capability",async()=>{
  let reply,calls=0;const editor=makeEditor(()=>{calls++;return new Promise(resolve=>{reply=resolve;});});
  const entity=catalogueEntity("on"),old=editor._hass.states["light.room"];
  editor._entityIndex.set(entity.entity_id,entity);editor._entityStateRefs.set(entity,old);editor._selectedSlot=2;
  editor._hass.states["light.room"]={state:"unavailable",attributes:{}};
  const first=editor.fetchSelectedEntity(),second=editor.fetchSelectedEntity();assert.equal(calls,1);
  reply({entities:[]});await first;await second;
  assert.equal(editor.entityFor("light.room"),undefined);assert.equal(editor._selectedEntityPending,null);
  assert.equal(editor.cardAt(2).entity_id,"light.room");assert.equal(editor.dirty,false);
});

test("a metadata response for a previous screen cannot populate the new screen",async()=>{
  let reply;const editor=makeEditor(()=>new Promise(resolve=>{reply=resolve;}));
  const entity=catalogueEntity("on"),old=editor._hass.states["light.room"];
  trackCatalogue(editor,entity,old);editor._selectedSlot=2;
  editor._hass.states["light.room"]={state:"off",attributes:{}};
  const pending=editor.fetchSelectedEntity();editor.selectEntry("screen-b");
  reply({entities:[{...catalogueEntity("off"),name:"Previous screen data"}]});await pending;
  assert.equal(editor._entityIndex.has("light.room"),false);assert.equal(editor._selectedEntityPending,null);
});

test("timer preset field has localized seconds, optional whole-second bounds and no implied resume reset",()=>{
  const editor=makeEditor();const descriptor={type:"number",min:1,max:86400,step:1,required:false};
  const field=editor.fieldMarkup("duration",descriptor,90);
  assert.match(field,/Duration \(seconds\)/);assert.match(field,/min="1"/);assert.match(field,/max="86400"/);assert.match(field,/step="1"/);assert.match(field,/value="90"/);
  for(const value of ["1","90","86400"])assert.equal(editor.parseFieldValue({value,dataset:{field:"data:duration"}},descriptor),Number(value));
  assert.equal(editor.parseFieldValue({value:"",dataset:{field:"data:duration"}},descriptor),undefined);
  for(const value of ["0","86401","1.5","1.0000001"])assert.throws(()=>editor.parseFieldValue({value,dataset:{field:"data:duration"}},descriptor));
  editor._hass={language:"pl"};assert.match(editor.fieldMarkup("duration",descriptor,90),/Czas \(sekundy\)/);
});

test("timer preset guidance appears only for an explicit start action and does not mutate a draft",()=>{
  const editor=makeEditor();editor._selectedSlot=2;
  Object.assign(editor.cardAt(2),{entity_id:"timer.example",action:{kind:"service",service:"timer.start",data:{duration:90}}});
  editor._entityIndex.set("timer.example",{entity_id:"timer.example",actions:[{service:"timer.start",fields:{duration:{type:"number",min:1,max:86400,step:1,required:false}}}]});
  const before=clone(editor._draft);const markup=editor.inspectorMarkup();assert.match(markup,/data-timer-duration/);assert.match(markup,/remaining time when resuming/);assert.deepEqual(clone(editor._draft),before);
  editor.cardAt(2).action={kind:"default"};assert.doesNotMatch(editor.inspectorMarkup(),/data-timer-duration/);
  editor.cardAt(2).action={kind:"service",service:"timer.cancel",data:{}};assert.doesNotMatch(editor.inspectorMarkup(),/data-timer-duration/);
});

test("state color is opt-in, uses exact live on and retains the user's configured palette",()=>{
  const editor=makeEditor(),card=editor.cardAt(2);card.palette="secondary";
  for(const state of ["on","off","unknown","unavailable"]){editor._hass={states:{"light.room":{state}}};assert.equal(editor.effectivePalette(card),"secondary");}
  card.state_color=true;
  for(const state of ["on","off","unknown","unavailable","ON"]){editor._hass={states:{"light.room":{state}}};assert.equal(editor.effectivePalette(card),state==="on"?"secondary":"surface");}
  editor._hass={states:{}};assert.equal(editor.effectivePalette(card),"surface");assert.equal(card.palette,"secondary");
  assert.equal(editor.stateColorEligible({...card,entity_id:"cover.example"}),false);assert.equal(editor.stateColorEligible({...card,type:"sensor"}),false);
});

test("live state colors patch only existing CSS and preserve focus, draft and history",()=>{
  const editor=makeEditor();editor.cardAt(2).state_color=true;const before=clone(editor._draft),focus={};
  const css={},writes=[];const node={dataset:{slot:"2"},style:{getPropertyValue:key=>css[key]||"",setProperty(key,value){css[key]=value;writes.push([key,value]);}}};
  editor.shadowRoot.activeElement=focus;editor.shadowRoot.querySelectorAll=selector=>selector===".preview-card[data-slot]"?[node]:[];
  editor._hass={states:{"light.room":{state:"off"}}};editor.paintValues();const off=css["--tile-bg"];
  const count=writes.length;editor.paintValues();assert.equal(writes.length,count);
  editor._hass={states:{"light.room":{state:"on"}}};editor.paintValues();assert.notEqual(css["--tile-bg"],off);
  assert.equal(editor.shadowRoot.activeElement,focus);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
});

test("state color survives draft recovery and copies but rejects unsupported semantics",()=>{
  const editor=makeEditor();editor.cardAt(2).state_color=true;
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:2,profile:editor.profile.id,cards:clone(editor._draft.cards)}};
  assert.doesNotThrow(()=>editor.validateStoredDraft(clone(record)));
  for(const mutate of [r=>{r.layout.cards[1].state_color="true";},r=>{r.layout.cards[1].entity_id="timer.example";},r=>{r.layout.cards[1].type="action";}]){const bad=clone(record);mutate(bad);assert.throws(()=>editor.validateStoredDraft(bad));}
  assert.equal(editor.copyCard(2),true);assert.equal(editor.pasteCard(13),true);assert.equal(editor.cardAt(13).state_color,true);
  editor.history("undo");assert.equal(editor.cardAt(13),undefined);assert.equal(editor.cardAt(2).state_color,true);
});

test("state color editor is localized and absent for unsupported cards",()=>{
  const editor=makeEditor();editor._selectedSlot=2;editor._hass={language:"pl"};
  assert.match(editor.inspectorMarkup(),/Wyróżniaj stan aktywny/);assert.match(editor.inspectorMarkup(),/data-field="state_color"/);
  editor.cardAt(2).entity_id="timer.example";assert.doesNotMatch(editor.inspectorMarkup(),/data-field="state_color"/);
});

test("per-card precision preview matches the backend golden decimal text without float rounding",()=>{
  const cases=JSON.parse(fs.readFileSync(path.resolve(__dirname,"fixtures/card_precision.json"),"utf8"));
  for(const item of cases)for(const language of ["pl","en"]){
    const editor=makeEditor();Object.assign(editor.cardAt(2),{type:"sensor",entity_id:"sensor.example",action:{kind:"none"},display_precision:item.precision});
    editor._hass={language,states:{"sensor.example":{state:item.state,attributes:{unit_of_measurement:item.unit}}},formatEntityState:()=>"fallback"};
    assert.equal(editor.stateText(editor.cardAt(2)),item[language],JSON.stringify([item,language]));
  }
});

test("calendar date preview shares strict Gregorian cases with native projection and ignores precision",()=>{
  const cases=JSON.parse(fs.readFileSync(path.resolve(__dirname,"fixtures/calendar_dates.json"),"utf8"));
  for(const item of cases)for(const language of ["pl","en"])for(const precision of [undefined,0,6]) {
    const editor=makeEditor(),card=editor.cardAt(2);
    Object.assign(card,{type:"sensor",entity_id:"sensor.example",action:{kind:"none"},display_precision:precision});
    editor._hass={language,states:{"sensor.example":{state:item.state,attributes:{device_class:"date",unit_of_measurement:"ignored"}}},formatEntityState:()=>"incorrect fallback"};
    assert.equal(editor.stateText(card),item[language] ?? editor.t("unknown"),JSON.stringify([item,language,precision]));
  }
});
test("calendar mappings and exceptional states remain authoritative without timezone conversion",()=>{
  const editor=makeEditor(),card=editor.cardAt(2);
  Object.assign(card,{type:"sensor",entity_id:"sensor.example",action:{kind:"none"},state_labels:{"2000-02-29":"Przestępny"}});
  editor._hass={language:"en",locale:{language:"PL_pl"},states:{"sensor.example":{state:"2000-02-29",attributes:{device_class:"date"}}}};
  assert.equal(editor.stateText(card),"Przestępny");delete card.state_labels;
  assert.equal(editor.stateText(card),"29.02.2000");
  editor._hass.states[card.entity_id].state="unavailable";assert.equal(editor.stateText(card),editor.t("offline"));
  editor._hass.states[card.entity_id].state="unknown";assert.equal(editor.stateText(card),editor.t("unknown"));
  editor._hass.states[card.entity_id].state="x".repeat(100000);assert.equal(editor.stateText(card),editor.t("unknown"));
  editor._hass.states[card.entity_id].state="2000-02-29";editor._hass.formatEntityState=()=>"HA unchanged";
  for(const domain of ["number","input_number","input_text"]) {
    const entity=domain+".example";editor._hass.states[entity]={state:"2000-02-29",attributes:{device_class:"date",mode:"text"}};card.entity_id=entity;
    assert.equal(editor.stateText(card),domain==="input_text" ? "2000-02-29" : "HA unchanged");
  }
});
test("date/time helpers share all three strict local modes with the backend",()=>{
  const cases=JSON.parse(fs.readFileSync(path.resolve(__dirname,"fixtures/datetime_helpers.json"),"utf8"));
  for(const item of cases)for(const language of ["pl","en"]) {
    const editor=makeEditor(),card=editor.cardAt(2);Object.assign(card,{type:"sensor",entity_id:"input_datetime.example",action:{kind:"none"}});
    editor._hass={language,states:{"input_datetime.example":{state:item.state,attributes:item.attributes}},formatEntityState:()=>"incorrect fallback"};
    assert.equal(editor.stateText(card),item[language] ?? editor.t("unknown"),JSON.stringify([item,language]));
  }
});
function datetimeEditor(callWS) {
  const editor=sunEditor(callWS);editor.profile.datetime_text_slots=[3,5,8,9,10,11,12];
  editor.profile.slots.push({...clone(editor.slotAt(11)),slot:5});
  editor._entityIndex.set("input_datetime.example",{entity_id:"input_datetime.example",name:"Budzik",domain:"input_datetime",state:"12:34:56",available:true,actions:[]});
  return editor;
}
test("date/time helper assignment, swaps and clipboard preserve passive text-place admission",()=>{
  for(const destination of [2,13,14,15]) {
    const editor=datetimeEditor(),before=clone(editor._draft);
    assert.equal(editor.assignEntity("input_datetime.example",destination),false);assert.deepEqual(clone(editor._draft),before);
    assert.equal(editor._error,editor.t("datetimePlacement"));
    assert.equal(editor.assignEntity("input_datetime.example",11),true);
    assert.equal(editor.cardAt(11).type,"sensor");assert.equal(editor.cardAt(11).icon,"clock");assert.deepEqual(clone(editor.cardAt(11).action),{kind:"none"});
    const placed=clone(editor._draft);assert.equal(editor.moveCard(11,destination),false);assert.deepEqual(clone(editor._draft),placed);
    assert.equal(editor.moveCard(11,3),true);editor.history("undo");
    assert.deepEqual(clone(editor._draft),placed);
    assert.equal(editor.copyCard(11),true);assert.equal(editor.pasteCard(destination),false);assert.equal(editor.pasteCard(5),true);
  }
  const absent=datetimeEditor();delete absent.profile.datetime_text_slots;
  assert.equal(absent.assignEntity("input_datetime.example",11),false);assert.equal(absent._undo.length,0);
});
test("date/time helper invalid import, draft recovery and save fail closed with the right message",async()=>{
  let calls=0;const editor=datetimeEditor(async()=>{calls++;assert.fail("Invalid date/time layout must not send");});
  const item=editor.newCard({entity_id:"input_datetime.example",name:"Budzik"},13);
  const layout={version:2,profile:editor.profile.id,cards:[item]},backup={format:"atmosfera-layout",version:1,layout};
  await assert.rejects(editor.importText(JSON.stringify(backup)),new RegExp(editor.t("datetimePlacement")));
  assert.throws(()=>editor.validateStoredDraft({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout}),new RegExp(editor.t("datetimePlacement")));
  editor._draft.cards.push(item);const before=clone(editor._draft);
  assert.equal(await editor.save(),false);assert.deepEqual(clone(editor._draft),before);assert.equal(calls,0);assert.equal(editor._error,editor.t("datetimePlacement"));
});
test("date/time helper mapped and exceptional values retain their existing priority",()=>{
  const editor=datetimeEditor(),card=editor.cardAt(2);Object.assign(card,{type:"sensor",entity_id:"input_datetime.example",action:{kind:"none"},state_labels:{"2000-02-29 12:34:56":"Rocznica"}});
  editor._hass={language:"pl",states:{"input_datetime.example":{state:"2000-02-29 12:34:56",attributes:{has_date:true,has_time:true,timestamp:0}}}};
  assert.equal(editor.stateText(card),"Rocznica");delete card.state_labels;assert.equal(editor.stateText(card),"29.02.2000 12:34:56");
  editor._hass.states[card.entity_id].state="unknown";assert.equal(editor.stateText(card),editor.t("unknown"));
  editor._hass.states[card.entity_id].state="unavailable";assert.equal(editor.stateText(card),editor.t("offline"));
});
test("precision is explicit, optional and does not replace HA timestamp or duration formatting",()=>{
  const editor=makeEditor(),card=editor.cardAt(2);Object.assign(card,{type:"sensor",entity_id:"sensor.example",action:{kind:"none"}});
  editor._hass={language:"en",states:{"sensor.example":{state:"1.245",attributes:{unit_of_measurement:"W"}}},formatEntityState:()=>"from HA"};
  assert.equal(editor.stateText(card),"from HA");card.display_precision=2;assert.equal(editor.stateText(card),"1.24 W");
  editor._hass.states["sensor.example"].attributes.device_class="duration";assert.equal(editor.stateText(card),"from HA");
  editor._hass.states["sensor.example"].attributes.device_class="timestamp";assert.equal(editor.stateText(card),"from HA");
  editor._hass.states["sensor.example"].state="unavailable";assert.equal(editor.stateText(card),editor.t("offline"));
});

test("precision draft recovery retains zero and rejects invalid values or actionable cards",()=>{
  const editor=makeEditor();Object.assign(editor.cardAt(2),{type:"sensor",entity_id:"sensor.example",action:{kind:"none"},display_precision:0});
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:2,profile:editor.profile.id,cards:clone(editor._draft.cards)}};
  assert.doesNotThrow(()=>editor.validateStoredDraft(clone(record)));
  for(const value of [true,null,-1,7,"2",1.5]){const bad=clone(record);bad.layout.cards[1].display_precision=value;assert.throws(()=>editor.validateStoredDraft(bad));}
  const bad=clone(record);bad.layout.cards[1].type="entity";assert.throws(()=>editor.validateStoredDraft(bad));
});

test("binary information can opt into active-state colors and automatic class icons without becoming actionable",()=>{
  const editor=makeEditor(),card=editor.cardAt(2);Object.assign(card,{type:"sensor",entity_id:"binary_sensor.example",icon:"auto",state_color:true,action:{kind:"none"}});
  editor._data.icons.push("auto","sensor","presence","door");
  for(const [deviceClass,icon] of [["door","door"],["window","door"],["motion","presence"],["presence","presence"],["power","sensor"]]){
    editor._hass={states:{"binary_sensor.example":{state:"on",attributes:{device_class:deviceClass}}}};
    assert.equal(editor.stateColorEligible(card),true);assert.equal(editor.effectiveIcon(card),icon);assert.equal(editor.effectivePalette(card),card.palette);
    editor._hass.states[card.entity_id].state="unknown";assert.equal(editor.effectivePalette(card),"surface");
  }
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:2,profile:editor.profile.id,cards:clone(editor._draft.cards)}};
  assert.doesNotThrow(()=>editor.validateStoredDraft(record));assert.deepEqual(clone(card.action),{kind:"none"});
  const bad=clone(record);bad.layout.cards[1].entity_id="sensor.example";assert.throws(()=>editor.validateStoredDraft(bad));
});

test("automatic icon patches class changes on the same node without replacing focused controls",()=>{
  const editor=makeEditor();Object.assign(editor.cardAt(2),{type:"sensor",entity_id:"binary_sensor.example",icon:"auto",action:{kind:"none"}});
  const focus={},attributes={},writes=[];const icon={getAttribute:key=>attributes[key],setAttribute(key,value){attributes[key]=value;writes.push(value);}};
  const node={dataset:{slot:"2"},querySelector:()=>icon};editor.shadowRoot.activeElement=focus;editor.shadowRoot.querySelectorAll=selector=>selector===".preview-card[data-slot]"?[node]:[];
  editor._hass={states:{"binary_sensor.example":{state:"on",attributes:{device_class:"door"}}}};editor.paintValues();assert.equal(attributes.icon,"mdi:window-closed-variant");
  editor._hass.states["binary_sensor.example"].attributes.device_class="motion";editor.paintValues();assert.equal(attributes.icon,"mdi:account-group-outline");
  editor.paintValues();assert.equal(writes.length,2);assert.equal(editor.shadowRoot.activeElement,focus);assert.equal(editor.cardAt(2).icon,"auto");assert.equal(editor._undo.length,0);
});

test("Polish binary presence replaces the stock English fallback while respecting explicit entity translations",()=>{
  const editor=makeEditor(),card=editor.cardAt(2);Object.assign(card,{type:"sensor",entity_id:"binary_sensor.example",action:{kind:"none"}});
  editor._hass={language:"pl",states:{"binary_sensor.example":{state:"on",attributes:{device_class:"presence"}}},formatEntityState:()=>"Home"};
  assert.equal(editor.stateText(card),"Obecność");editor._hass.states[card.entity_id].state="off";editor._hass.formatEntityState=()=>"Away";assert.equal(editor.stateText(card),"Brak obecności");
  editor._hass.entities={[card.entity_id]:{translation_key:"custom"}};assert.equal(editor.stateText(card),"Away");
  editor._hass.language="en";assert.equal(editor.stateText(card),"Away");
});

test("automation default preview offers enable or disable and never infers Run",()=>{
  const editor=makeEditor(),card=editor.cardAt(2);Object.assign(card,{type:"action",entity_id:"automation.example",state_color:true,action:{kind:"default"}});
  editor._hass={language:"pl",states:{[card.entity_id]:{state:"off",attributes:{}}}};
  assert.equal(editor.stateText(card),"Włącz");assert.equal(editor.effectivePalette(card),"surface");
  editor._hass.states[card.entity_id].state="on";assert.equal(editor.stateText(card),"Wyłącz");assert.equal(editor.effectivePalette(card),card.palette);
  card.action={kind:"service",service:"automation.trigger",data:{skip_condition:false}};assert.equal(editor.stateText(card),"Uruchom");
  editor._hass.states[card.entity_id].state="unavailable";assert.equal(editor.stateText(card),editor.t("offline"));
});

test("automation parameters and scope hints explain empty HA defaults without executing preview",()=>{
  const editor=makeEditor(),card=editor.cardAt(2);Object.assign(card,{type:"action",entity_id:"automation.example",action:{kind:"default"}});editor._selectedSlot=2;
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,actions:[{service:"automation.trigger",fields:{skip_condition:{type:"boolean",required:false}}}]});
  assert.match(editor.inspectorMarkup(),/future triggers/);assert.match(editor.inspectorMarkup(),/allowed to finish/);
  card.action={kind:"service",service:"automation.trigger",data:{skip_condition:false}};
  const before=clone(editor._draft),markup=editor.inspectorMarkup();assert.match(markup,/>Run<\/option>/);assert.match(markup,/Skip conditions/);assert.match(markup,/No checks them/);assert.deepEqual(clone(editor._draft),before);
  editor._hass={language:"pl"};assert.match(editor.fieldMarkup("stop_actions",{type:"boolean"},false),/Zatrzymaj trwające akcje/);
  for(const value of ["false","true"]){assert.equal(editor.parseFieldValue({value,dataset:{field:"data:skip_condition"}},{type:"boolean"}),value==="true");}
});

function choiceEditor(callWS) {
  const editor=lightEditor(callWS),card=editor.cardAt(2);card.entity_id="input_select.helper";
  const options=["Eco","Komfort","Żółty"];
  editor.profile.schema_control_types=["light","number","choice"];
  editor._status={...editor._status,entity_control_status:"ready",native_control_types:["entity_control_v1"],control_kinds:["light","number","choice"]};
  editor._hass.states[card.entity_id]={state:"Eco",attributes:{options:[...options]}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"input_select",name:"Tryb",state:"Eco",available:true,actions:[{service:"input_select.select_option",fields:{option:{type:"select",options:[...options],required:true}}}],choice_control:{options:[...options],index:0}});
  return editor;
}

function fanPresetEditor() {
  const editor=choiceEditor(),card=editor.cardAt(2),options=["Eco","Komfort","Żółty"];
  card.entity_id="fan.helper";
  editor._hass.states[card.entity_id]={state:"on",attributes:{supported_features:8,preset_modes:[...options],preset_mode:"Eco"}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"fan",name:"Wentylator",state:"on",available:true,
    actions:[{service:"fan.set_preset_mode",fields:{preset_mode:{type:"select",options:[...options],required:true}}}],choice_control:{options:[...options],index:0}});
  return editor;
}

test("fan manual mode requires explicit empty metadata and the current negotiated extension",()=>{
  const editor=fanPresetEditor(),card=editor.cardAt(2),state=editor._hass.states[card.entity_id],entity=editor.entityFor(card.entity_id);
  state.attributes.preset_mode=null;entity.choice_control.index=null;entity.choice_control.empty=true;
  assert.equal(editor.choiceControlAvailability(card).ready,false);
  editor._status.empty_choice_version=1;assert.equal(editor.choiceControlAvailability(card).ready,true);
  editor._selectedSlot=2;assert.equal(editor.requestLightControl("choice"),true);assert.equal(editor.confirmLightControl(),true);
  assert.equal(editor.stateText(card),"Manual mode");editor._hass.language="pl";editor._hass.locale={language:"pl"};assert.equal(editor.stateText(card),"Tryb ręczny");
  delete state.attributes.preset_mode;assert.equal(editor.choiceControlAvailability(card).ready,false);assert.equal(editor.stateText(card),editor.t("unknown"));
  state.attributes.preset_mode=null;entity.choice_control.empty=false;assert.equal(editor.choiceControlAvailability(card).ready,false);
  entity.choice_control.empty=true;editor._status.empty_choice_version=0;assert.equal(editor.choiceControlAvailability(card).ready,false);
  editor._status.empty_choice_version=1;state.state="unknown";assert.equal(editor.choiceControlAvailability(card).ready,false);
  state.state="on";state.attributes.supported_features=0;assert.equal(editor.stateText(card),editor.t("unknown"));
});

test("fan preset admission observes its preset rather than power and rechecks live capabilities",()=>{
  const editor=fanPresetEditor(),card=editor.cardAt(2),state=editor._hass.states[card.entity_id];
  assert.equal(editor.choiceControlAvailability(card).ready,true);
  state.state="off";assert.equal(editor.choiceControlAvailability(card).ready,true);
  for(const features of [0,32,true,-1,"8"]) {state.attributes.supported_features=features;assert.equal(editor.choiceControlAvailability(card).ready,false);}
  state.attributes.supported_features=8;
  state.attributes.preset_mode="absent";assert.equal(editor.choiceControlAvailability(card).ready,false);
  state.attributes.preset_mode="Eco";state.attributes.preset_modes=["Komfort","Eco"];assert.equal(editor.choiceControlAvailability(card).ready,false);
  state.attributes.preset_modes=["Eco","Komfort","Żółty"];state.state="unavailable";assert.equal(editor.choiceControlAvailability(card).ready,false);
});

test("Core fan preset admission accepts either speed or preset feature and preserves negative gates",()=>{
  for(const features of [1,8,9,55,56,63]){
    const editor=fanPresetEditor(),card=editor.cardAt(2);editor._hass.states[card.entity_id].attributes.supported_features=features;
    assert.equal(editor.choiceControlAvailability(card).ready,true,features);
  }
  for(const features of [0,2,4,16,32,48,true,-1,"8",null,Number.MAX_SAFE_INTEGER+1]){
    const editor=fanPresetEditor(),card=editor.cardAt(2);editor._hass.states[card.entity_id].attributes.supported_features=features;
    assert.equal(editor.choiceControlAvailability(card).ready,false,String(features));
  }
  for(const mutate of [e=>{e._entityIndex.get("fan.helper").actions=[];},e=>{e._hass.states["fan.helper"].state="unavailable";},
      e=>{delete e._hass.states["fan.helper"].attributes.preset_mode;},e=>{e._hass.states["fan.helper"].attributes.preset_mode="absent";},
      e=>{e._entityIndex.get("fan.helper").choice_control.options=["Eco","Eco"];},e=>{e._status.device_available=false;}]){
    const editor=fanPresetEditor();editor._hass.states["fan.helper"].attributes.supported_features=55;mutate(editor);
    assert.equal(editor.choiceControlAvailability().ready,false);
  }
});

test("speed-feature preset conversion remains an explicit reversible draft with no service or layout save",()=>{
  const editor=fanPresetEditor(),before=clone(editor._draft),card=editor.cardAt(2);let calls=0;
  editor._hass.callWS=async()=>{calls++;throw Error("Unexpected live request");};
  editor._hass.callService=async()=>{calls++;throw Error("Unexpected service request");};
  editor._hass.states[card.entity_id].attributes.supported_features=55;
  editor._selectedSlot=2;assert.equal(editor.requestLightControl("choice"),true);
  assert.deepEqual(clone(editor._draft),before);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"choice"});
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);assert.equal(calls,0);
});

test("full fan editor retains backend service admission with Core mask55 and no percentage observation",()=>{
  const editor=fanPanelEditor(),card=editor.cardAt(2),state=editor._hass.states[card.entity_id];
  state.attributes.supported_features=55;state.attributes.percentage=null;state.attributes.preset_mode="Eco";
  assert.equal(editor.fanControlAvailability(card).ready,true);
  editor._entityIndex.get(card.entity_id).actions=editor._entityIndex.get(card.entity_id).actions.filter(a=>a.service!=="fan.set_preset_mode");
  assert.equal(editor.fanControlAvailability(card).ready,false);
});

test("fan choice conversion is reviewed and reversible and preview shows the authoritative preset",()=>{
  const editor=fanPresetEditor(),card=editor.cardAt(2),before=clone(editor._draft),state=editor._hass.states[card.entity_id];
  editor._selectedSlot=2;assert.equal(editor.requestLightControl("choice"),true);
  assert.deepEqual(clone(editor._draft),before);assert.equal(editor.confirmLightControl(),true);
  assert.equal(editor._draft.version,3);assert.deepEqual(clone(card.action),{kind:"control",control:"choice"});
  assert.equal(editor.stateText(card),"Eco");state.attributes.preset_mode="Żółty";assert.equal(editor.stateText(card),"Żółty");
  state.state="unknown";assert.equal(editor.stateText(card),editor.t("unknown"));
  state.state="unavailable";assert.equal(editor.stateText(card),editor.t("offline"));
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}};
  assert.doesNotThrow(()=>editor.validateStoredDraft(record));editor.history("undo");assert.deepEqual(clone(editor._draft),before);
});

function eventEditor() {
  const editor=makeEditor();editor.profile.schema_event_actions=true;editor.profile.layout_versions=[2,3];
  editor._status.event_press_supported=true;editor._selectedSlot=2;editor.cardAt(2).type="action";
  return editor;
}

function eventPanelEditor() {
  const editor=eventEditor();
  editor.profile.schema_control_types=["panel"];
  editor.profile.schema_panel_extra_profiles=[{name:"action",version:2},{name:"tile_event",version:1}];
  Object.assign(editor._status,{native_control_types:["panel"],entity_control_status:"ready",
    panel_extra_profiles:clone(editor.profile.schema_panel_extra_profiles)});
  return editor;
}

test("tile event panel conversion is explicit reviewed reversible and sends no event or save",()=>{
  const editor=eventPanelEditor(),before=clone(editor._draft),saved=clone(editor._saved),original=clone(editor.cardAt(2));let calls=0;
  editor._hass.callWS=async()=>{calls++;throw Error("No live requests");};
  assert.match(editor.inspectorMarkup(),/value="tile-event-panel"/);
  assert.equal(editor.requestTileEvent(true),true);assert.deepEqual(clone(editor._draft),before);
  assert.match(editor.modalMarkup(),/Only its Send event button/);
  assert.equal(editor.confirmTileEvent(),true);
  assert.equal(editor._draft.version,3);assert.equal(editor.cardAt(2).id,original.id);
  assert.equal(editor.cardAt(2).entity_id,"");
  assert.deepEqual(clone(editor.cardAt(2).action),{kind:"control",control:"panel",property:"tile_event"});
  assert.equal(editor.stateText(editor.cardAt(2)),"Open");
  assert.equal(editor.cardAt(2).palette,original.palette);assert.equal(calls,0);assert.deepEqual(clone(editor._saved),saved);
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}};
  assert.doesNotThrow(()=>editor.validateStoredDraft(record));
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);
});

test("tile event panel keeps direct automation action unchanged until explicit review and supports an empty slot",()=>{
  const editor=eventPanelEditor();editor.requestTileEvent();editor.confirmTileEvent();
  const direct=clone(editor._draft);assert.deepEqual(clone(editor.cardAt(2).action),{kind:"event"});
  editor.hass={...editor._hass};assert.deepEqual(clone(editor._draft),direct);
  assert.equal(editor.requestTileEvent(true),true);assert.equal(editor.confirmTileEvent(),true);
  assert.equal(editor.cardAt(2).action.property,"tile_event");
  editor._selectedSlot=13;assert.match(editor.inspectorMarkup(),/create-tile-event-panel/);
  assert.equal(editor.requestTileEvent(true),true);assert.equal(editor.confirmTileEvent(),true);
  assert.equal(editor.cardAt(13).type,"action");assert.equal(editor.cardAt(13).entity_id,"");
});

test("tile event panel needs both negotiated profiles and blocks changed review without migration",()=>{
  for(const change of [e=>{e._status.panel_extra_profiles=[{name:"action",version:2}];},
      e=>{e._status.panel_extra_profiles=[{name:"tile_event",version:1}];},
      e=>{e._status.panel_extra_profiles=[{name:"action",version:1},{name:"tile_event",version:1}];},
      e=>{e._status.device_available=false;},e=>{e._status.entity_control_status="pending";},
      e=>{e.profile.schema_panel_extra_profiles=[{name:"action",version:2}];}]){
    const editor=eventPanelEditor(),before=clone(editor._draft);change(editor);
    assert.equal(editor.requestTileEvent(true),false);assert.deepEqual(clone(editor._draft),before);
  }
  for(const change of [e=>{e._status.panel_extra_profiles.pop();},e=>{e.cardAt(2).title="changed";},e=>{e._saved.revision++;}]){
    const editor=eventPanelEditor();assert.equal(editor.requestTileEvent(true),true);change(editor);
    const before=clone(editor._draft);assert.equal(editor.confirmTileEvent(),false);assert.deepEqual(clone(editor._draft),before);
  }
});

test("tile event panel rejects smuggled entity and extra payload and localizes escaped review",()=>{
  const editor=eventPanelEditor();editor.cardAt(2).title='<img src=x>';editor._hass.locale.language="pl";
  editor.requestTileEvent(true);assert.match(editor.modalMarkup(),/Użyć panelu zdarzenia/);assert.match(editor.modalMarkup(),/&lt;img/);
  assert.doesNotMatch(editor.modalMarkup(),/<img src/);editor.confirmTileEvent();
  for(const mutate of [c=>{c.entity_id="event.foreign";},c=>{c.action.payload={evil:true};},c=>{c.type="entity";}]){
    const layout=clone(editor._draft);mutate(layout.cards.find(c=>c.slot===2));
    const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:layout.cards}};
    assert.throws(()=>editor.validateStoredDraft(record));
  }
});

test("automation button conversion is reviewed, clears the old target and remains one reversible draft edit",()=>{
  const editor=eventEditor(),before=clone(editor._draft),original=clone(editor.cardAt(2));
  assert.match(editor.inspectorMarkup(),/value="event"/);
  editor.editField(actionInput("event"));assert.equal(editor._pending.kind,"tile-event");assert.deepEqual(clone(editor._draft),before);
  assert.match(editor.modalMarkup(),/replaces the card/);assert.equal(editor.confirmTileEvent(),true);
  const current=editor.cardAt(2);assert.equal(editor._draft.version,3);assert.equal(current.id,original.id);assert.equal(current.title,original.title);
  assert.equal(current.entity_id,"");assert.deepEqual(clone(current.action),{kind:"event"});assert.equal(editor._undo.length,1);
  assert.match(editor.inspectorMarkup(),/Each press is available/);assert.doesNotMatch(editor.inspectorMarkup(),/entity-reference/);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).id,original.id);
});

test("an empty place can create an automation button without choosing an entity",()=>{
  const editor=eventEditor();editor._selectedSlot=13;assert.match(editor.inspectorMarkup(),/create-tile-event/);
  assert.equal(editor.requestTileEvent(),true);assert.match(editor.modalMarkup(),/Create a button/);assert.equal(editor.confirmTileEvent(),true);
  const card=clone(editor.cardAt(13));assert.match(card.id,/^card-/);assert.equal(card.type,"action");assert.equal(card.entity_id,"");assert.equal(card.title,"Automation");
  assert.deepEqual(card.action,{kind:"event"});editor.history("undo");assert.equal(editor.cardAt(13),undefined);
  editor.history("redo");assert.equal(editor.cardAt(13).id,card.id);
});

test("event review refuses stale identity, revisions, capabilities and input context without changing the draft",()=>{
  for(const change of [e=>{e._entryId="other";},e=>{e._selectionEpoch++;},e=>{e._hass.user={id:"other"};},e=>{e._selectedSlot=3;},e=>{e._saved.revision++;},e=>{e._draft.revision++;},e=>{e.cardAt(2).title="Changed";},e=>{e.profile.width++;},e=>{e._status.event_press_supported=false;},e=>{e._status.device_available=false;},e=>{e._statusError=true;},e=>{e._conflict=true;},e=>{e._carry={};},e=>{e._drag={};},e=>{e._fieldErrors.title="invalid";}]) {
    const editor=eventEditor();assert.equal(editor.requestTileEvent(),true);change(editor);const before=clone(editor._draft);
    assert.equal(editor.confirmTileEvent(),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
  }
});

test("event creation requires an explicit supported profile, connected reports and editable Action placement",()=>{
  for(const change of [e=>{delete e.profile.schema_event_actions;},e=>{e.profile.layout_versions=[2];},e=>{e._status.event_press_supported=1;},e=>{e._status.device_available=false;},e=>{e._profileStale=true;},e=>{e.cardAt(2).type="sensor";},e=>{e._selectedSlot=0;},e=>{e._busy=true;},e=>{e._selectingCards=true;}]) {
    const editor=eventEditor();change(editor);const before=clone(editor._draft);assert.equal(editor.requestTileEvent(),false);assert.deepEqual(clone(editor._draft),before);
  }
});

test("event drafts roundtrip and retain identity through move, copy and undo while rejecting hybrid targets",()=>{
  const editor=eventEditor();assert.equal(editor.requestTileEvent(),true);assert.equal(editor.confirmTileEvent(),true);
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  for(const change of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="light.room";},r=>{r.layout.cards[1].type="sensor";},r=>{r.layout.cards[1].action.service="light.toggle";},r=>{r.layout.cards[1].action.data={};},r=>{r.layout.cards[1].action.control="choice";}]){const bad=record();change(bad);assert.throws(()=>editor.validateStoredDraft(bad));}
  assert.equal(editor.moveCard(2,11),true);assert.equal(editor.cardAt(11).id,"first");assert.equal(editor.copyCard(11),true);
  assert.equal(editor.pasteCard(13),true);assert.notEqual(editor.cardAt(13).id,"first");assert.deepEqual(clone(editor.cardAt(13).action),{kind:"event"});
  editor.history("undo");assert.equal(editor.cardAt(13),undefined);assert.equal(editor.cardAt(11).id,"first");
});

test("saved event buttons stay visible but passive in an offline editor and type changes clear their declaration",()=>{
  const editor=eventEditor();editor.requestTileEvent();editor.confirmTileEvent();editor._status.device_available=false;
  const before=clone(editor._draft);assert.match(editor.inspectorMarkup(),/value="event" selected disabled/);assert.match(editor.inspectorMarkup(),/compatible touch reports/);
  assert.equal(editor.requestTileEvent(),false);assert.deepEqual(clone(editor._draft),before);
  editor.editField({dataset:{field:"type"},value:"entity",removeAttribute(){},setAttribute(){}});
  assert.deepEqual(clone(editor.cardAt(2).action),{kind:"none"});
});

test("automation button UI is localized and escapes card content in its review",()=>{
  const editor=eventEditor();editor._hass.locale.language="pl";editor.cardAt(2).title='<img src=x onerror="bad()">';
  editor.requestTileEvent();const markup=editor.modalMarkup();assert.match(markup,/Użyć przycisku automatyzacji/);
  assert.match(markup,/&lt;img/);assert.doesNotMatch(markup,/<img/);editor.confirmTileEvent();assert.equal(editor.stateText(editor.cardAt(2)),"Przycisk automatyzacji");
});

test("choice admission requires an actually negotiated kind and exact bounded live metadata",()=>{
  const editor=choiceEditor();assert.equal(editor.choiceControlAvailability().ready,true);assert.match(editor.inspectorMarkup(),/value="control-choice"/);
  for(const mutate of [e=>{e._status.control_kinds=["light","number"];},e=>{e._status.control_kinds="choice";},e=>{e._status.device_available=false;},e=>{e.profile.layout_versions="3";},e=>{e._entityIndex.get("input_select.helper").actions={};},e=>{e._hass.states["input_select.helper"].state="unknown";},e=>{e._hass.states["input_select.helper"].attributes.options.reverse();},e=>{e._entityIndex.get("input_select.helper").choice_control.index=true;}]) {
    const item=choiceEditor();mutate(item);assert.equal(item.choiceControlAvailability().ready,false);
  }
  for(const options of [["Eco","Eco"],["Eco",...Array(8).fill("x")],["Eco","ą".repeat(17)],["Eco","\u202ebad"],["Eco","unknown"],["Eco","unavailable"]]){
    const item=choiceEditor();item._entityIndex.get("input_select.helper").choice_control.options=options;item._hass.states["input_select.helper"].attributes.options=options;
    assert.equal(item.choiceControlAvailability().ready,false);
  }
});

test("choosing a control only edits a reviewed v3 draft and creates no HA command",()=>{
  let calls=0;const editor=choiceEditor(async()=>{calls++;throw Error("Unexpected request");}),before=clone(editor._draft);
  editor.editField(actionInput("control-choice"));assert.equal(editor._pending.controlKind,"choice");assert.deepEqual(clone(editor._draft),before);assert.match(editor.modalMarkup(),/option selection/);
  assert.equal(editor.confirmLightControl(),true);assert.equal(editor._draft.version,3);assert.deepEqual(clone(editor.cardAt(2).action),{kind:"control",control:"choice"});assert.equal(calls,0);assert.equal(editor._undo.length,1);
});

test("a changed option catalogue invalidates the captured configuration review",()=>{
  const editor=choiceEditor(),before=clone(editor._draft);assert.equal(editor.requestLightControl("choice"),true);
  editor._hass.states["input_select.helper"].attributes.options=["Eco","Other"];
  assert.equal(editor.confirmLightControl(),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._undo.length,0);
});

test("choice drafts roundtrip their explicit domain and PL inspector uses choice guidance",()=>{
  const editor=choiceEditor();editor._hass.locale.language="pl";editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"choice"};
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}};
  assert.doesNotThrow(()=>editor.validateStoredDraft(record));assert.match(editor.inspectorMarkup(),/Otwórz wybór opcji/);assert.match(editor.inspectorMarkup(),/następnie Zastosuj/);assert.doesNotMatch(editor.inspectorMarkup(),/jasnoś|sterowanie światłem|Włącz\/Wyłącz/iu);
  const invalid=clone(record);invalid.layout.cards[1].entity_id="light.example";assert.throws(()=>editor.validateStoredDraft(invalid));
});

function oscillationEditor() {
  const editor=makeEditor();editor._selectedSlot=2;
  editor.profile.schema_fan_oscillation=true;editor.profile.layout_versions=[2,3];
  editor._status={device_available:true,context_press_version:1,press_enabled_version:1};
  editor.cardAt(2).entity_id="fan.test";
  editor._hass.states["fan.test"]={state:"on",attributes:{supported_features:2,oscillating:false}};
  editor._entityIndex.set("fan.test",{entity_id:"fan.test",domain:"fan",available:true,state:"on",fan_oscillation:{value:false},actions:[{service:"fan.oscillate",fields:{oscillating:{type:"boolean",required:true}}}]});
  editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);
  return editor;
}

test("explicit fan oscillation drafts retain history without sending a service",()=>{
  const editor=oscillationEditor();assert.equal(editor.fanOscillationReady(editor.cardAt(2)),true);
  assert.match(editor.inspectorMarkup(),/Toggle oscillation/);
  editor.editField(actionInput("fan_oscillation"));
  editor.finishField();
  assert.equal(editor._draft.version,3);assert.deepEqual(clone(editor.cardAt(2).action),{kind:"fan_oscillation"});
  assert.match(editor.inspectorMarkup(),/Fan power stays unchanged/);
  editor.history("undo");assert.deepEqual(clone(editor.cardAt(2).action),{kind:"default"});
  assert.equal(editor.dirty,false);editor.history("redo");assert.equal(editor.cardAt(2).action.kind,"fan_oscillation");
});

test("oscillation preview and palette follow strict observed Boolean independently of power",()=>{
  const editor=oscillationEditor(),item=editor.cardAt(2);item.action={kind:"fan_oscillation"};item.state_color=true;
  for(const power of ["on","off"]){
    editor._hass.states["fan.test"].state=power;
    for(const value of [true,false]){
      editor._hass.states["fan.test"].attributes.oscillating=value;
      assert.equal(editor.stateText(item),value?"Oscillation: on":"Oscillation: off");
      assert.equal(editor.effectivePalette(item),value?"primary":"surface");
      editor._hass.locale.language="pl";assert.equal(editor.stateText(item),value?"Oscylacja wł.":"Oscylacja wył.");editor._hass.locale.language="en";
    }
  }
  for(const value of [null,0,1,"false",[],{}]){editor._hass.states["fan.test"].attributes.oscillating=value;assert.equal(editor.fanOscillationReady(item),false);assert.equal(editor.stateText(item),"Unknown");assert.equal(editor.effectivePalette(item),"surface");}
});

test("oscillation draft admission rejects wrong domain, old schema and hybrid service data",()=>{
  const editor=oscillationEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"fan_oscillation"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="light.room";},r=>{r.layout.cards[1].action.data={oscillating:true};},r=>{r.layout.cards[1].type="sensor";}]){const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));}
  editor.profile.schema_fan_oscillation=false;assert.throws(()=>editor.validateStoredDraft(record()));
});

function fanDirectionEditor() {
  const editor=fanPresetEditor(),card=editor.cardAt(2);editor._selectedSlot=2;
  editor.profile.schema_fan_direction=true;editor.profile.layout_versions=[2,3];
  Object.assign(editor._hass.states[card.entity_id],{state:"off",attributes:{supported_features:4|8,direction:"reverse",preset_modes:["Eco","Komfort","Żółty"],preset_mode:"Eco"}});
  Object.assign(editor.entityFor(card.entity_id),{fan_direction:{options:["forward","reverse"],index:1}});
  editor.entityFor(card.entity_id).actions.push({service:"fan.set_direction",fields:{direction:{type:"select",options:["forward","reverse"],required:true}}});
  return editor;
}

test("direction choice is reviewed separately from preset, localized and undoable without commands",()=>{
  const editor=fanDirectionEditor(),card=editor.cardAt(2);editor._saved.cards=clone(editor._draft.cards);
  const before=clone(editor._draft);assert.equal(editor.fanDirectionAvailability(card).ready,true);assert.equal(editor.choiceControlAvailability(card).ready,true);
  assert.match(editor.inspectorMarkup(),/value="control-direction"/);
  assert.equal(editor.requestLightControl("direction"),true);assert.equal(editor._pending.controlKind,"direction");assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"choice",property:"direction"});assert.equal(editor.stateText(card),"Reverse");
  assert.match(editor.inspectorMarkup(),/value="control-direction" selected/);assert.doesNotMatch(editor.inspectorMarkup(),/value="control-choice" selected/);
  editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"Wstecz");editor.history("undo");assert.deepEqual(clone(editor._draft),before);
  editor.history("redo");assert.equal(editor.cardAt(2).action.property,"direction");
});

test("direction review rejects state metadata drift, capability/service/outage and old profile",()=>{
  for(const mutate of [e=>{e.profile.schema_fan_direction=false;},e=>{e._status.entity_control_status="offline";},
      e=>{e._hass.states[e.cardAt(2).entity_id].state="unavailable";},e=>{e._hass.states[e.cardAt(2).entity_id].attributes.supported_features=8;},
      e=>{e._hass.states[e.cardAt(2).entity_id].attributes.direction=null;},e=>{e.entityFor(e.cardAt(2).entity_id).fan_direction.options.reverse();},
      e=>{e.entityFor(e.cardAt(2).entity_id).actions=e.entityFor(e.cardAt(2).entity_id).actions.filter(a=>a.service!=="fan.set_direction");}]) {
    const editor=fanDirectionEditor();mutate(editor);assert.equal(editor.fanDirectionAvailability().ready,false);assert.equal(editor.requestLightControl("direction"),false);
  }
  const editor=fanDirectionEditor();assert.equal(editor.requestLightControl("direction"),true);editor.entityFor(editor.cardAt(2).entity_id).fan_direction.index=0;
  assert.equal(editor.confirmLightControl(),false);assert.notEqual(editor.cardAt(2).action.property,"direction");
});

test("direction draft requires the exact explicit v3 fan property and rejects hybrid imports",()=>{
  const editor=fanDirectionEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"choice",property:"direction"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="select.test";},r=>{r.layout.cards[1].action.data={};},r=>{r.layout.cards[1].action.property="preset";},r=>{r.layout.cards[1].type="sensor";}]) {
    const r=record();mutate(r);assert.throws(()=>editor.validateStoredDraft(r));
  }
  editor.profile.schema_fan_direction=false;assert.throws(()=>editor.validateStoredDraft(record()));
});

function effectEditor() {
  const editor=choiceEditor(),card=editor.cardAt(2),options=["Solid","Pulse"," Żółty "];
  card.entity_id="light.effect_test";editor.profile.schema_light_effect=true;editor._status.empty_choice_version=1;
  editor._hass.states[card.entity_id]={state:"off",attributes:{supported_features:4,supported_color_modes:["onoff"],effect_list:[...options],effect:null}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"light",available:true,
    light_effect:{options:[...options],index:null,empty:true},
    actions:[{service:"light.turn_on",fields:{effect:{type:"select",options:[...options],required:false}}}]});
  editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);return editor;
}

test("light effect review explains activation, starts from known empty and stays reversible without preview commands",()=>{
  const editor=effectEditor(),card=editor.cardAt(2),before=clone(editor._draft);
  assert.equal(editor.lightEffectAvailability(card).ready,true);assert.match(editor.inspectorMarkup(),/value="control-effect"/);
  assert.equal(editor.requestLightControl("effect"),true);assert.match(editor.modalMarkup(),/can turn the light on/);
  assert.equal(editor.confirmLightControl(),true);assert.deepEqual(clone(card.action),{kind:"control",control:"choice",property:"effect"});
  assert.equal(editor.stateText(card),"No effect");assert.equal(editor.groupTargetCompatible(card,11),true);
  assert.match(editor.inspectorMarkup(),/value="control-effect" selected/);assert.doesNotMatch(editor.inspectorMarkup(),/These settings define|do not add a slider/);
  editor._hass.states[card.entity_id].state="on";editor._hass.states[card.entity_id].attributes.effect="Pulse";
  assert.equal(editor.stateText(card),"Pulse");
  editor._hass.formatEntityAttributeValue=(_state,attr)=>attr==="effect"?"HA translated effect":"wrong";assert.equal(editor.stateText(card),"HA translated effect");delete editor._hass.formatEntityAttributeValue;
  editor._hass.locale.language="pl";editor._hass.states[card.entity_id].state="off";editor._hass.states[card.entity_id].attributes.effect=null;
  assert.equal(editor.stateText(card),"Brak efektu");assert.match(editor.controlText("controlReviewV3","effect"),/może włączyć światło/);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).action.property,"effect");
});

test("light effects require negotiated empty only for explicit null, never for a real none option",()=>{
  const editor=effectEditor(),card=editor.cardAt(2),state=editor._hass.states[card.entity_id];editor._status.empty_choice_version=0;
  assert.equal(editor.lightEffectAvailability(card).ready,false);
  state.state="on";state.attributes.effect="Pulse";assert.equal(editor.lightEffectAvailability(card).ready,true);
  const options=["none","Solid"];state.attributes.effect_list=options;state.attributes.effect="none";
  editor.entityFor(card.entity_id).light_effect.options=[...options];editor.entityFor(card.entity_id).actions[0].fields.effect.options=[...options];
  assert.equal(editor.observedLightEffect(card).index,0);assert.equal(editor.observedLightEffect(card).empty,false);
  assert.equal(editor.lightEffectAvailability(card).ready,true);
});

test("light effects reject missing or stale off values, malformed lists, lost service fields and untrusted readiness",()=>{
  for(const mutate of [e=>{e.profile.schema_light_effect=false;},e=>{e._status.entity_control_status="offline";},
    e=>{e._hass.states["light.effect_test"].state="unavailable";},e=>{delete e._hass.states["light.effect_test"].attributes.effect;},
    e=>{e._hass.states["light.effect_test"].attributes.effect="Pulse";},e=>{e._hass.states["light.effect_test"].attributes.supported_features=0;},
    e=>{e._hass.states["light.effect_test"].attributes.effect_list=[];},e=>{e.entityFor("light.effect_test").actions[0].fields={};},
    e=>{e.entityFor("light.effect_test").light_effect.options=["bad\u202e"];e._hass.states["light.effect_test"].attributes.effect_list=["bad\u202e"];},
    e=>{e.entityFor("light.effect_test").light_effect.options=["x".repeat(33)];e._hass.states["light.effect_test"].attributes.effect_list=["x".repeat(33)];}]){
    const editor=effectEditor();mutate(editor);assert.equal(editor.lightEffectAvailability().ready,false);assert.equal(editor.requestLightControl("effect"),false);
  }
});

test("effect review is invalidated by changed options or empty-state semantics",()=>{
  for(const mutate of [e=>{e.entityFor("light.effect_test").light_effect.options.reverse();e.entityFor("light.effect_test").actions[0].fields.effect.options.reverse();e._hass.states["light.effect_test"].attributes.effect_list.reverse();},
    e=>{e._hass.states["light.effect_test"].state="on";e._hass.states["light.effect_test"].attributes.effect="Pulse";}]){
    const editor=effectEditor();assert.equal(editor.requestLightControl("effect"),true);mutate(editor);assert.equal(editor.confirmLightControl(),false);
    assert.notEqual(editor.cardAt(2).action.property,"effect");
  }
});

test("effect recovery keeps explicit facet and field scope without repurposing ordinary light control",()=>{
  const editor=effectEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"choice",property:"effect"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  const fixed=record();fixed.layout.cards[1].action={kind:"service",service:"light.turn_on",data:{effect:"Pulse"}};assert.doesNotThrow(()=>editor.validateStoredDraft(fixed));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="humidifier.test";},r=>{r.layout.cards[1].action.data={effect:"Pulse"};},
    r=>{r.layout.cards[1].action.property="effect_list";},r=>{r.layout.cards[1].type="sensor";}]){const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));}
  const wrong=clone(fixed);wrong.layout.cards[1].action.service="light.turn_off";assert.throws(()=>editor.validateStoredDraft(wrong));
  editor.profile.schema_light_effect=false;assert.throws(()=>editor.validateStoredDraft(record()));
  const ordinary=record();ordinary.layout.cards[1].action={kind:"control",control:"light"};assert.doesNotThrow(()=>editor.validateStoredDraft(ordinary));
});

function fanSpeedEditor() {
  const editor=choiceEditor(),card=editor.cardAt(2);card.entity_id="fan.speed_test";editor.profile.schema_fan_speed=true;
  editor._hass.states[card.entity_id]={state:"on",attributes:{supported_features:9,percentage_step:100/3,percentage:33,preset_mode:"eco",preset_modes:["eco","sleep"]}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"fan",available:true,state:"on",fan_speed:{options:["0","33","66","100"],index:1,speed_count:3},actions:[{service:"fan.set_percentage",fields:{percentage:{type:"number",min:0,max:100,required:true}}}]});
  editor._selectedSlot=2;editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);return editor;
}

test("fan speed selection reviews activation and renders actual percentages independently of presets",()=>{
  const editor=fanSpeedEditor(),card=editor.cardAt(2),before=clone(editor._draft);
  assert.equal(editor.fanSpeedAvailability(card).ready,true);assert.match(editor.inspectorMarkup(),/value="control-speed"/);
  assert.equal(editor.requestLightControl("speed"),true);assert.match(editor.modalMarkup(),/start or stop the fan/);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"choice",property:"percentage"});assert.equal(editor.stateText(card),"33 %");
  assert.match(editor.inspectorMarkup(),/Changing speed can start or stop/);assert.doesNotMatch(editor.inspectorMarkup(),/Manual mode|They do not add a slider|Choose a supported option/);
  editor._hass.states[card.entity_id].attributes.percentage=66;assert.equal(editor.stateText(card),"66 %");
  editor._hass.states[card.entity_id].state="off";assert.equal(editor.stateText(card),"66 %");
  assert.equal(editor.groupTargetCompatible(card,11),true);editor._hass.locale.language="pl";assert.match(editor.inspectorMarkup(),/może uruchomić lub zatrzymać wentylator/);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).action.property,"percentage");
});

test("fan speed refuses rounded steps, null or off-list state and incomplete count or service metadata",()=>{
  for(const mutate of [e=>{e.profile.schema_fan_speed=false;},e=>{e._status.entity_control_status="offline";},e=>{e._hass.states["fan.speed_test"].state="unavailable";},
    e=>{e._hass.states["fan.speed_test"].attributes.percentage_step=33;},e=>{e._hass.states["fan.speed_test"].attributes.percentage=34;},
    e=>{e._hass.states["fan.speed_test"].attributes.percentage=null;},e=>{e._hass.states["fan.speed_test"].attributes.percentage="33";},
    e=>{e._hass.states["fan.speed_test"].attributes.supported_features=8;},e=>{e.entityFor("fan.speed_test").fan_speed.speed_count=8;},
    e=>{e.entityFor("fan.speed_test").fan_speed.options.reverse();},e=>{e.entityFor("fan.speed_test").fan_speed.options=["0","33","33","100"];},
    e=>{e.entityFor("fan.speed_test").actions=[];}]){
    const editor=fanSpeedEditor();mutate(editor);assert.equal(editor.fanSpeedAvailability().ready,false);assert.equal(editor.requestLightControl("speed"),false);
  }
  const editor=fanSpeedEditor();assert.equal(editor.requestLightControl("speed"),true);editor._hass.states["fan.speed_test"].attributes.percentage_step=25;assert.equal(editor.confirmLightControl(),false);
});

test("seven actual speeds fit eight bounded rows and preview accepts exact zero without inventing it",()=>{
  const editor=fanSpeedEditor(),state=editor._hass.states["fan.speed_test"],meta=editor.entityFor("fan.speed_test").fan_speed;
  state.attributes.percentage_step=100/7;state.attributes.percentage=14;meta.speed_count=7;meta.options=["0","14","28","42","57","71","85","100"];
  assert.equal(editor.fanSpeedAvailability().ready,true);editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"choice",property:"percentage"};
  assert.equal(editor.stateText(editor.cardAt(2)),"14 %");state.attributes.percentage=0;assert.equal(editor.stateText(editor.cardAt(2)),"0 %");
  state.attributes.percentage=null;assert.equal(editor.stateText(editor.cardAt(2)),editor.t("unknown"));
});

test("speed draft recovery is explicit v3 fan only while ordinary fan choice remains preset",()=>{
  const editor=fanSpeedEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"choice",property:"percentage"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="light.test";},r=>{r.layout.cards[1].action.data={};},r=>{r.layout.cards[1].action.control="number";},r=>{r.layout.cards[1].type="sensor";}]){
    const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));
  }
  editor.profile.schema_fan_speed=false;assert.throws(()=>editor.validateStoredDraft(record()));
  assert.equal(fanPresetEditor().choiceControlAvailability().ready,true);
});

function kelvinEditor() {
  const editor=numberEditor(),card=editor.cardAt(2);card.entity_id="light.test";editor.profile.schema_light_color_temperature=true;
  editor._hass.states[card.entity_id]={state:"on",attributes:{supported_color_modes:["color_temp","hs"],color_mode:"color_temp",min_color_temp_kelvin:2000,max_color_temp_kelvin:6500,color_temp_kelvin:2700,brightness:127}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"light",available:true,state:"on",light_color_temperature:{domain:{schema:"numeric_steps_v1",min:"2000",max:"6500",step:"1",unit:"K",max_index:4500},index:700},actions:[{service:"light.turn_on",fields:{color_temp_kelvin:{type:"number",min:2000,max:6500,step:1,required:false},brightness_pct:{type:"number",min:0,max:100,required:false}}}]});
  editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);return editor;
}

test("precise color temperature review states 1 K and preserves reversible draft and observed caption",()=>{
  const editor=kelvinEditor(),card=editor.cardAt(2),before=clone(editor._draft);
  assert.equal(editor.lightColorTemperatureAvailability(card).ready,true);assert.match(editor.inspectorMarkup(),/value="control-kelvin"/);
  assert.equal(editor.requestLightControl("kelvin"),true);assert.match(editor.modalMarkup(),/1 K/);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"number",property:"color_temp_kelvin"});assert.equal(editor.stateText(card),"2700 K");
  assert.match(editor.inspectorMarkup(),/Fine adjustment by 1 K/);assert.doesNotMatch(editor.inspectorMarkup(),/These settings define|They do not add a slider|Brightness unavailable/);
  assert.equal(editor.groupTargetCompatible(card,11),true);
  editor._hass.states[card.entity_id].attributes.color_temp_kelvin=2701;assert.equal(editor.stateText(card),"2701 K");
  editor._hass.locale.language="pl";assert.match(editor.inspectorMarkup(),/Precyzyjne dostrajanie co 1 K/);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).action.property,"color_temp_kelvin");
});

test("precise Kelvin rejects off or other mode and stale malformed metadata rather than inventing current state",()=>{
  for(const mutate of [e=>{e.profile.schema_light_color_temperature=false;},e=>{e._status.entity_control_status="offline";},e=>{e._hass.states["light.test"].state="off";},
    e=>{e._hass.states["light.test"].attributes.color_mode="hs";},e=>{e._hass.states["light.test"].attributes.color_temp_kelvin=null;},
    e=>{e._hass.states["light.test"].attributes.color_temp_kelvin=2700.5;},e=>{e._hass.states["light.test"].attributes.color_temp_kelvin="2700";},
    e=>{e._hass.states["light.test"].attributes.supported_color_modes=["brightness"];},e=>{e._hass.states["light.test"].attributes.min_color_temp_kelvin=2001;},
    e=>{e.entityFor("light.test").light_color_temperature.domain.step="100";},e=>{e.entityFor("light.test").actions[0].fields={};},
    e=>{e.entityFor("light.test").actions[0].fields.color_temp_kelvin.max=6000;}]){
    const editor=kelvinEditor();mutate(editor);assert.equal(editor.lightColorTemperatureAvailability().ready,false);assert.equal(editor.requestLightControl("kelvin"),false);
  }
  const editor=kelvinEditor();assert.equal(editor.requestLightControl("kelvin"),true);editor._hass.states["light.test"].attributes.color_mode="hs";assert.equal(editor.confirmLightControl(),false);
});

test("Kelvin draft recovery admits only explicit trusted v3 light property and keeps ordinary light scalar",()=>{
  const editor=kelvinEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"number",property:"color_temp_kelvin"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="climate.test";},r=>{r.layout.cards[1].action.data={};},r=>{r.layout.cards[1].action.property="color_temp";},r=>{r.layout.cards[1].type="sensor";}]){
    const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));
  }
  editor.profile.schema_light_color_temperature=false;assert.throws(()=>editor.validateStoredDraft(record()));
  const ordinary=lightEditor();assert.equal(ordinary.lightControlAvailability().ready,true);
});

test("saved light effects show only their own actionable hint",()=>{
  const editor=effectEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"choice",property:"effect"};
  assert.match(editor.inspectorMarkup(),/This starts the effect and can turn the light on/);
  assert.doesNotMatch(editor.inspectorMarkup(),/Brightness unavailable|They do not add a slider/);
});

function climateHumidityEditor() {
  const editor=numberEditor(),card=editor.cardAt(2);card.entity_id="climate.humidity_test";editor.profile.schema_climate_humidity=true;
  editor._hass.states[card.entity_id]={state:"auto",attributes:{supported_features:4,humidity:45,current_humidity:99,min_humidity:30,max_humidity:70,temperature:21.5}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"climate",available:true,state:"auto",climate_humidity:{domain:{schema:"numeric_steps_v1",min:"30",max:"70",step:"1",unit:"%",max_index:40},index:15},actions:[{service:"climate.set_humidity",fields:{humidity:{type:"number",min:30,max:70,step:1,required:true}}}]});
  editor._selectedSlot=2;editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);return editor;
}

test("climate target humidity is explicitly reviewed and independent of measured humidity and HVAC mode",()=>{
  const editor=climateHumidityEditor(),card=editor.cardAt(2),before=clone(editor._draft);
  assert.equal(editor.climateHumidityAvailability(card).ready,true);assert.match(editor.inspectorMarkup(),/value="control-climatehumidity"/);
  assert.equal(editor.requestLightControl("climatehumidity"),true);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"number",property:"humidity"});assert.equal(editor.stateText(card),"Target 45 %");
  assert.match(editor.inspectorMarkup(),/HVAC mode and target temperature have separate controls/);assert.doesNotMatch(editor.inspectorMarkup(),/They do not add a slider|Use one supported target temperature/);
  for(const mode of ["off","heat","heat_cool","auto","dry"]){editor._hass.states[card.entity_id].state=mode;assert.equal(editor.stateText(card),"Target 45 %");}
  assert.equal(editor.groupTargetCompatible(card,11),true);editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"Cel 45 %");
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).action.property,"humidity");
});

test("climate humidity rejects missing feature, target, service or exact domain metadata",()=>{
  for(const mutate of [e=>{e.profile.schema_climate_humidity=false;},e=>{e._status.entity_control_status="offline";},e=>{e._hass.states["climate.humidity_test"].state="unavailable";},
    e=>{e._hass.states["climate.humidity_test"].attributes.supported_features=1;},e=>{e._hass.states["climate.humidity_test"].attributes.humidity=null;},
    e=>{e._hass.states["climate.humidity_test"].attributes.humidity="45";},e=>{e._hass.states["climate.humidity_test"].attributes.min_humidity=30.5;},
    e=>{e._hass.states["climate.humidity_test"].attributes.target_humidity_step=null;},e=>{e.entityFor("climate.humidity_test").actions=[];},
    e=>{e.entityFor("climate.humidity_test").actions[0].fields.humidity.max=71;}]){
    const editor=climateHumidityEditor();mutate(editor);assert.equal(editor.climateHumidityAvailability().ready,false);assert.equal(editor.requestLightControl("climatehumidity"),false);
  }
  const editor=climateHumidityEditor();assert.equal(editor.requestLightControl("climatehumidity"),true);editor._hass.states["climate.humidity_test"].attributes.max_humidity=71;assert.equal(editor.confirmLightControl(),false);
});

test("climate humidity recovery needs its own schema and leaves humidifier admission separate",()=>{
  const editor=climateHumidityEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"number",property:"humidity"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="fan.test";},r=>{r.layout.cards[1].action.data={};},r=>{r.layout.cards[1].action.control="choice";},r=>{r.layout.cards[1].type="sensor";}]){
    const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));
  }
  editor.profile.schema_climate_humidity=false;assert.throws(()=>editor.validateStoredDraft(record()));
  assert.equal(humidityEditor().humidifierHumidityAvailability().ready,true);
});

function humidityEditor() {
  const editor=numberEditor(),card=editor.cardAt(2);card.entity_id="humidifier.test";
  editor.profile.schema_humidifier_humidity=true;
  editor._hass.states[card.entity_id]={state:"off",attributes:{min_humidity:30,max_humidity:70,humidity:45,current_humidity:99,mode:"eco",supported_features:0}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"humidifier",available:true,
    actions:[{service:"humidifier.set_humidity",fields:{humidity:{type:"number",min:30,max:70,step:1}}}],
    humidifier_humidity:{domain:{schema:"numeric_steps_v1",min:"30",max:"70",step:"1",unit:"%",max_index:40},index:15}});
  editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);return editor;
}

test("humidity target is explicitly reviewed, localized and undoable without using measurement or changing power/mode",()=>{
  const editor=humidityEditor(),card=editor.cardAt(2),before=clone(editor._draft);
  assert.equal(editor.humidifierHumidityAvailability(card).ready,true);assert.match(editor.inspectorMarkup(),/value="control-humidity"/);
  assert.equal(editor.requestLightControl("humidity"),true);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"number",property:"humidity"});assert.equal(editor.stateText(card),"Target 45 %");
  assert.equal(editor.groupTargetCompatible(card,11),true);assert.match(editor.inspectorMarkup(),/value="control-humidity" selected/);
  assert.doesNotMatch(editor.inspectorMarkup(),/These settings define|do not add a slider/);
  editor._hass.states[card.entity_id].attributes.humidity=50;assert.equal(editor.stateText(card),"Target 50 %");
  editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"Cel 50 %");
  assert.equal(editor._hass.states[card.entity_id].state,"off");assert.equal(editor._hass.states[card.entity_id].attributes.mode,"eco");
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).action.property,"humidity");
});

test("humidity domain is exact and integer and rejects missing data, fractions, unknown targets and stale reviewed ranges",()=>{
  for(const mutate of [e=>{e.profile.schema_humidifier_humidity=false;},e=>{e._status.entity_control_status="offline";},e=>{e._hass.states["humidifier.test"].state="unavailable";},
    e=>{e._hass.states["humidifier.test"].attributes.humidity=null;},e=>{e._hass.states["humidifier.test"].attributes.humidity="45";},
    e=>{e._hass.states["humidifier.test"].attributes.min_humidity=30.5;},e=>{delete e._hass.states["humidifier.test"].attributes.max_humidity;},
    e=>{e._hass.states["humidifier.test"].attributes.target_humidity_step=null;},e=>{e._hass.states["humidifier.test"].attributes.target_humidity_step=.5;},
    e=>{e.entityFor("humidifier.test").humidifier_humidity.domain.unit="°C";},e=>{e.entityFor("humidifier.test").actions=[];}]){
    const editor=humidityEditor();mutate(editor);assert.equal(editor.humidifierHumidityAvailability().ready,false);assert.equal(editor.requestLightControl("humidity"),false);
  }
  const editor=humidityEditor();assert.equal(editor.requestLightControl("humidity"),true);
  editor._hass.states["humidifier.test"].attributes.max_humidity=65;assert.equal(editor.confirmLightControl(),false);
});

test("humidity step honors the actual lattice and does not invent a fractional last step",()=>{
  const editor=humidityEditor(),state=editor._hass.states["humidifier.test"],d=editor.entityFor("humidifier.test").humidifier_humidity.domain;
  state.attributes.target_humidity_step=5;state.attributes.max_humidity=71;d.step="5";d.max="71";d.max_index=8;
  assert.equal(editor.humidifierHumidityAvailability().ready,true);
  state.attributes.humidity=71;assert.equal(editor.humidifierHumidityAvailability().ready,false);
  state.attributes.humidity=70;assert.equal(editor.humidifierHumidityAvailability().ready,true);
  state.attributes.min_humidity=0;state.attributes.max_humidity=100;d.min="0";d.max="100";d.max_index=20;
  for(const value of [0,100]){state.attributes.humidity=value;assert.equal(editor.observedHumidity(editor.cardAt(2)).value,value);}
});

test("humidity property survives reviewed draft recovery while hybrids and other domains are rejected",()=>{
  const editor=humidityEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"number",property:"humidity"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  const fixed=record();fixed.layout.cards[1].action={kind:"service",service:"humidifier.set_humidity",data:{humidity:45}};assert.doesNotThrow(()=>editor.validateStoredDraft(fixed));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="climate.test";},r=>{r.layout.cards[1].action.data={humidity:45};},
    r=>{r.layout.cards[1].action.property="current_humidity";},r=>{r.layout.cards[1].type="sensor";}]){
    const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));
  }
  editor.profile.schema_humidifier_humidity=false;assert.throws(()=>editor.validateStoredDraft(record()));
});

function temperatureEditor() {
  const editor=numberEditor(),card=editor.cardAt(2);card.entity_id="climate.test";
  editor.profile.schema_climate_temperature=true;editor._hass.config={unit_system:{temperature:"°C"}};
  editor._hass.states[card.entity_id]={state:"off",attributes:{supported_features:1,min_temp:16,max_temp:30,target_temp_step:.5,temperature:21.5,current_temperature:99}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"climate",available:true,actions:[{service:"climate.set_temperature",fields:{temperature:{type:"number",min:16,max:30,step:.5}}}],
    climate_temperature:{domain:{schema:"numeric_steps_v1",min:"16",max:"30",step:"0.5",unit:"°C",max_index:28},index:11}});
  return editor;
}

test("temperature conversion reviews one target, preserves Undo and shows live target rather than measured heat",()=>{
  const editor=temperatureEditor(),card=editor.cardAt(2);editor._saved.cards=clone(editor._draft.cards);const before=clone(editor._draft);
  assert.equal(editor.climateTemperatureAvailability(card).ready,true);assert.match(editor.inspectorMarkup(),/value="control-temperature"/);
  assert.equal(editor.requestLightControl("temperature"),true);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"number",property:"temperature"});assert.equal(editor.stateText(card),"Target 21.5 °C");
  assert.match(editor.inspectorMarkup(),/value="control-temperature" selected/);assert.equal(editor.groupTargetCompatible(card,11),true);
  editor._hass.states[card.entity_id].attributes.temperature=22;assert.equal(editor.stateText(card),"Target 22 °C");assert.equal(editor.climateTemperatureAvailability(card).ready,true);
  editor._hass.locale.language="pl";editor._hass.states[card.entity_id].attributes.temperature=21.5;assert.equal(editor.stateText(card),"Cel 21,5 °C");
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).action.property,"temperature");
});

test("temperature rejects unknown/off-grid/range-only/auto/unit mismatch and stale reviewed domains",()=>{
  for(const mutate of [e=>{e.profile.schema_climate_temperature=false;},e=>{e._status.entity_control_status="offline";},
      e=>{e._hass.states[e.cardAt(2).entity_id].state="auto";},e=>{e._hass.states[e.cardAt(2).entity_id].state="heat_cool";},
      e=>{e._hass.states[e.cardAt(2).entity_id].attributes.supported_features=3;},e=>{e._hass.states[e.cardAt(2).entity_id].attributes.temperature=null;},
      e=>{e._hass.states[e.cardAt(2).entity_id].attributes.temperature=21.3;},e=>{e._hass.config.unit_system.temperature="°F";},
      e=>{delete e._hass.states[e.cardAt(2).entity_id].attributes.target_temp_step;},e=>{e.entityFor(e.cardAt(2).entity_id).actions=[];}]) {
    const editor=temperatureEditor();mutate(editor);assert.equal(editor.climateTemperatureAvailability().ready,false);assert.equal(editor.requestLightControl("temperature"),false);
  }
  const editor=temperatureEditor();assert.equal(editor.requestLightControl("temperature"),true);editor._hass.states[editor.cardAt(2).entity_id].attributes.target_temp_step=.25;
  assert.equal(editor.confirmLightControl(),false);assert.notEqual(editor.cardAt(2).action.property,"temperature");
});

test("negotiated thermostat is selectable for a climate without a writable step",()=>{
  const editor=temperatureEditor(),card=editor.cardAt(2);
  delete editor._hass.states[card.entity_id].attributes.target_temp_step;
  editor._status.thermostat_version=1;
  assert.equal(editor.climateTemperatureAvailability(card).caps.readOnly,true);
  assert.equal(editor.requestLightControl("temperature"),true);
  assert.equal(editor.confirmLightControl(),true);
  assert.match(editor.inspectorMarkup(),/view-only mode/);
  editor._status.thermostat_version=0;
  assert.equal(editor.climateTemperatureAvailability(card).ready,false);
});

test("temperature explicit property survives v3 recovery while hybrid imports and wrong domains are refused",()=>{
  const editor=temperatureEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"number",property:"temperature"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="number.test";},r=>{r.layout.cards[1].action.data={};},r=>{r.layout.cards[1].action.property="humidity";},r=>{r.layout.cards[1].type="sensor";}]) {
    const r=record();mutate(r);assert.throws(()=>editor.validateStoredDraft(r));
  }
  editor.profile.schema_climate_temperature=false;assert.throws(()=>editor.validateStoredDraft(record()));
});

function hvacEditor() {
  const editor=temperatureEditor(),card=editor.cardAt(2),options=["off","heat","cool","auto"];
  editor.profile.schema_climate_hvac_mode=true;editor.profile.schema_control_types.push("choice");editor._status.control_kinds.push("choice");
  editor._hass.states[card.entity_id].attributes.hvac_modes=[...options];
  editor.entityFor(card.entity_id).climate_hvac_mode={options:[...options],index:0};
  editor.entityFor(card.entity_id).actions.push({service:"climate.set_hvac_mode",fields:{hvac_mode:{type:"select",options:[...options],required:true}}});
  return editor;
}

test("operating mode selection is explicitly reviewed, localized and undoable separately from temperature",()=>{
  const editor=hvacEditor(),card=editor.cardAt(2);editor._saved.cards=clone(editor._draft.cards);const before=clone(editor._draft);
  assert.equal(editor.climateHVACAvailability(card).ready,true);assert.equal(editor.climateTemperatureAvailability(card).ready,true);
  assert.match(editor.inspectorMarkup(),/value="control-hvac"/);assert.equal(editor.requestLightControl("hvac"),true);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"choice",property:"hvac_mode"});assert.equal(editor.stateText(card),"Off");
  assert.match(editor.inspectorMarkup(),/value="control-hvac" selected/);assert.equal(editor.groupTargetCompatible(card,11),true);
  editor._hass.states[card.entity_id].state="heat";assert.equal(editor.stateText(card),"Heating");assert.equal(editor.climateHVACAvailability(card).ready,true);
  editor._hass.formatEntityState=()=>"HA heat";assert.equal(editor.stateText(card),"HA heat");delete editor._hass.formatEntityState;
  editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"Ogrzewanie");assert.equal(editor._hass.states[card.entity_id].attributes.temperature,21.5);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).action.property,"hvac_mode");
});

test("operating mode admission rejects stale catalogues, unknown modes, outage and lost service",()=>{
  for(const mutate of [e=>{e.profile.schema_climate_hvac_mode=false;},e=>{e._status.entity_control_status="offline";},
      e=>{e._hass.states[e.cardAt(2).entity_id].state="unavailable";},e=>{e._hass.states[e.cardAt(2).entity_id].state="away";},
      e=>{e._hass.states[e.cardAt(2).entity_id].attributes.hvac_modes=[];},e=>{e.entityFor(e.cardAt(2).entity_id).climate_hvac_mode.options.reverse();},
      e=>{e.entityFor(e.cardAt(2).entity_id).actions=e.entityFor(e.cardAt(2).entity_id).actions.filter(a=>a.service!=="climate.set_hvac_mode");}]) {
    const editor=hvacEditor();mutate(editor);assert.equal(editor.climateHVACAvailability().ready,false);assert.equal(editor.requestLightControl("hvac"),false);
  }
  const editor=hvacEditor();assert.equal(editor.requestLightControl("hvac"),true);editor._hass.states[editor.cardAt(2).entity_id].attributes.hvac_modes.reverse();
  assert.equal(editor.confirmLightControl(),false);assert.notEqual(editor.cardAt(2).action.property,"hvac_mode");
});

test("operating mode property requires its explicit trusted v3 climate schema in recovered or imported drafts",()=>{
  const editor=hvacEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"choice",property:"hvac_mode"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="fan.test";},r=>{r.layout.cards[1].action.data={};},r=>{r.layout.cards[1].action.property="fan_mode";},r=>{r.layout.cards[1].type="sensor";}]) {
    const r=record();mutate(r);assert.throws(()=>editor.validateStoredDraft(r));
  }
  editor.profile.schema_climate_hvac_mode=false;assert.throws(()=>editor.validateStoredDraft(record()));
});

function climatePresetEditor() {
  const editor=hvacEditor(),card=editor.cardAt(2),options=["none","eco","comfort","sleep"];
  editor.profile.schema_climate_preset_mode=true;
  Object.assign(editor._hass.states[card.entity_id].attributes,{supported_features:17,preset_modes:[...options],preset_mode:"none"});
  editor.entityFor(card.entity_id).climate_preset_mode={options:[...options],index:0};
  editor.entityFor(card.entity_id).actions.push({service:"climate.set_preset_mode",fields:{preset_mode:{type:"select",options:[...options],required:true}}});
  return editor;
}

test("climate program is reviewed and undoable separately from HVAC and uses live HA attribute translations",()=>{
  const editor=climatePresetEditor(),card=editor.cardAt(2);editor._saved.cards=clone(editor._draft.cards);const before=clone(editor._draft);
  assert.equal(editor.climatePresetAvailability(card).ready,true);assert.match(editor.inspectorMarkup(),/value="control-preset"/);
  assert.equal(editor.requestLightControl("preset"),true);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"choice",property:"preset_mode"});assert.equal(editor.stateText(card),"No program");
  assert.match(editor.inspectorMarkup(),/value="control-preset" selected/);assert.equal(editor.groupTargetCompatible(card,11),true);
  editor._hass.states[card.entity_id].attributes.preset_mode="comfort";assert.equal(editor.stateText(card),"Comfort");
  editor._hass.formatEntityAttributeValue=(state,attr)=>attr==="preset_mode"?"HA comfort":"bad";assert.equal(editor.stateText(card),"HA comfort");delete editor._hass.formatEntityAttributeValue;
  editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"Komfort");
  assert.equal(editor._hass.states[card.entity_id].state,"off");assert.equal(editor._hass.states[card.entity_id].attributes.temperature,21.5);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).action.property,"preset_mode");
});

test("climate program distinguishes literal none option from negotiated known-empty and refuses stale or invalid provider states",()=>{
  const editor=climatePresetEditor(),card=editor.cardAt(2),state=editor._hass.states[card.entity_id],meta=editor.entityFor(card.entity_id).climate_preset_mode;
  assert.equal(editor.observedClimatePreset(card).index,0);assert.equal(editor.observedClimatePreset(card).empty,false);
  state.attributes.preset_modes=["eco","comfort"];meta.options=["eco","comfort"];meta.index=null;meta.empty=true;
  for(const value of [null,"none"]){state.attributes.preset_mode=value;assert.equal(editor.climatePresetAvailability(card).ready,false);editor._status.empty_choice_version=1;assert.equal(editor.climatePresetAvailability(card).ready,true);delete editor._status.empty_choice_version;}
  for(const mutate of [e=>{e.profile.schema_climate_preset_mode=false;},e=>{e._status.entity_control_status="offline";},e=>{e._hass.states[e.cardAt(2).entity_id].state="unavailable";},
    e=>{e._hass.states[e.cardAt(2).entity_id].attributes.supported_features=1;},e=>{e._hass.states[e.cardAt(2).entity_id].attributes.preset_mode="absent";},
    e=>{delete e._hass.states[e.cardAt(2).entity_id].attributes.preset_mode;},e=>{e.entityFor(e.cardAt(2).entity_id).climate_preset_mode.options.reverse();},e=>{e.entityFor(e.cardAt(2).entity_id).actions=[];}]){
    const item=climatePresetEditor();mutate(item);assert.equal(item.climatePresetAvailability().ready,false);assert.equal(item.requestLightControl("preset"),false);
  }
  const stale=climatePresetEditor();assert.equal(stale.requestLightControl("preset"),true);stale._hass.states[stale.cardAt(2).entity_id].attributes.preset_modes.reverse();assert.equal(stale.confirmLightControl(),false);
});

test("climate program recovery accepts only explicit trusted v3 climate property without arbitrary service data",()=>{
  const editor=climatePresetEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"choice",property:"preset_mode"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="fan.test";},r=>{r.layout.cards[1].action.data={};},r=>{r.layout.cards[1].action.property="preset";},r=>{r.layout.cards[1].type="sensor";}]){
    const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));
  }
  editor.profile.schema_climate_preset_mode=false;assert.throws(()=>editor.validateStoredDraft(record()));
});

function climateFanEditor() {
  const editor=hvacEditor(),card=editor.cardAt(2),options=["auto","low","medium","high"];
  editor.profile.schema_climate_fan_mode=true;
  Object.assign(editor._hass.states[card.entity_id].attributes,{supported_features:9,fan_modes:[...options],fan_mode:"auto",preset_mode:"comfort"});
  editor.entityFor(card.entity_id).climate_fan_mode={options:[...options],index:0};
  editor.entityFor(card.entity_id).actions.push({service:"climate.set_fan_mode",fields:{fan_mode:{type:"select",options:[...options],required:true}}});
  return editor;
}

test("climate fan mode reviews exact choice separately from HVAC and preview follows live translated fan attribute",()=>{
  const editor=climateFanEditor(),card=editor.cardAt(2);editor._saved.cards=clone(editor._draft.cards);const before=clone(editor._draft);
  assert.equal(editor.climateFanAvailability(card).ready,true);assert.match(editor.inspectorMarkup(),/value="control-airflow"/);
  assert.equal(editor.requestLightControl("airflow"),true);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"choice",property:"fan_mode"});assert.equal(editor.stateText(card),"Automatic");
  assert.match(editor.inspectorMarkup(),/value="control-airflow" selected/);assert.doesNotMatch(editor.inspectorMarkup(),/These settings define|They do not add a slider/);assert.equal(editor.groupTargetCompatible(card,11),true);
  editor._hass.states[card.entity_id].attributes.fan_mode="medium";assert.equal(editor.stateText(card),"Medium");
  editor._hass.formatEntityAttributeValue=(state,attr)=>attr==="fan_mode"?"HA medium":"bad";assert.equal(editor.stateText(card),"HA medium");delete editor._hass.formatEntityAttributeValue;
  editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"Średni");
  assert.equal(editor._hass.states[card.entity_id].state,"off");assert.equal(editor._hass.states[card.entity_id].attributes.preset_mode,"comfort");assert.equal(editor._hass.states[card.entity_id].attributes.temperature,21.5);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).action.property,"fan_mode");
});

test("climate fan mode refuses unknown or null despite empty negotiation and rechecks exact list feature and service",()=>{
  for(const mutate of [e=>{e.profile.schema_climate_fan_mode=false;},e=>{e._status.entity_control_status="offline";},e=>{e._hass.states[e.cardAt(2).entity_id].state="unavailable";},
    e=>{e._hass.states[e.cardAt(2).entity_id].attributes.supported_features=1;},e=>{e._hass.states[e.cardAt(2).entity_id].attributes.fan_mode="absent";},
    e=>{e._hass.states[e.cardAt(2).entity_id].attributes.fan_mode=null;e._status.empty_choice_version=1;},e=>{delete e._hass.states[e.cardAt(2).entity_id].attributes.fan_mode;},
    e=>{e.entityFor(e.cardAt(2).entity_id).climate_fan_mode.options.reverse();},e=>{e.entityFor(e.cardAt(2).entity_id).actions=[];}]){
    const item=climateFanEditor();mutate(item);assert.equal(item.climateFanAvailability().ready,false);assert.equal(item.requestLightControl("airflow"),false);
  }
  const editor=climateFanEditor();assert.equal(editor.requestLightControl("airflow"),true);editor._hass.states[editor.cardAt(2).entity_id].attributes.fan_modes.reverse();assert.equal(editor.confirmLightControl(),false);
});

test("climate fan mode draft recovery admits only explicit trusted v3 climate property with no arbitrary payload",()=>{
  const editor=climateFanEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"choice",property:"fan_mode"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="fan.test";},r=>{r.layout.cards[1].action.data={};},r=>{r.layout.cards[1].action.property="fan_modes";},r=>{r.layout.cards[1].type="sensor";}]){
    const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));
  }
  editor.profile.schema_climate_fan_mode=false;assert.throws(()=>editor.validateStoredDraft(record()));
});

function climateSwingEditor() {
  const editor=hvacEditor(),card=editor.cardAt(2),options=["off","on","vertical","horizontal","both"];
  editor.profile.schema_climate_swing_mode=true;
  Object.assign(editor._hass.states[card.entity_id].attributes,{supported_features:33,swing_modes:[...options],swing_mode:"off",preset_mode:"comfort"});
  editor.entityFor(card.entity_id).climate_swing_mode={options:[...options],index:0};
  editor.entityFor(card.entity_id).actions.push({service:"climate.set_swing_mode",fields:{swing_mode:{type:"select",options:[...options],required:true}}});
  return editor;
}

test("climate swing mode reviews exact choice separately from HVAC and preview follows live translated swing attribute",()=>{
  const editor=climateSwingEditor(),card=editor.cardAt(2);editor._saved.cards=clone(editor._draft.cards);const before=clone(editor._draft);
  assert.equal(editor.climateSwingAvailability(card).ready,true);assert.match(editor.inspectorMarkup(),/value="control-swing"/);
  assert.equal(editor.requestLightControl("swing"),true);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"choice",property:"swing_mode"});assert.equal(editor.stateText(card),"Off");
  assert.match(editor.inspectorMarkup(),/value="control-swing" selected/);assert.equal(editor.groupTargetCompatible(card,11),true);assert.doesNotMatch(editor.inspectorMarkup(),/These settings define|They do not add a slider/);
  editor._hass.states[card.entity_id].attributes.swing_mode="vertical";assert.equal(editor.stateText(card),"Vertical");
  editor._hass.formatEntityAttributeValue=(state,attr)=>attr==="swing_mode"?"HA vertical":"bad";assert.equal(editor.stateText(card),"HA vertical");delete editor._hass.formatEntityAttributeValue;
  editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"Pionowo");
  assert.equal(editor._hass.states[card.entity_id].state,"off");assert.equal(editor._hass.states[card.entity_id].attributes.preset_mode,"comfort");assert.equal(editor._hass.states[card.entity_id].attributes.temperature,21.5);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).action.property,"swing_mode");
});

test("climate swing mode refuses unknown or null despite empty negotiation and rechecks exact list feature and service",()=>{
  for(const mutate of [e=>{e.profile.schema_climate_swing_mode=false;},e=>{e._status.entity_control_status="offline";},e=>{e._hass.states[e.cardAt(2).entity_id].state="unavailable";},
    e=>{e._hass.states[e.cardAt(2).entity_id].attributes.supported_features=512;},e=>{e._hass.states[e.cardAt(2).entity_id].attributes.swing_mode="absent";},
    e=>{e._hass.states[e.cardAt(2).entity_id].attributes.swing_mode=null;e._status.empty_choice_version=1;},e=>{delete e._hass.states[e.cardAt(2).entity_id].attributes.swing_mode;},
    e=>{e.entityFor(e.cardAt(2).entity_id).climate_swing_mode.options.reverse();},e=>{e.entityFor(e.cardAt(2).entity_id).actions=[];}]){
    const item=climateSwingEditor();mutate(item);assert.equal(item.climateSwingAvailability().ready,false);assert.equal(item.requestLightControl("swing"),false);
  }
  const editor=climateSwingEditor();assert.equal(editor.requestLightControl("swing"),true);editor._hass.states[editor.cardAt(2).entity_id].attributes.swing_modes.reverse();assert.equal(editor.confirmLightControl(),false);
});

test("climate swing mode draft recovery admits only explicit trusted v3 climate property with no arbitrary payload",()=>{
  const editor=climateSwingEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"choice",property:"swing_mode"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="fan.test";},r=>{r.layout.cards[1].action.data={};},r=>{r.layout.cards[1].action.property="swing_modes";},r=>{r.layout.cards[1].type="sensor";}]){
    const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));
  }
  editor.profile.schema_climate_swing_mode=false;assert.throws(()=>editor.validateStoredDraft(record()));
});

function climateHorizontalEditor() {
  const editor=hvacEditor(),card=editor.cardAt(2),options=["off","on","Prawy Żółty"];
  editor.profile.schema_climate_swing_horizontal_mode=true;
  Object.assign(editor._hass.states[card.entity_id].attributes,{supported_features:513,swing_horizontal_modes:[...options],swing_horizontal_mode:"off",preset_mode:"comfort"});
  editor.entityFor(card.entity_id).climate_swing_horizontal_mode={options:[...options],index:0};
  editor.entityFor(card.entity_id).actions.push({service:"climate.set_swing_horizontal_mode",fields:{swing_horizontal_mode:{type:"select",options:[...options],required:true}}});
  return editor;
}

test("climate horizontal movement reviews exact choice separately from HVAC and preview follows live translated horizontal attribute",()=>{
  const editor=climateHorizontalEditor(),card=editor.cardAt(2);editor._saved.cards=clone(editor._draft.cards);const before=clone(editor._draft);
  assert.equal(editor.climateHorizontalAvailability(card).ready,true);assert.match(editor.inspectorMarkup(),/value="control-horizontal"/);
  assert.equal(editor.requestLightControl("horizontal"),true);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"choice",property:"swing_horizontal_mode"});assert.equal(editor.stateText(card),"Off");
  assert.match(editor.inspectorMarkup(),/value="control-horizontal" selected/);assert.equal(editor.groupTargetCompatible(card,11),true);assert.doesNotMatch(editor.inspectorMarkup(),/These settings define|They do not add a slider/);
  editor._hass.states[card.entity_id].attributes.swing_horizontal_mode="Prawy Żółty";assert.equal(editor.stateText(card),"Prawy Żółty");
  editor._hass.formatEntityAttributeValue=(state,attr)=>attr==="swing_horizontal_mode"?"HA exact horizontal":"bad";assert.equal(editor.stateText(card),"HA exact horizontal");delete editor._hass.formatEntityAttributeValue;
  editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"Prawy Żółty");
  assert.equal(editor._hass.states[card.entity_id].state,"off");assert.equal(editor._hass.states[card.entity_id].attributes.preset_mode,"comfort");assert.equal(editor._hass.states[card.entity_id].attributes.temperature,21.5);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).action.property,"swing_horizontal_mode");
});

test("climate horizontal movement refuses unknown or null despite empty negotiation and rechecks exact list feature and service",()=>{
  for(const mutate of [e=>{e.profile.schema_climate_swing_horizontal_mode=false;},e=>{e._status.entity_control_status="offline";},e=>{e._hass.states[e.cardAt(2).entity_id].state="unavailable";},
    e=>{e._hass.states[e.cardAt(2).entity_id].attributes.supported_features=32;},e=>{e._hass.states[e.cardAt(2).entity_id].attributes.swing_horizontal_mode="absent";},
    e=>{e._hass.states[e.cardAt(2).entity_id].attributes.swing_horizontal_mode=null;e._status.empty_choice_version=1;},e=>{delete e._hass.states[e.cardAt(2).entity_id].attributes.swing_horizontal_mode;},
    e=>{e.entityFor(e.cardAt(2).entity_id).climate_swing_horizontal_mode.options.reverse();},e=>{e.entityFor(e.cardAt(2).entity_id).actions=[];}]){
    const item=climateHorizontalEditor();mutate(item);assert.equal(item.climateHorizontalAvailability().ready,false);assert.equal(item.requestLightControl("horizontal"),false);
  }
  const editor=climateHorizontalEditor();assert.equal(editor.requestLightControl("horizontal"),true);editor._hass.states[editor.cardAt(2).entity_id].attributes.swing_horizontal_modes.reverse();assert.equal(editor.confirmLightControl(),false);
});

test("climate horizontal movement draft recovery admits only explicit trusted v3 climate property with no arbitrary payload",()=>{
  const editor=climateHorizontalEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"choice",property:"swing_horizontal_mode"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="fan.test";},r=>{r.layout.cards[1].action.data={};},r=>{r.layout.cards[1].action.property="swing_horizontal_modes";},r=>{r.layout.cards[1].type="sensor";}]){
    const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));
  }
  editor.profile.schema_climate_swing_horizontal_mode=false;assert.throws(()=>editor.validateStoredDraft(record()));
});

function humidifierEditor() {
  const editor=makeEditor();editor.profile.schema_humidifier_power=true;
  editor._data.icons.push("climate");editor._selectedSlot=11;
  editor._status={device_available:true,context_press_version:1,press_enabled_version:1};
  editor._hass.states["humidifier.test"]={state:"off",attributes:{supported_features:0,device_class:"humidifier",humidity:45,mode:"sleep"}};
  editor._entityIndex.set("humidifier.test",{entity_id:"humidifier.test",domain:"humidifier",name:"Humidifier",available:true,state:"off",actions:["turn_on","turn_off","toggle"].map(operation=>({service:`humidifier.${operation}`,fields:{}}))});
  return editor;
}

test("humidifier assignment creates a reversible ordinary power card without preview commands",()=>{
  const editor=humidifierEditor();assert.equal(editor.assignEntity("humidifier.test",11),true);const item=editor.cardAt(11),id=item.id;
  assert.equal(item.type,"entity");assert.equal(item.icon,"climate");assert.deepEqual(clone(item.action),{kind:"default"});assert.equal(editor.humidifierPowerReady(item),true);
  assert.match(editor.inspectorMarkup(),/switch the humidifier or dehumidifier on or off/);assert.doesNotMatch(editor.inspectorMarkup(),/These settings define/);
  editor.history("undo");assert.equal(editor.cardAt(11),undefined);editor.history("redo");assert.equal(editor.cardAt(11).id,id);
  editor._hass.locale.language="pl";assert.match(editor.inspectorMarkup(),/włącza lub wyłącza nawilżacz albo osuszacz/);
});

test("humidifier preview follows observed power and HA translation with opt-in palette for both device classes",()=>{
  const editor=humidifierEditor();editor.assignEntity("humidifier.test",11);const item=editor.cardAt(11),state=editor._hass.states[item.entity_id];item.state_color=true;
  for(const deviceClass of ["humidifier","dehumidifier"]){state.attributes.device_class=deviceClass;
    for(const power of ["on","off"]){state.state=power;assert.equal(editor.stateText(item),power==="on"?"On":"Off");assert.equal(editor.effectivePalette(item),power==="on"?"primary":"surface");editor._hass.locale.language="pl";assert.equal(editor.stateText(item),power==="on"?"Włączony":"Wyłączony");editor._hass.locale.language="en";}
  }
  editor._hass.formatEntityState=()=>"HA exact";assert.equal(editor.stateText(item),"HA exact");delete editor._hass.formatEntityState;
  state.state="unavailable";assert.equal(editor.humidifierPowerReady(item),false);assert.equal(editor.effectivePalette(item),"surface");
});

test("humidifier draft recovery keeps explicit power while readiness rejects old peer, unknown state or lost opposite service",()=>{
  const editor=humidifierEditor();editor.assignEntity("humidifier.test",11);const item=editor.cardAt(11);item.state_color=true;
  const record={version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:2,profile:editor.profile.id,cards:clone(editor._draft.cards)}};
  assert.doesNotThrow(()=>editor.validateStoredDraft(record));
  for(const mutate of [e=>{e.profile.schema_humidifier_power=false;},e=>{e._status.device_available=false;},e=>{e._status.context_press_version=0;},e=>{e._status.press_enabled_version=0;},e=>{e._hass.states["humidifier.test"].state="humidifying";},e=>{e._entityIndex.get("humidifier.test").actions=[];}]){
    const testEditor=humidifierEditor();testEditor.assignEntity("humidifier.test",11);mutate(testEditor);assert.equal(testEditor.humidifierPowerReady(testEditor.cardAt(11)),false);
  }
  const invalid=clone(record);invalid.layout.cards.find(c=>c.slot===11).action={kind:"service",service:"humidifier.turn_on",data:{humidity:45}};assert.throws(()=>editor.validateStoredDraft(invalid));
});

function humidifierModeEditor() {
  const editor=choiceEditor(),card=editor.cardAt(2),options=["normal","sleep"," Żółty "];
  editor._selectedSlot=2;editor.profile.schema_humidifier_mode=true;card.entity_id="humidifier.test";
  editor._hass.states[card.entity_id]={state:"off",attributes:{supported_features:1,available_modes:[...options],mode:"normal",humidity:45}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"humidifier",available:true,state:"off",humidifier_mode:{options:[...options],index:0},actions:[{service:"humidifier.set_mode",fields:{mode:{type:"select",options:[...options],required:true}}}]});
  editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);return editor;
}

function vacuumPowerEditor() {
  const editor=choiceEditor(),card=editor.cardAt(2),options=["quiet","normal"," Żółty "];
  editor._selectedSlot=2;editor.profile.schema_vacuum_fan_speed=true;card.entity_id="vacuum.test";
  editor._hass.states[card.entity_id]={state:"docked",attributes:{supported_features:32,fan_speed_list:[...options],fan_speed:"quiet"}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"vacuum",available:true,state:"docked",vacuum_fan_speed:{options:[...options],index:0},actions:[{service:"vacuum.set_fan_speed",fields:{fan_speed:{type:"select",options:[...options],required:true}}}]});
  editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);return editor;
}

function coverPositionEditor() {
  const editor=choiceEditor(),card=editor.cardAt(2),domain={schema:"numeric_steps_v1",min:"0",max:"100",step:"1",unit:"%",max_index:100};
  editor._selectedSlot=2;editor.profile.schema_cover_position=true;card.entity_id="cover.test";
  editor._status.control_kinds.push("number");
  editor._hass.states[card.entity_id]={state:"open",attributes:{supported_features:4,current_position:45,current_tilt_position:99}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"cover",available:true,state:"open",cover_position:{domain,index:45},actions:[{service:"cover.set_cover_position",fields:{position:{type:"number",min:0,max:100,step:1,required:true}}}]});
  editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);return editor;
}

test("cover opening is explicitly reviewed and reversible with an observed percentage and separate Stop hint",()=>{
  const editor=coverPositionEditor(),card=editor.cardAt(2),before=clone(editor._draft);
  assert.equal(editor.coverPositionAvailability().ready,true);assert.match(editor.inspectorMarkup(),/value="control-coverposition"/);
  assert.equal(editor.requestLightControl("coverposition"),true);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"number",property:"position"});assert.equal(editor.groupTargetCompatible(card,11),true);
  for(const status of ["open","closed","opening","closing"]){editor._hass.states[card.entity_id].state=status;assert.equal(editor.stateText(card),"Opening 45 %");}
  editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"Otwarcie 45 %");assert.match(editor.inspectorMarkup(),/Zamknięcie tego ekranu nie zatrzymuje ruchu/);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).action.property,"position");
});

test("cover opening requires an exact known integer position, current feature and service, without tilt or state inference",()=>{
  for(const mutate of [e=>{e.profile.schema_cover_position=false;},e=>{e._status.entity_control_status="offline";},e=>{e._hass.states["cover.test"].state="unknown";},
    e=>{e._hass.states["cover.test"].attributes.supported_features=0;},e=>{e._hass.states["cover.test"].attributes.current_position=null;},
    e=>{delete e._hass.states["cover.test"].attributes.current_position;},e=>{e._hass.states["cover.test"].attributes.current_position=45.5;},e=>{e.entityFor("cover.test").actions=[];}]){
    const editor=coverPositionEditor();mutate(editor);assert.equal(editor.coverPositionAvailability().ready,false);assert.equal(editor.requestLightControl("coverposition"),false);
  }
  const editor=coverPositionEditor();assert.equal(editor.requestLightControl("coverposition"),true);editor._hass.states["cover.test"].attributes.supported_features=0;assert.equal(editor.confirmLightControl(),false);
});

test("cover opening recovery is exact v3 and preserves raw integer service semantics",()=>{
  const editor=coverPositionEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"number",property:"position"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  const fixed=record();fixed.layout.cards[1].action={kind:"service",service:"cover.set_cover_position",data:{position:46}};assert.doesNotThrow(()=>editor.validateStoredDraft(fixed));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="number.test";},r=>{r.layout.cards[1].action.data={position:46};},r=>{r.layout.cards[1].action.property="current_position";}]){
    const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));
  }
  editor.profile.schema_cover_position=false;assert.throws(()=>editor.validateStoredDraft(record()));
});

test("vacuum suction has explicit review, reversible draft and translated observed level independent of activity",()=>{
  const editor=vacuumPowerEditor(),card=editor.cardAt(2),before=clone(editor._draft);
  assert.equal(editor.vacuumPowerAvailability().ready,true);assert.match(editor.inspectorMarkup(),/value="control-vacuumfan"/);
  assert.equal(editor.requestLightControl("vacuumfan"),true);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"choice",property:"fan_speed"});assert.equal(editor.groupTargetCompatible(card,11),true);
  for(const activity of ["docked","cleaning","paused","returning","idle","error"]){editor._hass.states[card.entity_id].state=activity;assert.equal(editor.stateText(card),"Quiet");}
  editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"Cicha");assert.match(editor.inspectorMarkup(),/Rozpoczęcie sprzątania i powrót do bazy są osobnymi akcjami/);
  editor._hass.formatEntityAttributeValue=(state,attribute)=>attribute==="fan_speed"?"HA moc":"bad";assert.equal(editor.stateText(card),"HA moc");
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).action.property,"fan_speed");
});

test("vacuum suction refuses unknown value, old peer, reordered list and feature loss without pretending manual mode",()=>{
  for(const mutate of [e=>{e.profile.schema_vacuum_fan_speed=false;},e=>{e._status.entity_control_status="offline";},e=>{e._hass.states["vacuum.test"].state="unknown";},
    e=>{e._hass.states["vacuum.test"].attributes.supported_features=0;},e=>{e._hass.states["vacuum.test"].attributes.fan_speed=null;e._status.empty_choice_version=1;},
    e=>{e._hass.states["vacuum.test"].attributes.fan_speed=0;},e=>{e._hass.states["vacuum.test"].attributes.fan_speed="other";},e=>{e.entityFor("vacuum.test").actions=[];}]){
    const editor=vacuumPowerEditor();mutate(editor);assert.equal(editor.vacuumPowerAvailability().ready,false);assert.equal(editor.requestLightControl("vacuumfan"),false);
  }
  const editor=vacuumPowerEditor();assert.equal(editor.requestLightControl("vacuumfan"),true);editor._hass.states["vacuum.test"].attributes.fan_speed_list.reverse();assert.equal(editor.confirmLightControl(),false);
});

test("vacuum recovery only admits the exact v3 facet or exact fixed service and raw names survive translation collisions",()=>{
  const editor=vacuumPowerEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"choice",property:"fan_speed"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  const fixed=record();fixed.layout.cards[1].action={kind:"service",service:"vacuum.set_fan_speed",data:{fan_speed:" Żółty "}};assert.doesNotThrow(()=>editor.validateStoredDraft(fixed));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="fan.test";},r=>{r.layout.cards[1].action.data={fan_speed:"normal"};},r=>{r.layout.cards[1].action.property="fan_speed_list";}]){
    const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));
  }
  editor._hass.locale.language="pl";assert.equal(editor.vacuumPowerLabel("quiet",["quiet","silent"]),"quiet");
  editor.profile.schema_vacuum_fan_speed=false;assert.throws(()=>editor.validateStoredDraft(record()));
});

test("humidifier mode is explicitly reviewed and undoable and its live caption takes precedence over power",()=>{
  const editor=humidifierModeEditor(),card=editor.cardAt(2),before=clone(editor._draft);
  assert.equal(editor.humidifierModeAvailability(card).ready,true);assert.match(editor.inspectorMarkup(),/value="control-humidifier"/);
  assert.equal(editor.requestLightControl("humidifier"),true);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"choice",property:"mode"});assert.equal(editor.stateText(card),"Normal");
  assert.equal(editor.groupTargetCompatible(card,11),true);assert.match(editor.inspectorMarkup(),/value="control-humidifier" selected/);
  editor._hass.states[card.entity_id].attributes.mode="sleep";assert.equal(editor.stateText(card),"Sleep");
  editor._hass.formatEntityAttributeValue=(state,attribute)=>attribute==="mode"?"HA program":"bad";assert.equal(editor.stateText(card),"HA program");delete editor._hass.formatEntityAttributeValue;
  editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"Sen");assert.equal(editor._hass.states[card.entity_id].state,"off");assert.equal(editor._hass.states[card.entity_id].attributes.humidity,45);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).action.property,"mode");
});

test("humidifier mode refuses sticky feature with missing or empty list and never treats null as manual",()=>{
  for(const mutate of [e=>{e.profile.schema_humidifier_mode=false;},e=>{e._status.entity_control_status="offline";},e=>{e._hass.states["humidifier.test"].state="unavailable";},
    e=>{e._hass.states["humidifier.test"].attributes.supported_features=0;},e=>{e._hass.states["humidifier.test"].attributes.available_modes=[];e.entityFor("humidifier.test").humidifier_mode.options=[];},
    e=>{e._hass.states["humidifier.test"].attributes.available_modes=null;},e=>{e._hass.states["humidifier.test"].attributes.mode=null;e._status.empty_choice_version=1;},
    e=>{e._hass.states["humidifier.test"].attributes.mode="other";},e=>{e.entityFor("humidifier.test").actions=[];}]){
    const editor=humidifierModeEditor();mutate(editor);assert.equal(editor.humidifierModeAvailability().ready,false);assert.equal(editor.requestLightControl("humidifier"),false);
  }
  const editor=humidifierModeEditor();assert.equal(editor.requestLightControl("humidifier"),true);editor._hass.states["humidifier.test"].attributes.available_modes.reverse();assert.equal(editor.confirmLightControl(),false);
});

test("humidifier mode recovery and fixed-service mode field are explicit without allowing hybrid or wrong-domain controls",()=>{
  const editor=humidifierModeEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"choice",property:"mode"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  const fixed=record();fixed.layout.cards[1].action={kind:"service",service:"humidifier.set_mode",data:{mode:"sleep"}};assert.doesNotThrow(()=>editor.validateStoredDraft(fixed));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="climate.test";},r=>{r.layout.cards[1].action.data={mode:"sleep"};},r=>{r.layout.cards[1].action.property="available_modes";},r=>{r.layout.cards[1].type="sensor";}]){
    const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));
  }
  editor.profile.schema_humidifier_mode=false;assert.throws(()=>editor.validateStoredDraft(record()));
});

function coverTiltEditor() {
  const editor=choiceEditor(),card=editor.cardAt(2),domain={schema:"numeric_steps_v1",min:"0",max:"100",step:"1",unit:"%",max_index:100};
  editor._selectedSlot=2;editor.profile.schema_cover_tilt=true;card.entity_id="cover.test";
  editor._status.control_kinds.push("number");
  editor._hass.states[card.entity_id]={state:"open",attributes:{supported_features:128,current_tilt_position:45,current_position:99}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"cover",available:true,state:"open",cover_tilt:{domain,index:45},actions:[{service:"cover.set_cover_tilt_position",fields:{tilt_position:{type:"number",min:0,max:100,step:1,required:true}}}]});
  editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);return editor;
}

test("slat tilt is explicitly reviewed and reversible with an observed percentage and separate Stop hint",()=>{
  const editor=coverTiltEditor(),card=editor.cardAt(2),before=clone(editor._draft);
  assert.equal(editor.coverTiltAvailability().ready,true);assert.match(editor.inspectorMarkup(),/value="control-covertilt"/);
  assert.equal(editor.requestLightControl("covertilt"),true);assert.equal(editor.confirmLightControl(),true);
  assert.deepEqual(clone(card.action),{kind:"control",control:"number",property:"tilt_position"});assert.equal(editor.groupTargetCompatible(card,11),true);
  for(const status of ["open","closed","opening","closing"]){editor._hass.states[card.entity_id].state=status;assert.equal(editor.stateText(card),"Tilt 45 %");}
  editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"Pochylenie 45 %");assert.match(editor.inspectorMarkup(),/Zamknięcie tego ekranu nie zatrzymuje ruchu/);
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(2).action.property,"tilt_position");
});

test("slat tilt requires an exact known integer position, independent tilt feature and service, without primary-position or state inference",()=>{
  for(const mutate of [e=>{e.profile.schema_cover_tilt=false;},e=>{e._status.entity_control_status="offline";},e=>{e._hass.states["cover.test"].state="unknown";},
    e=>{e._hass.states["cover.test"].attributes.supported_features=0;},e=>{e._hass.states["cover.test"].attributes.current_tilt_position=null;},
    e=>{delete e._hass.states["cover.test"].attributes.current_tilt_position;},e=>{e._hass.states["cover.test"].attributes.current_tilt_position=45.5;},e=>{e.entityFor("cover.test").actions=[];}]){
    const editor=coverTiltEditor();mutate(editor);assert.equal(editor.coverTiltAvailability().ready,false);assert.equal(editor.requestLightControl("covertilt"),false);
  }
  const editor=coverTiltEditor();assert.equal(editor.requestLightControl("covertilt"),true);editor._hass.states["cover.test"].attributes.supported_features=0;assert.equal(editor.confirmLightControl(),false);
});

test("slat tilt recovery is exact v3 and preserves raw integer service semantics",()=>{
  const editor=coverTiltEditor();editor._draft.version=3;editor.cardAt(2).action={kind:"control",control:"number",property:"tilt_position"};
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  const fixed=record();fixed.layout.cards[1].action={kind:"service",service:"cover.set_cover_tilt_position",data:{tilt_position:46}};assert.doesNotThrow(()=>editor.validateStoredDraft(fixed));
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="number.test";},r=>{r.layout.cards[1].action.data={position:46};},r=>{r.layout.cards[1].action.property="current_tilt_position";}]){
    const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));
  }
  editor.profile.schema_cover_tilt=false;assert.throws(()=>editor.validateStoredDraft(record()));
});

function calendarEditor() {
  const editor=makeEditor(),fields={message:"Plan dnia",all_day:false,start_time:"2026-11-01 17:15:00",end_time:"2026-11-01 18:15:00"};
  editor.profile.schema_calendar_next=true;editor.profile.calendar_text_slots=[12];
  editor.profile.slots.push({slot:12,page_id:"home-2",x:180,y:606,width:440,height:76,radius:38,editable:true,hidden:false,types:["entity","sensor","action"]});
  if(!editor._data.icons.includes("clock"))editor._data.icons.push("clock");
  editor._hass.states["calendar.test"]={state:"off",attributes:clone(fields)};
  editor._entityIndex.set("calendar.test",{entity_id:"calendar.test",domain:"calendar",name:"Calendar",available:true,state:"off",actions:[],calendar_next:{state:"off",fields:clone(fields),text:{pl:"01.11.2026 17:15 · Plan dnia",en:"2026-11-01 17:15 · Plan dnia"}}});
  return editor;
}

test("calendar assignment is passive and reversible and requires the existing wide information row",()=>{
  const editor=calendarEditor(),before=clone(editor._draft);
  assert.equal(editor.assignEntity("calendar.test",3),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._error,editor.t("calendarPlacement"));
  assert.equal(editor.assignEntity("calendar.test",12),true);editor._selectedSlot=12;const card=editor.cardAt(12),id=card.id;
  assert.equal(card.type,"sensor");assert.equal(card.icon,"clock");assert.deepEqual(clone(card.action),{kind:"none"});
  assert.equal(editor.stateText(card),"2026-11-01 17:15 · Plan dnia");assert.match(editor.inspectorMarkup(),/data-calendar-next/);
  assert.equal(editor.groupTargetCompatible(card,3),false);assert.equal(editor.acceptsCard(editor.slotAt(12),card),true);
  editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"01.11.2026 17:15 · Plan dnia");
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(12).id,id);
});

test("calendar preview uses server normalization only for the exact current event observation",()=>{
  const editor=calendarEditor();editor.assignEntity("calendar.test",12);const card=editor.cardAt(12),state=editor._hass.states[card.entity_id],meta=editor.entityFor(card.entity_id).calendar_next;
  state.attributes.message="Other event";assert.equal(editor.stateText(card),"Unknown");
  meta.fields.message="Other event";meta.text.en="2026-11-01 17:15 · Other event";assert.equal(editor.stateText(card),meta.text.en);
  state.attributes.start_time="2026-11-01 18:15:00";assert.equal(editor.stateText(card),"Unknown");
  meta.fields.start_time=state.attributes.start_time;meta.text.en="2026-11-01 18:15 · Other event";assert.equal(editor.stateText(card),meta.text.en);
  state.attributes.all_day=true;assert.equal(editor.stateText(card),"Unknown");
  state.state="unavailable";assert.equal(editor.stateText(card),"Offline");
});

test("calendar recovery rejects an old profile, smaller placement and actuator action",()=>{
  const editor=calendarEditor();editor.assignEntity("calendar.test",12);
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:2,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  for(const mutate of [r=>{r.layout.cards.find(c=>c.slot===12).slot=11;r.layout.cards=r.layout.cards.filter(c=>c.id===editor.cardAt(12).id);},r=>{r.layout.cards.find(c=>c.slot===12).action={kind:"default"};},r=>{r.layout.cards.find(c=>c.slot===12).type="entity";}]){
    const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));
  }
  editor.profile.schema_calendar_next=false;assert.throws(()=>editor.validateStoredDraft(record()));
});

test("known empty calendar is distinct from an active event without details and from stale metadata",()=>{
  const editor=calendarEditor();editor.assignEntity("calendar.test",12);const card=editor.cardAt(12),state=editor._hass.states[card.entity_id],entity=editor.entityFor(card.entity_id);
  state.attributes={friendly_name:"Calendar"};entity.calendar_next={state:"off",fields:{},text:{pl:"Brak wydarzeń",en:"No events"}};
  assert.equal(editor.stateText(card),"No events");editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"Brak wydarzeń");
  state.state="on";assert.equal(editor.stateText(card),"Nieznany");
  state.state="off";state.attributes.message=null;assert.equal(editor.stateText(card),"Nieznany");
});

function personEditor() {
  const editor=calendarEditor();editor.profile.schema_person_presence=true;editor.profile.person_text_slots=[12];
  if(!editor._data.icons.includes("presence"))editor._data.icons.push("presence");
  editor._hass.states["person.qa"]={state:"home",attributes:{entity_picture:"/PRIVATE",latitude:1.2}};
  editor._entityIndex.set("person.qa",{entity_id:"person.qa",domain:"person",name:"Person QA",available:true,state:"home",actions:[],person_presence:{state:"home",text:{pl:"W domu",en:"Home"}}});
  return editor;
}

test("person assignment is passive, exact-home accent by default, wide and reversible",()=>{
  const editor=personEditor(),before=clone(editor._draft);
  assert.equal(editor.assignEntity("person.qa",3),false);assert.deepEqual(clone(editor._draft),before);assert.equal(editor._error,editor.t("personPlacement"));
  assert.equal(editor.assignEntity("person.qa",12),true);editor._selectedSlot=12;const card=editor.cardAt(12);
  assert.equal(card.type,"sensor");assert.equal(card.icon,"presence");assert.equal(card.state_color,true);assert.deepEqual(clone(card.action),{kind:"none"});
  assert.equal(editor.stateText(card),"Home");assert.equal(editor.effectivePalette(card),"primary");assert.match(editor.inspectorMarkup(),/data-person-presence/);
  assert.equal(editor.groupTargetCompatible(card,3),false);editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"W domu");
  for(const state of ["not_home","Home","home office","unknown","unavailable"]){editor._hass.states[card.entity_id].state=state;assert.equal(editor.effectivePalette(card),"surface");}
  card.state_color=false;assert.equal(editor.effectivePalette(card),"primary");
  editor.history("undo");assert.deepEqual(clone(editor._draft),before);editor.history("redo");assert.equal(editor.cardAt(12).entity_id,"person.qa");
});

test("person caption follows only an exact bounded current observation and never guesses a stale zone",()=>{
  const editor=personEditor();editor.assignEntity("person.qa",12);const card=editor.cardAt(12),state=editor._hass.states[card.entity_id],meta=editor.entityFor(card.entity_id).person_presence;
  state.state="Praca_Północ";assert.equal(editor.stateText(card),"Unknown");
  meta.state=state.state;meta.text={pl:"Praca_Północ",en:"Praca_Północ"};assert.equal(editor.stateText(card),"Praca_Północ");
  state.attributes.latitude=99;state.attributes.entity_picture="/OTHER";assert.equal(editor.stateText(card),"Praca_Północ");
  state.state="unknown";assert.equal(editor.stateText(card),"Unknown");state.state="unavailable";assert.equal(editor.stateText(card),"Offline");
  delete editor._hass.states[card.entity_id];assert.equal(editor.stateText(card),"Offline");
});

test("person recovery rejects old profile, short captions and actionable or hybrid cards",()=>{
  const editor=personEditor();editor.assignEntity("person.qa",12);
  const record=()=>({version:1,profile:editor.profile.id,base_revision:4,updated_at:1,layout:{version:2,profile:editor.profile.id,cards:clone(editor._draft.cards)}});
  assert.doesNotThrow(()=>editor.validateStoredDraft(record()));
  for(const mutate of [r=>{r.layout.cards.find(c=>c.slot===12).slot=11;},r=>{r.layout.cards.find(c=>c.slot===12).action={kind:"default"};},r=>{r.layout.cards.find(c=>c.slot===12).type="entity";}]){
    const value=record();mutate(value);assert.throws(()=>editor.validateStoredDraft(value));
  }
  editor.profile.schema_person_presence=false;assert.throws(()=>editor.validateStoredDraft(record()));
});

function mowerEditor() {
  const editor=makeEditor(),card=editor.cardAt(2);editor._selectedSlot=2;editor.profile.schema_mower_actions=true;
  editor._status={...editor._status,device_available:true,context_press_version:1,press_enabled_version:1};
  card.entity_id="lawn_mower.qa";card.action={kind:"none"};
  editor._hass.states[card.entity_id]={state:"docked",attributes:{supported_features:7}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"lawn_mower",available:true,state:"docked",actions:["start_mowing","pause","dock"].map(op=>({service:`lawn_mower.${op}`,fields:{}})),mower_actions:{state:"docked",features:7,supported:["start_mowing","pause","dock"],eligible:["start_mowing"]}});
  editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);return editor;
}

test("mower action buttons edit one exact no-data service with stable identity and reversible history only",()=>{
  const editor=mowerEditor(),before=clone(editor._draft),card=editor.cardAt(2),id=card.id;
  assert.match(editor.inspectorMarkup(),/data-mower-actions/);
  for(const op of ["start_mowing","pause","dock"]){
    assert.equal(editor.mowerOperationReady(card,op),true);assert.equal(editor.configureMowerAction(op),true);
    assert.deepEqual(clone(card.action),{kind:"service",service:`lawn_mower.${op}`,data:{}});assert.equal(card.id,id);
  }
  editor.history("undo");assert.equal(editor.cardAt(2).action.service,"lawn_mower.pause");
  editor.history("undo");editor.history("undo");assert.deepEqual(clone(editor._draft),before);
  editor.history("redo");assert.equal(editor.cardAt(2).action.service,"lawn_mower.start_mowing");
});

test("mower setup is blocked by stale observations, absent capability, old peer and information-only cards",()=>{
  for(const mutate of [e=>{e.profile.schema_mower_actions=false;},e=>{e._status.press_enabled_version=0;},e=>{e._status.context_press_version=0;},e=>{e._status.device_available=false;},
    e=>{e._hass.connected=false;},e=>{e._hass.states["lawn_mower.qa"].state="unknown";},e=>{e._hass.states["lawn_mower.qa"].state="mowing";},e=>{e._hass.states["lawn_mower.qa"].attributes.supported_features=true;},
    e=>{e._hass.states["lawn_mower.qa"].attributes.supported_features=6;},e=>{e.entityFor("lawn_mower.qa").actions=[];},e=>{e.cardAt(2).type="sensor";},e=>{e._profileStale=true;}]){
    const editor=mowerEditor(),before=clone(editor._draft);mutate(editor);const current=clone(editor._draft);
    assert.equal(editor.configureMowerAction("start_mowing"),false);assert.deepEqual(clone(editor._draft),current);assert.equal(editor._undo.length,0);
  }
  const editor=mowerEditor();assert.equal(editor.configureMowerAction("stop"),false);assert.equal(editor.configureMowerAction("turn_on"),false);
});

test("new mower cards never infer starting and supported pause can be configured while docked",async()=>{
  const editor=mowerEditor();const created=editor.newCard({entity_id:"lawn_mower.new",name:"Mower"},3);
  assert.deepEqual(clone(created.action),{kind:"none"});assert.equal(created.type,"entity");
  const button={disabled:false,dataset:{action:"mower-configure",operation:"pause"}};
  await editor.onClick({target:{closest:()=>button},preventDefault(){}});
  assert.equal(editor.cardAt(2).action.service,"lawn_mower.pause");assert.equal(editor._hass.states["lawn_mower.qa"].state,"docked");
  assert.equal(editor.mowerOperationReady(editor.cardAt(2),"pause"),true);
});

test("mower preview displays observed activity and HA labels rather than pretending that a configured command ran",()=>{
  const editor=mowerEditor(),card=editor.cardAt(2),state=editor._hass.states[card.entity_id];editor.configureMowerAction("start_mowing");
  assert.equal(editor.stateText(card),"Docked");editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"W bazie");
  state.state="mowing";assert.equal(editor.stateText(card),"Koszenie");state.state="returning";assert.equal(editor.stateText(card),"Powrót");
  state.state="unknown";assert.equal(editor.stateText(card),"Nieznany");state.state="unavailable";assert.equal(editor.stateText(card),"Offline");
  state.state="paused";editor._hass.formatEntityState=()=>"HA pauza";assert.equal(editor.stateText(card),"HA pauza");
  state.state="returning";editor._hass.formatEntityState=()=>"Returning";assert.equal(editor.stateText(card),"Powrót");
  editor._hass.entities={[card.entity_id]:{translation_key:"specific"}};assert.equal(editor.stateText(card),"Returning");
});

function vacuumActionsEditor() {
  const editor=makeEditor(),card=editor.cardAt(2);editor._selectedSlot=2;editor.profile.schema_vacuum_actions=true;
  editor._status={...editor._status,device_available:true,context_press_version:1,press_enabled_version:1};
  card.entity_id="vacuum.qa";card.action={kind:"none"};
  editor._hass.states[card.entity_id]={state:"docked",attributes:{supported_features:9756}};
  editor._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain:"vacuum",available:true,state:"docked",actions:["start","pause","stop","return_to_base","locate","clean_spot"].map(op=>({service:`vacuum.${op}`,fields:{}})),vacuum_actions:{state:"docked",features:9756,supported:["start","pause","stop","return_to_base","locate","clean_spot"],eligible:["start"]}});
  editor._saved=clone(editor._draft);editor.entry.layout=clone(editor._draft);return editor;
}

test("vacuum action buttons edit one exact no-data service with stable identity and reversible history only",()=>{
  const editor=vacuumActionsEditor(),before=clone(editor._draft),card=editor.cardAt(2),id=card.id;
  assert.match(editor.inspectorMarkup(),/data-vacuum-actions/);
  for(const op of ["start","pause","stop","return_to_base","locate","clean_spot"]){
    assert.equal(editor.vacuumOperationReady(card,op),true);assert.equal(editor.configureVacuumAction(op),true);
    assert.deepEqual(clone(card.action),{kind:"service",service:`vacuum.${op}`,data:{}});assert.equal(card.id,id);
  }
  editor.history("undo");assert.equal(editor.cardAt(2).action.service,"vacuum.locate");
  for(let i=0;i<5;i++) editor.history("undo");assert.deepEqual(clone(editor._draft),before);
  editor.history("redo");assert.equal(editor.cardAt(2).action.service,"vacuum.start");
});

test("vacuum setup is blocked by stale observations, absent capability, old peer and information-only cards",()=>{
  for(const mutate of [e=>{e.profile.schema_vacuum_actions=false;},e=>{e._status.press_enabled_version=0;},e=>{e._status.context_press_version=0;},e=>{e._status.device_available=false;},
    e=>{e._hass.connected=false;},e=>{e._hass.states["vacuum.qa"].state="unknown";},e=>{e._hass.states["vacuum.qa"].state="cleaning";},e=>{e._hass.states["vacuum.qa"].attributes.supported_features=true;},
    e=>{e._hass.states["vacuum.qa"].attributes.supported_features=1564;},e=>{e.entityFor("vacuum.qa").actions=[];},e=>{e.cardAt(2).type="sensor";},e=>{e._profileStale=true;}]){
    const editor=vacuumActionsEditor(),before=clone(editor._draft);mutate(editor);const current=clone(editor._draft);
    assert.equal(editor.configureVacuumAction("start"),false);assert.deepEqual(clone(editor._draft),current);assert.equal(editor._undo.length,0);
  }
  const editor=vacuumActionsEditor();assert.equal(editor.configureVacuumAction("send_command"),false);assert.equal(editor.configureVacuumAction("turn_on"),false);
});

test("new vacuum cards never infer starting and supported pause can be configured while docked",async()=>{
  const editor=vacuumActionsEditor();const created=editor.newCard({entity_id:"vacuum.new",name:"Vacuum"},3);
  assert.deepEqual(clone(created.action),{kind:"none"});assert.equal(created.type,"entity");
  const button={disabled:false,dataset:{action:"vacuum-configure",operation:"pause"}};
  await editor.onClick({target:{closest:()=>button},preventDefault(){}});
  assert.equal(editor.cardAt(2).action.service,"vacuum.pause");assert.equal(editor._hass.states["vacuum.qa"].state,"docked");
  assert.equal(editor.vacuumOperationReady(editor.cardAt(2),"pause"),true);
});

test("vacuum preview displays observed activity and HA labels rather than pretending that a configured command ran",()=>{
  const editor=vacuumActionsEditor(),card=editor.cardAt(2),state=editor._hass.states[card.entity_id];editor.configureVacuumAction("start");
  assert.equal(editor.stateText(card),"Docked");editor._hass.locale.language="pl";assert.equal(editor.stateText(card),"W bazie");
  state.state="cleaning";assert.equal(editor.stateText(card),"Sprzątanie");state.state="returning";assert.equal(editor.stateText(card),"Powrót");
  state.state="unknown";assert.equal(editor.stateText(card),"Nieznany");state.state="unavailable";assert.equal(editor.stateText(card),"Offline");
  state.state="paused";editor._hass.formatEntityState=()=>"HA pauza";assert.equal(editor.stateText(card),"HA pauza");
  state.state="returning";editor._hass.formatEntityState=()=>"Returning";assert.equal(editor.stateText(card),"Powrót");
  editor._hass.entities={[card.entity_id]:{translation_key:"specific"}};assert.equal(editor.stateText(card),"Returning");
});


test("vacuum selected chip and friendly service label are explicit, and setup retains inspector scroll",()=>{
  const editor=vacuumActionsEditor();editor._hass.locale.language="pl";
  const pane={scrollTop:390,querySelector:()=>({focus(options){assert.equal(options.preventScroll,true);}})};
  editor.shadowRoot.querySelector=selector=>selector==="#inspector"?pane:null;
  editor.render=()=>{pane.scrollTop=0;};
  assert.equal(editor.configureVacuumAction("pause"),true);assert.equal(pane.scrollTop,390);
  assert.equal(editor.serviceLabel("vacuum.pause"),"Wstrzymaj sprzątanie");
  assert.match(editor.inspectorMarkup(),/data-operation="pause" aria-pressed="true"/);
  const count=editor._undo.length;assert.equal(editor.configureVacuumAction("pause"),false);assert.equal(editor._undo.length,count);
  editor._pending={kind:"review"};assert.equal(editor.configureVacuumAction("stop"),false);
});

test("generic Polish vacuum return text fits the compact caption while entity-specific labels retain precedence",()=>{
 const editor=vacuumActionsEditor(),card=editor.cardAt(2);editor._hass.locale.language="pl";editor._hass.states[card.entity_id].state="returning";
 editor._hass.formatEntityState=()=>"wraca do stacji dokującej";assert.equal(editor.stateText(card),"Powrót do bazy");
 editor._hass.entities={[card.entity_id]:{translation_key:"custom"}};assert.equal(editor.stateText(card),"wraca do stacji dokującej");
});

function vacuumRoomEditor(){
 const editor=vacuumActionsEditor(),id="vacuum.qa";editor.profile.schema_vacuum_area=true;
 editor._hass.states[id].attributes.supported_features=26140;
 const entity=editor.entityFor(id);entity.vacuum_actions.features=26140;
 entity.vacuum_area={state:"docked",features:26140,areas:[{id:"living",name:"Salon"},{id:"office",name:"Biuro"}]};
 entity.actions.push({service:"vacuum.clean_area",fields:{cleaning_area_id:{type:"select",required:true,options:["living","office"],option_labels:["Salon","Biuro"]}}});
 return editor;
}

test("mapped-room selection stores exactly one Core area with Undo, without vendor segments or automatic start",()=>{
 const editor=vacuumRoomEditor(),before=clone(editor._draft);assert.equal(editor.vacuumAreas().length,2);
 assert.equal(editor.configureVacuumArea("office"),true);
 assert.deepEqual(clone(editor.cardAt(2).action),{kind:"service",service:"vacuum.clean_area",data:{cleaning_area_id:"office"}});
 assert.equal(editor._hass.states["vacuum.qa"].state,"docked");
 assert.match(editor.inspectorMarkup(),/value="office" selected>Biuro/);
 assert.equal(editor.serviceLabel("vacuum.clean_area"),"Clean a room");
 editor.history("undo");assert.deepEqual(clone(editor._draft),before);
});

test("room chooser rejects missing, stale, malformed, unsupported and disconnected metadata",()=>{
 for(const mutate of [e=>{e.profile.schema_vacuum_area=false;},e=>{e._status.press_enabled_version=0;},e=>{e._status.device_available=false;},e=>{e._hass.connected=false;},e=>{e._profileStale=true;},
   e=>{e._hass.states["vacuum.qa"].state="unknown";},e=>{e.entityFor("vacuum.qa").vacuum_area.state="cleaning";},e=>{e.entityFor("vacuum.qa").vacuum_area.areas=[];},
   e=>{e.entityFor("vacuum.qa").vacuum_area.areas[1].id="living";},e=>{e.entityFor("vacuum.qa").actions=[];},e=>{e.cardAt(2).type="sensor";},e=>{e._pending={kind:"review"};}]){
   const editor=vacuumRoomEditor();mutate(editor);const before=clone(editor._draft);assert.equal(editor.configureVacuumArea("living"),false);assert.deepEqual(clone(editor._draft),before);
 }
 const editor=vacuumRoomEditor();assert.equal(editor.configureVacuumArea("17"),false);assert.equal(editor.configureVacuumArea("Bedroom"),false);
});

test("room field requires exact text on its service, preserves Unicode labels and never substitutes the first room",()=>{
 const editor=vacuumRoomEditor(),before=clone(editor._draft);
 assert.equal(editor.configureVacuumArea(""),false);assert.deepEqual(clone(editor._draft),before);
 editor.entityFor("vacuum.qa").vacuum_area.areas[1].name="Biuro <test> Żółć";
 assert.match(editor.inspectorMarkup(),/Biuro &lt;test&gt; Żółć/);
 assert.equal(editor.configureVacuumArea("living"),true);const draft=clone(editor._draft);delete draft.revision;
 const record={version:1,profile:editor.profile.id,base_revision:editor._saved.revision,updated_at:Date.now(),layout:draft};editor.validateStoredDraft(record);
 draft.cards.find(card=>card.slot===2).action.data.cleaning_area_id=["living"];
 assert.throws(()=>editor.validateStoredDraft(record));
});

test("area selector events use one reversible action transaction and periodic metadata refresh reuses the existing cadence",()=>{
 const editor=vacuumRoomEditor();editor.editField({dataset:{field:"vacuum-area"},value:"living"});
 assert.equal(editor._undo.length,1);assert.equal(editor.cardAt(2).action.data.cleaning_area_id,"living");
 let calls=[];editor.fetchSelectedEntity=force=>calls.push(force);editor.refreshEntityMetadata();assert.deepEqual(calls,[true]);
});

test("duration preview matches the native bounded decimal contract across units, ties, signs and locales",()=>{
 const cases=JSON.parse(fs.readFileSync(path.join(__dirname,"fixtures/duration_preview.json"),"utf8"));
 const editor=makeEditor(),card=editor.cardAt(2);card.entity_id="sensor.duration";card.type="sensor";card.action={kind:"none"};
 for(const item of cases) for(const language of ["en","pl"]){
  editor._hass.locale.language=language;editor._hass.entities={[card.entity_id]:item.precision===null?{}:{display_precision:item.precision}};
  const state={state:item.state,attributes:{device_class:"duration",unit_of_measurement:item.unit}};editor._hass.states[card.entity_id]=state;
  assert.equal(editor.durationStateText(card,state),item[language],JSON.stringify({item,language}));
 }
 assert.ok(editor._precisionFormats.size<=7);
});

test("duration projection keeps exact labels and numeric-card overrides separate from registry precision",()=>{
 const editor=makeEditor(),card=editor.cardAt(2);card.entity_id="sensor.duration";card.type="sensor";card.action={kind:"none"};card.display_precision=6;
 const state={state:"59.9995",attributes:{device_class:"duration",unit_of_measurement:"s"}};editor._hass.states[card.entity_id]=state;
 editor._hass.entities={[card.entity_id]:{display_precision:3}};assert.equal(editor.stateText(card),"1 min");
 card.state_labels={"59.9995":"My label"};assert.equal(editor.stateText(card),"My label");delete card.state_labels;
 editor._hass.entities={[card.entity_id]:{dp:3}};assert.equal(editor.stateText(card),"1 min");
 editor._hass.entities={[card.entity_id]:{display_precision:true}};assert.equal(editor.stateText(card),"59.9995 s");
 for(const change of [{device_class:"timestamp"},{unit_of_measurement:"months"}]){
  const before={...state.attributes};Object.assign(state.attributes,change);assert.equal(editor.durationStateText(card,state),null);state.attributes=before;
 }
 state.state="unknown";assert.equal(editor.stateText(card),editor.t("unknown"));state.state="unavailable";assert.equal(editor.stateText(card),editor.t("offline"));
});

test("removed mapped room remains an explicit unavailable saved target without selecting another room",()=>{
 const editor=vacuumRoomEditor();assert.equal(editor.configureVacuumArea("living"),true);const before=clone(editor._draft);
 const entity=editor.entityFor("vacuum.qa");entity.vacuum_area.areas=[{id:"office",name:"Biuro"}];entity.actions.find(a=>a.service==="vacuum.clean_area").fields.cleaning_area_id.options=["office"];
 const markup=editor.inspectorMarkup();assert.match(markup,/aria-label="Clean a room"/);assert.match(markup,/<option selected disabled value="living">Selected room is unavailable/);
 let repainted=0;editor.paintInspector=()=>{repainted++;};assert.equal(editor.configureVacuumArea("living"),false);assert.equal(repainted,1);assert.deepEqual(clone(editor._draft),before);
 assert.equal(editor.configureVacuumArea("office"),true);assert.equal(editor.cardAt(2).action.data.cleaning_area_id,"office");
});

function remotePowerEditor() {
 const e=makeEditor(),c=e.cardAt(2);e._selectedSlot=2;e.profile.schema_remote_power=true;
 e._status={...e._status,device_available:true,context_press_version:1,press_enabled_version:1};
 c.entity_id="remote.qa";c.action={kind:"none"};e._hass.states[c.entity_id]={state:"off",attributes:{supported_features:0}};
 e._entityIndex.set(c.entity_id,{entity_id:c.entity_id,domain:"remote",available:true,actions:["turn_on","turn_off"].map(op=>({service:`remote.${op}`,fields:{}})),remote_power:{state:"off",supported:["turn_on","turn_off"]}});
 e._saved=clone(e._draft);e.entry.layout=clone(e._draft);return e;
}
test("remote power explicitly edits the draft with reversible exact targets and no API",()=>{
 const e=remotePowerEditor(),before=clone(e._draft),id=e.cardAt(2).id;
 assert.match(e.inspectorMarkup(),/data-remote-power/);
 assert.equal(e.configureRemotePower("turn_on"),true);assert.deepEqual(clone(e.cardAt(2).action),{kind:"service",service:"remote.turn_on",data:{}});
 assert.equal(e.cardAt(2).id,id);e.history("undo");assert.deepEqual(clone(e._draft),before);
 assert.equal(e.configureRemotePower("turn_off"),true);assert.equal(e.cardAt(2).action.service,"remote.turn_off");
 assert.equal(e.newCard({entity_id:"remote.new"},3).action.kind,"none");
});
test("remote setup rejects unsupported operations, stale metadata and unavailable peers",()=>{
 for(const change of [e=>{e.profile.schema_remote_power=false;},e=>{e._status.press_enabled_version=0;},e=>{e._status.context_press_version=0;},e=>{e._status.device_available=false;},e=>{e._hass.connected=false;},e=>{e._hass.states["remote.qa"].state="on";},e=>{e._hass.states["remote.qa"].state="unknown";},e=>{e.entityFor("remote.qa").actions=[];},e=>{e.cardAt(2).type="sensor";},e=>{e._conflict=true;},e=>{e.cardAt(2).visible=false;}]) {
  const e=remotePowerEditor();change(e);const before=clone(e._draft);assert.equal(e.configureRemotePower("turn_on"),false);assert.deepEqual(clone(e._draft),before);
 }
 const e=remotePowerEditor();for(const op of ["toggle","send_command","learn_command"]) assert.equal(e.configureRemotePower(op),false);
});

function remoteActivityEditor() {
 const e=remotePowerEditor();e.profile.schema_remote_activity=true;e.profile.layout_versions=[2,3];e.profile.schema_control_types=["choice"];
 e._status={...e._status,entity_control_status:"ready",native_control_types:["entity_control_v1"],control_kinds:["choice"],empty_choice_version:1};
 e._hass.states["remote.qa"].attributes={supported_features:4,activity_list:["Telewizja","Radio"],current_activity:"Telewizja"};
 e.entityFor("remote.qa").remote_activity={options:["Telewizja","Radio"],index:null,empty:true};return e;
}
test("remote activity reviews v3 migration before any draft mutation and Undo restores power setup",()=>{
 const e=remoteActivityEditor(),before=clone(e._draft),id=e.cardAt(2).id;
 assert.equal(e.observedRemoteActivity(e.cardAt(2)).empty,true);assert.equal(e.remoteActivityAvailability().ready,true);
 assert.match(e.inspectorMarkup(),/control-remoteactivity/);assert.equal(e.requestLightControl("remoteactivity"),true);
 assert.deepEqual(clone(e._draft),before);assert.equal(e.confirmLightControl(),true);
 assert.equal(e._draft.version,3);assert.deepEqual(clone(e.cardAt(2).action),{kind:"control",control:"choice",property:"activity"});assert.equal(e.cardAt(2).id,id);
 assert.equal(e.cardControlKind(e.cardAt(2)),"remoteactivity");assert.equal([...e.inspectorMarkup().matchAll(/<option[^>]*>Choose remote activity<\/option>/g)].length,1);assert.doesNotMatch(e.inspectorMarkup(),/data-remote-power/);assert.match(e.inspectorMarkup(),/aria-label="On tap"/);e.history("undo");assert.deepEqual(clone(e._draft),before);
});
test("remote activity distinguishes known off, known running and unknown activity for old peers",()=>{
 const e=remoteActivityEditor();e._status.empty_choice_version=0;assert.equal(e.remoteActivityAvailability().ready,false);
 const state=e._hass.states["remote.qa"],meta=e.entityFor("remote.qa").remote_activity;
 state.state="on";meta.index=0;delete meta.empty;assert.equal(e.remoteActivityAvailability().ready,true);
 state.attributes.current_activity="Missing";meta.index=null;assert.equal(e.remoteActivityAvailability().ready,false);
 state.state="off";meta.empty=true;e._status.empty_choice_version=1;assert.equal(e.remoteActivityAvailability().ready,true);
});
test("remote activity blocks stale catalogue, flags, target and changed reviews",()=>{
 for(const change of [e=>{e._hass.states["remote.qa"].attributes.supported_features=0;},e=>{e._hass.states["remote.qa"].state="unknown";},e=>{e.entityFor("remote.qa").actions=[];},e=>{e.entityFor("remote.qa").remote_activity.options.reverse();},e=>{e.profile.schema_remote_activity=false;},e=>{e._status.device_available=false;},e=>{e._hass.states["remote.qa"].attributes.activity_list=[];}]){
  const e=remoteActivityEditor();change(e);const before=clone(e._draft);assert.equal(e.requestLightControl("remoteactivity"),false);assert.deepEqual(clone(e._draft),before);
 }
 const e=remoteActivityEditor(),before=clone(e._draft);assert.equal(e.requestLightControl("remoteactivity"),true);
 e._hass.states["remote.qa"].attributes.activity_list=["Radio","Telewizja"];assert.equal(e.confirmLightControl(),false);assert.deepEqual(clone(e._draft),before);
});

function mediaMuteEditor() {
 const e=remotePowerEditor(),c=e.cardAt(2);e.profile.schema_media_mute=true;c.entity_id="media_player.qa";
 e._hass.states[c.entity_id]={state:"playing",attributes:{supported_features:8,is_volume_muted:false,volume_level:.42,media_title:"Track QA"}};
 e._entityIndex.set(c.entity_id,{entity_id:c.entity_id,domain:"media_player",available:true,actions:[{service:"media_player.volume_mute",fields:{is_volume_muted:{type:"boolean",required:true}}}],media_mute:{state:"playing",features:8,value:false,text:{en:"Sound on",pl:"Dźwięk wł."}}});
 e._saved=clone(e._draft);e.entry.layout=clone(e._draft);return e;
}
test("media mute and restore only edit one explicit boolean service with undo",()=>{
 const e=mediaMuteEditor(),before=clone(e._draft),id=e.cardAt(2).id;
 assert.equal(e.mediaMuteReady(),true);assert.match(e.inspectorMarkup(),/data-media-mute/);
 assert.equal(e.configureMediaMute(true),true);assert.deepEqual(clone(e.cardAt(2).action),{kind:"service",service:"media_player.volume_mute",data:{is_volume_muted:true}});
 assert.equal(e.stateText(e.cardAt(2)),"Sound on");assert.match(e.inspectorMarkup(),/aria-label="Mute sound"/);
 assert.equal(e.configureMediaMute(false),true);assert.equal(e.cardAt(2).id,id);
 e.history("undo");assert.equal(e.cardAt(2).action.data.is_volume_muted,true);e.history("undo");assert.deepEqual(clone(e._draft),before);
 assert.equal(e._hass.states["media_player.qa"].attributes.volume_level,.42);assert.equal(e._hass.states["media_player.qa"].state,"playing");
});
test("media mute setup rejects stale metadata, unknown booleans, absent capability and old peers",()=>{
 for(const change of [e=>{e.profile.schema_media_mute=false;},e=>{e._status.press_enabled_version=0;},e=>{e._status.context_press_version=0;},e=>{e._status.device_available=false;},e=>{e._hass.connected=false;},e=>{e.cardAt(2).type="sensor";},e=>{e._hass.states["media_player.qa"].state="off";},e=>{e._hass.states["media_player.qa"].attributes.is_volume_muted="false";},e=>{e._hass.states["media_player.qa"].attributes.supported_features=1;},e=>{e.entityFor("media_player.qa").media_mute.value=true;},e=>{e.entityFor("media_player.qa").actions=[];},e=>{e.entityFor("media_player.qa").domain="fan";}]) {
  const e=mediaMuteEditor();change(e);const before=clone(e._draft);assert.equal(e.configureMediaMute(true),false);assert.deepEqual(clone(e._draft),before);
 }
 const e=mediaMuteEditor();for(const value of ["true",1,null])assert.equal(e.configureMediaMute(value),false);
});
test("media mute preview reports actual status and outages independently of desired target",()=>{
 const e=mediaMuteEditor();e.configureMediaMute(false);const state=e._hass.states["media_player.qa"],meta=e.entityFor("media_player.qa").media_mute;
 state.attributes.is_volume_muted=true;meta.value=true;meta.text.en="Muted";assert.equal(e.stateText(e.cardAt(2)),"Muted");
 state.state="off";assert.equal(e.stateText(e.cardAt(2)),"Off");state.state="unavailable";assert.equal(e.stateText(e.cardAt(2)),e.t("offline"));
 delete e._hass.states["media_player.qa"];assert.equal(e.stateText(e.cardAt(2)),e.t("offline"));
});

function mediaSourceEditor() {
 const e=remoteActivityEditor(),c=e.cardAt(2);c.entity_id="media_player.qa";e.profile.schema_media_source=true;
 e._hass.states[c.entity_id]={state:"playing",attributes:{supported_features:2048,source_list:["HDMI 1","Radio"," Żółty "],source:"HDMI 1",media_title:"Track QA"}};
 e._entityIndex.set(c.entity_id,{entity_id:c.entity_id,domain:"media_player",available:true,media_source:{options:["HDMI 1","Radio"," Żółty "],index:0},actions:[{service:"media_player.select_source",fields:{source:{type:"select",required:true,options:["HDMI 1","Radio"," Żółty "]}}}]});
 e._saved=clone(e._draft);e.entry.layout=clone(e._draft);return e;
}
test("media sources review one v3 choice action and Undo without media commands",()=>{
 const e=mediaSourceEditor(),before=clone(e._draft),id=e.cardAt(2).id;
 assert.equal(e.mediaSourceAvailability().ready,true);assert.equal(e.requestLightControl("mediasource"),true);assert.deepEqual(clone(e._draft),before);
 assert.equal(e.confirmLightControl(),true);assert.deepEqual(clone(e.cardAt(2).action),{kind:"control",control:"choice",property:"source"});assert.equal(e._draft.version,3);
 assert.equal(e.cardControlKind(e.cardAt(2)),"mediasource");assert.equal(e.stateText(e.cardAt(2)),"HDMI 1");assert.equal(e.cardAt(2).id,id);
 assert.equal([...e.inspectorMarkup().matchAll(/<option[^>]*>Choose player source<\/option>/g)].length,1);assert.match(e.inspectorMarkup(),/data-media-source/);
 assert.doesNotMatch(e.inspectorMarkup(),/data-media-mute/);
 const record={version:1,profile:e.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:e.profile.id,cards:clone(e._draft.cards)}};
 assert.doesNotThrow(()=>e.validateStoredDraft(record));e.history("undo");assert.deepEqual(clone(e._draft),before);
});
test("media sources reject unsupported state, unobserved index, stale list and reviewed changes",()=>{
 for(const change of [e=>{e.profile.schema_media_source=false;},e=>{e._status.control_kinds=[];},e=>{e._hass.states["media_player.qa"].state="off";},e=>{e._hass.states["media_player.qa"].state="standby";},e=>{e._hass.states["media_player.qa"].attributes.source=null;},e=>{e._hass.states["media_player.qa"].attributes.supported_features=8;},e=>{e.entityFor("media_player.qa").media_source.index=1;},e=>{e.entityFor("media_player.qa").actions=[];},e=>{e.entityFor("media_player.qa").media_source.options.reverse();}]) {
  const e=mediaSourceEditor();change(e);const before=clone(e._draft);assert.equal(e.requestLightControl("mediasource"),false);assert.deepEqual(clone(e._draft),before);
 }
 const e=mediaSourceEditor(),before=clone(e._draft);assert.equal(e.requestLightControl("mediasource"),true);e._hass.states["media_player.qa"].attributes.source="Radio";assert.equal(e.confirmLightControl(),false);assert.deepEqual(clone(e._draft),before);
});
test("media source caption uses observed source and never falls back to first or track title",()=>{
 const e=mediaSourceEditor();e.requestLightControl("mediasource");e.confirmLightControl();const state=e._hass.states["media_player.qa"],meta=e.entityFor("media_player.qa").media_source;
 state.attributes.source="Radio";meta.index=1;assert.equal(e.stateText(e.cardAt(2)),"Radio");state.attributes.source="Missing";meta.index=null;assert.equal(e.stateText(e.cardAt(2)),e.t("unknown"));
 state.state="unknown";assert.equal(e.stateText(e.cardAt(2)),e.t("unknown"));delete e._hass.states["media_player.qa"];assert.equal(e.stateText(e.cardAt(2)),e.t("offline"));
});

function mediaRepeatEditor() {
 const e=mediaSourceEditor();e.profile.schema_media_repeat=true;const entity=e.entityFor("media_player.qa");
 e._hass.states["media_player.qa"].attributes={supported_features:262144,repeat:"off",media_title:"Track QA"};
 entity.media_repeat={options:["off","one","all"],index:0};entity.actions=[{service:"media_player.repeat_set",fields:{repeat:{type:"select",required:true,options:["off","one","all"]}}}];return e;
}
test("repeat mode reviews one generic choice action and supports local recovery and Undo",()=>{
 const e=mediaRepeatEditor(),before=clone(e._draft);assert.equal(e.mediaRepeatAvailability().ready,true);assert.equal(e.requestLightControl("mediarepeat"),true);
 assert.deepEqual(clone(e._draft),before);assert.equal(e.confirmLightControl(),true);assert.deepEqual(clone(e.cardAt(2).action),{kind:"control",control:"choice",property:"repeat"});
 assert.equal(e.cardControlKind(e.cardAt(2)),"mediarepeat");assert.equal(e.stateText(e.cardAt(2)),"Repeat: Off");assert.equal([...e.inspectorMarkup().matchAll(/<option[^>]*>Choose repeat mode<\/option>/g)].length,1);
 const record={version:1,profile:e.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:e.profile.id,cards:clone(e._draft.cards)}};assert.doesNotThrow(()=>e.validateStoredDraft(record));
 e.history("undo");assert.deepEqual(clone(e._draft),before);
});
test("repeat selection rejects unknown modes, stale capabilities and changed review",()=>{
 for(const change of [e=>{e.profile.schema_media_repeat=false;},e=>{e._hass.states["media_player.qa"].state="off";},e=>{e._hass.states["media_player.qa"].attributes.repeat=null;},e=>{e._hass.states["media_player.qa"].attributes.repeat="OFF";},e=>{e._hass.states["media_player.qa"].attributes.supported_features=8;},e=>{e.entityFor("media_player.qa").media_repeat.index=1;},e=>{e.entityFor("media_player.qa").media_repeat.options.reverse();},e=>{e.entityFor("media_player.qa").actions=[];}]) {
  const e=mediaRepeatEditor();change(e);const before=clone(e._draft);assert.equal(e.requestLightControl("mediarepeat"),false);assert.deepEqual(clone(e._draft),before);
 }
 const e=mediaRepeatEditor(),before=clone(e._draft);e.requestLightControl("mediarepeat");e._hass.states["media_player.qa"].attributes.repeat="all";assert.equal(e.confirmLightControl(),false);assert.deepEqual(clone(e._draft),before);
});
test("repeat caption follows reported mode and HA translation rather than pending target",()=>{
 const e=mediaRepeatEditor();e.requestLightControl("mediarepeat");e.confirmLightControl();const state=e._hass.states["media_player.qa"],meta=e.entityFor("media_player.qa").media_repeat;
 state.attributes.repeat="one";meta.index=1;assert.equal(e.stateText(e.cardAt(2)),"Repeat: One track");
 e._hass.formatEntityAttributeValue=()=>"HA localized";assert.equal(e.stateText(e.cardAt(2)),"Repeat: HA localized");state.attributes.repeat="missing";meta.index=null;assert.equal(e.stateText(e.cardAt(2)),e.t("unknown"));
 state.state="unavailable";assert.equal(e.stateText(e.cardAt(2)),e.t("offline"));
});

test("repeat preview prefers HA measured compact captions only for matching observed metadata",()=>{
 const e=mediaRepeatEditor();e.requestLightControl("mediarepeat");e.confirmLightControl();const meta=e.entityFor("media_player.qa").media_repeat;
 meta.captions={en:"Repeat: Off",pl:"Powt.: wyłączono"};e._hass.locale={language:"pl-PL"};assert.equal(e.stateText(e.cardAt(2)),"Powt.: wyłączono");
 e._hass.states["media_player.qa"].attributes.repeat="one";assert.equal(e.stateText(e.cardAt(2)),e.t("unknown"));
});

test("source preview shares measured caption while full catalogue names remain command values",()=>{
 const e=mediaSourceEditor(),state=e._hass.states["media_player.qa"],meta=e.entityFor("media_player.qa").media_source,name="Bluetooth Living Room Speaker";
 state.attributes.source_list=[name,"HDMI 2 - Salon - Telewizor"];state.attributes.source=name;meta.options=[...state.attributes.source_list];meta.captions={en:"Bluetooth Liv...",pl:"Bluetooth Liv..."};e.entityFor("media_player.qa").actions[0].fields.source.options=[...meta.options];
 e.requestLightControl("mediasource");assert.equal(e.confirmLightControl(),true);assert.equal(e.stateText(e.cardAt(2)),"Bluetooth Liv...");assert.equal(meta.options[0],name);
 state.attributes.source=meta.options[1];assert.equal(e.stateText(e.cardAt(2)),e.t("unknown"));
});

function mediaShuffleEditor() {
 const e=mediaMuteEditor();e.profile.schema_media_shuffle=true;e._hass.states["media_player.qa"].attributes={supported_features:32768,shuffle:false,is_volume_muted:false,repeat:"off",volume_level:.42,media_title:"Track QA"};
 const entity=e.entityFor("media_player.qa");entity.actions=[{service:"media_player.shuffle_set",fields:{shuffle:{type:"boolean",required:true}}}];entity.media_shuffle={state:"playing",features:32768,value:false,text:{en:"In order",pl:"Po kolei"}};return e;
}
test("shuffle and sequential setup are explicit bool drafts with Undo and no playback changes",()=>{
 const e=mediaShuffleEditor(),before=clone(e._draft);assert.equal(e.mediaShuffleReady(),true);assert.equal(e.configureMediaShuffle(true),true);
 assert.deepEqual(clone(e.cardAt(2).action),{kind:"service",service:"media_player.shuffle_set",data:{shuffle:true}});assert.equal(e.stateText(e.cardAt(2)),"In order");assert.match(e.inspectorMarkup(),/aria-label="Shuffle playback"/);
 assert.equal(e.configureMediaShuffle(false),true);e.history("undo");assert.equal(e.cardAt(2).action.data.shuffle,true);e.history("undo");assert.deepEqual(clone(e._draft),before);
 const attrs=e._hass.states["media_player.qa"].attributes;assert.equal(attrs.volume_level,.42);assert.equal(attrs.is_volume_muted,false);assert.equal(attrs.repeat,"off");assert.equal(attrs.media_title,"Track QA");
});
test("shuffle setup rejects stale bool metadata, missing capability and old peers",()=>{
 for(const change of [e=>{e.profile.schema_media_shuffle=false;},e=>{e._status.press_enabled_version=0;},e=>{e._status.context_press_version=0;},e=>{e._hass.states["media_player.qa"].attributes.shuffle="false";},e=>{e._hass.states["media_player.qa"].attributes.supported_features=8;},e=>{e._hass.states["media_player.qa"].state="off";},e=>{e.entityFor("media_player.qa").media_shuffle.value=true;},e=>{e.entityFor("media_player.qa").actions=[];}]) {
  const e=mediaShuffleEditor();change(e);const before=clone(e._draft);assert.equal(e.configureMediaShuffle(true),false);assert.deepEqual(clone(e._draft),before);
 }
 const e=mediaShuffleEditor();for(const value of [1,"true",null])assert.equal(e.configureMediaShuffle(value),false);
});
test("shuffle caption reports observed bool and outages independently of chosen target",()=>{
 const e=mediaShuffleEditor();e.configureMediaShuffle(true);assert.equal(e.stateText(e.cardAt(2)),"In order");const state=e._hass.states["media_player.qa"],meta=e.entityFor("media_player.qa").media_shuffle;
 state.attributes.shuffle=true;meta.value=true;meta.text.en="Shuffle: Yes";assert.equal(e.stateText(e.cardAt(2)),"Shuffle: Yes");state.state="off";assert.equal(e.stateText(e.cardAt(2)),"Off");
 state.state="unavailable";assert.equal(e.stateText(e.cardAt(2)),e.t("offline"));delete e._hass.states["media_player.qa"];assert.equal(e.stateText(e.cardAt(2)),e.t("offline"));
});

function mediaVolumeEditor() {
 const e=mediaShuffleEditor();e.profile.schema_media_volume_actions=true;e._hass.states["media_player.qa"].attributes.supported_features=4;
 const entity=e.entityFor("media_player.qa");entity.actions=[{service:"media_player.volume_up",fields:{}},{service:"media_player.volume_down",fields:{}}];entity.media_volume={state:"playing",features:4,value:.42,operations:["volume_up","volume_down"],text:{en:"Volume: 42 %",pl:"Głośn.: 42 %"}};return e;
}
test("relative volume setup edits empty-data actions with Undo and current percentage preview",()=>{
 const e=mediaVolumeEditor(),before=clone(e._draft);assert.equal(e.mediaVolumeReady(e.cardAt(2),"volume_up"),true);assert.equal(e.configureMediaVolume("volume_up"),true);
 assert.deepEqual(clone(e.cardAt(2).action),{kind:"service",service:"media_player.volume_up",data:{}});assert.equal(e.stateText(e.cardAt(2)),"Volume: 42 %");assert.match(e.inspectorMarkup(),/data-media-volume/);
 assert.equal(e.configureMediaVolume("volume_down"),true);e.history("undo");assert.equal(e.cardAt(2).action.service,"media_player.volume_up");e.history("undo");assert.deepEqual(clone(e._draft),before);
 assert.equal(e._hass.states["media_player.qa"].attributes.volume_level,.42);
});
test("relative volume rejects stale or invalid raw observation and capability changes",()=>{
 for(const change of [e=>{e.profile.schema_media_volume_actions=false;},e=>{e._status.press_enabled_version=0;},e=>{e._hass.states["media_player.qa"].attributes.volume_level="0.5";},e=>{e._hass.states["media_player.qa"].attributes.volume_level=null;},e=>{e._hass.states["media_player.qa"].attributes.volume_level=NaN;},e=>{e._hass.states["media_player.qa"].attributes.volume_level=1.1;},e=>{e._hass.states["media_player.qa"].attributes.supported_features=8;},e=>{e._hass.states["media_player.qa"].state="off";},e=>{e.entityFor("media_player.qa").media_volume.value=.5;},e=>{e.entityFor("media_player.qa").actions=[];}]) {
  const e=mediaVolumeEditor();change(e);const before=clone(e._draft);assert.equal(e.configureMediaVolume("volume_up"),false);assert.deepEqual(clone(e._draft),before);
 }
 const e=mediaVolumeEditor();for(const value of ["set",true,1])assert.equal(e.configureMediaVolume(value),false);
});
test("relative volume captions preserve source precision metadata and handle outages",()=>{
 const e=mediaVolumeEditor();e.configureMediaVolume("volume_down");const state=e._hass.states["media_player.qa"],meta=e.entityFor("media_player.qa").media_volume;
 state.attributes.volume_level=.420000007;meta.value=.420000007;assert.equal(e.stateText(e.cardAt(2)),"Volume: 42 %");assert.equal(e.observedMediaVolume(e.cardAt(2)).value,.420000007);
 state.state="off";assert.equal(e.stateText(e.cardAt(2)),"Off");state.state="unavailable";assert.equal(e.stateText(e.cardAt(2)),e.t("offline"));delete e._hass.states["media_player.qa"];assert.equal(e.stateText(e.cardAt(2)),e.t("offline"));
});

function mediaSoundEditor() {
 const e=remoteActivityEditor(),c=e.cardAt(2);c.entity_id="media_player.qa";e.profile.schema_media_sound_mode=true;
 e._hass.states[c.entity_id]={state:"playing",attributes:{supported_features:65536,sound_mode_list:["Music","Movie"," Żółty "],sound_mode:"Music",media_title:"Track QA"}};
 e._entityIndex.set(c.entity_id,{entity_id:c.entity_id,domain:"media_player",available:true,media_sound_mode:{options:["Music","Movie"," Żółty "],index:0},actions:[{service:"media_player.select_sound_mode",fields:{sound_mode:{type:"select",required:true,options:["Music","Movie"," Żółty "]}}}]});
 e._saved=clone(e._draft);e.entry.layout=clone(e._draft);return e;
}
test("sound modes review one v3 choice action and Undo without media commands",()=>{
 const e=mediaSoundEditor(),before=clone(e._draft),id=e.cardAt(2).id;
 assert.equal(e.mediaSoundAvailability().ready,true);assert.equal(e.requestLightControl("mediasound"),true);assert.deepEqual(clone(e._draft),before);
 assert.equal(e.confirmLightControl(),true);assert.deepEqual(clone(e.cardAt(2).action),{kind:"control",control:"choice",property:"sound_mode"});assert.equal(e._draft.version,3);
 assert.equal(e.cardControlKind(e.cardAt(2)),"mediasound");assert.equal(e.stateText(e.cardAt(2)),"Sound: Music");assert.equal(e.cardAt(2).id,id);
 assert.equal([...e.inspectorMarkup().matchAll(/<option[^>]*>Choose sound mode<\/option>/g)].length,1);assert.match(e.inspectorMarkup(),/data-media-sound/);
 assert.doesNotMatch(e.inspectorMarkup(),/data-media-mute/);
 const record={version:1,profile:e.profile.id,base_revision:4,updated_at:1,layout:{version:3,profile:e.profile.id,cards:clone(e._draft.cards)}};
 assert.doesNotThrow(()=>e.validateStoredDraft(record));e.history("undo");assert.deepEqual(clone(e._draft),before);
});
test("sound modes reject unsupported state, unobserved index, stale list and reviewed changes",()=>{
 for(const change of [e=>{e.profile.schema_media_sound_mode=false;},e=>{e._status.control_kinds=[];},e=>{e._hass.states["media_player.qa"].state="off";},e=>{e._hass.states["media_player.qa"].state="standby";},e=>{e._hass.states["media_player.qa"].attributes.sound_mode=null;},e=>{e._hass.states["media_player.qa"].attributes.supported_features=8;},e=>{e.entityFor("media_player.qa").media_sound_mode.index=1;},e=>{e.entityFor("media_player.qa").actions=[];},e=>{e.entityFor("media_player.qa").media_sound_mode.options.reverse();}]) {
  const e=mediaSoundEditor();change(e);const before=clone(e._draft);assert.equal(e.requestLightControl("mediasound"),false);assert.deepEqual(clone(e._draft),before);
 }
 const e=mediaSoundEditor(),before=clone(e._draft);assert.equal(e.requestLightControl("mediasound"),true);e._hass.states["media_player.qa"].attributes.sound_mode="Movie";assert.equal(e.confirmLightControl(),false);assert.deepEqual(clone(e._draft),before);
});
test("sound mode caption uses observed source and never falls back to first or track title",()=>{
 const e=mediaSoundEditor();e.requestLightControl("mediasound");e.confirmLightControl();const state=e._hass.states["media_player.qa"],meta=e.entityFor("media_player.qa").media_sound_mode;
 state.attributes.sound_mode="Movie";meta.index=1;assert.equal(e.stateText(e.cardAt(2)),"Sound: Movie");state.attributes.sound_mode="Missing";meta.index=null;assert.equal(e.stateText(e.cardAt(2)),e.t("unknown"));
 state.state="unknown";assert.equal(e.stateText(e.cardAt(2)),e.t("unknown"));delete e._hass.states["media_player.qa"];assert.equal(e.stateText(e.cardAt(2)),e.t("offline"));
});


test("sound mode compact caption preserves full service labels and native choices",()=>{
 const e=mediaSoundEditor(),entity=e.entityFor("media_player.qa"),state=e._hass.states[entity.entity_id];
 const name="Dolby Surround Living Room";state.attributes.sound_mode_list=[name,"Movie"];state.attributes.sound_mode=name;
 entity.media_sound_mode={options:[name,"Movie"],index:0,captions:{en:"Sound: Dolby...",pl:"Tryb: Dolby..."}};
 entity.actions=[{service:"media_player.select_sound_mode",fields:{sound_mode:{type:"select",required:true,options:[name,"Movie"]}}}];
 assert.equal(e.requestLightControl("mediasound"),true);assert.equal(e.confirmLightControl(),true);
 assert.equal(e.stateText(e.cardAt(2)),"Sound: Dolby...");assert.equal(entity.media_sound_mode.options[0],name);
 assert.deepEqual(clone(e.cardAt(2).action),{kind:"control",control:"choice",property:"sound_mode"});
});

function mediaStopEditor() {
 const e=mediaVolumeEditor(),card=e.cardAt(2),entity=e.entityFor(card.entity_id);e.profile.schema_media_stop=true;
 e._hass.states[card.entity_id]={state:"playing",attributes:{supported_features:4096,media_title:"Track QA"}};
 entity.media_stop={state:"playing",features:4096,eligible:true,text:{en:"State: Playing",pl:"Stan: Odtwarzanie"}};
 entity.actions=[{service:"media_player.media_stop",fields:{}}];e._saved=clone(e._draft);e.entry.layout=clone(e._draft);return e;
}
test("Stop draft shortcut has no data, preserves identity and supports Undo and stored recovery",()=>{
 const e=mediaStopEditor(),before=clone(e._draft),id=e.cardAt(2).id;
 assert.equal(Boolean(e.mediaStopReady()),true);assert.equal(e.configureMediaStop(),true);
 assert.deepEqual(clone(e.cardAt(2).action),{kind:"service",service:"media_player.media_stop",data:{}});
 assert.equal(e.cardAt(2).id,id);assert.equal(e.stateText(e.cardAt(2)),"State: Playing");
 assert.match(e.inspectorMarkup(),/data-media-stop/);assert.equal(e.serviceLabel("media_player.media_stop"),"Stop playback");
 const record={version:1,profile:e.profile.id,base_revision:4,updated_at:1,layout:{version:e._draft.version,profile:e.profile.id,cards:clone(e._draft.cards)}};
 assert.doesNotThrow(()=>e.validateStoredDraft(record));e.history("undo");assert.deepEqual(clone(e._draft),before);
});
test("Stop is configurable while known inactive but its observed eligibility remains false",()=>{
 for(const power of ["on","idle","off","standby"]){
  const e=mediaStopEditor(),state=e._hass.states["media_player.qa"],meta=e.entityFor("media_player.qa").media_stop;
  state.state=meta.state=power;meta.eligible=false;meta.text.en="State: "+power;
  assert.equal(Boolean(e.mediaStopReady()),true);assert.equal(e.configureMediaStop(),true);
  assert.equal(e.observedMediaStop(e.cardAt(2)).eligible,false);assert.equal(e.stateText(e.cardAt(2)),"State: "+power);
 }
});
test("Stop setup rejects stale metadata, unknown states, lost support and unnegotiated peers",()=>{
 for(const change of [e=>{e.profile.schema_media_stop=false;},e=>{e._status.press_enabled_version=0;},e=>{e._hass.states["media_player.qa"].state="unknown";},e=>{e._hass.states["media_player.qa"].attributes.supported_features=0;},e=>{e.entityFor("media_player.qa").media_stop.eligible=false;},e=>{e.entityFor("media_player.qa").media_stop.state="paused";},e=>{e.entityFor("media_player.qa").actions=[];},e=>{e.entityFor("media_player.qa").actions[0].fields=[];},e=>{e.cardAt(2).visible=false;}]){
  const e=mediaStopEditor();change(e);const before=clone(e._draft);assert.equal(e.configureMediaStop(),false);assert.deepEqual(clone(e._draft),before);
 }
});
test("Stop caption describes observed playback and outages rather than its intended idle result",()=>{
 const e=mediaStopEditor();e.configureMediaStop();const state=e._hass.states["media_player.qa"],meta=e.entityFor("media_player.qa").media_stop;
 state.state=meta.state="paused";meta.text.en="State: Paused";assert.equal(e.stateText(e.cardAt(2)),"State: Paused");
 state.state="unknown";assert.equal(e.stateText(e.cardAt(2)),e.t("unknown"));
 state.state="unavailable";assert.equal(e.stateText(e.cardAt(2)),e.t("offline"));
 delete e._hass.states["media_player.qa"];assert.equal(e.stateText(e.cardAt(2)),e.t("offline"));
});

function mediaVolumeTargetEditor() {
 const e=mediaVolumeEditor(),entity=e.entityFor("media_player.qa");e.profile.schema_media_volume_target=true;
 entity.actions=[{service:"media_player.volume_set",fields:{volume_level:{type:"number",min:0,max:1,required:true}}}];
 e._hass.states["media_player.qa"].attributes.volume_level=.425;
 entity.media_volume_target={state:"playing",features:4,value:.425,text:{en:"Volume: 42.5 %",pl:"Głośn.: 42,5 %"}};
 return e;
}
test("fixed volume setup preserves raw initial level and percent input never sends a command",()=>{
 const e=mediaVolumeTargetEditor(),before=clone(e._draft),source=clone(e._hass.states["media_player.qa"]);
 assert.equal(Boolean(e.mediaVolumeTargetReady()),true);assert.equal(e.configureMediaVolumeTarget(),true);
 assert.deepEqual(clone(e.cardAt(2).action),{kind:"service",service:"media_player.volume_set",data:{volume_level:.425}});
 assert.equal(e.stateText(e.cardAt(2)),"Volume: 42.5 %");
 const markup=e.inspectorMarkup();assert.match(markup,/Target volume \(%\)/);assert.match(markup,/value="42.5"/);assert.match(markup,/data-media-volume-target/);
 const descriptor=e.entityFor("media_player.qa").actions[0].fields.volume_level;
 for(const [percent,target]of [["0",0],["47.25",.4725],["100",1]])assert.equal(e.parseFieldValue({value:percent,dataset:{field:"data:volume_level"}},descriptor),target);
 assert.deepEqual(clone(e._hass.states["media_player.qa"]),source);e.history("undo");assert.deepEqual(clone(e._draft),before);
});
test("fixed volume percent input validates displayed units without affecting other numeric fields",()=>{
 const e=mediaVolumeTargetEditor();e.configureMediaVolumeTarget();const descriptor={type:"number",min:0,max:1,required:true};
 for(const value of [""," ","-0.1","100.001","NaN","Infinity"])assert.throws(()=>e.parseFieldValue({value,dataset:{field:"data:volume_level"}},descriptor));
 assert.equal(e.parseFieldValue({value:".25",dataset:{field:"data:brightness_pct"}},{type:"number",min:0,max:100}),.25);
});
test("fixed volume setup rejects stale metadata, step-only support and missing press negotiation",()=>{
 for(const change of [e=>{e.profile.schema_media_volume_target=false;},e=>{e._status.press_enabled_version=0;},e=>{e._status.context_press_version=0;},e=>{e._hass.states["media_player.qa"].attributes.supported_features=1024;},e=>{e._hass.states["media_player.qa"].attributes.volume_level=.426;},e=>{e._hass.states["media_player.qa"].state="off";},e=>{e.entityFor("media_player.qa").actions=[];},e=>{e.entityFor("media_player.qa").actions[0].fields.volume_level.max=100;},e=>{e.entityFor("media_player.qa").actions[0].fields.extra={};},e=>{e.cardAt(2).visible=false;}]) {
  const e=mediaVolumeTargetEditor();change(e);const before=clone(e._draft);assert.equal(e.configureMediaVolumeTarget(),false);assert.deepEqual(clone(e._draft),before);
 }
});
test("fixed volume preview remains observed until feedback and stored drafts retain exact target",()=>{
 const e=mediaVolumeTargetEditor();e.configureMediaVolumeTarget();e.cardAt(2).action.data.volume_level=.4725;
 assert.equal(e.stateText(e.cardAt(2)),"Volume: 42.5 %");
 const record={version:1,profile:e.profile.id,base_revision:4,updated_at:1,layout:clone({version:e._draft.version,profile:e._draft.profile,cards:e._draft.cards})};assert.doesNotThrow(()=>e.validateStoredDraft(record));
 for(const value of [true,"0.5",-1,1.1]){const bad=clone(record);bad.layout.cards.find(c=>c.id===e.cardAt(2).id).action.data.volume_level=value;assert.throws(()=>e.validateStoredDraft(bad));}
 const state=e._hass.states["media_player.qa"],meta=e.entityFor("media_player.qa").media_volume_target;
 state.attributes.volume_level=meta.value=.4725;meta.text.en="Volume: 47.2 %";assert.equal(e.stateText(e.cardAt(2)),"Volume: 47.2 %");
 state.state="unavailable";assert.equal(e.stateText(e.cardAt(2)),e.t("offline"));
 delete e._hass.states["media_player.qa"];assert.equal(e.stateText(e.cardAt(2)),e.t("offline"));
});

function extraPanelEditor(domain="sensor",type=domain==="lock"?"entity":"sensor") {
 const e=lightEditor(),card=e.cardAt(2),family=domain==="lock"?"lock":"info";
 card.entity_id=`${domain}.test`;card.type=type;card.action={kind:type==="sensor"?"none":"default"};
 e.profile.schema_control_types.push("panel");e.profile.schema_panel_extra_profiles=[{name:"info",version:1},{name:"lock",version:1}];
 e.profile.schema_calendar_next=true;e.profile.calendar_text_slots=[2,13];
 Object.assign(e._status,{entity_control_status:"ready",native_control_types:["entity_control_v1"],control_kinds:["light","panel"],panel_extra_profiles:clone(e.profile.schema_panel_extra_profiles)});
 const caps=family==="lock"?{lock:true}:{info_type:domain==="alarm_control_panel"?"alarm":domain,device_class:domain==="binary_sensor"?"moisture":domain==="sensor"?"temperature":null};
 const state={source:"known",updated_text:"2026-11-04T12:00:00+01:00",...({
  sensor:{value_status:"value",value_text:"21.8",unit_text:"°C"},binary_sensor:{text_status:"value",state_text:"Wet",active:true},
  alarm_control_panel:{text_status:"value",state_text:"Disarmed",phase:"disarmed"},lock:{phase:"unlocked"},
  calendar:{event:"present",active:false,summary:"Team meeting",start_text:"2026-11-05 10:00:00",end_text:"2026-11-05 11:00:00",zone_text:"Europe/Warsaw",all_day:false,location:"Office",description:"Planning",truncated_fields:0},
 })[domain]};
 e._hass.states[card.entity_id]={state:({sensor:"21.8",binary_sensor:"on",alarm_control_panel:"disarmed",lock:"unlocked",calendar:"off"})[domain],attributes:{...(caps.device_class?{device_class:caps.device_class}:{})},last_updated:"2026-11-04T11:00:00.999Z"};
 e._entityIndex.set(card.entity_id,{entity_id:card.entity_id,domain,available:true,extra_panel:{version:1,panel_type:family,caps,state,fingerprint:"b".repeat(64),available:true,eligible_actions:family==="lock"?1:0},actions:family==="lock"?[{service:"lock.lock",fields:{}}]:[]});
 return e;
}
function agendaEditor(type="sensor") {
 const e=extraPanelEditor("calendar",type);e._selectedSlot=2;
 e.profile.schema_info_agenda_version=1;e._status.info_agenda_version=1;
 e.entityFor(e.cardAt(2).entity_id).agenda={version:1,read_only:true};
 return e;
}
function statisticsEditor(type="sensor") {
 const e=extraPanelEditor("sensor",type);e._selectedSlot=2;
 e.profile.schema_info_statistics_version=1;e._status.info_statistics_version=1;
 e.entityFor(e.cardAt(2).entity_id).statistics={version:1,read_only:true,hours:24};
 return e;
}

test("Statistics129 saved inspector keeps the selected action and offers Info",()=>{
 for(const type of ["sensor","entity"]) {
  const e=statisticsEditor(type);e.requestLightControl("statisticspanel");e.confirmLightControl();
  const before=clone(e._draft),markup=e.inspectorMarkup();
  const option=markup.match(/<option value="control-statisticspanel"[^>]*>/g);
  assert.equal(option?.length,1);assert.match(option[0],/\bselected\b/);
  assert.match(markup,/<option value="control-infopanel"/);
  assert.doesNotMatch(markup,/<option value="none"[^>]*\bselected\b/);
  assert.deepEqual(clone(e._draft),before);
 }
});

test("Statistics129 has one truthful hint and retains unavailable saved action",()=>{
 const e=statisticsEditor();e.requestLightControl("statisticspanel");e.confirmLightControl();
 const before=clone(e._draft);
 assert.equal(e.inspectorMarkup().split(e.t("statisticsHint")).length-1,1);
 e._status.info_statistics_version=0;
 const markup=e.inspectorMarkup();
 assert.match(markup,/<option value="control-statisticspanel"[^>]*selected[^>]*disabled/);
 assert.equal(markup.split(e.t("statisticsHint")).length-1,0);
 assert.equal(markup.split(e.t("statisticsUnavailable")).length-1,1);
 assert.match(markup,/<option value="control-infopanel"/);
 assert.deepEqual(clone(e._draft),before);
});

test("Statistics129 returning to Info is review draft and Undo only",()=>{
 const e=statisticsEditor();e.requestLightControl("statisticspanel");e.confirmLightControl();
 const before=clone(e._draft);e._saved=clone(before);
 assert.equal(e.requestLightControl("infopanel"),true);assert.deepEqual(clone(e._draft),before);
 assert.equal(e.confirmLightControl(),true);assert.equal(e.cardAt(2).action.property,"info");
 assert.match(e.inspectorMarkup(),/<option value="control-infopanel"[^>]*selected/);
 assert.deepEqual(clone(e._saved),before);e.history("undo");assert.deepEqual(clone(e._draft),before);
});

test("Statistics explicit review preserves Info and changes only draft with Undo",()=>{
 for(const type of ["sensor","entity"]) {
  const e=statisticsEditor(type);enableExtra(e);const before=clone(e._draft);e._saved=clone(before);
  assert.equal(e.statisticsAvailability().ready,true);assert.equal(e.cardAt(2).action.property,"info");
  assert.match(e.inspectorMarkup(),/value="control-statisticspanel"/);
  assert.equal(e.requestLightControl("statisticspanel"),true);assert.deepEqual(clone(e._draft),before);
  assert.match(e.modalMarkup(),/hourly statistics/);assert.equal(e.confirmLightControl(),true);
  assert.deepEqual(clone(e.cardAt(2).action),{kind:"control",control:"panel",property:"statistics"});
  assert.equal(e.cardAt(2).type,type);assert.equal(e.cardControlKind(e.cardAt(2)),"statisticspanel");
  assert.equal(e.stateText(e.cardAt(2)),"Hourly statistics");assert.doesNotThrow(()=>e.validateStoredDraft(extraStored(e)));
  assert.deepEqual(clone(e._saved),before);assert.match(e.inspectorMarkup(),/data-statistics-panel/);
  e.history("undo");assert.deepEqual(clone(e._draft),before);
 }
});

test("Statistics closed capability metadata and current negotiation gate both review phases",()=>{
 for(const change of [e=>delete e._status.info_statistics_version,e=>e._status.info_statistics_version=true,
  e=>e._status.panel_extra_profiles=[],e=>e.profile.schema_info_statistics_version=0,e=>e._status.entity_control_status="offline",
  e=>e._hass.connected=false,e=>e._profileStale=true,e=>delete e.entityFor(e.cardAt(2).entity_id).statistics,
  e=>e.entityFor(e.cardAt(2).entity_id).statistics.version=true,e=>e.entityFor(e.cardAt(2).entity_id).statistics.extra=1,
  e=>e.entityFor(e.cardAt(2).entity_id).statistics.hours=48,e=>e.entityFor(e.cardAt(2).entity_id).statistics.read_only=1,
  e=>e.cardAt(2).entity_id="calendar.test",e=>e.cardAt(2).visible=false]) {
  const e=statisticsEditor();change(e);
  assert.equal(e.statisticsAvailability().ready,false);assert.equal(e.requestLightControl("statisticspanel"),false);
  assert.equal(e._pending,null);
 }
 for(const change of [e=>e._status.info_statistics_version=0,e=>e._entryId="screen-b",e=>e._hass.user={id:"other"},
  e=>e.entityFor(e.cardAt(2).entity_id).statistics.hours=48]) {
  const e=statisticsEditor();assert.equal(e.requestLightControl("statisticspanel"),true);change(e);
  assert.equal(e.confirmLightControl(),false);assert.equal(e.cardAt(2).action.kind,"none");
 }
});

test("Statistics stored action rejects arbitrary fields wrong domain and v2",()=>{
 const e=statisticsEditor();e.requestLightControl("statisticspanel");e.confirmLightControl();
 for(const change of [r=>r.layout.version=2,r=>r.layout.cards[1].action.url="http://example.test",
  r=>r.layout.cards[1].action.hours=24,r=>r.layout.cards[1].action.data={},
  r=>r.layout.cards[1].entity_id="calendar.test",r=>r.layout.cards[1].type="action"]) {
  const r=extraStored(e);change(r);assert.throws(()=>e.validateStoredDraft(r));
 }
});

test("Statistics saved launcher reads only catalogue without Recorder or device commands",async()=>{
 const e=statisticsEditor();e.requestLightControl("statisticspanel");e.confirmLightControl();
 const c=e.cardAt(2),row=clone(e.entityFor(c.entity_id)),before=clone(e._draft),calls=[];
 e._selectedSlot=null;e._entityIndex.delete(c.entity_id);let finish;
 e._hass.callWS=message=>{calls.push(message);return new Promise(resolve=>finish=resolve);};
 const pending=e.fetchPreviewEntities();assert.equal(calls.length,1);
 assert.equal(calls[0].type,"atmosfera_echo_hub/catalogue/get");
 finish({entities:[row],total:1,truncated:false});await Promise.all(pending);
 assert.equal(e.stateText(c),"Hourly statistics");assert.deepEqual(clone(e._draft),before);
});

test("Agenda explicit review preserves Info and changes only draft until Save with Undo",()=>{
 for(const type of ["sensor","entity"]) {
  const e=agendaEditor(type);enableExtra(e);const before=clone(e._draft);e._saved=clone(before);
  assert.equal(e.agendaAvailability().ready,true);assert.equal(e.cardAt(2).action.property,"info");
  assert.match(e.inspectorMarkup(),/value="control-agendapanel"/);
  assert.equal(e.requestLightControl("agendapanel"),true);assert.deepEqual(clone(e._draft),before);
  assert.match(e.modalMarkup(),/dedicated agenda/);assert.equal(e.confirmLightControl(),true);
  assert.deepEqual(clone(e.cardAt(2).action),{kind:"control",control:"panel",property:"agenda"});
  assert.equal(e.cardAt(2).type,type);assert.equal(e.cardControlKind(e.cardAt(2)),"agendapanel");
  assert.equal(e.stateText(e.cardAt(2)),"Open agenda");assert.doesNotThrow(()=>e.validateStoredDraft(extraStored(e)));
  assert.deepEqual(clone(e._saved),before);assert.match(e.inspectorMarkup(),/data-agenda-panel/);
  e.history("undo");assert.deepEqual(clone(e._draft),before);
 }
});

test("Agenda requires independent current negotiation and loaded calendar metadata",()=>{
 for(const change of [e=>delete e._status.info_agenda_version,e=>e._status.info_agenda_version=true,
  e=>e._status.panel_extra_profiles=[],e=>e.profile.schema_info_agenda_version=0,e=>e._status.entity_control_status="offline",
  e=>e._hass.connected=false,e=>e._profileStale=true,e=>delete e.entityFor(e.cardAt(2).entity_id).agenda,
  e=>e.entityFor(e.cardAt(2).entity_id).agenda.version=true,e=>e.entityFor(e.cardAt(2).entity_id).agenda.secret=1,
  e=>e.cardAt(2).entity_id="sensor.test",e=>e.cardAt(2).visible=false]) {
  const e=agendaEditor(),before=clone(e._draft);change(e);
  assert.equal(e.agendaAvailability().ready,false);assert.equal(e.requestLightControl("agendapanel"),false);
  assert.equal(e._pending,null);
 }
 const e=agendaEditor();assert.equal(e.requestLightControl("agendapanel"),true);
 e._status.info_agenda_version=0;assert.equal(e.confirmLightControl(),false);
 assert.equal(e.cardAt(2).action.kind,"none");
});

test("Agenda closed stored action never admits arbitrary fields, wrong domain or v2",()=>{
 const e=agendaEditor();e.requestLightControl("agendapanel");e.confirmLightControl();
 for(const change of [r=>r.layout.version=2,r=>r.layout.cards[1].action.url="http://example.test",
  r=>r.layout.cards[1].action.data={},r=>r.layout.cards[1].action.duration=7,
  r=>r.layout.cards[1].entity_id="sensor.test",r=>r.layout.cards[1].type="action"]) {
  const r=extraStored(e);change(r);assert.throws(()=>e.validateStoredDraft(r));
 }
});

test("Agenda saved launcher fetches visible metadata without opening provider events",async()=>{
 const e=agendaEditor();e.requestLightControl("agendapanel");e.confirmLightControl();
 const c=e.cardAt(2),row=clone(e.entityFor(c.entity_id)),before=clone(e._draft),calls=[];
 e._selectedSlot=null;e._entityIndex.delete(c.entity_id);let finish;
 e._hass.callWS=message=>{calls.push(message);return new Promise(resolve=>finish=resolve);};
 const pending=e.fetchPreviewEntities();assert.equal(calls.length,1);
 assert.equal(calls[0].type,"atmosfera_echo_hub/catalogue/get");
 finish({entities:[row],total:1,truncated:false});await Promise.all(pending);
 assert.equal(e.stateText(c),"Open agenda");assert.deepEqual(clone(e._draft),before);
});
function extraStored(e) {
 return {version:1,profile:e.profile.id,base_revision:4,updated_at:1,layout:{version:e._draft.version,profile:e.profile.id,cards:clone(e._draft.cards)}};
}
function enableExtra(e) {
 const family=e.extraPanelFamily(e.cardAt(2));assert.equal(e.requestLightControl(family+"panel"),true);assert.equal(e.confirmLightControl(),true);
}

test("Extra profiles are explicit draft-only choices for all five families and both Info card types",()=>{
 for(const domain of ["sensor","binary_sensor","calendar","alarm_control_panel","lock"]) for(const type of domain==="lock"?["entity"]:["entity","sensor"]) {
  const e=extraPanelEditor(domain,type),before=clone(e._draft),family=e.extraPanelFamily(e.cardAt(2));
  assert.equal(e.extraPanelAvailability().ready,true);assert.deepEqual(clone(e._draft),before);
  assert.match(e.inspectorMarkup(),new RegExp(`value="control-${family}panel"`));
  e.editField(actionInput(`control-${family}panel`));assert.deepEqual(clone(e._draft),before);
  assert.match(e.modalMarkup(),/no service is called|No service is called/);
  assert.equal(e.confirmLightControl(),true);assert.deepEqual(clone(e.cardAt(2).action),{kind:"control",control:"panel",property:family});
  assert.equal(e._draft.version,3);assert.doesNotThrow(()=>e.validateStoredDraft(extraStored(e)));
  assert.equal(e.cardAt(2).type,type);e.history("undo");assert.deepEqual(clone(e._draft),before);
 }
});

test("Extra negotiation cannot fall back to old Panel v1 or detail feature flags",()=>{
 for(const change of [e=>delete e._status.panel_extra_profiles,e=>e._status.panel_extra_profiles=[],e=>e._status.panel_extra_profiles=[{name:"info",version:2}],
  e=>e._status.panel_extra_profiles=[{name:"info",version:1},{name:"info",version:1}],e=>e._status.panel_extra_profiles=[{name:"info",version:1,extra:true}],
  e=>e.profile.schema_panel_extra_profiles=[{name:"lock",version:1}],e=>e._status.native_control_types=[],e=>e._status.control_kinds=[],e=>e._status.entity_control_status="offline",
  e=>e._status.device_available=false,e=>e._hass.connected=false,e=>e._profileStale=true,e=>e.profile.layout_versions=[2],e=>e.profile.schema_control_types=[]]) {
  const e=extraPanelEditor(),before=clone(e._draft);Object.assign(e._status,{panel_version:1,panel_types:["timer","remote","power"],detail_version:1,climate_panel_version:1});change(e);
  assert.equal(e.requestLightControl("infopanel"),false);assert.deepEqual(clone(e._draft),before);
 }
 const e=extraPanelEditor();e._status.panel_extra_profiles.push({name:"future_profile",version:2});assert.equal(e.extraPanelAvailability().ready,true);
 assert.equal(e.panelControlAvailability(e.cardAt(2),"info").ready,false);
});

test("Extra review fingerprints exclude observations but detect capability and binding changes",()=>{
 for(const domain of ["sensor","binary_sensor","calendar","alarm_control_panel","lock"]) {
  const e=extraPanelEditor(domain);e.requestLightControl(e.extraPanelFamily(e.cardAt(2))+"panel");
  e._hass.states[e.cardAt(2).entity_id].state="unavailable";
  e._hass.states[e.cardAt(2).entity_id].last_updated="2026-11-04T13:00:00Z";
  assert.equal(e.confirmLightControl(),true);
 }
 for(const change of [e=>e.entityFor(e.cardAt(2).entity_id).extra_panel.fingerprint="c".repeat(64),
  e=>e._hass.states[e.cardAt(2).entity_id].attributes.device_class="humidity",e=>e._status.panel_extra_profiles=[],
  e=>delete e._hass.states[e.cardAt(2).entity_id],e=>e._selectionEpoch++]) {
  const e=extraPanelEditor(),before=clone(e._draft);e.requestLightControl("infopanel");change(e);assert.equal(e.confirmLightControl(),false);assert.deepEqual(clone(e._draft),before);
 }
 const e=extraPanelEditor("lock");e.requestLightControl("lockpanel");e.entityFor(e.cardAt(2).entity_id).actions=[];assert.equal(e.confirmLightControl(),false);
});

test("Info and Lock admit unknown sources and service-less locks only for passive opening",()=>{
 for(const domain of ["sensor","binary_sensor","calendar","alarm_control_panel","lock"]) {
  const e=extraPanelEditor(domain);e._hass.states[e.cardAt(2).entity_id].state="unknown";assert.equal(e.extraPanelAvailability().ready,true);enableExtra(e);
  assert.doesNotMatch(e.extraPanelPreviewMarkup(e.cardAt(2)),/21.8|Wet|Team meeting|unlocked|Disarmed/);
 }
 const e=extraPanelEditor("lock"),m=e.entityFor(e.cardAt(2).entity_id);m.extra_panel.caps.lock=false;m.extra_panel.eligible_actions=0;m.actions=[];
 assert.equal(e.extraPanelAvailability().ready,true);assert.equal(e.extraPanelAvailability().reason,"extraLockPassive");enableExtra(e);
 assert.deepEqual(clone(e.cardAt(2).action),{kind:"control",control:"panel",property:"lock"});
 assert.doesNotMatch(e.extraPanelPreviewMarkup(e.cardAt(2)),/data-action|<button/);
});

test("Stored Extra launchers survive offline negotiation loss without silently replacing intent",()=>{
 for(const domain of ["sensor","calendar","lock"]) {
  const e=extraPanelEditor(domain);enableExtra(e);const record=extraStored(e),family=e.extraPanelFamily(e.cardAt(2));e._status.panel_extra_profiles=[];
  assert.match(e.inspectorMarkup(),new RegExp(`value="control-${family}panel" selected disabled`));assert.doesNotThrow(()=>e.validateStoredDraft(record));
  for(const patch of [{property:"unlock"},{property:family==="info"?"lock":"info"},{detail:1},{initial_duration:120},{service:"lock.unlock"},{data:{}},{extra:true}]) {
   const bad=clone(record);Object.assign(bad.layout.cards.find(c=>c.slot===2).action,patch);assert.throws(()=>e.validateStoredDraft(bad));
  }
  const bad=clone(record);bad.layout.version=2;assert.throws(()=>e.validateStoredDraft(bad));
 }
});

test("Information sensor cards expose only None and the explicit Info choice",()=>{
 const e=extraPanelEditor(),markup=e.inspectorMarkup(),select=markup.match(/<select data-field="action-kind"[^>]*>(.*?)<\/select>/s)[0];
 assert.doesNotMatch(select,/disabled|value="default"|value="service"/);assert.match(select,/value="none"/);assert.match(select,/value="control-infopanel"/);
 enableExtra(e);const before=clone(e.cardAt(2).action);e.editField(actionInput("service"));assert.deepEqual(clone(e.cardAt(2).action),before);
 const input=value=>({dataset:{field:"type"},value,removeAttribute(){},setAttribute(){}});
 e.editField(input("entity"));assert.deepEqual(clone(e.cardAt(2).action),before);e.editField(input("sensor"));assert.deepEqual(clone(e.cardAt(2).action),before);
 e.editField(input("action"));assert.deepEqual(clone(e.cardAt(2).action),{kind:"none"});
 const old=makeEditor();old._selectedSlot=2;old.cardAt(2).type="sensor";assert.equal(old.sensorActionEditable(old.cardAt(2)),false);
});

test("Calendar Info explicitly extends placement while legacy Calendar stays restricted",()=>{
 const e=extraPanelEditor("calendar");assert.equal(e.acceptsCard(e.slotAt(11),e.cardAt(2)),false);enableExtra(e);
 assert.equal(e.acceptsCard(e.slotAt(11),e.cardAt(2)),true);assert.equal(e.groupTargetCompatible(e.cardAt(2),11),true);
 assert.equal(e.acceptsCard(e.slotAt(0),e.cardAt(2)),false);assert.equal(e.moveCard(2,11),true);assert.doesNotThrow(()=>e.validateStoredDraft(extraStored(e)));
 const bad=extraStored(e);bad.layout.cards.find(c=>c.slot===11).action={kind:"none"};assert.throws(()=>e.validateStoredDraft(bad));
 e._selectedSlot=11;e.editField(actionInput("none"));assert.equal(e.cardAt(11).action.property,"info");
 assert.doesNotThrow(()=>e.validateStoredDraft(extraStored(e)));
});

test("Info telemetry changes do not invalidate a pending capability review",()=>{
 const e=extraPanelEditor();e.requestLightControl("infopanel");const m=e.entityFor(e.cardAt(2).entity_id).extra_panel;
 m.state.value_text="22.1";m.state.updated_text="2026-11-04T13:01:00+01:00";
 e._hass.states[e.cardAt(2).entity_id].state="22.1";assert.equal(e.confirmLightControl(),true);
});

test("Extra metadata rejects malformed fields, wrong families and invented eligibility",()=>{
 for(const change of [m=>m.caps.info_type="alarm",m=>m.caps.device_class="Not a class",m=>m.caps.other=true,m=>m.version=true,
  m=>m.fingerprint="bad",m=>m.eligible_actions=1,m=>m.available=false,m=>m.state.extra="bad",m=>m.state.value_text="x".repeat(97),
  m=>m.state.unit_text="u".repeat(25),m=>m.state.updated_text="t".repeat(49),m=>m.state.value_status="too_long",m=>m.state.value_text="\ud800",m=>m.state.value_text="x\ny"]) {
  const e=extraPanelEditor();change(e.entityFor(e.cardAt(2).entity_id).extra_panel);assert.equal(e.extraPanelMetadata(e.cardAt(2)),null);assert.equal(e.extraPanelAvailability().ready,false);
 }
 for(const change of [m=>m.caps.lock="true",m=>m.caps.unlock=true,m=>m.state.phase="disarmed",m=>m.eligible_actions=0]) {
  const e=extraPanelEditor("lock");change(e.entityFor(e.cardAt(2).entity_id).extra_panel);assert.equal(e.extraPanelMetadata(e.cardAt(2)),null);
 }
});

test("Every actual backend observation fixture validates in the editor without widening its wire schema",()=>{
 const fixtures=JSON.parse(fs.readFileSync(path.join(__dirname,"fixtures/extra_panel/observations.json"),"utf8"));
 for(const [name,fixture] of Object.entries(fixtures)) {
  const domain=name.split(".")[0],e=extraPanelEditor(domain),v=fixture.value,m=e.entityFor(e.cardAt(2).entity_id).extra_panel;
  Object.assign(m,{panel_type:v.panel_type,caps:v.panel_caps,state:v.panel_state,available:v.available,eligible_actions:v.eligible_actions});
  assert.notEqual(e.extraPanelMetadata(e.cardAt(2)),null,name);
 }
});

test("Extra previews never leak stale values or events after loss of source or a newer HA update",()=>{
 for(const domain of ["sensor","binary_sensor","calendar","alarm_control_panel","lock"]) {
  for(const next of ["unknown","unavailable","newer","missing","disconnected"]) {
   const e=extraPanelEditor(domain);enableExtra(e);const id=e.cardAt(2).entity_id,old=e.extraPreview(e.cardAt(2)).message;
   assert.ok(e.extraPanelPreviewMarkup(e.cardAt(2)).includes(old));
   if(next==="disconnected")e._hass.connected=false;else if(next==="newer")e._hass.states[id].last_updated="2026-11-04T12:00:01Z";else if(next==="missing")delete e._hass.states[id];else e._hass.states[id].state=next;
   const html=e.extraPanelPreviewMarkup(e.cardAt(2));assert.ok(!html.includes(old),`${domain} ${next}`);assert.doesNotMatch(html,/Team meeting|Planning|21.8|Wet/);
  }
 }
});

test("Sensor, Binary and Alarm show explicit invalid or over-limit status instead of empty or truncated observations",()=>{
 for(const domain of ["sensor","binary_sensor","alarm_control_panel"]) for(const status of ["too_long","invalid","empty"]) {
  const e=extraPanelEditor(domain);enableExtra(e);const m=e.entityFor(e.cardAt(2).entity_id).extra_panel,state=m.state,sensor=domain==="sensor";
  state[sensor?"value_status":"text_status"]=status;state[sensor?"value_text":"state_text"]="";
  assert.notEqual(e.extraPanelMetadata(e.cardAt(2)),null);const html=e.extraPanelPreviewMarkup(e.cardAt(2));
  assert.match(html,new RegExp(status==="too_long"?"complete value exceeds":status==="invalid"?"supported observation":"empty value"));
  state[sensor?"value_text":"state_text"]="prefix";assert.equal(e.extraPanelMetadata(e.cardAt(2)),null);assert.doesNotMatch(e.extraPanelPreviewMarkup(e.cardAt(2)),/prefix/);
 }
});

test("Calendar preview keeps dates and zones complete and labels only descriptive excerpts",()=>{
 const e=extraPanelEditor("calendar");enableExtra(e);const m=e.entityFor(e.cardAt(2).entity_id).extra_panel;
 Object.assign(m.state,{summary:"<script>alert(1)</script>",description:"short…",truncated_fields:5,all_day:true,start_text:"2026-10-24",end_text:"2026-10-26"});
 const html=e.extraPanelPreviewMarkup(e.cardAt(2));assert.match(html,/&lt;script&gt;/);assert.doesNotMatch(html,/<script>/);
 assert.equal((html.match(/Description excerpt/g)||[]).length,2);assert.match(html,/2026-10-24/);assert.match(html,/2026-10-26/);assert.doesNotMatch(html,/2026-10-27/);assert.match(html,/Europe\/Warsaw/);assert.match(html,/<strong>End<\/strong>/);assert.doesNotMatch(html,/exclusive for all-day/);assert.match(html,/All-day event/);
 m.state.truncated_fields=8;assert.equal(e.extraPanelMetadata(e.cardAt(2)),null);
});

test("Binary moisture preview uses the actual device class and never invents a door contact",()=>{
 const e=extraPanelEditor("binary_sensor");e.cardAt(2).title="Kontakt";enableExtra(e);assert.equal(e.extraPanelIcon(e.cardAt(2)),"mdi:water-alert-outline");
 assert.match(e.extraPanelPreviewMarkup(e.cardAt(2)),/mdi:water-alert-outline/);assert.doesNotMatch(e.extraPanelPreviewMarkup(e.cardAt(2)),/mdi:door/);
 e._hass.locale.language="pl";assert.match(e.extraPanelPreviewMarkup(e.cardAt(2)),/Podgląd danych widoku/);
});

test("Extra preview updates on live refresh without replacing the surrounding editable form",()=>{
 const e=extraPanelEditor();enableExtra(e);const element={outerHTML:""};
 e.shadowRoot.querySelector=selector=>selector==="[data-extra-panel-preview]"?element:null;
 e._hass.states[e.cardAt(2).entity_id].state="unavailable";e.paintValues();
 assert.match(element.outerHTML,/Offline/);assert.doesNotMatch(element.outerHTML,/21.8/);
});

const mediaPanelFixtures=JSON.parse(fs.readFileSync(path.join(__dirname,"fixtures/media_panel/editor.json"),"utf8"));
const actionPanelFixtures=JSON.parse(fs.readFileSync(path.join(__dirname,"fixtures/action_panel/editor-ui.json"),"utf8"));
const actualActionPanelFixtures=JSON.parse(fs.readFileSync(path.join(__dirname,"fixtures/action_panel/actual-domain.json"),"utf8"));
function actionPanelEditor(subtype="button",fixtures=actionPanelFixtures) {
 const e=lightEditor(),c=e.cardAt(2),f=clone(fixtures[subtype]);
 c.entity_id=f.entity_id;c.type="action";c.action={kind:"default"};
 e.profile.schema_control_types.push("panel");e.profile.schema_panel_extra_profiles=[{name:"action",version:2}];
 Object.assign(e._status,{entity_control_status:"ready",native_control_types:["entity_control_v1"],control_kinds:["light","panel"],panel_extra_profiles:clone(e.profile.schema_panel_extra_profiles)});
 e._hass.states[c.entity_id]={state:f.state,attributes:{}};
 e._hass.services={[subtype]:Object.fromEntries(f.services.map(name=>[name,{}]))};
 e._entityIndex.set(c.entity_id,{entity_id:c.entity_id,domain:subtype,available:true,action_panel:f.metadata.action_panel || f.metadata,actions:f.services.map(name=>({service:subtype+"."+name,fields:{}}))});
 return e;
}
test("Action panel explicitly reviews five subtypes without service calls or saved-layout mutation",()=>{
 for(const fixtures of [actionPanelFixtures,actualActionPanelFixtures]) for(const subtype of Object.keys(fixtures)) {
  const e=actionPanelEditor(subtype,fixtures),before=clone(e._draft),saved=clone(e._saved),live=clone(e._hass.states);
  assert.equal(e.actionPanelAvailability().ready,true,subtype);
  assert.match(e.inspectorMarkup(),/value="control-actionpanel"/);
  e.editField(actionInput("control-actionpanel"));assert.deepEqual(clone(e._draft),before);
  assert.equal(e.confirmLightControl(),true);
  assert.deepEqual(clone(e.cardAt(2).action),{kind:"control",control:"panel",property:"action",...(subtype==="automation"?{skip_condition:false,stop_actions:false}:{})});
  assert.deepEqual(clone(e._saved),saved);assert.deepEqual(clone(e._hass.states),live);
  assert.doesNotThrow(()=>e.validateStoredDraft(extraStored(e)));
  e.history("undo");assert.deepEqual(clone(e._draft),before);
 }
});
test("Action panel preserves true legacy HA defaults and strict false overrides separately from new defaults",()=>{
 for(const [service,key] of [["automation.trigger","skip_condition"],["automation.turn_off","stop_actions"]]) {
  for(const value of [undefined,true,false]) {
   const e=actionPanelEditor("automation");e.cardAt(2).action={kind:"service",service,data:value===undefined?{}:{[key]:value}};
   const before=clone(e._draft);assert.equal(e.requestLightControl("actionpanel"),true);
   assert.equal(e._pending.actionPolicies[key],value===undefined?true:value);assert.deepEqual(clone(e._draft),before);
   assert.equal(e.confirmLightControl(),true);assert.equal(e.cardAt(2).action[key],value===undefined?true:value);
  }
 }
 for(const bad of [null,0,1,"true",[]]) {
  const e=actionPanelEditor("automation");e.cardAt(2).action={kind:"service",service:"automation.trigger",data:{skip_condition:bad}};
  assert.equal(e.requestLightControl("actionpanel"),false);
 }
});
test("Action panel refuses to silently discard legacy script variables or unrelated service data",()=>{
 for(const [domain,service,data] of [["script","script.turn_on",{variables:{mode:"night"}}],["script","script.other",{}],["automation","automation.trigger",{skip_condition:true,other:1}],["button","button.press",{unknown:true}]]) {
  const e=actionPanelEditor(domain);e.cardAt(2).action={kind:"service",service,data};const before=clone(e._draft);
  assert.equal(e.actionPanelAvailability().reason,"actionPanelLegacyData");assert.equal(e.requestLightControl("actionpanel"),false);assert.deepEqual(clone(e._draft),before);
 }
 const e=actionPanelEditor("script");e.cardAt(2).action={kind:"service",service:"script.turn_on",data:{}};
 assert.equal(e.requestLightControl("actionpanel"),true);assert.match(e.modalMarkup(),/does not pass script parameters/);
});
test("Action panel stages automation policy edits for review and never rewrites catalogue fingerprints",()=>{
 const e=actionPanelEditor("automation");e.requestLightControl("actionpanel");e.confirmLightControl();
 const before=clone(e._draft),meta=clone(e.entityFor(e.cardAt(2).entity_id).action_panel);
 assert.equal(e.requestActionPanelPolicy("stop_actions",true),true);assert.deepEqual(clone(e._draft),before);
 assert.match(e.modalMarkup(),/even if already disabled/);
 assert.equal(e.confirmLightControl(),true);assert.equal(e.cardAt(2).action.stop_actions,true);
 assert.deepEqual(clone(e.entityFor(e.cardAt(2).entity_id).action_panel),meta);
 assert.match(e.inspectorMarkup(),/data-field="action-policy-stop_actions" checked/);
 e.history("undo");assert.deepEqual(clone(e._draft),before);
});
test("Action panel review ignores timestamp and current telemetry but rejects capability service or policy drift",()=>{
 const e=actionPanelEditor("automation");assert.equal(e.requestLightControl("actionpanel"),true);
 Object.assign(e.entityFor(e.cardAt(2).entity_id).action_panel.state,{last_used_status:"value",last_used_text:"2026-11-05T15:00:00.123456+01:00",current:3});
 e._hass.states[e.cardAt(2).entity_id].attributes.current=3;
 assert.equal(e.confirmLightControl(),true);
 for(const change of [e=>e.entityFor(e.cardAt(2).entity_id).action_panel.fingerprint="a".repeat(64),
  e=>delete e._hass.services.automation.trigger,e=>e._saved.revision++,e=>e._selectionEpoch++,
  e=>e.entityFor(e.cardAt(2).entity_id).action_panel.caps.stop_actions=true]) {
  const e=actionPanelEditor("automation"),before=clone(e._draft);e.requestLightControl("actionpanel");change(e);
  assert.equal(e.confirmLightControl(),false);assert.deepEqual(clone(e._draft),before);
 }
 const script=actionPanelEditor("script");script.requestLightControl("actionpanel");script.entityFor(script.cardAt(2).entity_id).action_panel.caps.run_blocked="needs_parameters";
 assert.equal(script.confirmLightControl(),false);
});
test("Action panel keeps parameter-policy reasons separate from source availability",()=>{
 for(const reason of ["needs_parameters","metadata_unavailable"]) {
  const e=actionPanelEditor("script"),m=e.entityFor(e.cardAt(2).entity_id).action_panel;m.caps.run_blocked=reason;m.eligible_actions=0;
  assert.equal(e.actionPanelAvailability().ready,true);e.requestLightControl("actionpanel");assert.equal(e.confirmLightControl(),true);
  assert.match(e.inspectorMarkup(),reason==="needs_parameters"?/parameters are required/:/metadata is missing/);
  assert.equal(m.available,true);
 }
});
test("Action panel negotiation strict schema and live service masks fail closed",()=>{
 for(const change of [e=>e._status.panel_extra_profiles=[],e=>e._status.panel_extra_profiles=[{name:"action",version:1}],
  e=>e.profile.schema_panel_extra_profiles=[],e=>e._hass.connected=false,e=>delete e._hass.services.button.press,
  e=>e.cardAt(2).type="sensor",e=>e.entityFor(e.cardAt(2).entity_id).action_panel.caps.operations=true,
  e=>e.entityFor(e.cardAt(2).entity_id).action_panel.caps.operations=2,e=>e.entityFor(e.cardAt(2).entity_id).action_panel.caps.stop_actions=false,
  e=>e.entityFor(e.cardAt(2).entity_id).action_panel.caps.other=1,e=>e.entityFor(e.cardAt(2).entity_id).action_panel.state.phase="idle",
  e=>e.entityFor(e.cardAt(2).entity_id).action_panel.eligible_actions=0]) {
  const e=actionPanelEditor();change(e);const before=clone(e._draft);assert.equal(e.requestLightControl("actionpanel"),false);assert.deepEqual(clone(e._draft),before);
 }
});
test("Action panel saved intent survives offline and accepts entity or action placements only",()=>{
 for(const type of ["entity","action"]) {
  const e=actionPanelEditor("automation");e.cardAt(2).type=type;e.requestLightControl("actionpanel");e.confirmLightControl();const record=extraStored(e);
  e._status.panel_extra_profiles=[];assert.match(e.inspectorMarkup(),/value="control-actionpanel" selected disabled/);
  assert.doesNotThrow(()=>e.validateStoredDraft(record));assert.equal(e.groupTargetCompatible(e.cardAt(2),11),true);
  for(const patch of [{skip_condition:1},{stop_actions:null},{initial_duration:1},{detail:1},{data:{}},{service:"automation.trigger"}]) {
   const bad=clone(record);Object.assign(bad.layout.cards.find(c=>c.slot===2).action,patch);assert.throws(()=>e.validateStoredDraft(bad));
  }
  const bad=clone(record);delete bad.layout.cards.find(c=>c.slot===2).action.stop_actions;assert.throws(()=>e.validateStoredDraft(bad));
 }
 const e=actionPanelEditor("button");e.requestLightControl("actionpanel");e.confirmLightControl();const bad=extraStored(e);bad.layout.cards.find(c=>c.slot===2).action.skip_condition=false;assert.throws(()=>e.validateStoredDraft(bad));
});
test("Action panel first use remains honest and telemetry is escaped in the inspector",()=>{
 const e=actionPanelEditor();e.requestLightControl("actionpanel");e.confirmLightControl();assert.match(e.inspectorMarkup(),/No last-use data/);
 e._hass.locale.language="pl";assert.match(e.inspectorMarkup(),/Brak danych o ostatnim użyciu/);assert.doesNotMatch(e.inspectorMarkup(),/<img|background-image/);
 const m=e.entityFor(e.cardAt(2).entity_id).action_panel;m.state.last_used_status="value";m.state.last_used_text="<script>alert(1)</script>";
 assert.equal(e.actionPanelMetadata(e.cardAt(2)),null);assert.doesNotMatch(e.inspectorMarkup(),/<script>/);
});
test("Action panel masks stale catalogue observations after a live phase or source change without invalidating capability review",()=>{
 for(const domain of ["script","automation"]) {
  const e=actionPanelEditor(domain),m=e.entityFor(e.cardAt(2).entity_id).action_panel;
  Object.assign(m.state,{last_used_status:"value",last_used_text:"2026-11-05T15:03:01+01:00",current:7});
  e.requestLightControl("actionpanel");e._hass.states[e.cardAt(2).entity_id].state="on";
  assert.equal(e.confirmLightControl(),true,"phase telemetry must not invalidate the configuration review");
  for(const live of ["on","unknown","unavailable"]) {
   e._hass.states[e.cardAt(2).entity_id].state=live;const html=e.actionPanelPreviewMarkup(e.cardAt(2));
   assert.match(html,/Waiting for refreshed panel data/);assert.match(html,/Catalogue observation/);
   assert.doesNotMatch(html,/5 November 2026|Running or queued: 7/);
  }
  e._hass.states[e.cardAt(2).entity_id].state="off";
  assert.match(e.actionPanelPreviewMarkup(e.cardAt(2)),/5 November 2026 · 15:03:01 · UTC\+01:00/);
 }
 const first=actionPanelEditor("button");first.requestLightControl("actionpanel");first.confirmLightControl();
 assert.match(first.actionPanelPreviewMarkup(first.cardAt(2)),/No last-use data/);
 assert.doesNotMatch(first.actionPanelPreviewMarkup(first.cardAt(2)),/Waiting for refreshed/);
});
function mediaPanelEditor(suffix="music") {
 const e=lightEditor(),c=e.cardAt(2),f=clone(mediaPanelFixtures[suffix]);
 c.entity_id=f.entity_id;c.type="entity";c.action={kind:"default"};
 e.profile.schema_control_types.push("panel");e.profile.schema_panel_extra_profiles=[{name:"info",version:1},{name:"lock",version:1},{name:"media",version:1}];
 Object.assign(e._status,{entity_control_status:"ready",native_control_types:["entity_control_v1"],control_kinds:["light","panel"],panel_extra_profiles:clone(e.profile.schema_panel_extra_profiles)});
 e._hass.states[c.entity_id]={state:f.state,attributes:f.attributes};
 e._hass.services={media_player:Object.fromEntries(f.services.map(name=>[name,{}]))};
 e._entityIndex.set(c.entity_id,{entity_id:c.entity_id,domain:"media_player",available:true,media_panel:f.metadata,actions:f.services.map(name=>({service:"media_player."+name,fields:{}}))});
 return e;
}

test("Media uses actual music and TV capability profiles and an explicit draft-only review",()=>{
 for(const suffix of ["music","tv"]) {
  const e=mediaPanelEditor(suffix),before=clone(e._draft),source=clone(e._hass.states);
  assert.equal(e.mediaPanelAvailability().ready,true);
  assert.match(e.inspectorMarkup(),/value="control-mediapanel"/);
  e.editField(actionInput("control-mediapanel"));assert.deepEqual(clone(e._draft),before);
  assert.equal(e.confirmLightControl(),true);
  assert.deepEqual(clone(e.cardAt(2).action),{kind:"control",control:"panel",property:"media"});
  assert.deepEqual(clone(e._hass.states),source);
  assert.doesNotThrow(()=>e.validateStoredDraft(extraStored(e)));
  e.history("undo");assert.deepEqual(clone(e._draft),before);
 }
});

test("Media negotiation, exact features and live service identity fail closed",()=>{
 for(const change of [e=>e._status.panel_extra_profiles=[],e=>e._status.panel_extra_profiles=[{name:"media",version:2}],
  e=>e.profile.schema_panel_extra_profiles=[],e=>e._status.entity_control_status="offline",e=>e._hass.connected=false,
  e=>delete e._hass.services,e=>delete e._hass.services.media_player.media_pause,
  e=>e._hass.states[e.cardAt(2).entity_id].attributes.supported_features=true,
  e=>e._hass.states[e.cardAt(2).entity_id].attributes.supported_features=4,
  e=>e.entityFor(e.cardAt(2).entity_id).media_panel.caps.facets=15,
  e=>e.entityFor(e.cardAt(2).entity_id).media_panel.fingerprint="bad",
  e=>e.entityFor(e.cardAt(2).entity_id).media_panel.caps.other=true,
  e=>e.cardAt(2).type="sensor"]) {
  const e=mediaPanelEditor();change(e);const before=clone(e._draft);
  assert.equal(e.requestLightControl("mediapanel"),false);assert.deepEqual(clone(e._draft),before);
 }
 const tv=mediaPanelEditor("tv"),meta=tv.entityFor(tv.cardAt(2).entity_id).media_panel;
 assert.equal(meta.caps.operations&(128|256|512|1024),0);assert.equal(tv.mediaPanelAvailability().ready,true);
 meta.caps.operations|=128;meta.caps.facets|=1;
 assert.equal(tv.mediaPanelAvailability().ready,false,"Stray volume/mute attributes cannot authorize controls");
});

test("Media capability review ignores position/title/volume updates but detects source catalogue or service changes",()=>{
 const e=mediaPanelEditor();assert.equal(e.requestLightControl("mediapanel"),true);
 Object.assign(e._hass.states[e.cardAt(2).entity_id].attributes,{volume_level:.425,media_position:99,media_title:"New track"});
 e._hass.states[e.cardAt(2).entity_id].state="unavailable";
 assert.equal(e.confirmLightControl(),true);
 for(const change of [e=>e._hass.states[e.cardAt(2).entity_id].attributes.source_list=["dvd","new"],
  e=>delete e._hass.services.media_player.select_source,
  e=>e.entityFor(e.cardAt(2).entity_id).media_panel.fingerprint="d".repeat(64),e=>e._selectionEpoch++]) {
  const e=mediaPanelEditor("tv"),before=clone(e._draft);e.requestLightControl("mediapanel");change(e);
  assert.equal(e.confirmLightControl(),false);assert.deepEqual(clone(e._draft),before);
 }
});

test("Media saved intent survives offline and supports bounded placement without changing legacy Choice",()=>{
 const e=mediaPanelEditor();e.requestLightControl("mediapanel");e.confirmLightControl();const record=extraStored(e);
 e._status.panel_extra_profiles=[];
 assert.match(e.inspectorMarkup(),/value="control-mediapanel" selected disabled/);
 assert.doesNotThrow(()=>e.validateStoredDraft(record));assert.equal(e.groupTargetCompatible(e.cardAt(2),11),true);
 for(const patch of [{property:"player"},{detail:1},{service:"media_player.media_play_pause"},{data:{}},{initial_duration:30}]) {
  const bad=clone(record);Object.assign(bad.layout.cards.find(c=>c.slot===2).action,patch);assert.throws(()=>e.validateStoredDraft(bad));
 }
 const tv=mediaPanelEditor("tv");tv.cardAt(2).action={kind:"control",control:"choice",property:"source"};
 const before=clone(tv.cardAt(2).action);assert.equal(tv.cardControlKind(tv.cardAt(2)),"mediasource");
 assert.match(tv.inspectorMarkup(),/value="control-mediapanel"/);assert.deepEqual(clone(tv.cardAt(2).action),before);
});

test("Media view copy explains external-player scope in both languages without bitmap artwork",()=>{
 const e=mediaPanelEditor();assert.match(e.inspectorMarkup(),/dedicated Atmosfera Player/);
 e._hass.locale.language="pl";assert.match(e.inspectorMarkup(),/Dedykowany Player Atmosfery/);
 assert.doesNotMatch(e.inspectorMarkup(),/<img|background-image/);
});

const mediaLegacySections=["mute","volume-target","stop","volume","shuffle"];
function mediaPanelWithLegacyShortcuts() {
 const e=mediaPanelEditor();
 for(const key of ["mute","volume_target","stop","volume_actions","shuffle"]) e.profile[`schema_media_${key}`]=true;
 return e;
}
test("Media panel inspector hides legacy shortcut sections and fixed-target copy in both languages",()=>{
 for(const language of ["en","pl"]) {
  const e=mediaPanelWithLegacyShortcuts();e._hass.locale.language=language;
  const before=e.inspectorMarkup();
  for(const section of mediaLegacySections) assert.ok(before.includes(`<div data-media-${section}>`),section);
  assert.equal(e.requestLightControl("mediapanel"),true);assert.equal(e.confirmLightControl(),true);
  const draft=clone(e._draft),states=clone(e._hass.states),html=e.inspectorMarkup();
  for(const section of mediaLegacySections) {
   assert.ok(!html.includes(`<div data-media-${section}>`),section);
   assert.ok(!html.includes(`data-action="media-${section}-configure"`),section);
  }
  assert.ok(!html.includes(e.t("mediaVolumeTargetHint")));
  assert.ok(html.includes(e.t("mediaPanelHint")));
  assert.match(html,/value="control-mediapanel" selected/);
  assert.deepEqual(clone(e._draft),draft);assert.deepEqual(clone(e._hass.states),states);
 }
});
test("Media panel inspector keeps legacy shortcuts hidden when the saved view is unavailable",()=>{
 for(const change of [e=>e._status.panel_extra_profiles=[],e=>e._hass.connected=false,
  e=>e._hass.states[e.cardAt(2).entity_id].state="unavailable",
  e=>delete e.entityFor(e.cardAt(2).entity_id).media_panel]) {
  const e=mediaPanelWithLegacyShortcuts();e.requestLightControl("mediapanel");e.confirmLightControl();change(e);
  const draft=clone(e._draft),html=e.inspectorMarkup();
  assert.match(html,/value="control-mediapanel" selected(?: disabled)?/);
  for(const section of mediaLegacySections) assert.ok(!html.includes(`<div data-media-${section}>`),section);
  assert.ok(!html.includes(e.t("mediaVolumeTargetHint")));assert.deepEqual(clone(e._draft),draft);
 }
});
test("Media panel inspector restores legacy shortcuts after changing to a legacy intent",()=>{
 for(const action of [{kind:"default"},{kind:"control",control:"choice",property:"sound_mode"},
  {kind:"service",service:"media_player.volume_set",data:{volume_level:.425}},
  {kind:"service",service:"media_player.volume_mute",data:{is_volume_muted:true}},
  {kind:"service",service:"media_player.media_stop",data:{}},
  {kind:"service",service:"media_player.volume_up",data:{}},
  {kind:"service",service:"media_player.shuffle_set",data:{shuffle:true}}]) {
  const e=mediaPanelWithLegacyShortcuts();e.requestLightControl("mediapanel");e.confirmLightControl();
  e.cardAt(2).action=clone(action);const draft=clone(e._draft),html=e.inspectorMarkup();
  for(const section of mediaLegacySections) assert.ok(html.includes(`<div data-media-${section}>`),section);
  assert.ok(html.includes(e.t("mediaVolumeTargetHint")));assert.match(html,/value="control-mediapanel"/);
  assert.deepEqual(clone(e._draft),draft);
 }
});


test("Extra caption112 Lock uses HA localization with explicit language-pack fallback",()=>{
 const e=extraPanelEditor("lock");enableExtra(e);const c=e.cardAt(2),m=e.entityFor(c.entity_id).extra_panel,s=e._hass.states[c.entity_id];
 s.state=m.state.phase="locked";m.eligible_actions=0;e._hass.locale.language="pl";
 e._hass.formatEntityState=state=>{assert.equal(state.state,"locked");return "zablokowano";};
 assert.equal(e.stateText(c),"zablokowano");assert.match(e.extraPanelPreviewMarkup(c),/zablokowano/);
 e._hass.formatEntityState=()=>"locked";assert.equal(e.stateText(c),"Zaryglowany");
 e._hass.formatEntityState=()=>{throw new Error("unloaded");};assert.equal(e.extraPreview(c).message,"Zaryglowany");
 e._hass.locale.language="en";assert.equal(e.stateText(c),"Locked");
 m.state.phase="unknown";assert.equal(e.stateText(c),e.t("unknown"));
});

test("Extra caption112 Calendar retains the existing dated tile caption and full Inspector dates",()=>{
 const e=extraPanelEditor("calendar");enableExtra(e);const c=e.cardAt(2),m=e.entityFor(c.entity_id),s=e._hass.states[c.entity_id];
 const fields={message:"Team meeting",all_day:false,start_time:"2026-11-05 10:00:00",end_time:"2026-11-05 11:00:00"};
 s.attributes=clone(fields);m.calendar_next={state:"off",fields:clone(fields),text:{pl:"05.11.2026 10:00 Team meeting",en:"2026-11-05 10:00 Team meeting"}};
 for(const language of ["pl","en"]) {
  e._hass.locale.language=language;assert.equal(e.stateText(c),m.calendar_next.text[language]);
  const html=e.extraPanelPreviewMarkup(c);assert.match(html,/2026-11-05 10:00:00/);assert.match(html,/2026-11-05 11:00:00/);assert.match(html,/Europe\/Warsaw/);
 }
 s.attributes.start_time="2026-11-06 10:00:00";assert.equal(e.stateText(c),e.t("unknown"));
});

test("Extra caption112 preserves configured state labels on valid sensor launchers",()=>{
 for(const domain of ["sensor","binary_sensor"]) {
  const e=extraPanelEditor(domain);enableExtra(e);const c=e.cardAt(2),s=e._hass.states[c.entity_id];
  c.state_labels={[s.state]:"Custom observation"};assert.equal(e.stateText(c),"Custom observation");
  s.state="unknown";assert.equal(e.stateText(c),e.t("unknown"));
 }
});

test("Extra caption112 preserves numeric tile formatting without rounding the Inspector observation",()=>{
 const e=extraPanelEditor();enableExtra(e);const c=e.cardAt(2),s=e._hass.states[c.entity_id],m=e.entityFor(c.entity_id).extra_panel;
 s.state=m.state.value_text="21.375";s.attributes.unit_of_measurement=m.state.unit_text="°C";c.display_precision=2;e._hass.locale.language="pl";
 assert.equal(e.stateText(c),"21,38 °C");assert.equal(e.extraPreview(c).message,"21.375 °C");
 assert.match(e.extraPanelPreviewMarkup(c),/21.375 °C/);
 delete c.display_precision;e._hass.formatEntityState=()=>"21,375 °C";assert.equal(e.stateText(c),"21,375 °C");
});

test("Extra caption112 preserves source, stale-catalogue and invalid-observation guards before ordinary formatting",()=>{
 for(const domain of ["sensor","binary_sensor","calendar","alarm_control_panel","lock"]) {
  for(const next of ["unknown","unavailable","newer","missing","disconnected"]) {
   const e=extraPanelEditor(domain);enableExtra(e);const c=e.cardAt(2),s=e._hass.states[c.entity_id];
   e._hass.formatEntityState=()=>{throw new Error("Must not format a stale observation");};
   if(next==="newer")s.last_updated="2026-11-04T11:00:01Z";
   else if(next==="missing")delete e._hass.states[c.entity_id];
   else if(next==="disconnected")e._hass.connected=false;
   else s.state=next;
   assert.equal(e.stateText(c),e.t(next==="unknown"?"unknown":next==="newer"?"extraRefreshing":"offline"));
  }
 }
 for(const status of ["too_long","empty","invalid"]) {
  const e=extraPanelEditor();enableExtra(e);const c=e.cardAt(2),o=e.entityFor(c.entity_id).extra_panel.state;
  o.value_status=status;o.value_text="";e._hass.formatEntityState=()=>"Should not appear";
  assert.equal(e.stateText(c),e.t(({too_long:"extraTooLong",empty:"extraEmpty",invalid:"extraInvalid"})[status]));
 }
});


test("moisture auto icon uses the internal humidity key and preserves all explicit icons",()=>{
 const e=extraPanelEditor("binary_sensor");enableExtra(e);const c=e.cardAt(2),s=e._hass.states[c.entity_id];c.icon="auto";
 for(const value of ["on","off","unknown","unavailable"]){
  s.state=value;s.attributes.device_class="moisture";
  assert.equal(e.effectiveIcon(c),"humidity");assert.match(e.icon(e.effectiveIcon(c)),/mdi:water/);
  for(const icon of ["sensor","door","presence","lock","light","alarm"]){
   c.icon=icon;assert.equal(e.effectiveIcon(c),icon);c.icon="auto";
  }
 }
 for(const cls of [undefined,null,[],{},42,"unknown","humidity","temperature","power"]){
  s.attributes.device_class=cls;assert.equal(e.effectiveIcon(c),"sensor");
 }
 delete e._hass.states[c.entity_id];assert.equal(e.effectiveIcon(c),"sensor");
 assert.equal(c.icon,"auto");
});

test("moisture auto icon updates the existing live node without changing card layout or text",()=>{
 const e=makeEditor(),c=e.cardAt(2);Object.assign(c,{type:"sensor",entity_id:"binary_sensor.example",icon:"auto",action:{kind:"none"}});
 const saved=clone(e._draft),focus={},attrs={},writes=[];
 const icon={getAttribute:key=>attrs[key],setAttribute(key,value){attrs[key]=value;writes.push(value);}};
 const node={dataset:{slot:"2"},querySelector:()=>icon};e.shadowRoot.activeElement=focus;e.shadowRoot.querySelectorAll=selector=>selector===".preview-card[data-slot]"?[node]:[];
 e._hass={states:{[c.entity_id]:{state:"off",attributes:{device_class:"door"}}},formatEntityState:()=>"brak"};
 for(const [cls,expected] of [["door","mdi:window-closed-variant"],["moisture","mdi:water"],["motion","mdi:account-group-outline"],["unknown","mdi:thermometer"]]){
  e._hass.states[c.entity_id].attributes.device_class=cls;e.paintValues();assert.equal(attrs.icon,expected);
 }
 e._hass.states[c.entity_id].attributes.device_class="moisture";e.paintValues();assert.equal(e.stateText(c),"brak");
 e.paintValues();assert.equal(writes.length,5);assert.equal(e.shadowRoot.activeElement,focus);
 assert.deepEqual(clone(e._draft),saved);assert.equal(e._undo.length,0);
});


test("Action2 negotiation is distinct from v1 catalogue metadata and other Extra profiles",()=>{
 const e=actionPanelEditor();
 assert.equal(e.entityFor(e.cardAt(2).entity_id).action_panel.version,1);
 assert.equal(e.actionPanelAvailability().ready,true);
 for(const key of ["schema_panel_extra_profiles","panel_extra_profiles"]){
  const target=key==="schema_panel_extra_profiles"?e.profile:e._status,original=clone(target[key]);
  target[key]=[{name:"action",version:1}];assert.equal(e.actionPanelAvailability().ready,false);
  target[key]=original;
 }
 e.entityFor(e.cardAt(2).entity_id).action_panel.version=2;
 assert.equal(e.actionPanelAvailability().ready,false);
 for(const name of ["info","lock","media"]){
  assert.equal(e.hasExtraProfile([{name,version:1}],name),true);
  assert.equal(e.hasExtraProfile([{name,version:2}],name),false);
 }
 assert.equal(e.hasExtraProfile([{name:"action",version:2},{name:"info",version:1}],"action"),true);
 assert.equal(e.hasExtraProfile([{name:"action",version:2},{name:"action",version:1}],"action"),false);
});


test("Caption116 momentary Action launchers say Open without replacing Inspector history",()=>{
 for(const domain of ["button","input_button","scene"]) for(const language of ["en","pl"]) {
  const e=actionPanelEditor(domain),c=e.cardAt(2),live=e._hass.states[c.entity_id];
  e.requestLightControl("actionpanel");assert.equal(e.confirmLightControl(),true);
  e._hass.locale.language=language;e._hass.formatEntityState=()=>"formatted historical timestamp";
  const m=e.entityFor(c.entity_id).action_panel;
  m.state.last_used_status="value";m.state.last_used_text="2026-11-05T12:34:56+01:00";
  for(const state of ["2026-11-05T12:34:56+01:00","unknown"]) {
   live.state=state;assert.equal(e.stateText(c),language==="pl"?"Otwórz":"Open");
   assert.match(e.actionPanelPreviewMarkup(c),language==="pl"?/5 listopada 2026 · 12:34:56 · UTC\+01:00/:/5 November 2026 · 12:34:56 · UTC\+01:00/);
  }
 }
});

test("Caption116 retains missing and unavailable state plus exact saved-action boundaries",()=>{
 const e=actionPanelEditor("input_button"),c=e.cardAt(2),live=e._hass.states[c.entity_id];
 e.requestLightControl("actionpanel");e.confirmLightControl();
 const saved=clone(c.action);e._hass.formatEntityState=()=>"legacy date";
 live.state="unavailable";assert.equal(e.stateText(c),e.t("offline"));
 delete e._hass.states[c.entity_id];assert.equal(e.stateText(c),e.t("unknown"));
 e._hass.states[c.entity_id]=live;live.state="2026-11-05T12:34:56+01:00";
 for(const action of [{kind:"default"},{kind:"none"},{kind:"service",service:"input_button.press",data:{}},{...saved,extra:true}]) {
  c.action=action;assert.equal(e.stateText(c),"legacy date");
 }
 c.action=saved;c.state_labels={[live.state]:"stray history override"};
 e._status.panel_extra_profiles=[];assert.equal(e.stateText(c),"Open");
});

test("Caption116 preserves script automation and configured sensor caption semantics",()=>{
 for(const domain of ["script","automation"]) {
  const e=actionPanelEditor(domain),c=e.cardAt(2);
  e.requestLightControl("actionpanel");e.confirmLightControl();
  e._hass.formatEntityState=()=>"existing state caption";assert.equal(e.stateText(c),"existing state caption");
 }
 const e=extraPanelEditor(),c=e.cardAt(2);enableExtra(e);c.type="sensor";c.state_labels={"21.8":"Przyjemnie"};
 e.profile.schema_state_labels=true;assert.equal(e.stateText(c),"Przyjemnie");
});


const infoContextFixtures=JSON.parse(fs.readFileSync(path.join(__dirname,"fixtures/info_context/editor-context.json"),"utf8"));
function infoContextEditor(name="person-home-pl",type="sensor") {
 const f=clone(infoContextFixtures.cases.find(item=>item.name===name));assert.ok(f,name);
 const e=extraPanelEditor("sensor",type),c=e.cardAt(2);c.entity_id=f.entity_id;
 e.profile.schema_panel_extra_profiles.push({name:"info_context",version:1});
 e._status.panel_extra_profiles=clone(e.profile.schema_panel_extra_profiles);
 e.profile.schema_person_presence=true;e.profile.person_text_slots=[13];e.profile.sun_text_slots=[13];
 e._hass.states[c.entity_id]={state:f.live_state,attributes:{},last_updated:f.metadata.state.updated_text};
 e._entityIndex.set(c.entity_id,{entity_id:c.entity_id,domain:f.entity_id.split(".")[0],available:f.metadata.available,extra_panel:f.metadata,actions:[]});
 return e;
}

test("InfoContext117 admits all41 frozen closed wire observations through the existing Extra metadata envelope",()=>{
 assert.equal(infoContextFixtures.cases.length,41);
 for(const row of infoContextFixtures.cases) {
  const e=infoContextEditor(row.name),c=e.cardAt(2);
  assert.ok(e.extraPanelMetadata(c),row.name);assert.equal(e.extraPanelAvailability(c).ready,true,row.name);
  enableExtra(e);assert.doesNotThrow(()=>e.validateStoredDraft(extraStored(e)),row.name);
  assert.doesNotMatch(e.extraPanelPreviewMarkup(c),/<button|data-action=/,row.name);
 }
});

test("InfoContext117 requires both exact profiles and keeps passive placement and saved intent",()=>{
 for(const name of ["person-home-pl","sun-day"]) for(const type of ["sensor","entity"]) {
  const e=infoContextEditor(name,type),c=e.cardAt(2),before=clone(e._draft);
  assert.equal(e.acceptsCard(e.slotAt(2),c),false);assert.equal(e.requestLightControl("infopanel"),true);
  assert.deepEqual(clone(e._draft),before);assert.equal(e.confirmLightControl(),true);
  assert.equal(e.acceptsCard(e.slotAt(3),c),true);
  const record=extraStored(e);e._status.panel_extra_profiles=[];assert.doesNotThrow(()=>e.validateStoredDraft(record));
  assert.match(e.inspectorMarkup(),/value="control-infopanel" selected disabled/);
  c.action={kind:"none"};c.type="sensor";assert.equal(e.acceptsCard(e.slotAt(3),c),false);assert.equal(e.acceptsCard(e.slotAt(13),c),true);
 }
 for(const target of ["schema","runtime"]) for(const entries of [[],[{name:"info",version:1}],[{name:"info_context",version:1}],
  [{name:"info",version:1},{name:"info_context",version:2}],[{name:"info",version:1},{name:"info_context",version:1},{name:"info_context",version:1}]]) {
  const e=infoContextEditor(),before=clone(e._draft);
  if(target==="schema")e.profile.schema_panel_extra_profiles=entries;else e._status.panel_extra_profiles=entries;
  assert.equal(e.requestLightControl("infopanel"),false);assert.deepEqual(clone(e._draft),before);
 }
 const old=extraPanelEditor();assert.equal(old.extraPanelAvailability().ready,true);
});

test("InfoContext117 capability review ignores time telemetry but rejects extension or capability changes",()=>{
 const e=infoContextEditor(),c=e.cardAt(2);assert.equal(e.requestLightControl("infopanel"),true);
 e.entityFor(c.entity_id).extra_panel.state.changed_text="2026-11-06T01:23:45+01:00";
 e._hass.states[c.entity_id].state="unavailable";assert.equal(e.confirmLightControl(),true);
 for(const change of [e=>e._status.panel_extra_profiles=e._status.panel_extra_profiles.filter(p=>p.name!=="info_context"),
  e=>e.entityFor(e.cardAt(2).entity_id).extra_panel.fingerprint="c".repeat(64),
  e=>e.entityFor(e.cardAt(2).entity_id).extra_panel.caps.device_class="temperature"]) {
  const e=infoContextEditor();e.requestLightControl("infopanel");change(e);assert.equal(e.confirmLightControl(),false);
 }
});

test("InfoContext117 friendly local dates preserve DST offsets and calendar validity independently of browser timezone",()=>{
 const e=infoContextEditor();e._hass.locale.language="pl";
 assert.equal(e.contextDateText("value","2026-10-25T02:30:59+02:00"),"25 października 2026 · 02:30 · UTC+02:00");
 assert.equal(e.contextDateText("value","2026-10-25T02:30:00+01:00"),"25 października 2026 · 02:30 · UTC+01:00");
 e._hass.locale.language="en";assert.equal(e.contextDateText("value","2028-02-29T00:00:59-03:30"),"29 February 2028 · 00:00 · UTC-03:30");
 for(const bad of ["2026-02-29T00:00:00+00:00","0000-01-01T00:00:00+00:00","2026-01-01T24:00:00+00:00","2026-01-01T00:00:60+00:00", "2026-01-01T00:00:00+24:00","2026-01-01T00:00:00Z","2026-01-01T00:00:00.000+00:00"]) assert.equal(e.contextDateParts(bad),null,bad);
 for(const [status,key] of [["unknown","contextDateUnknown"],["invalid","contextDateInvalid"],["stale","contextDateStale"],["too_long","extraTooLong"]]) assert.equal(e.contextDateText(status,""),e.t(key));
});

test("InfoContext117 exact angles reject rounded boundary overflow and preserve source precision",()=>{
 const e=infoContextEditor("sun-angle-max");enableExtra(e);e._hass.locale.language="pl";
 assert.match(e.extraPanelPreviewMarkup(e.cardAt(2)),/-0,123456789012345678901°/);
 for(const value of ["90.000000000000000000001","-90.00000000000000000001","NaN","Infinity","1,2","true","1e24"]) assert.equal(e.contextAngleValid(value,true,90),false,value);
 for(const value of ["90","-90","89.999999999999999999999","1.","5e-324","-0","+00.0000",".25"]) assert.equal(e.contextAngleValid(value,true,90),true,value);
 assert.equal(e.contextAngleValid("-0.000000000000000000001",false,360),false);
 assert.equal(e.contextAngleValid("360.00000000000000000001",false,360),false);
});

test("InfoContext117 preview masks stale source or phase and renders independent natural statuses",()=>{
 for(const name of ["person-home-pl","sun-day"]) {
  const e=infoContextEditor(name),c=e.cardAt(2);enableExtra(e);
  const before=clone(e._hass.states[c.entity_id]);
  for(const state of ["unknown","unavailable",name.startsWith("person")?"not_home":"below_horizon"]) {
   e._hass.states[c.entity_id].state=state;const html=e.extraPanelPreviewMarkup(c);
   assert.doesNotMatch(html,/2026|Europe\/Warsaw|23\.45|W domu/);assert.match(html,/Catalogue observation/);
  }
  e._hass.states[c.entity_id]=before;e._hass.states[c.entity_id].last_updated="2026-12-31T12:00:00Z";
  assert.match(e.extraPanelPreviewMarkup(c),/Waiting for refreshed panel data/);
 }
 const e=infoContextEditor("sun-next_rising-stale"),c=e.cardAt(2);enableExtra(e);e._hass.locale.language="pl";
 const html=e.extraPanelPreviewMarkup(c);assert.match(html,/Oczekiwanie na aktualny termin/);assert.match(html,/6 listopada 2026/);assert.match(html,/UTC\+01:00/);assert.doesNotMatch(html,/2026-11-06T/);
 assert.match(html,/mdi:white-balance-sunny/);
});

test("InfoContext117 closed metadata rejects extra fields, correlation and invalid dates without truncation",()=>{
 for(const change of [o=>o.extra=true,o=>o.changed_text="2026-02-30T12:00:00+01:00",o=>o.zone_text="",o=>o.state_text="a".repeat(97),
  o=>o.changed_status="unknown",o=>o.source="unavailable",o=>o.updated_text="2026-11-05T20:16:32Z"]) {
  const e=infoContextEditor(),c=e.cardAt(2);change(e.entityFor(c.entity_id).extra_panel.state);assert.equal(e.extraPanelMetadata(c),null);
 }
 const e=infoContextEditor("person-zone"),c=e.cardAt(2),o=e.entityFor(c.entity_id).extra_panel.state;
 o.state_text="<script>alert(1)</script>";e._hass.states[c.entity_id].state=o.state_text;enableExtra(e);
 assert.match(e.extraPanelPreviewMarkup(c),/&lt;script&gt;/);assert.doesNotMatch(e.extraPanelPreviewMarkup(c),/<script>/);
 assert.equal(e.stateLabelsEligible(c),false);
});

test("InfoContext117 actual Python adapter metadata and existing passive hints agree with the explicit launcher",()=>{
 const rows=JSON.parse(fs.readFileSync(path.join(__dirname,"fixtures/info_context/actual-domain.json"),"utf8"));
 assert.equal(Object.keys(rows).length,9);
 for(const [name,row] of Object.entries(rows)) {
  const e=infoContextEditor(row.entity_id.startsWith("person.")?"person-home-pl":"sun-day"),c=e.cardAt(2);
  e._hass.states[c.entity_id]={state:row.state,attributes:{},last_updated:row.metadata.extra_panel.state.updated_text};
  e.entityFor(c.entity_id).extra_panel=clone(row.metadata.extra_panel);
  assert.ok(e.extraPanelMetadata(c),name);assert.equal(e.requestLightControl("infopanel"),true,name);assert.equal(e.confirmLightControl(),true,name);
  assert.doesNotMatch(e.inspectorMarkup(),/data-sun-placement|data-person-presence/,name);
  const html=e.extraPanelPreviewMarkup(c);assert.match(html,/Catalogue observation/,name);
  if(!["unknown","unavailable"].includes(row.state)) {assert.match(html,/November 2026/,name);assert.doesNotMatch(html,/2026-11-05T/,name);}
  c.action={kind:"none"};assert.match(e.inspectorMarkup(),row.entity_id.startsWith("person.")?/data-person-presence/:/data-sun-placement/);
 }
});

test("InfoContext117 same-second raw zone changes mask catalogue history without invalidating capability review",()=>{
 const e=infoContextEditor("person-zone"),c=e.cardAt(2),live=e._hass.states[c.entity_id],entity=e.entityFor(c.entity_id);
 entity.state=live.state;assert.ok(e.extraPreview(c).observation);
 assert.equal(e.requestLightControl("infopanel"),true);
 const stamp=live.last_updated;live.state="Inna strefa";
 assert.equal(live.last_updated,stamp);assert.equal(e.extraPreview(c).message,e.t("extraRefreshing"));
 assert.equal(e.lightControlReviewCurrent(),true);
 assert.equal(e.confirmLightControl(),true);assert.doesNotMatch(e.extraPanelPreviewMarkup(c),/Pracownia|Europe\/Warsaw/);
 entity.state=live.state;entity.extra_panel.state.state_text=live.state;
 assert.equal(e.extraPreview(c).message,"Inna strefa");
});

// These tests exercise only the editor's mocked, read-only WebSocket catalogue.
function preview118Editor(names=["person-home-pl","sun-day"]) {
 const e=infoContextEditor(names[0]),rows=new Map(),calls=[],pending=[];
 e._draft.cards=e._draft.cards.filter(c=>c.slot===0);
 names.forEach((name,index)=>{
  const f=clone(infoContextFixtures.cases.find(item=>item.name===name));assert.ok(f,name);
  const slot=index===0?2:3,c={...card(`preview-${slot}`,slot,f.entity_id),type:"sensor",action:{kind:"control",control:"panel",property:"info"}};
  e._draft.cards.push(c);
  e._hass.states[f.entity_id]={state:f.live_state,attributes:{},last_updated:f.metadata.state.updated_text};
  rows.set(f.entity_id,{entity_id:f.entity_id,domain:f.entity_id.split(".")[0],state:f.live_state,available:f.metadata.available,extra_panel:f.metadata,actions:[]});
  if(f.entity_id.startsWith("person."))rows.get(f.entity_id).person_presence={state:f.live_state,text:{en:"Home",pl:"W domu"}};
 });
 e._hass.formatEntityState=state=>({above_horizon:"Above horizon",below_horizon:"Below horizon"})[state.state] || state.state;
 e._draft.version=3;e._saved=clone(e._draft);e._selectedSlot=null;e._entityIndex.clear();e._catalogue=[];
 e._hass.callWS=message=>{calls.push(clone(message));return new Promise((resolve,reject)=>pending.push({message:clone(message),resolve,reject}));};
 return {e,rows,calls,pending};
}
function preview118Reply(request,row) {request.resolve({entities:row?[clone(row)]:[],total:row?1:0,truncated:false});}
function preview118AssertReadOnly(e,calls,before) {
 assert.ok(calls.every(call=>call.type==="atmosfera_echo_hub/catalogue/get"));
 assert.deepEqual(clone(e._draft),before);assert.equal(e.dirty,false);assert.equal(e._undo.length,0);
}

test("Preview118 visible Person and Sun load outside a filtered 200-row catalogue without selection and repaint captions",async()=>{
 const {e,rows,calls,pending}=preview118Editor(),before=clone(e._draft);
 e._query="kitchen";e._domain="light";e._area="area:kitchen";
 const catalogue=context.TestEditor.prototype.fetchCatalogue.call(e);
 pending[0].resolve({entities:Array.from({length:200},(_,i)=>areaEntity(`light.room_${i}`)),total:250,truncated:true,areas:[{area_id:"kitchen",area_name:"Kitchen"}],areas_truncated:false});await catalogue;
 const labels=[2,3].map(slot=>({dataset:{liveSlot:String(slot)},textContent:e.stateText(e.cardAt(slot))}));
 e.shadowRoot.querySelectorAll=selector=>selector==="[data-live-slot]"?labels:[];
 for(const label of labels)assert.equal(label.textContent,e.t("extraLoading"));
 e.paintPreview();const requests=[...e._entityMetadataRequests.values()].map(p=>p.promise);
 assert.equal(requests.length,2);assert.equal(e._selectedSlot,null);
 for(const request of pending.slice(1)) {
  assert.deepEqual(request.message,{type:"atmosfera_echo_hub/catalogue/get",entry_id:"screen-a",query:request.message.query,limit:20});
  assert.ok(rows.has(request.message.query));preview118Reply(request,rows.get(request.message.query));
 }
 await Promise.all(requests);
 for(const [index,slot]of [2,3].entries()) {
  assert.equal(labels[index].textContent,["Home","Above horizon"][index]);
  assert.ok(e.extraPreview(e.cardAt(slot)).observation);assert.notEqual(labels[index].textContent,e.t("extraLoading"));
 }
 assert.equal(e._catalogue.length,200);assert.equal(e._catalogueTotal,250);assert.equal(e._selectedSlot,null);
 e.paintPreview();assert.equal(calls.length,3);preview118AssertReadOnly(e,calls,before);
});

test("Preview118 render and inspector share one pending exact lookup and discard unrelated substring results",async()=>{
 const {e,rows,calls,pending}=preview118Editor(["person-home-pl"]),before=clone(e._draft),id=e.cardAt(2).entity_id;
 e._draft.cards.push({...clone(e.cardAt(2)),id:"duplicate",slot:3});e._saved=clone(e._draft);const saved=clone(e._draft);
 e.render();e.paintPreview();const preview=e.fetchPreviewEntities();e._selectedSlot=2;
 const selected=e.fetchSelectedEntity(true);assert.equal(calls.length,1);
 const unrelated={...clone(rows.get(id)),entity_id:id+"_other"};
 pending[0].resolve({entities:[unrelated,clone(rows.get(id))],total:2});await Promise.all([...preview,selected]);
 assert.ok(e.entityFor(id));assert.equal(e.entityFor(unrelated.entity_id),undefined);assert.equal(e._entityMetadataRequests.size,0);
 assert.equal(e._selectedEntityPending,null);preview118AssertReadOnly(e,calls,saved);
 assert.equal(before.cards.length+1,saved.cards.length);
});

test("Preview118 a completed missing or invalid entity is distinct from loading and is not fetched every paint",async()=>{
 for(const result of ["missing","invalid"]) {
  const {e,rows,calls,pending}=preview118Editor(["person-home-pl"]),c=e.cardAt(2),before=clone(e._draft);
  assert.equal(e.extraPreview(c).message,e.t("extraLoading"));const work=e.fetchPreviewEntities();
  assert.equal(e.extraPreview(c).message,e.t("extraLoading"));const row=clone(rows.get(c.entity_id));
  if(result==="invalid")delete row.extra_panel;
  preview118Reply(pending[0],result==="missing"?null:row);await Promise.all(work);
  assert.equal(e.extraPreview(c).message,e.t("extraEntity"));e.paintPreview();e.refreshEntityMetadata();
  assert.equal(calls.length,1);preview118AssertReadOnly(e,calls,before);
 }
});

test("Preview118 transport failures show a retry message and retry only on the existing status cadence",async()=>{
 const {e,rows,calls,pending}=preview118Editor(["person-home-pl"]),c=e.cardAt(2),before=clone(e._draft);
 const first=e.fetchPreviewEntities();pending[0].reject(new Error("offline transport"));await Promise.all(first);
 assert.equal(e.extraPreview(c).message,e.t("extraLoadFailed"));e.paintPreview();e.render();assert.equal(calls.length,1);
 e.refreshEntityMetadata();e.refreshEntityMetadata();assert.equal(calls.length,2);
 const second=[...e._entityMetadataRequests.values()].map(p=>p.promise);preview118Reply(pending[1],rows.get(c.entity_id));await Promise.all(second);
 assert.ok(e.extraPreview(c).observation);preview118AssertReadOnly(e,calls,before);
});

test("Preview118 an in-flight old observation stays stale until the existing cadence obtains the new state",async()=>{
 const {e,rows,calls,pending}=preview118Editor(["person-home-pl"]),c=e.cardAt(2),id=c.entity_id,before=clone(e._draft);
 const oldLive=e._hass.states[id],first=e.fetchPreviewEntities();
 // HA can replace an entry in the same states map while the request is pending.
 e._hass.states[id]={...clone(oldLive),state:"not_home",last_updated:"2026-11-05T21:36:00+01:00"};
 preview118Reply(pending[0],rows.get(id));await Promise.all(first);
 assert.equal(e.entityMetadataStale(e.entityFor(id)),true);assert.equal(e.extraPreview(c).message,e.t("extraRefreshing"));
 e.refreshEntityMetadata();assert.equal(calls.length,2);const second=[...e._entityMetadataRequests.values()].map(p=>p.promise);
 const fresh=clone(rows.get(id));fresh.state="not_home";
 Object.assign(fresh.extra_panel.state,{phase:"away",state_text:"Poza domem",updated_text:e._hass.states[id].last_updated,changed_text:e._hass.states[id].last_updated});
 preview118Reply(pending[1],fresh);await Promise.all(second);
 assert.equal(e.entityMetadataStale(e.entityFor(id)),false);assert.equal(e.extraPreview(c).message,"Poza domem");
 preview118AssertReadOnly(e,calls,before);
});

test("Preview118 out-of-order catalogue and exact responses cannot replace the newer metadata",async()=>{
 for(const newer of ["exact","catalogue"]) {
  const {e,rows,calls,pending}=preview118Editor(["person-home-pl"]),id=e.cardAt(2).entity_id,before=clone(e._draft);
  const startCatalogue=()=>context.TestEditor.prototype.fetchCatalogue.call(e);
  const startExact=()=>Promise.all(e.fetchPreviewEntities());
  const first=newer==="exact"?startCatalogue():startExact(),second=newer==="exact"?startExact():startCatalogue();
  const fresh=clone(rows.get(id));fresh.name="Newest metadata";
  preview118Reply(pending[1],fresh);await second;
  const older=clone(rows.get(id));older.name="Stale metadata";preview118Reply(pending[0],older);await first;
  assert.equal(e.entityFor(id).name,"Newest metadata");assert.ok(e.extraPreview(e.cardAt(2)).observation);
  assert.equal(e._entityMetadataRequests.size,0);preview118AssertReadOnly(e,calls,before);
 }
});

test("Preview118 old-screen replies neither populate the new epoch nor retire its pending request",async()=>{
 const {e,rows,calls,pending}=preview118Editor(["person-home-pl"]),id=e.cardAt(2).entity_id;
 const first=Promise.all(e.fetchPreviewEntities());
 const target=e._data.entries.find(entry=>entry.entry_id==="screen-b");
 target.layout=clone(e._draft);target.profile=clone(e.profile);target.status=clone(e._status);
 e.selectEntry("screen-b");e._pageId="home-2";e.paintPreview();const second=[...e._entityMetadataRequests.values()].map(p=>p.promise);
 assert.equal(calls.length,2);assert.equal(calls[1].entry_id,"screen-b");
 preview118Reply(pending[0],{...clone(rows.get(id)),name:"Old screen"});await first;
 assert.equal(e.entityFor(id),undefined);assert.equal(e._entityMetadataRequests.size,1);
 preview118Reply(pending[1],{...clone(rows.get(id)),name:"New screen"});await Promise.all(second);
 assert.equal(e.entityFor(id).name,"New screen");assert.equal(e._entityMetadataRequests.size,0);
 preview118AssertReadOnly(e,calls,clone(target.layout));
});

test("Preview118 preloading is bounded to visible negotiated Extra launchers on the current page",async()=>{
 const changes=[e=>e.cardAt(2).visible=false,e=>e._pageId="home-4",e=>e.cardAt(2).action={kind:"none"},
  e=>e._status.panel_extra_profiles=[],e=>e.profile.schema_panel_extra_profiles=[],e=>e._hass.connected=false,
  e=>e.isConnected=false,e=>e._profileStale=true,e=>e._statusError=true,e=>e._pending={kind:"review"},
  e=>e._drag={},e=>e._carry={},e=>e._busy=true,e=>delete e._hass.states[e.cardAt(2).entity_id]];
 for(const change of changes) {
  const {e,calls}=preview118Editor(["person-home-pl"]);change(e);const before=clone(e._draft);
  await Promise.all(e.fetchPreviewEntities());assert.equal(calls.length,0);assert.deepEqual(clone(e._draft),before);
 }
 for(const owner of ["schema","runtime"]) {
  const {e}=preview118Editor(["person-home-pl"]);
  if(owner==="schema")e.profile.schema_panel_extra_profiles=[];else e._status.panel_extra_profiles=[];
  assert.equal(e.extraPreview(e.cardAt(2)).message,e.t("extraUnsupported"));
 }
 const {e,rows,calls,pending}=preview118Editor(["person-home-pl"]);
 e._pageId="home-4";e.paintPreview();assert.equal(calls.length,0);
 e._pageId="home-2";e.paintPreview();const work=[...e._entityMetadataRequests.values()].map(p=>p.promise);
 assert.equal(calls.length,1);preview118Reply(pending[0],rows.get(e.cardAt(2).entity_id));await Promise.all(work);
 assert.ok(e.extraPreview(e.cardAt(2)).observation);
});

test("Preview118 negative cache from an older live state cannot imply that the new state was already queried",async()=>{
 for(const previous of ["missing","failed"]) {
  const {e,rows,calls,pending}=preview118Editor(["person-home-pl"]),c=e.cardAt(2),before=clone(e._draft);
  const first=e.fetchPreviewEntities();
  if(previous==="missing")preview118Reply(pending[0],null);else pending[0].reject(new Error("temporary transport failure"));
  await Promise.all(first);
  assert.equal(e.extraPreview(c).message,e.t(previous==="missing"?"extraEntity":"extraLoadFailed"));
  e._hass.states={...e._hass.states,[c.entity_id]:clone(e._hass.states[c.entity_id])};
  assert.equal(e.extraPreview(c).message,e.t("extraLoading"));
  const next=e.fetchPreviewEntities();assert.equal(calls.length,2);preview118Reply(pending[1],rows.get(c.entity_id));await Promise.all(next);
  assert.ok(e.extraPreview(c).observation);preview118AssertReadOnly(e,calls,before);
 }
});

test("Preview118 replies after disconnect never repaint or install either successful or failed metadata",async()=>{
 for(const outcome of ["success","failure"]) {
  const {e,rows,calls,pending}=preview118Editor(["person-home-pl"]),id=e.cardAt(2).entity_id,before=clone(e._draft);
  let paints=0;e.paintValues=()=>{paints++;};const first=e.fetchPreviewEntities();e.isConnected=false;
  if(outcome==="success")preview118Reply(pending[0],rows.get(id));else pending[0].reject(new Error("closed connection"));
  await Promise.all(first);assert.equal(paints,0);assert.equal(e.entityFor(id),undefined);
  assert.equal(e._entityMetadataRequests.size,0);preview118AssertReadOnly(e,calls,before);
 }
});
function datetime119Editor(mode="datetime",sensor=false) {
 const e=lightEditor(),c=e.cardAt(2),values={year:2028,month:2,day:29,hour:23,minute:58,second:37};
 c.entity_id="input_datetime.demo";c.type=sensor?"sensor":"entity";c.action={kind:"none"};
 e.profile.schema_control_types=["light","panel"];e.profile.schema_panel_extra_profiles=[{name:"datetime",version:1}];
 e.profile.datetime_text_slots=[2,3];e.profile.layout_versions=[2,3];
 Object.assign(e._status,{entity_control_status:"ready",native_control_types:["entity_control_v1"],control_kinds:["light","panel"],panel_extra_profiles:[{name:"datetime",version:1}]});
 const tuple=Object.fromEntries(Object.entries(values).map(([k,v])=>[k,(mode==="date"&&["hour","minute","second"].includes(k) || mode==="time"&&["year","month","day"].includes(k))?null:v]));
 const raw=({date:"2028-02-29",time:"23:58:37",datetime:"2028-02-29 23:58:37"})[mode],stamp="2026-11-05T22:00:00+01:00";
 e._hass.states[c.entity_id]={state:raw,attributes:{has_date:mode!=="time",has_time:mode!=="date",editable:false,...Object.fromEntries(Object.entries(tuple).filter(([,v])=>v!==null))},last_updated:stamp};
 e._hass.services={input_datetime:{set_datetime:{}}};
 e._entityIndex.set(c.entity_id,{entity_id:c.entity_id,domain:"input_datetime",state:raw,available:true,actions:[],
  datetime_panel:{version:1,panel_type:"datetime",caps:{mode,can_set:true,zone_text:mode==="datetime"?"Europe/Warsaw":""},fingerprint:"d".repeat(64),state:{source:"known",...tuple,updated_text:stamp},available:true,eligible_actions:1}});
 return e;
}
function enableDatetime119(e) { assert.equal(e.requestLightControl("datetimepanel"),true);assert.equal(e.confirmLightControl(),true); }

test("Datetime119 three modes require explicit draft review and keep provider data untouched",()=>{
 for(const mode of ["date","time","datetime"]) {
  const e=datetime119Editor(mode),before=clone(e._draft),live=clone(e._hass.states);
  assert.equal(e.datetimePanelAvailability().ready,true);assert.match(e.inspectorMarkup(),/control-datetimepanel/);
  e.editField(actionInput("control-datetimepanel"));assert.deepEqual(clone(e._draft),before);
  assert.equal(e.confirmLightControl(),true);assert.equal(e._draft.version,3);
  assert.deepEqual(clone(e.cardAt(2).action),{kind:"control",control:"panel",property:"datetime"});
  assert.deepEqual(clone(e._hass.states),live);assert.doesNotThrow(()=>e.validateStoredDraft(extraStored(e)));
  assert.doesNotMatch(e.datetimePanelPreviewMarkup(e.cardAt(2)),/<button|data-action=/);
  e.history("undo");assert.deepEqual(clone(e._draft),before);
 }
});
test("Datetime119 passive wide sensor converts only after review and then moves to ordinary slots",()=>{
 const e=datetime119Editor("datetime",true),c=e.cardAt(2);
 e.profile.schema_state_labels=true;c.state_labels={"2028-02-29 23:58:37":"Custom"};
 const before=clone(e._draft);assert.equal(e.acceptsCard(e.slotAt(13),c),false);
 assert.equal(e.sensorActionEditable(c),true);assert.equal(e.requestLightControl("datetimepanel"),true);
 assert.match(e.modalMarkup(),/Sensor-only formatting will be removed/);assert.deepEqual(clone(e._draft),before);
 assert.equal(e.confirmLightControl(),true);assert.equal(c.type,"entity");assert.equal(c.state_labels,undefined);
 assert.equal(e.acceptsCard(e.slotAt(13),c),true);assert.equal(e.moveCard(2,13),true);
 assert.doesNotThrow(()=>e.validateStoredDraft(extraStored(e)));
 assert.equal(e.isDatetimePanelAction({...c,type:"sensor"}),false);
});
test("Datetime119 needs its own actual schema and runtime profile without Info or Action dependencies",()=>{
 for(const change of [e=>e._status.panel_extra_profiles=[],e=>e.profile.schema_panel_extra_profiles=[],
  e=>e._status.panel_extra_profiles=[{name:"datetime",version:2}],e=>e._status.panel_extra_profiles=[{name:"datetime",version:1},{name:"datetime",version:1}],
  e=>e._status.control_kinds=[],e=>e._status.entity_control_status="offline",e=>e._hass.connected=false,
  e=>e._statusError=true,e=>e._profileStale=true,e=>e.profile.layout_versions=[2],e=>e.profile.schema_control_types=["light"]]) {
  const e=datetime119Editor();change(e);const before=clone(e._draft);
  assert.equal(e.requestLightControl("datetimepanel"),false);assert.deepEqual(clone(e._draft),before);
 }
 const e=datetime119Editor();assert.equal(e.datetimePanelAvailability().ready,true);
 enableDatetime119(e);const record=extraStored(e);e._status.panel_extra_profiles=[];
 assert.doesNotThrow(()=>e.validateStoredDraft(record));e.profile.schema_panel_extra_profiles=[];
 assert.throws(()=>e.validateStoredDraft(record));
});
test("Datetime119 closed metadata rejects coercion, field masks, bad Gregorian dates and extra keys",()=>{
 const changes=[m=>m.other=true,m=>m.caps.other=true,m=>m.state.other=true,m=>delete m.state.second,m=>m.version=2,
  m=>m.caps.can_set=1,m=>m.caps.mode="clock",m=>m.state.year=true,m=>m.state.year="2028",m=>m.state.year=2028.5,
  m=>m.state.year=0,m=>m.state.year=10000,m=>m.state.year=2100,m=>m.state.month=13,m=>m.state.day=30,
  m=>m.state.hour=24,m=>m.state.minute=60,m=>m.state.second=60,m=>m.state.hour=null,m=>m.state.source="other",
  m=>m.state.updated_text="2026-02-30T00:00:00+01:00",m=>m.state.updated_text="2026-11-05T22:00:00Z",
  m=>m.caps.zone_text="a".repeat(49),m=>m.caps.zone_text="bad\nzone",m=>m.fingerprint="bad",m=>m.available=1,m=>m.eligible_actions=true];
 for(const change of changes){const e=datetime119Editor();change(e.entityFor(e.cardAt(2).entity_id).datetime_panel);assert.equal(e.datetimePanelMetadata(e.cardAt(2)),null);}
 for(const mode of ["date","time"]){const e=datetime119Editor(mode),c=e.cardAt(2),m=e.entityFor(c.entity_id).datetime_panel;m.caps.zone_text="Europe/Warsaw";assert.equal(e.datetimePanelMetadata(c),null);m.caps.zone_text="";m.state[mode==="date"?"second":"year"]=1;assert.equal(e.datetimePanelMetadata(c),null);}
});
test("Datetime119 observation uses exact attributes, equivalent bounded years and all seconds",()=>{
 const e=datetime119Editor(),c=e.cardAt(2),m=e.entityFor(c.entity_id).datetime_panel,live=e._hass.states[c.entity_id];enableDatetime119(e);
 for(const year of [1,4,100,400,999,1000,9999]) {
  Object.assign(m.state,{year,month:1,day:1});Object.assign(live.attributes,{year,month:1,day:1});
  for(const spelling of [String(year),String(year).padStart(4,"0")]) {
   live.state=`${spelling}-01-01 23:58:37`;e.entityFor(c.entity_id).state=live.state;
   assert.ok(e.datetimePanelPreview(c).observation);assert.match(e.stateText(c),/23:58:37$/);
  }
 }
 for(const bad of [" 9999-01-01 23:58:37","9999-1-01 23:58:37","9999-01-01 23:58:37Z","+9999-01-01 23:58:37","９９９９-01-01 23:58:37"]){live.state=bad;e.entityFor(c.entity_id).state=bad;assert.equal(e.datetimePanelPreview(c).observation,undefined);}
 live.state="9999-01-01 23:58:37";e.entityFor(c.entity_id).state=live.state;live.attributes.second="37";
 assert.equal(e.datetimePanelPreview(c).observation,undefined);
 for(const mode of ["date","time","datetime"]) {
  const x=datetime119Editor(mode),card=x.cardAt(2),state=x._hass.states[card.entity_id];
  state.state+="\n";assert.equal(x.datetimeObservedTuple(state,mode),null);
 }
});
test("Datetime119 read-only service capability and YAML editable false do not hide the view",()=>{
 const e=datetime119Editor(),c=e.cardAt(2),m=e.entityFor(c.entity_id).datetime_panel;
 assert.equal(e._hass.states[c.entity_id].attributes.editable,false);assert.equal(e.datetimePanelAvailability().ready,true);
 delete e._hass.services.input_datetime.set_datetime;assert.equal(e.datetimePanelAvailability().ready,false);
 m.caps.can_set=false;m.eligible_actions=0;assert.equal(e.datetimePanelAvailability().ready,true);
 assert.equal(e.datetimePanelAvailability().reason,"datetimePanelPassive");enableDatetime119(e);
 assert.ok(e.datetimePanelPreview(c).observation);
});
test("Datetime119 unknown and unavailable snapshots have no invented tuple",()=>{
 for(const source of ["unknown","unavailable"]) {
  const e=datetime119Editor(),c=e.cardAt(2),m=e.entityFor(c.entity_id).datetime_panel;
  m.state.source=source;for(const key of ["year","month","day","hour","minute","second"])m.state[key]=null;
  m.available=false;m.eligible_actions=0;e.entityFor(c.entity_id).state=source;e._hass.states[c.entity_id].state=source;
  assert.ok(e.datetimePanelMetadata(c));enableDatetime119(e);
  assert.equal(e.stateText(c),e.t(source==="unavailable"?"offline":"unknown"));
  assert.doesNotMatch(e.datetimePanelPreviewMarkup(c),/2028|23:58:37|Europe\/Warsaw/);
 }
});
test("Datetime119 config review ignores value telemetry and zone but detects changed capabilities",()=>{
 const e=datetime119Editor(),c=e.cardAt(2),m=e.entityFor(c.entity_id).datetime_panel;
 assert.equal(e.requestLightControl("datetimepanel"),true);
 m.state.second=38;m.caps.zone_text="UTC";e._hass.states[c.entity_id].attributes.second=38;
 assert.equal(e.confirmLightControl(),true);
 for(const mutate of [e=>e.entityFor(e.cardAt(2).entity_id).datetime_panel.fingerprint="e".repeat(64),e=>delete e._hass.services.input_datetime.set_datetime,e=>e._hass.states[e.cardAt(2).entity_id].attributes.has_time=false]){
  const x=datetime119Editor();assert.equal(x.requestLightControl("datetimepanel"),true);mutate(x);assert.equal(x.confirmLightControl(),false);
 }
});
test("Datetime119 preview masks same-second stale values and escapes metadata",()=>{
 const e=datetime119Editor(),c=e.cardAt(2),m=e.entityFor(c.entity_id).datetime_panel,live=e._hass.states[c.entity_id];enableDatetime119(e);
 m.caps.zone_text="<img src=x onerror=alert(1)>";
 assert.match(e.datetimePanelPreviewMarkup(c),/&lt;img/);assert.doesNotMatch(e.datetimePanelPreviewMarkup(c),/<img/);
 live.state="2028-02-29 23:58:38";live.attributes.second=38;
 assert.equal(e.stateText(c),e.t("extraRefreshing"));assert.doesNotMatch(e.datetimePanelPreviewMarkup(c),/23:58:37|onerror/);
 e.entityFor(c.entity_id).state=live.state;m.state.second=38;assert.match(e.stateText(c),/23:58:38/);
 live.last_updated="2026-11-05T22:00:01+01:00";assert.equal(e.stateText(c),e.t("extraRefreshing"));
});
test("Datetime119 saved launcher preloads on visible page and shares selected lookup without writes",async()=>{
 const e=datetime119Editor(),c=e.cardAt(2);enableDatetime119(e);const row=clone(e.entityFor(c.entity_id)),before=clone(e._draft),calls=[];
 e._entityIndex.delete(c.entity_id);e._selectedSlot=null;
 let finish;e._hass.callWS=message=>{calls.push(message);return new Promise(resolve=>{finish=resolve;});};
 assert.equal(e.stateText(c),e.t("extraLoading"));const pending=e.fetchPreviewEntities();assert.equal(calls.length,1);
 assert.equal(calls[0].type,"atmosfera_echo_hub/catalogue/get");assert.equal(calls[0].query,c.entity_id);
 e._selectedSlot=2;const selected=e.fetchSelectedEntity();assert.equal(calls.length,1);
 finish({entities:[row],total:1,truncated:false});await Promise.all([...pending,selected]);
 assert.match(e.stateText(c),/23:58:37/);assert.deepEqual(clone(e._draft),before);
});
test("Datetime119 actual backend catalogue observations pass closed UI preview and explicit conversion",()=>{
 const rows=JSON.parse(fs.readFileSync(path.join(__dirname,"fixtures/datetime_panel/actual-domain.json"),"utf8"));
 assert.equal(rows.length,8);
 for(const row of rows) {
  const e=datetime119Editor(row.metadata.datetime_panel.caps.mode),c=e.cardAt(2);c.entity_id=row.entity_id;
  e._hass.states[c.entity_id]=clone(row.state);
  e._hass.services={input_datetime:Object.fromEntries(row.services.map(key=>[key,{}]))};
  e._entityIndex.set(c.entity_id,{entity_id:c.entity_id,domain:"input_datetime",state:row.state.state,actions:[],...clone(row.metadata)});
  assert.ok(e.datetimePanelMetadata(c),row.name);assert.equal(e.datetimePanelAvailability(c).ready,true,row.name);
  enableDatetime119(e);assert.doesNotThrow(()=>e.validateStoredDraft(extraStored(e)),row.name);
  const preview=e.datetimePanelPreview(c);
  assert.equal(Boolean(preview.observation),row.metadata.datetime_panel.available,row.name);
  if(row.metadata.datetime_panel.available) assert.notEqual(preview.message,e.t("extraRefreshing"),row.name);
 }
});

function text120Editor({value="Zażółć gęślą jaźń",attrs={},sensor=false,service=true}={}) {
 const e=lightEditor(),c=e.cardAt(2);
 c.entity_id="input_text.demo";c.type=sensor?"sensor":"entity";c.action={kind:"none"};
 e.profile.schema_control_types=["light","panel"];e.profile.schema_panel_extra_profiles=[{name:"text",version:1}];e.profile.layout_versions=[2,3];
 Object.assign(e._status,{entity_control_status:"ready",native_control_types:["entity_control_v1"],control_kinds:["light","panel"],panel_extra_profiles:[{name:"text",version:1}]});
 e._hass.states[c.entity_id]={state:value,attributes:{mode:"text",min:0,max:255,editable:false,...attrs}};
 e._hass.services={input_text:service?{set_value:{}}:{}};
 const actual=e.textPanelLive(e._hass.states[c.entity_id]);
 e._entityIndex.set(c.entity_id,{entity_id:c.entity_id,domain:"input_text",state:value,actions:[],text_panel:{version:1,panel_type:"text",
  caps:clone(actual.caps),fingerprint:"d".repeat(64),state:clone(actual.state),available:actual.state.source==="known",eligible_actions:actual.state.source==="known"&&actual.caps.can_set?1:0}});
 return e;
}
function enableText120(e) { assert.equal(e.requestLightControl("textpanel"),true);assert.equal(e.confirmLightControl(),true); }

test("Text120 explicit conversion reviews draft only, removes sensor formatting and supports Undo",()=>{
 for(const sensor of [false,true]) {
  const e=text120Editor({sensor}),c=e.cardAt(2),live=clone(e._hass.states);
  if(sensor){e.profile.schema_state_labels=true;c.state_labels={"Zażółć gęślą jaźń":"Caption"};}
  const before=clone(e._draft);assert.equal(e.textPanelAvailability().ready,true);assert.equal(e.sensorActionEditable(c),true);
  assert.match(e.inspectorMarkup(),/control-textpanel/);e.editField(actionInput("control-textpanel"));assert.deepEqual(clone(e._draft),before);
  assert.match(e.modalMarkup(),/No text is sent/);assert.equal(e.confirmLightControl(),true);
  assert.equal(e._draft.version,3);assert.equal(c.type,"entity");assert.equal(c.state_labels,undefined);
  assert.deepEqual(clone(c.action),{kind:"control",control:"panel",property:"text"});
  assert.doesNotThrow(()=>e.validateStoredDraft(extraStored(e)));assert.deepEqual(clone(e._hass.states),live);
  assert.doesNotMatch(e.textPanelPreviewMarkup(c),/<button|data-action=/);
  assert.equal(e.moveCard(2,13),true);e.history("undo");e.history("undo");assert.deepEqual(clone(e._draft),before);
 }
});

test("Text120 requires independent profile and connection, saved layout remains usable by older peer",()=>{
 for(const mutate of [e=>e._status.panel_extra_profiles=[],e=>e.profile.schema_panel_extra_profiles=[],e=>e._status.panel_extra_profiles=[{name:"text",version:2}],
  e=>e._status.panel_extra_profiles=[{name:"text",version:1},{name:"text",version:1}],e=>e._status.entity_control_status="offline",e=>e._status.control_kinds=[],
  e=>e._hass.connected=false,e=>e._profileStale=true,e=>e._statusError=true,e=>e.profile.layout_versions=[2]]) {
  const e=text120Editor();mutate(e);const before=clone(e._draft);assert.equal(e.requestLightControl("textpanel"),false);assert.deepEqual(clone(e._draft),before);
 }
 const e=text120Editor();enableText120(e);const stored=extraStored(e);e._status.panel_extra_profiles=[];
 assert.doesNotThrow(()=>e.validateStoredDraft(stored));e.profile.schema_panel_extra_profiles=[];assert.throws(()=>e.validateStoredDraft(stored));
});

test("Text120 exact strings, full Polish codepoints, empty and whitespace remain unchanged",()=>{
 for(const value of [""," ","Zażółć gęślą jaźń","Ż".repeat(255),'\\"'.repeat(127)+'"']) {
  const e=text120Editor({value}),c=e.cardAt(2);enableText120(e);const p=e.textPanelPreview(c);
  assert.equal(p.observation.value,value);assert.equal(p.message,value || e.t("textPanelEmpty"));
  assert.match(e.textPanelPreviewMarkup(c),new RegExp(`${[...value].length} / 255`));
 }
 for(const [value,reason] of [["x".repeat(256),"length"],["\ud800","encoding"],[null,"encoding"],[1,"encoding"],["a\n","characters"],["🙂","characters"],["a\u0301","characters"],["\x7f","characters"]]) {
  const e=text120Editor({value}),c=e.cardAt(2);assert.equal(e.textPanelLive(e._hass.states[c.entity_id]).state.reason,reason);
  assert.ok(e.textPanelMetadata(c));enableText120(e);assert.equal(e.textPanelPreview(c).observation,undefined);
 }
 for(const value of ["unknown","unavailable"]) {
  const e=text120Editor({value}),c=e.cardAt(2);enableText120(e);assert.equal(e.textPanelPreview(c).observation,undefined);
  assert.equal(e.stateText(c),e.t(value==="unknown"?"unknown":"offline"));
 }
});

test("Text120 privacy wins over stale metadata without reading hidden live value",()=>{
 for(const mode of ["password","other",undefined]) {
  const e=text120Editor(),c=e.cardAt(2);enableText120(e);const live=e._hass.states[c.entity_id];live.attributes.mode=mode;
  Object.defineProperty(live,"state",{get(){throw new Error("private state read");}});
  assert.equal(e.textPanelPreview(c).message,e.t("textPanelHidden"));
  assert.doesNotMatch(e.textPanelPreviewMarkup(c),/Zażółć/);
 }
 for(const pattern of ["", ".*", "[a-z]+", false]) {
  const e=text120Editor({attrs:{pattern}}),c=e.cardAt(2);assert.ok(e.textPanelMetadata(c));enableText120(e);
  assert.equal(e.textPanelPreview(c).message,e.t("textPanelPattern"));assert.doesNotMatch(e.textPanelPreviewMarkup(c),/Zażółć/);
 }
 const e=text120Editor({attrs:{pattern:null}});assert.equal(e.textPanelAvailability().ready,true);
});

test("Text120 closed metadata rejects coercion and inconsistent unsupported matrix",()=>{
 for(const mutate of [m=>m.other=1,m=>m.caps.other=1,m=>m.state.other=1,m=>m.caps.min=true,m=>m.caps.max="255",m=>m.caps.max=256,
  m=>m.caps.min=-1,m=>m.caps.max=0,m=>m.caps.can_set=1,m=>m.state.value=null,m=>m.state.value="unknown",m=>m.state.value="\n",
  m=>m.state.source=[],m=>m.state.reason=[],m=>m.state.reason="password",m=>m.available=1,m=>m.eligible_actions=true,m=>m.version=2,m=>m.fingerprint="bad"]) {
  const e=text120Editor(),c=e.cardAt(2);mutate(e.entityFor(c.entity_id).text_panel);assert.equal(e.textPanelMetadata(c),null);
 }
 for(const attrs of [{min:true},{max:256},{min:2,max:1}]) {
  const e=text120Editor({attrs}),c=e.cardAt(2);assert.ok(e.textPanelMetadata(c));enableText120(e);assert.equal(e.textPanelPreview(c).message,e.t("textPanelBounds"));
 }
});

test("Text120 source telemetry does not cancel configuration review, capability or stale metadata does",()=>{
 const e=text120Editor(),c=e.cardAt(2);assert.equal(e.requestLightControl("textpanel"),true);
 e._hass.states[c.entity_id].state="New";e.entityFor(c.entity_id).text_panel.state.value="New";
 assert.equal(e.confirmLightControl(),true);
 for(const mutate of [e=>e.entityFor(e.cardAt(2).entity_id).text_panel.fingerprint="e".repeat(64),e=>delete e._hass.services.input_text.set_value,
  e=>e._hass.states[e.cardAt(2).entity_id].attributes.max=254,e=>e._hass.states[e.cardAt(2).entity_id].attributes.mode="password"]) {
  const x=text120Editor();assert.equal(x.requestLightControl("textpanel"),true);mutate(x);assert.equal(x.confirmLightControl(),false);
 }
});

test("Text120 preview escapes public value and never paints stale value",()=>{
 const e=text120Editor({value:'<img src=x onerror="bad">'}),c=e.cardAt(2);enableText120(e);
 assert.match(e.textPanelPreviewMarkup(c),/&lt;img/);assert.doesNotMatch(e.textPanelPreviewMarkup(c),/<img/);
 e._hass.states[c.entity_id].state="New";assert.equal(e.stateText(c),e.t("extraRefreshing"));assert.doesNotMatch(e.textPanelPreviewMarkup(c),/onerror/);
 const meta=e.entityFor(c.entity_id);e._entityStateRefs.set(meta,e._hass.states[c.entity_id]);e._hass.states[c.entity_id]=clone(e._hass.states[c.entity_id]);
 meta.text_panel.state.value="New";assert.equal(e.stateText(c),e.t("extraRefreshing"));
});

test("Text120 actual adapter corpus passes independent closed metadata validation",()=>{
 const rows=JSON.parse(fs.readFileSync(path.join(__dirname,"fixtures/text_panel/catalog.json"),"utf8"));assert.equal(rows.length,16);
 for(const row of rows) {
  const e=text120Editor(),c=e.cardAt(2);e.entityFor(c.entity_id).text_panel=clone(row.metadata);
  assert.ok(e.textPanelMetadata(c),row.name);
 }
});

test("Text120 saved launcher fetches read-only catalogue and shares selected lookup",async()=>{
 const e=text120Editor(),c=e.cardAt(2);enableText120(e);const row=clone(e.entityFor(c.entity_id)),before=clone(e._draft),calls=[];
 e._entityIndex.delete(c.entity_id);e._selectedSlot=null;let finish;
 e._hass.callWS=message=>{calls.push(message);return new Promise(resolve=>{finish=resolve;});};
 const pending=e.fetchPreviewEntities();assert.equal(calls.length,1);assert.equal(calls[0].type,"atmosfera_echo_hub/catalogue/get");
 e._selectedSlot=2;const selected=e.fetchSelectedEntity();assert.equal(calls.length,1);
 finish({entities:[row],total:1,truncated:false});await Promise.all([...pending,selected]);
 assert.equal(e.stateText(c),"Zażółć gęślą jaźń");assert.deepEqual(clone(e._draft),before);
});


test("Action friendly last-use keeps microseconds and the supplied DST offset in both locales",()=>{
 const e=actionPanelEditor(),c=e.cardAt(2);c.action={kind:"control",control:"panel",property:"action"};
 const meta=e.entityFor(c.entity_id).action_panel;
 for(const [language,month] of [["en","October"],["pl","października"]]) {
  e._hass.locale.language=language;
  for(const offset of ["+02:00","+01:00","+05:45","-03:30"]) {
   const value=`2026-10-25T02:30:59.000001${offset}`;
   meta.state.last_used_status="value";meta.state.last_used_text=value;
   const before=JSON.stringify({draft:e._draft,meta});
   assert.equal(e.actionLastUsedText(value),`25 ${month} 2026 · 02:30:59.000001 · UTC${offset}`);
   assert.ok(e.actionPanelPreviewMarkup(c).includes(`25 ${month} 2026 · 02:30:59.000001 · UTC${offset}`));
   assert.equal(JSON.stringify({draft:e._draft,meta}),before);
  }
 }
});

test("Action friendly last-use rejects invalid dates without inventing a time for unknown states",()=>{
 const e=actionPanelEditor(),c=e.cardAt(2);c.action={kind:"control",control:"panel",property:"action"};
 for(const value of ["2026-02-29T12:00:00+00:00","2100-02-29T12:00:00+00:00","2026-04-31T12:00:00+00:00",
  "0000-01-01T12:00:00+00:00","2026-01-01T24:00:00+00:00","2026-01-01T12:00:60+00:00",
  "2026-01-01T12:00:00.1234567+00:00","2026-01-01T12:00:00+24:00","2026-01-01T12:00:00Z","<script>"])
  assert.equal(e.actionLastUsedText(value),e.t("actionPanelLastInvalid"));
 for(const value of ["2000-02-29T00:00:00.1+00:00","2400-02-29T23:59:59.123456-03:30"])
  assert.ok(e.actionLastUsedText(value).startsWith("29 February"));
 const meta=e.entityFor(c.entity_id).action_panel;
 for(const [status,key] of [["unknown","actionPanelLastUnknown"],["invalid","actionPanelLastInvalid"],["too_long","actionPanelLastInvalid"]]) {
  meta.state.last_used_status=status;meta.state.last_used_text="";
  assert.ok(e.actionPanelPreviewMarkup(c).includes(e.t(key)));
 }
});

test("Camera launcher preview captions are short while configuration wording and saved intent stay explicit",()=>{
 const e=cameraPreviewEditor(),c=e.cardAt(2);c.action={kind:"camera_preview",duration_seconds:35};
 c.title="My custom camera name";
 for(const [language,ready,unavailable,review] of [["en","Open","Unavailable","Open camera"],["pl","Otwórz","Niedostępna","Otwórz kamerę"]]) {
  e._hass.locale.language=language;e._status.camera_preview_supported=true;
  const before=JSON.stringify(e._draft);
  assert.equal(e.stateText(c),ready);
  assert.equal(e.t("cameraPreview"),review);
  e._status.camera_preview_supported=false;
  assert.equal(e.stateText(c),unavailable);
  assert.equal(JSON.stringify(e._draft),before);
 }
});

function actionParametersEditor(defaultValue=null) {
 const e=actionPanelEditor("script"),c=e.cardAt(2),entity=e.entityFor(c.entity_id);
 e.profile.schema_action_parameters_version=1;e._status.action_parameters_version=1;e._hass.user={id:"editor-user"};
 entity.action_parameters=clone(entity.action_panel);
 Object.assign(entity.action_parameters.caps,{parameters_version:1,parameter_status:"ready",parameter_label:"Potwierdź test",parameter_default:defaultValue});
 entity.action_parameters.fingerprint="1".repeat(64);
 return e;
}
function enableActionParameters(e) {
 assert.equal(e.requestLightControl("actionparameterspanel"),true);
 assert.equal(e.confirmLightControl(),true);
}

test("ActionParams1 requires explicit reviewed opt-in and Undo never stores a parameter value",()=>{
 for(const type of ["entity","action"]) for(const defaultValue of [null,false,true]) {
  const e=actionParametersEditor(defaultValue),c=e.cardAt(2);c.type=type;
  const before=clone(e._draft),saved=clone(e._saved),live=clone(e._hass.states);
  assert.match(e.inspectorMarkup(),/value="control-actionpanel"/);
  assert.match(e.inspectorMarkup(),/value="control-actionparameterspanel"/);
  e.editField(actionInput("control-actionparameterspanel"));
  assert.deepEqual(clone(e._draft),before);assert.match(e.modalMarkup(),/No parameter value is saved/);
  assert.match(e.modalMarkup(),defaultValue===null?/No default/:defaultValue?/Default: Yes/:/Default: No/);
  assert.doesNotMatch(e.modalMarkup(),/does not pass script parameters/);
  assert.equal(e.confirmLightControl(),true);
  assert.deepEqual(clone(c.action),{kind:"control",control:"panel",property:"action",parameters:"boolean_v1"});
  assert.equal(e.isActionPanelAction(c),false);assert.equal(e.validActionParametersAction(c),true);
  assert.match(e.inspectorMarkup(),/value="control-actionparameterspanel" selected/);
  assert.deepEqual(clone(e._saved),saved);assert.deepEqual(clone(e._hass.states),live);
  assert.doesNotThrow(()=>e.validateStoredDraft(extraStored(e)));
  e.history("undo");assert.deepEqual(clone(e._draft),before);
 }
});

test("ActionParams1 conversion is explicit both ways and does not migrate old Action2",()=>{
 const e=actionParametersEditor();e.requestLightControl("actionpanel");e.confirmLightControl();
 const old=clone(e.cardAt(2).action);assert.deepEqual(old,{kind:"control",control:"panel",property:"action"});
 assert.equal(e.cardControlKind(e.cardAt(2)),"actionpanel");
 enableActionParameters(e);assert.equal(e.requestLightControl("actionparameterspanel"),false);
 assert.match(e.inspectorMarkup(),/value="control-actionpanel"/);
 assert.equal(e.requestLightControl("actionpanel"),true);assert.equal(e.confirmLightControl(),true);
 assert.deepEqual(clone(e.cardAt(2).action),old);
 e.history("undo");assert.equal(e.cardAt(2).action.parameters,"boolean_v1");
});

test("ActionParams1 is script-only, rejects legacy variables and never derives the direct service from entity suffix",()=>{
 const e=actionParametersEditor(),old=e.cardAt(2).entity_id,newId="script.renamed_entity";
 e._hass.states[newId]=e._hass.states[old];delete e._hass.states[old];
 e._entityIndex.set(newId,{...e.entityFor(old),entity_id:newId});e.cardAt(2).entity_id=newId;
 delete e._hass.services.script.turn_on;e._hass.services.script.original_registered_id={};
 assert.equal(e.actionParametersAvailability().ready,true);enableActionParameters(e);
 for(const domain of ["button","input_button","scene","automation"]) {
  const other=actionPanelEditor(domain);other.profile.schema_action_parameters_version=1;other._status.action_parameters_version=1;
  other.entityFor(other.cardAt(2).entity_id).action_parameters=clone(e.entityFor(newId).action_parameters);
  assert.equal(other.requestLightControl("actionparameterspanel"),false);
 }
 for(const a of [{kind:"service",service:"script.turn_on",data:{variables:{enabled:false}}},
  {kind:"service",service:"script.other",data:{}},{kind:"control",control:"panel",property:"action",parameters:"future"}]) {
  const bad=actionParametersEditor();bad.cardAt(2).action=a;const before=clone(bad._draft);
  assert.equal(bad.requestLightControl("actionparameterspanel"),false);assert.deepEqual(clone(bad._draft),before);
 }
});

test("ActionParams1 negotiation and exact metadata fail closed without changing saved intent",()=>{
 const changes=[e=>delete e.profile.schema_action_parameters_version,e=>e.profile.schema_action_parameters_version=true,
  e=>e._status.action_parameters_version=0,e=>e._status.action_parameters_version=true,e=>e._status.panel_extra_profiles=[],
  e=>e.profile.schema_panel_extra_profiles=[{name:"action",version:1}],e=>e._hass.connected=false,e=>e._status.device_available=false,
  e=>e._status.entity_control_status="loading",e=>e._profileStale=true,e=>e._statusError="lost",
  e=>e.cardAt(2).visible=false,e=>e.cardAt(2).type="sensor",e=>e.profile.slots.find(s=>s.slot===2).hidden=true,
  e=>delete e._hass.services.script.turn_off,e=>delete e._hass.states[e.cardAt(2).entity_id]];
 for(const change of changes) {const e=actionParametersEditor(),before=clone(e._draft);change(e);
  const changed=clone(e._draft);assert.equal(e.requestLightControl("actionparameterspanel"),false);assert.deepEqual(clone(e._draft),changed);}
 const invalid=[{parameters_version:2},{parameters_version:true},{parameter_status:"optional"},{parameter_label:""},
  {parameter_label:" "},{parameter_label:"a\n"},{parameter_label:"ą".repeat(49)},{parameter_label:3},
  {parameter_default:0},{parameter_default:"false"},{parameter_default:[]},{parameter_key:"enabled"},
  {run_blocked:"needs_parameters"},{operations:true}];
 for(const patch of invalid) {const e=actionParametersEditor();Object.assign(e.entityFor(e.cardAt(2).entity_id).action_parameters.caps,patch);
  assert.equal(e.actionParametersMetadata(e.cardAt(2)),null,JSON.stringify(patch));assert.equal(e.requestLightControl("actionparameterspanel"),false);}
 for(const status of ["unsupported","metadata_unavailable"]) {const e=actionParametersEditor();enableActionParameters(e);
  const c=e.entityFor(e.cardAt(2).entity_id).action_parameters.caps;
  Object.assign(c,{parameter_status:status,parameter_label:"",parameter_default:null,run_blocked:status==="unsupported"?"needs_parameters":"metadata_unavailable"});
  e.entityFor(e.cardAt(2).entity_id).action_parameters.eligible_actions=0;
  assert.ok(e.actionParametersMetadata(e.cardAt(2)));assert.equal(e.actionParametersAvailability().ready,false);
  assert.match(e.inspectorMarkup(),/value="control-actionparameterspanel" selected disabled/);
  assert.doesNotThrow(()=>e.validateStoredDraft(extraStored(e)));assert.equal(e.cardAt(2).action.parameters,"boolean_v1");}
});

test("ActionParams1 review fences descriptor, default, fingerprint, channel and layout changes",()=>{
 const changes=[e=>e.entityFor(e.cardAt(2).entity_id).action_parameters.caps.parameter_default=false,
  e=>e.entityFor(e.cardAt(2).entity_id).action_parameters.caps.parameter_label="Replacement",
  e=>e.entityFor(e.cardAt(2).entity_id).action_parameters.fingerprint="2".repeat(64),
  e=>e._status.action_parameters_version=0,e=>e._selectionEpoch++,e=>e._saved.revision++,e=>e._hass.user.id="other"];
 for(const change of changes) {const e=actionParametersEditor(),before=clone(e._draft);
  assert.equal(e.requestLightControl("actionparameterspanel"),true);change(e);
  assert.equal(e.confirmLightControl(),false);assert.deepEqual(clone(e._draft),before);}
 const e=actionParametersEditor();assert.equal(e.requestLightControl("actionparameterspanel"),true);
 const m=e.entityFor(e.cardAt(2).entity_id).action_parameters;
 Object.assign(m.state,{last_used_status:"value",last_used_text:"2026-11-07T12:34:56.123456+01:00",current:4});
 assert.equal(e.confirmLightControl(),true);assert.match(e.actionPanelPreviewMarkup(e.cardAt(2)),/12:34:56.123456 · UTC\+01:00/);
});

test("ActionParams1 stored schema rejects value injection, wrong domains and accidental old-peer acceptance",()=>{
 const e=actionParametersEditor();enableActionParameters(e);const record=extraStored(e);
 for(const patch of [{parameter_value:false},{parameters:true},{parameters:"boolean_v2"},{skip_condition:false},{data:{}},
  {property:"info"},{control:"choice"},{kind:"default"}]) {
  const bad=clone(record);Object.assign(bad.layout.cards.find(c=>c.slot===2).action,patch);assert.throws(()=>e.validateStoredDraft(bad));}
 const old=clone(record);delete e.profile.schema_action_parameters_version;assert.throws(()=>e.validateStoredDraft(old));
 e.profile.schema_action_parameters_version=1;
 for(const type of ["sensor"]) {const bad=clone(record);bad.layout.cards.find(c=>c.slot===2).type=type;assert.throws(()=>e.validateStoredDraft(bad));}
 for(const domain of ["button","automation"]) {const bad=clone(record);bad.layout.cards.find(c=>c.slot===2).entity_id=domain+".test";assert.throws(()=>e.validateStoredDraft(bad));}
 e._status.action_parameters_version=0;assert.doesNotThrow(()=>e.validateStoredDraft(record));
 assert.match(e.inspectorMarkup(),/value="control-actionparameterspanel" selected disabled/);
 assert.equal(e.requestLightControl("actionparameterspanel"),false);
});

test("ActionParams1 escapes complete metadata labels and distinguishes no default from false in both locales",()=>{
 for(const language of ["pl","en"]) for(const value of [null,false,true]) {
  const e=actionParametersEditor(value);e._hass.locale.language=language;
  e.entityFor(e.cardAt(2).entity_id).action_parameters.caps.parameter_label='<img src=x onerror="boom">';
  const html=e.actionParametersPreviewMarkup(e.cardAt(2));
  assert.match(html,/&lt;img/);assert.doesNotMatch(html,/<img|data-field=|<input/);
  assert.match(html,language==="pl"?(value===null?/Brak wartości domyślnej/:value?/Domyślnie: Tak/:/Domyślnie: Nie/):(value===null?/No default/:value?/Default: Yes/:/Default: No/));
 }
});

test("ActionParams1 refreshes its extra option when negotiation changes but ordinary Action2 stays ready",async()=>{
 const e=actionParametersEditor();e._status.action_parameters_version=0;
 const before=clone(e._draft);let paints=0,markup="";
 e.refreshEntityMetadata=()=>{};
 e.paintControlAvailability=()=>{paints++;markup=e.inspectorMarkup();};
 e.ws=async type=>{
  assert.equal(type,"layout/get");
  return {entries:[{...e.entry,layout:clone(e._saved),status:{...e._status,action_parameters_version:1}}]};
 };
 assert.equal(e.actionPanelAvailability().ready,true);
 assert.equal(e.actionParametersAvailability().ready,false);
 await e.refreshStatus();
 assert.equal(paints,1);assert.match(markup,/value="control-actionparameterspanel"/);
 assert.equal(e.actionPanelAvailability().ready,true);assert.deepEqual(clone(e._draft),before);
});

test("ActionParams1 actual backend metadata corpus passes strict independent UI parsing without becoming Action2",()=>{
 const rows=JSON.parse(fs.readFileSync(path.join(__dirname,"fixtures/action_parameters/metadata.json"),"utf8"));
 assert.equal(rows.length,8);
 for(const row of rows) {
  const e=actionParametersEditor(),c=e.cardAt(2),entity=e.entityFor(c.entity_id),m=clone(row.metadata);
  entity.action_parameters=m;
  e._hass.states[c.entity_id].state=m.state.source==="known"?(m.state.phase==="running"?"on":"off"):m.state.source;
  if(!(m.caps.operations&8))delete e._hass.services.script.turn_off;
  assert.deepEqual(clone(e.actionParametersMetadata(c)),m,row.name);
  assert.equal(e.actionParametersAvailability(c).ready,m.caps.parameter_status==="ready",row.name);
  entity.action_panel=clone(m);assert.equal(e.actionPanelMetadata(c),null,row.name);
  const extra=clone(m);extra.caps.parameter_value=false;entity.action_parameters=extra;
  assert.equal(e.actionParametersMetadata(c),null,row.name);
 }
});
