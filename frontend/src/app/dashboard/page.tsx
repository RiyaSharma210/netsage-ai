"use client";

import { useState, useEffect } from "react";
import { fetchAnalytics } from "@/lib/api";
import {
  LayoutDashboard,
  CheckCircle2,
  AlertTriangle,
  TrendingUp,
  Activity,
  ShieldCheck,
  Zap,
  Clock
} from "lucide-react";

export default function DashboardPage() {
  const [stats, setStats] = useState({
    total_cases: 30,
    resolved_cases: 24,
    avg_confidence: 0.94,
    category_breakdown: { VLAN: 6, STP: 4, Routing: 4, OSPF: 4, BGP: 3, DHCP: 3, ACL: 4, VPN: 2 },
  });

  useEffect(() => {
    fetchAnalytics()
      .then((data) => {
        if (data && data.total_cases) setStats(data);
      })
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <LayoutDashboard className="w-6 h-6 text-cyan-400" /> Operational Dashboard & Metrics
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Real-time telemetry and diagnostic resolution breakdown for Cisco enterprise infrastructure.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-2">
          <span className="text-xs text-slate-400 font-medium">Total Lab Cases</span>
          <div className="flex items-center justify-between">
            <span className="text-3xl font-extrabold text-white font-mono">{stats.total_cases}</span>
            <Activity className="w-6 h-6 text-cyan-400" />
          </div>
          <span className="text-[10px] text-emerald-400 flex items-center gap-1">
            <TrendingUp className="w-3 h-3" /> Active telemetry feed
          </span>
        </div>

        <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-2">
          <span className="text-xs text-slate-400 font-medium font-mono">Automated Fix Rate</span>
          <div className="flex items-center justify-between">
            <span className="text-3xl font-extrabold text-emerald-400 font-mono">
              {((stats.resolved_cases / stats.total_cases) * 100).toFixed(0)}%
            </span>
            <CheckCircle2 className="w-6 h-6 text-emerald-400" />
          </div>
          <span className="text-[10px] text-slate-400">{stats.resolved_cases} / {stats.total_cases} cases verified</span>
        </div>

        <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-2">
          <span className="text-xs text-slate-400 font-medium">Avg AI Confidence</span>
          <div className="flex items-center justify-between">
            <span className="text-3xl font-extrabold text-cyan-400 font-mono">
              {(stats.avg_confidence * 100).toFixed(0)}%
            </span>
            <Zap className="w-6 h-6 text-amber-400" />
          </div>
          <span className="text-[10px] text-slate-400">Hybrid Rule + LLM Inference</span>
        </div>

        <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-2">
          <span className="text-xs text-slate-400 font-medium">Human Guardrail</span>
          <div className="flex items-center justify-between">
            <span className="text-3xl font-extrabold text-purple-400 font-mono">100%</span>
            <ShieldCheck className="w-6 h-6 text-purple-400" />
          </div>
          <span className="text-[10px] text-purple-300">Human-in-the-Loop Active</span>
        </div>
      </div>

      {/* Analytics Charts & Activity Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Domain Distribution */}
        <div className="lg:col-span-7 bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider border-b border-slate-800 pb-3">
            Case Breakdown by Network Domain
          </h2>
          <div className="space-y-3">
            {Object.entries(stats.category_breakdown).map(([cat, count]) => (
              <div key={cat} className="space-y-1">
                <div className="flex justify-between text-xs text-slate-300 font-mono">
                  <span>{cat} Domain</span>
                  <span>{count} cases ({((count / stats.total_cases) * 100).toFixed(0)}%)</span>
                </div>
                <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-cyan-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${(count / stats.total_cases) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Audit Log */}
        <div className="lg:col-span-5 bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider border-b border-slate-800 pb-3 flex items-center gap-2">
            <Clock className="w-4 h-4 text-cyan-400" /> Recent Diagnostic Events
          </h2>
          <div className="space-y-3 text-xs">
            {[
              { id: "CASE-001", cat: "VLAN", device: "SW-1", status: "Verified", time: "2 mins ago" },
              { id: "CASE-004", cat: "OSPF", device: "RTR-2", status: "Pending Review", time: "14 mins ago" },
              { id: "CASE-008", cat: "ACL", device: "FW-1", status: "Verified", time: "1 hour ago" },
              { id: "CASE-012", cat: "BGP", device: "RTR-1", status: "Verified", time: "3 hours ago" },
            ].map((item) => (
              <div key={item.id} className="p-3 bg-slate-900 border border-slate-800 rounded-lg flex items-center justify-between">
                <div>
                  <span className="font-mono text-cyan-400 font-bold block">{item.id} ({item.cat})</span>
                  <span className="text-slate-400 text-[11px]">Device: {item.device}</span>
                </div>
                <div className="text-right">
                  <span className={`text-[10px] px-2 py-0.5 rounded border ${
                    item.status === "Verified"
                      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                      : "bg-amber-500/10 text-amber-400 border-amber-500/20"
                  }`}>
                    {item.status}
                  </span>
                  <span className="text-slate-500 block text-[10px] mt-1">{item.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}