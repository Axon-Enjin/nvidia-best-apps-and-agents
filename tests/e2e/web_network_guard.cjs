"use strict";
// Loaded with `node --require` into the Next.js test server. Any connection or
// lookup beyond loopback is recorded and refused, independent of app settings.
// This is a process-level audit for acceptance tests, not an OS firewall.
const dns = require("node:dns");
const fs = require("node:fs");
const net = require("node:net");

const logPath = process.env.SENTINEL_NETWORK_LOG;
const state = { probing: true };

function isLoopback(host) {
  if (host === undefined || host === null || host === "") return true; // Node defaults to localhost.
  const value = String(host).replace(/^\[|\]$/g, "").toLowerCase();
  if (value === "localhost" || value === "::1" || value === "::ffff:127.0.0.1") return true;
  return /^127(\.\d{1,3}){3}$/.test(value);
}

function refuse(kind, host) {
  if (!state.probing && logPath) fs.appendFileSync(logPath, `${kind} ${host}\n`);
  const error = new Error(`Test web server permits loopback only (${kind} ${host}).`);
  error.code = "ECONNREFUSED";
  return error;
}

function targetHost(args) {
  const first = args[0];
  if (Array.isArray(first)) return targetHost(first);
  if (first && typeof first === "object") return first.path ? "localhost" : first.host ?? first.hostname;
  if (typeof first === "string" && Number.isNaN(Number(first))) return "localhost"; // IPC path
  return typeof args[1] === "string" ? args[1] : undefined;
}

const connect = net.Socket.prototype.connect;
net.Socket.prototype.connect = function guardedConnect(...args) {
  const host = targetHost(args);
  if (!isLoopback(host)) {
    const error = refuse("connect", host);
    process.nextTick(() => this.destroy(error));
    return this;
  }
  return connect.apply(this, args);
};

const lookup = dns.lookup;
dns.lookup = function guardedLookup(hostname, ...rest) {
  if (!isLoopback(hostname)) {
    const callback = rest.find((value) => typeof value === "function");
    const error = refuse("lookup", hostname);
    if (callback) process.nextTick(() => callback(error));
    return {};
  }
  return lookup.call(this, hostname, ...rest);
};
const promiseLookup = dns.promises.lookup;
dns.promises.lookup = function guardedPromiseLookup(hostname, ...rest) {
  if (!isLoopback(hostname)) return Promise.reject(refuse("lookup", hostname));
  return promiseLookup.call(this, hostname, ...rest);
};

// Startup probe: a guard that does not block is a failed guard.
const probe = net.connect({ host: "198.51.100.1", port: 443 });
probe.on("error", () => {
  state.probing = false;
  if (logPath && !fs.existsSync(logPath)) fs.writeFileSync(logPath, "");
});
probe.on("connect", () => {
  process.stderr.write("Network acceptance guard failed its startup probe.\n");
  process.exit(70);
});
