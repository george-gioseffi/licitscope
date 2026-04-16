"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const PALETTE = ["#2b65f5", "#8b5cf6", "#2dd4bf", "#f59e0b", "#f43f5e", "#84b1ff", "#b4d0ff"];

export function Donut({
  data,
  dataKey = "value",
  nameKey = "name",
  height = 240,
}: {
  data: Array<Record<string, any>>;
  dataKey?: string;
  nameKey?: string;
  height?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Tooltip
          contentStyle={{
            background: "#0b1020",
            border: "1px solid #232d42",
            borderRadius: 8,
            color: "#e4e9f0",
            fontSize: 12,
          }}
        />
        <Pie
          data={data}
          dataKey={dataKey}
          nameKey={nameKey}
          innerRadius={50}
          outerRadius={90}
          stroke="#0b1020"
          strokeWidth={2}
          paddingAngle={2}
        >
          {data.map((_, idx) => (
            <Cell key={idx} fill={PALETTE[idx % PALETTE.length]} />
          ))}
        </Pie>
      </PieChart>
    </ResponsiveContainer>
  );
}
