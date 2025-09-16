import React from "react";

const ChartCard: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <section className="h-full backdrop-blur-[20px] bg-white/5 border border-white/20 rounded-2xl p-8 my-4 shadow-[0_8px_32px_rgba(0,0,0,0.1)]">
    <h3 className="mb-6 border-b border-white/10 pb-4 flex items-center gap-2 text-white/90 text-lg m-0">{title}</h3>
    {children}
  </section>
);

export default ChartCard;