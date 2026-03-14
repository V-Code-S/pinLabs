import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function SalesChart({ points = [] }) {
  return (
    <div className="market-glow soft-grid rounded-[32px] border border-white/80 bg-white/95 p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.24em] text-slate-600">Cash Prediction</p>
          <h3 className="font-display text-2xl text-slate-900">Projected balance</h3>
          <p className="mt-2 max-w-xl text-sm text-slate-700">A forward-looking view of working capital health based on live inflows and dues.</p>
        </div>
      </div>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={points}>
            <defs>
              <linearGradient id="balance" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ea580c" stopOpacity={0.72} />
                <stop offset="95%" stopColor="#fb923c" stopOpacity={0.06} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="date" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip />
            <Area type="monotone" dataKey="projected_balance" stroke="#ea580c" fill="url(#balance)" strokeWidth={3} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
