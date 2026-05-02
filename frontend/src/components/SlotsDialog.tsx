import { useEffect, useRef } from "react";

export interface SlotsDialogProps {
  open: boolean;
  lines: string[];
  onClose: () => void;
}

export function SlotsDialog({ open, lines, onClose }: SlotsDialogProps) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (open && lines.length > 0) {
      if (!el.open) {
        el.showModal();
      }
    } else if (el.open) {
      el.close();
    }
  }, [open, lines]);

  return (
    <dialog
      ref={ref}
      className="max-h-[85vh] w-[min(100%,28rem)] max-w-[calc(100vw-2rem)] rounded-xl border border-white/10 bg-zinc-950/95 p-0 text-zinc-100 shadow-2xl"
      onClose={onClose}
      onClick={(e) => {
        if (e.target === ref.current) {
          ref.current?.close();
        }
      }}
    >
      <div className="flex max-h-[85vh] flex-col p-4 md:p-5" onClick={(e) => e.stopPropagation()}>
        <div className="mb-3 flex items-start justify-between gap-3">
          <h2 className="text-lg font-semibold text-white">Available slots</h2>
          <button
            type="button"
            className="rounded-lg border border-white/15 px-3 py-1.5 text-sm text-zinc-200 hover:bg-white/10"
            onClick={() => ref.current?.close()}
          >
            Close
          </button>
        </div>
        <ul className="min-h-0 flex-1 space-y-2 overflow-y-auto pr-1">
          {lines.map((line, i) => (
            <li
              key={`${i}-${line.slice(0, 40)}`}
              className="rounded-lg border border-white/10 bg-black/30 px-3 py-2.5 text-sm leading-relaxed text-zinc-100"
            >
              {line}
            </li>
          ))}
        </ul>
      </div>
    </dialog>
  );
}
