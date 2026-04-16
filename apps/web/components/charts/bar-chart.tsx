"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, Cell } from "recharts";

interface Props {
  data: Array<Record<string, any>>;
  categoryKey: string;
  valueKey: string;
  height?: number;
  color?: string;
  layout?: "horizontal" | "vertical";
}

const PALETTE = ["#2b65f5", "#8b5cf6", "#2dd4bf", "#f59e0b", "#f43f5e", "#84b1ff", "#b4d0ff"];

export function CompactBar({
  data,
  categoryKey,
  valueKey,
  height = 240,
  color = "#2b65f5",
  layout = "vertical",
}: Props) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout={layout} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="#1f2a44" strokeDasharray="3 3" horizontal={layout === "horizontal"} vertical={layout === "vertical"} />
        {layout === "vertical" ? (
          <>
            <XAxis dataKey={categoryKey} stroke="#6b7891" fontSize={10} tickMargin={6} />
            <YAxis stroke="#6b7891" fontSize={10} width={36} />
          </>
        ) : (
          <>
            <XAxis type="number" stroke="#6b7891" fontSize={10} />
            <YAxis
              dataKey={categoryKey}
              type="category"
              stroke="#6b7891"
              fontSize={10}
              width={110}
            />
          </>
        )}
        <Tooltip
          contentStyle={{
            background: "#0b1020",
            border: "1px solid #232d42",
            borderRadius: 8,
            color: "#e4e9f0",
            fontSize: 12,
          }}
        />
        <Bar dataKey={valueKey} radius={4} fill={color}>
          {data.map((_, idx) => (
            <Cell key={idx} fill={PALETTE[idx % PALETTE.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
