"use client";

import { useState } from "react";
import { ShieldAlert, CheckCircle2, AlertTriangle, Terminal, Code2 } from "lucide-react";

export default function RuleCheckerPage() {
  const [cliInput, setCliInput] = useState(
    "interface GigabitEthernet0/1\n switchport mode trunk\n switchport trunk native vlan 10\n ip address 192.168.1.1 255.255.255.0"
  );
  const [results, setResults] = useState<{ type: "pass" | "warn" | "fail"; msg: string }[] | null>(null);

  const handleValidate = () => {
    const checks: { type: "pass" | "warn" | "fail"; msg: string }[] = [];
    
    if (cliInput.includes("switchport mode trunk") && cliInput.includes("ip address")) {
      checks.push({ type: "fail", msg: "Layer 2 trunk interface cannot have an IP address directly configured." });
    } else {
      checks.push({ type: "pass", msg: "Switchport mode configuration is valid." });
    }

    if (!cliInput.includes("no shutdown")) {
      checks.push({ type: "warn", msg: "Interface may remain shut down. Missing 'no shutdown' command." });
    }

    if (cliInput.includes("native vlan")) {
      checks.push({ type: "pass", msg: "Native VLAN specified explicitly." });
    }

    setResults(checks);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <ShieldAlert className="w-6 h-6 text-amber-400" /> CLI Syntax Rule Checker
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Validate proposed Cisco IOS CLI snippet commands against network safety guidelines.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-4">
          <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Terminal className="w-4 h-4 text-amber-400" /> Enter Cisco CLI Script
          </label>
          <textarea
            value={cliInput}
            onChange={(e) => setCliInput(e.target.value)}
            rows={10}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-amber-500/50"
          />
          <button
            onClick={handleValidate}
            className="w-full bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold py-2.5 rounded-lg text-xs transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            <Code2 className="w-4 h-4" /> Validate CLI Syntax
          </button>
        </div>

        <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-bold text-white border-b border-slate-800 pb-3">Validation Report</h2>
          {!results ? (
            <div className="text-xs text-slate-500 italic py-12 text-center">
              Click "Validate CLI Syntax" to run policy rules against your script.
            </div>
          ) : (
            <div className="space-y-3">
              {results.map((r, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-lg border text-xs flex items-start gap-3 ${
                    r.type === "pass"
                      ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                      : r.type === "warn"
                      ? "bg-amber-500/10 border-amber-500/20 text-amber-400"
                      : "bg-red-500/10 border-red-500/20 text-red-400"
                  }`}
                >
                  {r.type === "pass" ? (
                    <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                  )}
                  <span>{r.msg}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}