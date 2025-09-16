import React from "react";

const StatCardLine: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <section className="bg-white/10 p-6 rounded-xl text-center backdrop-blur-md border border-white/20 transition-all duration-300 ease-in-out hover:bg-white/15 hover:-translate-y-0.5">
    <h2 className="text-sm text-white/70">{label}</h2>
    {children}
  </section>
);

export default StatCardLine;