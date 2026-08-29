"use client";

import { useState } from "react";
import { FolderGit2, Search, Filter, ArrowRight, ShieldAlert } from "lucide-react";
import Link from "next/link";

const ALL_30_CASES = Array.from({ length: 30 }, (_, index) => {
  const i = index + 1;
  const categories = ["VLAN", "STP", "Routing", "OSPF", "BGP", "DHCP", "DNS", "ACL", "NAT", "VPN"];
  const cat = categories[(i - 1) % categories.length];
  return {
    id: `CASE-${String(i).padStart(3, "0")}`,
    title: `${cat} Misconfiguration Lab #${i}`,
    category: cat,
    device: i % 2 === 0 ? "SW-1" : "RTR-1",
    severity: i % 3 === 0 ? "Critical" : i % 2 === 0 ? "High" : "Medium",
    symptom: `Host unreachable across boundary in ${cat} domain. Interface dropped packets unexpectedly.`,
  };
});

export default function CasesPage() {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("ALL");

  const filteredCases = ALL_30_CASES.filter((c) => {
    const matchesSearch = c.title.toLowerCase().includes(search.toLowerCase()) || c.id.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategory === "ALL" || c.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4">
      <div className="border-b border-slate-800 pb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <FolderGit2 className="w-6 h-6 text-cyan-400" /> Lab Cases Repository (30 Available)
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Browse and inspect pre-configured Cisco enterprise diagnostic scenarios across OSI Layers 2–4.
          </p>
        </div>

        {/* Search & Filter Controls */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
            <input
              type="text"
              placeholder="Search case ID or title..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-[#111827] border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-white focus:outline-none focus:border-cyan-500 w-48 font-mono"
            />
          </div>

          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-[#111827] border border-slate-800 rounded-lg p-2 text-xs text-cyan-400 font-mono focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Categories</option>
            <option value="VLAN">VLAN</option>
            <option value="STP">STP</option>
            <option value="Routing">Routing</option>
            <option value="OSPF">OSPF</option>
            <option value="BGP">BGP</option>
            <option value="ACL">ACL</option>
          </select>
        </div>
      </div>

      {/* Grid of Lab Cases */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredCases.map((c) => (
          <div key={c.id} className="bg-[#111827] border border-slate-800 rounded-xl p-5 flex flex-col justify-between space-y-4 hover:border-slate-700 transition-all">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2.5 py-0.5 rounded-full font-bold">
                  {c.id}
                </span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border font-mono ${
                  c.severity === "Critical"
                    ? "bg-red-500/10 text-red-400 border-red-500/20"
                    : c.severity === "High"
                    ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                    : "bg-blue-500/10 text-blue-400 border-blue-500/20"
                }`}>
                  {c.severity}
                </span>
              </div>
              <h3 className="text-sm font-bold text-white">{c.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">{c.symptom}</p>
            </div>

            <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
              <span className="text-[11px] font-mono text-slate-400">Target: {c.device}</span>
              <Link
                href={`/diagnose?caseId=${c.id}`}
                className="text-xs text-cyan-400 font-bold hover:text-cyan-300 flex items-center gap-1 transition-colors"
              >
                Load in Studio <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}