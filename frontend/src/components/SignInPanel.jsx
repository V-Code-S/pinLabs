import { useState } from "react";

const LANGUAGES = [
  { value: "en", label: "English" },
  { value: "hi", label: "Hindi" },
  { value: "kn", label: "Kannada" },
];

export default function SignInPanel({ onSignIn }) {
  const [form, setForm] = useState({
    owner_name: "",
    business_name: "",
    phone_number: "",
    preferred_language: "en",
  });

  const update = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const submit = async (event) => {
    event.preventDefault();
    await onSignIn(form);
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl items-center px-4 py-10 md:px-8">
      <div className="grid w-full gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        <section className="relative overflow-hidden rounded-[36px] bg-ink p-8 text-white shadow-card md:p-10">
          <div
            className="absolute inset-0 opacity-12"
            style={{
              backgroundImage:
                "url('https://images.unsplash.com/photo-1604719312566-8912e9227c6a?auto=format&fit=crop&w=1400&q=80')",
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-br from-[#0f172a] via-[#1d3557]/90 to-[#264653]/90" />
          <div className="relative">
          <p className="text-sm uppercase tracking-[0.3em] text-orange-200">Realtime Merchant AI</p>
          <h1 className="mt-4 font-display text-5xl leading-tight">Sign in to your live cash-flow operating system.</h1>
          <p className="mt-5 max-w-xl text-lg leading-8 text-slate-300">
            Connect as a merchant, set your balance and supplier dues, then stream sales and let FinFlow automate split payments, alerts, and loan decisions.
          </p>
          <div className="mt-10 grid gap-4 md:grid-cols-2">
            <div className="rounded-[28px] bg-white/10 p-5">
              <p className="text-sm uppercase tracking-[0.2em] text-orange-200">What happens live</p>
              <p className="mt-3 text-sm leading-6 text-slate-200">
                POS sale arrives, forecast updates, AI re-evaluates, supplier payout or loan action gets logged, and the merchant message refreshes instantly.
              </p>
            </div>
            <div className="rounded-[28px] bg-white/10 p-5">
              <p className="text-sm uppercase tracking-[0.2em] text-orange-200">Hackathon mode</p>
              <p className="mt-3 text-sm leading-6 text-slate-200">
                Pine Labs remains safely mockable, but your sign-in, merchant setup, and transaction automation flow are fully interactive.
              </p>
            </div>
          </div>
          </div>
        </section>

        <section className="market-glow rounded-[36px] border border-white/80 bg-white/97 p-8 backdrop-blur">
          <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Merchant Sign In</p>
          <h2 className="mt-2 font-display text-3xl text-ink">Start your workspace</h2>
          <form className="mt-8 space-y-4" onSubmit={submit}>
            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-700">Owner name</span>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none transition focus:border-orange-400"
                value={form.owner_name}
                onChange={(event) => update("owner_name", event.target.value)}
                placeholder="Virupakshi"
                required
              />
            </label>
            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-700">Business name</span>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none transition focus:border-orange-400"
                value={form.business_name}
                onChange={(event) => update("business_name", event.target.value)}
                placeholder="Annapurna Kirana Store"
                required
              />
            </label>
            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-700">Phone number</span>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none transition focus:border-orange-400"
                value={form.phone_number}
                onChange={(event) => update("phone_number", event.target.value)}
                placeholder="+91 9876543210"
                required
              />
            </label>
            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-700">Preferred language</span>
              <select
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none transition focus:border-orange-400"
                value={form.preferred_language}
                onChange={(event) => update("preferred_language", event.target.value)}
              >
                {LANGUAGES.map((language) => (
                  <option key={language.value} value={language.value}>
                    {language.label}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="submit"
              className="w-full rounded-full bg-sunrise px-6 py-3 text-sm font-semibold text-white transition hover:translate-y-[-1px] hover:bg-orange-500"
            >
              Enter dashboard
            </button>
          </form>
        </section>
      </div>
    </main>
  );
}
