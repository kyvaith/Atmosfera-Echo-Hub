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
  assert.deepEqual(hints(markup),[editor.t("controlBrightness"),editor.t("controlHint")]);
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
  for(const mutate of [r=>{r.layout.version=2;},r=>{r.layout.cards[1].entity_id="number.provider";},r=>{r.layout.cards[1].action.token="private";}]) {
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
