import { Activity, BanknoteArrowDown, IndianRupee, WalletCards } from "lucide-react";

import SalesChart from "./SalesChart";
import CashflowInsights from "./CashflowInsights";

const currency = (value = 0) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);

function StatCard({ label, value, icon: Icon, tone }) {
  return (
    <div className={`market-glow rounded-[30px] border border-white/80 p-5 ${tone}`}>
      <div className="flex items-center justify-between">
        <p className="text-sm uppercase tracking-[0.2em] text-slate-700">{label}</p>
        <div className="rounded-full bg-white/70 p-2">
          <Icon className="h-5 w-5 text-slate-700" />
        </div>
      </div>
      <p className="mt-6 font-display text-3xl text-slate-900">{value}</p>
    </div>
  );
}

export default function Dashboard({ overview, latestUpdate, onEvaluate }) {
  const summary = overview?.summary || {};
  const forecast = overview?.forecast || {};
  const riskWindow = forecast?.risk_window_days;
  const profile = overview?.profile || {};
  const liveMetrics = overview?.live_metrics || {};
  const updatedAt = liveMetrics?.updated_at ? new Date(liveMetrics.updated_at).toLocaleTimeString() : "waiting";

  return (
    <div className="space-y-6">
      <div className="market-glow relative overflow-hidden rounded-[38px] border border-white/80">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-8"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1488459716781-31db52582fe9?auto=format&fit=crop&w=1400&q=80')",
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-r from-[#fffdf8] via-[#fffaf4] to-[#f6ecdd]" />
        <div className="relative flex flex-col gap-6 p-6 md:flex-row md:items-end md:justify-between md:p-8">
          <div>
            <p className="text-sm uppercase tracking-[0.3em] text-slate-600">Realtime Merchant Copilot</p>
            <h1 className="mt-3 font-display text-5xl text-slate-900">{profile.business_name || "FinFlow Agent"}</h1>
            <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-700">
              {profile.owner_name || "Merchant"} is signed in. Monitor POS sales, predict cash crunches, automate supplier payouts, and trigger working capital with a dashboard that feels live, local, and human.
            </p>
            <div className="mt-5 flex flex-wrap gap-3">
              <span className="rounded-full bg-emerald-100 px-4 py-2 text-sm font-semibold text-emerald-800">Live metrics updated at {updatedAt}</span>
              <span className="rounded-full bg-orange-100 px-4 py-2 text-sm font-semibold text-orange-800">Built for neighbourhood merchants</span>
            </div>
          </div>
          <div className="w-full max-w-sm rounded-[30px] border border-slate-800/20 bg-slate-900 p-5 text-white shadow-card">
            <p className="text-sm uppercase tracking-[0.24em] text-amber-200">Today at a glance</p>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              Revenue, risk, and payment intelligence update in one place as transactions land from POS or Pine Labs checkout.
            </p>
            <button
              type="button"
              onClick={onEvaluate}
              className="mt-5 w-full rounded-full bg-sunrise px-6 py-3 text-sm font-semibold text-white transition hover:translate-y-[-1px] hover:bg-orange-500"
            >
              Run AI evaluation
            </button>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Today's revenue" value={currency(summary.daily_sales)} icon={IndianRupee} tone="bg-gradient-to-br from-[#fff7ed] to-[#fde6bf]" />
        <StatCard label="Transactions" value={summary.transaction_count || 0} icon={Activity} tone="bg-gradient-to-br from-[#ecfdf5] to-[#d6f5ea]" />
        <StatCard label="Savings pool" value={currency(overview?.snapshot?.savings_balance)} icon={WalletCards} tone="bg-gradient-to-br from-[#ffffff] to-[#e8f1fb]" />
        <StatCard label="Risk window" value={riskWindow ? `${riskWindow} days` : "Safe"} icon={BanknoteArrowDown} tone="bg-gradient-to-br from-[#fffbea] to-[#fde68a]" />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.45fr_0.95fr]">
        <SalesChart points={forecast.forecast_points} />
        <CashflowInsights overview={overview} latestUpdate={latestUpdate} />
      </div>
    </div>
  );
}
