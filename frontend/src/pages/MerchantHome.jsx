import { useEffect, useState } from "react";

import ActivityFeed from "../components/ActivityFeed";
import ControlCenter from "../components/ControlCenter";
import Dashboard from "../components/Dashboard";
import SignInPanel from "../components/SignInPanel";
import {
  createUpdatesSocket,
  createPineLabsPayment,
  fetchMerchantProfile,
  fetchOverview,
  postTransaction,
  signInMerchant,
  triggerEvaluation,
  updateMerchantProfile,
} from "../services/api";

const EMPTY_TRANSACTION = {
  amount: "15000",
  category: "sale",
  channel: "pos",
  language: "en",
  customer_ref: "",
};

const EMPTY_PAYMENT = {
  amount: "100",
  description: "FinFlow Merchant Payment",
};

const STORAGE_KEY = "finflow-session";

export default function MerchantHome() {
  const [merchantId, setMerchantId] = useState(() => window.localStorage.getItem(STORAGE_KEY) || "");
  const [overview, setOverview] = useState(null);
  const [latestUpdate, setLatestUpdate] = useState(null);
  const [status, setStatus] = useState("Sign in to connect your merchant workspace.");
  const [profileForm, setProfileForm] = useState({
    owner_name: "",
    business_name: "",
    phone_number: "",
    preferred_language: "en",
    auto_automation_enabled: true,
    current_balance: 50000,
    supplier_due: 60000,
    savings_balance: 10000,
    working_capital_available: 15000,
  });
  const [transactionForm, setTransactionForm] = useState(EMPTY_TRANSACTION);
  const [paymentForm, setPaymentForm] = useState(EMPTY_PAYMENT);
  const [paymentState, setPaymentState] = useState(null);

  const loadOverview = async (currentMerchantId = merchantId) => {
    if (!currentMerchantId) {
      return;
    }
    const data = await fetchOverview(currentMerchantId);
    setOverview(data);
    setProfileForm((current) => ({
      ...current,
      owner_name: data.profile?.owner_name || current.owner_name,
      business_name: data.profile?.business_name || current.business_name,
      phone_number: data.profile?.phone_number || current.phone_number,
      preferred_language: data.profile?.preferred_language || current.preferred_language,
      auto_automation_enabled: data.profile?.auto_automation_enabled ?? current.auto_automation_enabled,
      current_balance: data.snapshot?.current_balance ?? current.current_balance,
      supplier_due: data.snapshot?.supplier_due ?? current.supplier_due,
      savings_balance: data.snapshot?.savings_balance ?? current.savings_balance,
      working_capital_available: data.snapshot?.working_capital_available ?? current.working_capital_available,
    }));
  };

  useEffect(() => {
    const socket = createUpdatesSocket();
    socket.onopen = () => {
      setStatus((current) =>
        current === "Sign in to connect your merchant workspace." ? current : "Live stream connected"
      );
      socket.send("subscribe");
    };
    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if ((payload.type === "agent_update" || payload.type === "transaction_update") && payload.merchant_id === merchantId) {
        setLatestUpdate(payload.payload);
        loadOverview();
      }
    };
    socket.onclose = () => setStatus("Live stream disconnected");
    return () => socket.close();
  }, [merchantId]);

  useEffect(() => {
    const bootstrap = async () => {
      if (!merchantId) {
        return;
      }
      const profile = await fetchMerchantProfile(merchantId);
      setProfileForm({
        owner_name: profile.owner_name,
        business_name: profile.business_name,
        phone_number: profile.phone_number,
        preferred_language: profile.preferred_language,
        auto_automation_enabled: profile.auto_automation_enabled,
        current_balance: profile.current_balance,
        supplier_due: profile.supplier_due,
        savings_balance: profile.savings_balance,
        working_capital_available: profile.working_capital_available,
      });
      await loadOverview(merchantId);
      setStatus("Merchant workspace ready");
    };
    bootstrap();
  }, [merchantId]);

  useEffect(() => {
    if (!merchantId) {
      return undefined;
    }
    const interval = window.setInterval(() => {
      loadOverview(merchantId);
    }, 5000);
    return () => window.clearInterval(interval);
  }, [merchantId]);

  const handleSignIn = async (form) => {
    setStatus("Signing in merchant...");
    const data = await signInMerchant(form);
    window.localStorage.setItem(STORAGE_KEY, data.merchant_id);
    setMerchantId(data.merchant_id);
    setStatus("Merchant signed in");
  };

  const updateProfileField = (field, value) => {
    setProfileForm((current) => ({ ...current, [field]: value }));
  };

  const updateTransactionField = (field, value) => {
    setTransactionForm((current) => ({ ...current, [field]: value }));
  };

  const updatePaymentField = (field, value) => {
    setPaymentForm((current) => ({ ...current, [field]: value }));
  };

  const handleSaveProfile = async () => {
    setStatus("Saving merchant settings...");
    await updateMerchantProfile(merchantId, {
      ...profileForm,
      current_balance: Number(profileForm.current_balance),
      supplier_due: Number(profileForm.supplier_due),
      savings_balance: Number(profileForm.savings_balance),
      working_capital_available: Number(profileForm.working_capital_available),
    });
    await loadOverview();
    setStatus("Merchant settings saved");
  };

  const handleEvaluate = async () => {
    setStatus("Running AI evaluation...");
    const data = await triggerEvaluation(merchantId, profileForm.preferred_language);
    setLatestUpdate(data);
    await loadOverview();
    setStatus("AI evaluation completed");
  };

  const handleTransactionSubmit = async () => {
    setStatus("Posting live transaction...");
    const response = await postTransaction({
      merchant_id: merchantId,
      amount: Number(transactionForm.amount),
      category: transactionForm.category,
      channel: transactionForm.channel,
      language: transactionForm.language,
      customer_ref: transactionForm.customer_ref || undefined,
    });
    setLatestUpdate(response.evaluation);
    await loadOverview();
    setStatus("Live transaction processed and automation updated");
    setTransactionForm(EMPTY_TRANSACTION);
  };

  const handleCreatePayment = async () => {
    setStatus("Creating Pine Labs payment...");
    const response = await createPineLabsPayment({
      merchant_id: merchantId,
      amount: Number(paymentForm.amount),
      description: paymentForm.description,
    });
    setPaymentState(response);
    setStatus("Pine Labs payment created. Open checkout to complete the test payment.");
  };

  const handleLogout = () => {
    window.localStorage.removeItem(STORAGE_KEY);
    setMerchantId("");
    setOverview(null);
    setLatestUpdate(null);
    setStatus("Sign in to connect your merchant workspace.");
  };

  if (!merchantId) {
    return <SignInPanel onSignIn={handleSignIn} />;
  }

  return (
    <main className="mx-auto max-w-7xl px-4 py-6 md:px-8 md:py-8">
      <div className="market-glow mb-6 flex flex-col gap-4 rounded-[34px] border border-white/80 bg-white/95 p-5 backdrop-blur md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.24em] text-slate-600">Realtime Workspace</p>
          <p className="mt-2 text-slate-800">{status}</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handleEvaluate}
            className="rounded-full border border-amber-300 bg-white/70 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-orange-400"
          >
            Run AI evaluation
          </button>
        </div>
      </div>
      <Dashboard overview={overview} latestUpdate={latestUpdate} onEvaluate={handleEvaluate} />
      <div className="mt-6">
        <ControlCenter
          profileForm={profileForm}
          transactionForm={transactionForm}
          paymentForm={paymentForm}
          paymentState={paymentState}
          onProfileChange={updateProfileField}
          onTransactionChange={updateTransactionField}
          onPaymentChange={updatePaymentField}
          onProfileSave={handleSaveProfile}
          onTransactionSubmit={handleTransactionSubmit}
          onCreatePayment={handleCreatePayment}
          onEvaluate={handleEvaluate}
          onLogout={handleLogout}
        />
      </div>
      <div className="mt-6">
        <ActivityFeed overview={overview} latestUpdate={latestUpdate} />
      </div>
    </main>
  );
}
