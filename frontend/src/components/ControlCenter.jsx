const currencyField = "w-full rounded-2xl border border-amber-200/70 bg-white/90 px-4 py-3 text-slate-900 outline-none transition focus:border-orange-400 focus:ring-2 focus:ring-orange-200";

export default function ControlCenter({
  profileForm,
  transactionForm,
  paymentForm,
  paymentState,
  onProfileChange,
  onTransactionChange,
  onPaymentChange,
  onProfileSave,
  onTransactionSubmit,
  onCreatePayment,
  onEvaluate,
  onLogout,
}) {
  return (
    <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <section className="market-glow rounded-[32px] border border-white/80 bg-white/95 p-6 backdrop-blur">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Merchant Settings</p>
            <h3 className="mt-2 font-display text-2xl text-ink">Update live automation inputs</h3>
          </div>
          <button type="button" onClick={onLogout} className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700">
            Switch merchant
          </button>
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <input className={currencyField} value={profileForm.owner_name} onChange={(e) => onProfileChange("owner_name", e.target.value)} placeholder="Owner name" />
          <input className={currencyField} value={profileForm.business_name} onChange={(e) => onProfileChange("business_name", e.target.value)} placeholder="Business name" />
          <input className={currencyField} value={profileForm.phone_number} onChange={(e) => onProfileChange("phone_number", e.target.value)} placeholder="Phone number" />
          <select className={currencyField} value={profileForm.preferred_language} onChange={(e) => onProfileChange("preferred_language", e.target.value)}>
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="kn">Kannada</option>
          </select>
          <input className={currencyField} type="number" value={profileForm.current_balance} onChange={(e) => onProfileChange("current_balance", e.target.value)} placeholder="Current balance" />
          <input className={currencyField} type="number" value={profileForm.supplier_due} onChange={(e) => onProfileChange("supplier_due", e.target.value)} placeholder="Supplier due" />
          <input className={currencyField} type="number" value={profileForm.savings_balance} onChange={(e) => onProfileChange("savings_balance", e.target.value)} placeholder="Savings balance" />
          <input className={currencyField} type="number" value={profileForm.working_capital_available} onChange={(e) => onProfileChange("working_capital_available", e.target.value)} placeholder="Working capital" />
        </div>
        <label className="mt-5 flex items-center gap-3 rounded-2xl bg-amber-50 px-4 py-3 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={profileForm.auto_automation_enabled}
            onChange={(e) => onProfileChange("auto_automation_enabled", e.target.checked)}
          />
          Enable autonomous supplier payouts and loan actions when new transactions arrive
        </label>
        <div className="mt-5 flex flex-wrap gap-3">
          <button type="button" onClick={onProfileSave} className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white">
            Save merchant settings
          </button>
          <button type="button" onClick={onEvaluate} className="rounded-full border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700">
            Re-run AI now
          </button>
        </div>
      </section>

      <div className="space-y-6">
        <section className="market-glow rounded-[32px] border border-white/80 bg-white/95 p-6 backdrop-blur">
        <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Live Sales Input</p>
        <h3 className="mt-2 font-display text-2xl text-ink">Push a realtime transaction</h3>
        <div className="mt-6 space-y-4">
          <input className={currencyField} type="number" value={transactionForm.amount} onChange={(e) => onTransactionChange("amount", e.target.value)} placeholder="Sale amount" />
          <select className={currencyField} value={transactionForm.channel} onChange={(e) => onTransactionChange("channel", e.target.value)}>
            <option value="pos">POS</option>
            <option value="upi">UPI</option>
            <option value="card">Card</option>
            <option value="pinelabs">Pine Labs</option>
          </select>
          <select className={currencyField} value={transactionForm.language} onChange={(e) => onTransactionChange("language", e.target.value)}>
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="kn">Kannada</option>
          </select>
          <input className={currencyField} value={transactionForm.customer_ref} onChange={(e) => onTransactionChange("customer_ref", e.target.value)} placeholder="Reference / invoice id" />
          <button type="button" onClick={onTransactionSubmit} className="w-full rounded-full bg-sunrise px-5 py-3 text-sm font-semibold text-white">
            Send live transaction
          </button>
        </div>
        </section>

        <section className="market-glow rounded-[32px] border border-white/80 bg-white/95 p-6 backdrop-blur">
          <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Pine Labs Checkout</p>
          <h3 className="mt-2 font-display text-2xl text-ink">Create a real Pine Labs payment</h3>
          <div className="mt-6 space-y-4">
            <input
              className={currencyField}
              type="number"
              value={paymentForm.amount}
              onChange={(e) => onPaymentChange("amount", e.target.value)}
              placeholder="Payment amount"
            />
            <input
              className={currencyField}
              value={paymentForm.description}
              onChange={(e) => onPaymentChange("description", e.target.value)}
              placeholder="Payment description"
            />
            <button type="button" onClick={onCreatePayment} className="w-full rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white">
              Create Pine Labs payment
            </button>
            {paymentState?.checkout_url ? (
              <a
                href={paymentState.checkout_url}
                target="_blank"
                rel="noreferrer"
                className="block rounded-2xl bg-emerald-50 px-4 py-3 text-sm font-semibold text-emerald-700"
              >
                Open checkout: {paymentState.checkout_url}
              </a>
            ) : null}
            {paymentState?.payment_id ? (
              <div className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
                Payment ID: {paymentState.payment_id} | Status: {paymentState.status}
              </div>
            ) : null}
          </div>
        </section>
      </div>
    </div>
  );
}
