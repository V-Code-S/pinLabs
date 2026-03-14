const currency = (value = 0) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);

export default function ActivityFeed({ overview, latestUpdate }) {
  const decisions = overview?.recent_decisions || [];
  const transactions = overview?.recent_transactions || [];
  const actions = latestUpdate?.actions || [];

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
      <section className="market-glow rounded-[32px] border border-white/80 bg-white/95 p-6 backdrop-blur">
        <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Live Activity</p>
        <h3 className="mt-2 font-display text-2xl text-ink">Recent automation feed</h3>
        <div className="mt-6 space-y-3">
          {actions.length === 0 && decisions.length === 0 ? (
            <p className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">No live automation yet. Sign in, save merchant settings, and post a transaction to start the flow.</p>
          ) : null}
          {actions.map((action, index) => (
            <div key={`${action.action}-${index}`} className="rounded-2xl bg-slate-50 p-4">
              <p className="text-sm font-semibold capitalize text-slate-800">{action.action.replaceAll("_", " ")}</p>
              <p className="mt-1 text-sm text-slate-600">{action.reference || action.status}</p>
            </div>
          ))}
          {decisions.map((decision, index) => (
            <div key={`${decision.created_at}-${index}`} className="rounded-2xl border border-slate-200 p-4">
              <p className="text-sm font-semibold capitalize text-slate-800">{decision.decision.replaceAll("_", " ")}</p>
              <p className="mt-1 text-sm text-slate-600">{decision.rationale}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="market-glow rounded-[32px] border border-white/80 bg-white/95 p-6 backdrop-blur">
        <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Incoming Transactions</p>
        <h3 className="mt-2 font-display text-2xl text-ink">Recent sales stream</h3>
        <div className="mt-6 space-y-3">
          {transactions.length === 0 ? (
            <p className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">Your signed-in merchant has not received any realtime transactions yet.</p>
          ) : null}
          {transactions.map((transaction) => (
            <div key={transaction.id} className="rounded-2xl border border-slate-200 p-4">
              <div className="flex items-center justify-between">
                <div>
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">{transaction.channel}</p>
                <p className="mt-1 text-sm text-slate-700">{new Date(transaction.created_at).toLocaleString()}</p>
                </div>
                <p className="font-display text-2xl text-ink">{currency(transaction.amount)}</p>
              </div>
              {transaction.allocation ? (
                <div className="mt-4 grid gap-2 sm:grid-cols-2">
                  <div className="rounded-xl bg-orange-50 px-3 py-2 text-sm text-slate-700">EMI {currency(transaction.allocation.emi)}</div>
                  <div className="rounded-xl bg-emerald-50 px-3 py-2 text-sm text-slate-700">Savings {currency(transaction.allocation.savings)}</div>
                  <div className="rounded-xl bg-sky-50 px-3 py-2 text-sm text-slate-700">Grocery {currency(transaction.allocation.grocery)}</div>
                  <div className="rounded-xl bg-slate-100 px-3 py-2 text-sm text-slate-700">Cash reserve {currency(transaction.allocation.cash_reserve)}</div>
                </div>
              ) : null}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
