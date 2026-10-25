import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import vm from "node:vm";

const source=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
const html=readFileSync(new URL("../../web/index.html",import.meta.url),"utf8");

function mount(){
 const nodes=new Map();
 const node=tag=>({
  tag,children:[],textContent:"",value:"",disabled:false,listeners:{},
  append(...children){this.children.push(...children);},
  replaceChildren(...children){this.children=[...children];},
  addEventListener(event,fn){this.listeners[event]=fn;},
  setAttribute(){},scrollIntoView(){},
  classList:{add(){},remove(){},toggle(){}}
 });
 const get=id=>{if(!nodes.has(id))nodes.set(id,node("div"));return nodes.get(id);};
 const doc={getElementById:get,createElement:node,addEventListener(){}};
 const context=vm.createContext({document:doc,location:{origin:"https://index.alexlab.media",search:""},URL,URLSearchParams,localStorage:{getItem(){return null;},setItem(){}}});
 vm.runInContext(source+"\nglobalThis.__test={state,renderResults};",context);
 return {state:context.__test.state,render:context.__test.renderResults,get};
}
const rows=(n,provider="knaben")=>Array.from({length:n},(_,i)=>({
 id:provider+"-"+i,provider,name:"Item "+String(i).padStart(4,"0"),seeders:i
}));
const pager=h=>h.get("resultsPagination").children[0];

test("PWA has a dedicated accessible navigation after result list",()=>{
 assert.match(html,/id="resultsPagination"/);
 assert.match(source,/const RESULTS_PER_PAGE=50/);
 assert.doesNotMatch(source,/sorted\.slice\(0,400\)/);
});

test("123 results become 50/50/23 cards with working previous/next buttons",()=>{
 const h=mount();h.state.items=rows(123);h.get("sort").value="name";h.render();
 assert.equal(h.get("resultCount").textContent,"123 MATCHES");
 assert.equal(h.get("results").children.length,50);
 assert.equal(h.state.resultsPage,1);
 assert.equal(pager(h).children[0].disabled,true);
 assert.match(pager(h).children[1].textContent,/Page 1 of 3/);
 pager(h).children[2].listeners.click();
 assert.equal(h.state.resultsPage,2);
 assert.equal(h.get("results").children.length,50);
 assert.match(pager(h).children[1].textContent,/51–100 of 123/);
 pager(h).children[2].listeners.click();
 assert.equal(h.state.resultsPage,3);
 assert.equal(h.get("results").children.length,23);
 assert.equal(pager(h).children[2].disabled,true);
 pager(h).children[0].listeners.click();
 assert.equal(h.state.resultsPage,2);
});

test("pagination clamps safely when results change during a search",()=>{
 const h=mount();h.state.items=rows(123);h.get("sort").value="name";h.state.resultsPage=3;
 h.render();assert.equal(h.get("results").children.length,23);
 h.state.items=rows(60);h.render();
 assert.equal(h.state.resultsPage,2);
 assert.equal(h.get("results").children.length,10);
 h.state.items=rows(4);h.render();
 assert.equal(h.state.resultsPage,1);
 assert.equal(h.get("resultsPagination").children.length,0);
 assert.equal(h.get("results").children.length,4);
});

test("SubsPlease does not leak into PWA results or saved bookmarks",()=>{
 const h=mount();h.get("sort").value="name";
 h.state.items=[...rows(51),...rows(5,"subsplease")];h.render();
 assert.equal(h.get("resultCount").textContent,"51 MATCHES");
 assert.equal(h.get("results").children.length,50);
 h.state.bookmarksMode=true;
 h.state.bookmarks={a:rows(1,"subsplease")[0],b:rows(1)[0]};
 h.state.resultsPage=1;h.render();
 assert.equal(h.get("resultCount").textContent,"1 SAVED");
 assert.equal(h.get("results").children.length,1);
});
