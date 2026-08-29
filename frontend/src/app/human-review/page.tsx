"use client";

import { useState } from "react";
import { UserCheck, CheckCircle2, XCircle } from "lucide-react";

export default function HumanReviewPage() {
  const [queue, setQueue] = useState([
    {
      id: "REV-101",
      case_id: "CASE-002",
      device: "SW-1",
      recommendation: "configure terminal\ninterface GigabitEthernet0/1\n switchport trunk allowed vlan add 20\n end",
      status: "Pending",
    },
    {
      id: "REV-102",
      case_id: "CASE-007",
      device: "RTR-2",
      recommendation: "configure terminal\nrouter ospf 1\n network 10.1.1.0 0.0.0.255 area 0\n end",
      status: "Pending",
    }
  ]);

  const handleDecision = (id: string, decision: "Approved" | "Rejected") => {
    setQueue((prev) =>
      prev.map((item) => (item.id === id ? { ...item, status: decision } : item))
    );
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <UserCheck className="w-6 h-6 text-purple-400" /> Human Review Queue
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Review and approve AI-generated CLI fixes before applying them to live equipment.
        </p>
      </div>

      <div className="space-y-4">
        {queue.map((item) => (
          <div key={item.id} className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-3">
                <span className="text-xs font-mono bg-purple-500/10 text-purple-400 border border-purple-500/20 px-2.5 py-1 rounded-full font-bold">
                  {item.id}
                </span>
                <span className="text-sm font-bold text-white">
                  {item.case_id} — Device: <span className="text-cyan-400 font-mono">{item.device}</span>
                </span>
              </div>
              <span className={`text-xs font-bold px-3 py-1 rounded-full border font-mono ${
                item.status === "Approved"
                  ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                  : item.status === "Rejected"
                  ? "bg-red-500/10 text-red-400 border-red-500/20"
                  : "bg-amber-500/10 text-amber-400 border-amber-500/20"
              }`}>
                {item.status}
              </span>
            </div>

            <pre className="p-4 bg-slate-950 border border-slate-800 rounded-lg text-xs text-emerald-400 font-mono overflow-x-auto">
              {item.recommendation}
            </pre>

            {item.status === "Pending" && (
              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => handleDecision(item.id, "Rejected")}
                  className="px-4 py-2 bg-slate-800 hover:bg-red-500/20 hover:text-red-400 text-slate-300 font-bold text-xs rounded-lg transition-all flex items-center gap-1.5 cursor-pointer border border-slate-700"
                >
                  <XCircle className="w-4 h-4 text-red-400" /> Reject
                </button>
                <button
                  onClick={() => handleDecision(item.id, "Approved")}
                  className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs rounded-lg transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <CheckCircle2 className="w-4 h-4" /> Approve & Sign Off
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}