"use client";

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface Props {
  data: Array<{ date: string; count: number; value?: number }>;
  dataKey?: "count" | "value";
  height?: number;
  gradientFrom?: string;
  gradientTo?: string;
  stroke?: string;
}

export function TimeSeriesArea({
  data,
  dataKey = "count",
  height = 240,
  gradientFrom = "#2b65f5",
  gradientTo = "rgba(43,101,245,0)",
  stroke = "#84b1ff",
}: Props) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 10, right: 12, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="gradFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={gradientFrom} stopOpacity={0.5} />
            <stop offset="100%" stopColor={gradientTo} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="#1f2a44" strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="date" stroke="#6b7891" fontSize={11} tickMargin={8} />
        <YAxis stroke="#6b7891" fontSize={11} width={30} />
        <Tooltip
          contentStyle={{
            background: "#0b1020",
            border: "1px solid #232d42",
            borderRadius: 8,
            color: "#e4e9f0",
            fontSize: 12,
          }}
          labelStyle={{ color: "#9aa6ba" }}
        />
        <Area
          type="monotone"
          dataKey={dataKey}
          stroke={stroke}
          strokeWidth={2}
          fill="url(#gradFill)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
