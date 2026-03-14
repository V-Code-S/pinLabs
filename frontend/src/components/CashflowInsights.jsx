const currency = (value = 0) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);

export default function CashflowInsights({ overview, latestUpdate }) {
  const decision = latestUpdate?.decision || overview?.recent_decisions?.[0];
  const message = latestUpdate?.message;
  const allocationPreview = overview?.live_metrics?.allocation_preview;

  return (
    <div className="relative overflow-hidden rounded-[32px] bg-[#14213d] p-6 text-white shadow-card">
      <div
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage:
            "url('https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80')",
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-[#14213d]/94 via-[#172554]/96 to-[#111827]" />
      <div className="relative">
      <p className="text-sm uppercase tracking-[0.24em] text-orange-200">Agent Brain</p>
      <h3 className="mt-2 font-display text-2xl">Autonomous recommendation</h3>
      <div className="mt-6 space-y-4">
        <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
          <p className="text-sm text-orange-100">Decision</p>
          <p className="mt-1 text-xl font-semibold">
            {decision?.decision?.replaceAll("_", " ") || "Waiting for live data"}
          </p>
          <p className="mt-2 text-sm text-slate-200">{decision?.rationale || "Run an evaluation to generate a recommendation."}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
          <p className="text-sm text-orange-100">Merchant summary</p>
          <p className="mt-2 text-sm leading-6 text-slate-200">{message || "Regional-language notification will appear here after a live event."}</p>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p className="text-sm text-orange-100">Current balance</p>
            <p className="mt-1 text-lg font-semibold">{currency(overview?.snapshot?.current_balance)}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p className="text-sm text-orange-100">Supplier due</p>
            <p className="mt-1 text-lg font-semibold">{currency(overview?.snapshot?.supplier_due)}</p>
          </div>
        </div>
        {allocationPreview ? (
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p className="text-sm text-orange-100">Auto breakdown for Rs. 500 payment</p>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <p className="text-sm text-slate-200">EMI {currency(allocationPreview.emi)}</p>
              <p className="text-sm text-slate-200">Savings {currency(allocationPreview.savings)}</p>
              <p className="text-sm text-slate-200">Grocery {currency(allocationPreview.grocery)}</p>
              <p className="text-sm text-slate-200">Cash reserve {currency(allocationPreview.cash_reserve)}</p>
            </div>
          </div>
        ) : null}
      </div>
      </div>
    </div>
  );
}
