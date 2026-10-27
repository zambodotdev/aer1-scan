#!/usr/bin/env node
"use strict";
// aer1-scan: check every zambo receipt in a file, a web page, or stdin. Sends only the receipt ids.
var fs = require("fs");
var UUID = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}";
var LINK_RE = new RegExp("zambo\\.dev\\/[^\\s\"'<>\\])]*?(" + UUID + ")", "gi");
var BARE_RE = new RegExp("^\\s*(" + UUID + ")\\s*$", "gm");
var MAX = 50;

function rawUrl(u) {
  try {
    var url = new URL(u);
    if (url.hostname === "gist.github.com") return u.replace(/\/?$/, "") + "/raw";
    if (url.hostname === "github.com" && url.pathname.indexOf("/blob/") !== -1) {
      return u.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/");
    }
  } catch (e) { /* not a URL, use as-is */ }
  return u;
}

function extract(text) {
  var seen = {}, ids = [], m;
  function add(id) { id = id.toLowerCase(); if (!seen[id]) { seen[id] = 1; ids.push(id); } }
  if (text.indexOf("receipt_schema_version") !== -1) { // a receipt JSON export: its own top-level id counts
    var jm = text.match(new RegExp("\"id\"\\s*:\\s*\"(" + UUID + ")\"", "i"));
    if (jm) add(jm[1]);
  }
  var r1 = new RegExp(LINK_RE.source, "gi"), r2 = new RegExp(BARE_RE.source, "gm");
  while ((m = r1.exec(text)) !== null) {
    if (/^zambo\.dev\/workflow\//i.test(m[0])) continue; // workflow ids are not receipt ids
    add(m[1]);
  }
  while ((m = r2.exec(text)) !== null) add(m[1]);
  return ids.slice(0, MAX);
}

function readStdin() {
  return new Promise(function (resolve) {
    var data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", function (c) { data += c; }).on("end", function () { resolve(data); });
  });
}

async function readInput(arg) {
  if (!arg || arg === "-") return readStdin();
  if (/^https?:\/\//i.test(arg)) {
    var res = await fetch(rawUrl(arg));
    if (!res.ok) throw new Error("could not fetch " + arg + " (http " + res.status + ")");
    return res.text();
  }
  return fs.readFileSync(arg, "utf8");
}

async function verify(id) {
  try {
    var res = await fetch("https://zambo.dev/api/v2/receipt/" + id + "/verify");
    if (res.status === 404) return "not found";
    if (!res.ok) return "could not verify";
    var data = await res.json();
    return data.verification_status === "verified" ? "verified" : String(data.verification_status || "could not verify");
  } catch (e) { return "could not verify"; }
}

async function main() {
  var text;
  try { text = await readInput(process.argv[2]); }
  catch (e) { console.error("aer1-scan: " + e.message); process.exit(1); }
  var ids = extract(text);
  if (!ids.length) { console.error("no zambo receipt links found. receipts look like zambo.dev/run/ followed by an id."); process.exit(1); }
  var failed = false;
  for (var i = 0; i < ids.length; i++) {
    var state = await verify(ids[i]);
    if (state !== "verified") failed = true;
    console.log(state + " " + ids[i] + " https://zambo.dev/verify/?id=" + ids[i]);
  }
  process.exit(failed ? 1 : 0);
}

main();
