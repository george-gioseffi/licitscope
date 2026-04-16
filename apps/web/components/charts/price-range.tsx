/**
 * Tiny inline visualization of a price distribution:
 *
 *    min ─────[ p25 ── median ── p75 ]───── max
 *
 * Used inside the pricing intelligence table to make the IQR legible at
 * a glance instead of forcing the reader to compare five numeric columns.
 */

export function PriceRange({
  min,
  p25,
  median,
  p75,
  max,
  anomaly,
}: {
  min: number;
  p25: number;
  median: number;
  p75: number;
  max: number;
  anomaly?: boolean;
}) {
  const span = Math.max(1e-6, max - min);
  const pct = (v: number) => ((v - min) / span) * 100;
  const iqrLeft = pct(p25);
  const iqrWidth = Math.max(2, pct(p75) - pct(p25));
  const medianLeft = pct(median);

  const barColor = anomaly ? "bg-rose-500/60" : "bg-brand-500/60";
  const medianColor = anomaly ? "bg-rose-300" : "bg-brand-200";

  return (
    <div className="relative h-2 w-full min-w-[100px] rounded-full bg-ink-800">
      {/* IQR */}
      <div
        className={`absolute top-0 h-full rounded-full ${barColor}`}
        style={{ left: `${iqrLeft}%`, width: `${iqrWidth}%` }}
      />
      {/* median tick */}
      <div
        className={`absolute top-[-2px] h-[12px] w-[2px] rounded ${medianColor}`}
        style={{ left: `calc(${medianLeft}% - 1px)` }}
      />
    </div>
  );
}
