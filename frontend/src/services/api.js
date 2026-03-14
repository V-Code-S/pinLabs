import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";
const WS_BASE = (import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000/api").replace(/^http/, "ws");

export const api = axios.create({
  baseURL: API_BASE,
});

export const fetchOverview = async (merchantId = "merchant-demo") => {
  const { data } = await api.get(`/cashflow/${merchantId}`);
  return data;
};

export const signInMerchant = async (payload) => {
  const { data } = await api.post("/merchant/sign-in", payload);
  return data;
};

export const fetchMerchantProfile = async (merchantId) => {
  const { data } = await api.get(`/merchant/${merchantId}/profile`);
  return data;
};

export const updateMerchantProfile = async (merchantId, payload) => {
  const { data } = await api.put(`/merchant/${merchantId}/profile`, payload);
  return data;
};

export const triggerEvaluation = async (merchantId = "merchant-demo", language = "en") => {
  const { data } = await api.post("/agent/evaluate", { merchant_id: merchantId, language });
  return data;
};

export const postTransaction = async (payload) => {
  const { data } = await api.post("/transactions", payload);
  return data;
};

export const createPineLabsPayment = async (payload) => {
  const { data } = await api.post("/pinelabs/payments/create", payload);
  return data;
};

export const createUpdatesSocket = () => new WebSocket(`${WS_BASE}/agent/stream`);
