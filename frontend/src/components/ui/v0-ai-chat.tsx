"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { ArrowUpIcon } from "lucide-react";

interface UseAutoResizeTextareaProps {
  minHeight: number;
  maxHeight?: number;
}

function useAutoResizeTextarea({
  minHeight,
  maxHeight,
}: UseAutoResizeTextareaProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(
    (reset?: boolean) => {
      const textarea = textareaRef.current;
      if (!textarea) return;

      if (reset) {
        textarea.style.height = `${minHeight}px`;
        return;
      }

      textarea.style.height = `${minHeight}px`;
      const newHeight = Math.max(
        minHeight,
        Math.min(
          textarea.scrollHeight,
          maxHeight ?? Number.POSITIVE_INFINITY,
        ),
      );
      textarea.style.height = `${newHeight}px`;
    },
    [minHeight, maxHeight],
  );

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = `${minHeight}px`;
    }
  }, [minHeight]);

  useEffect(() => {
    const handleResize = () => adjustHeight();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [adjustHeight]);

  return { textareaRef, adjustHeight };
}

export interface VercelV0ChatProps {
  onSend?: (message: string) => void | Promise<void>;
  disabled?: boolean;
  errorMessage?: string | null;
  heading?: string;
  placeholder?: string;
}

export function VercelV0Chat({
  onSend,
  disabled = false,
  errorMessage = null,
  heading = "What can I help you book?",
  placeholder = "Describe the appointment you need (specialty, date, preferences)…",
}: VercelV0ChatProps) {
  const [value, setValue] = useState("");
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 60,
    maxHeight: 200,
  });

  const submit = async () => {
    const text = value.trim();
    if (!text || disabled) return;
    setValue("");
    adjustHeight(true);
    await onSend?.(text);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void submit();
    }
  };

  return (
    <div className="flex w-full max-w-4xl flex-col items-center space-y-8 p-4">
      <h1 className="text-center text-3xl font-bold tracking-tight text-white drop-shadow-md md:text-4xl">
        {heading}
      </h1>

      {errorMessage ? (
        <p
          className="w-full rounded-lg border border-destructive/50 bg-destructive/10 px-3 py-2 text-center text-sm text-destructive"
          role="alert"
        >
          {errorMessage}
        </p>
      ) : null}

      <div className="w-full">
        <div className="relative rounded-xl border border-white/10 bg-zinc-950/55 shadow-lg backdrop-blur-md">
          <div className="overflow-y-auto">
            <Textarea
              ref={textareaRef}
              value={value}
              onChange={(e) => {
                setValue(e.target.value);
                adjustHeight();
              }}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={disabled}
              className={cn(
                "w-full px-4 py-3",
                "resize-none",
                "bg-transparent",
                "border-none",
                "text-sm text-zinc-100",
                "focus:outline-none",
                "focus-visible:ring-0 focus-visible:ring-offset-0",
                "placeholder:text-zinc-500 placeholder:text-sm",
                "min-h-[60px]",
              )}
              style={{ overflow: "hidden" }}
            />
          </div>

          <div className="flex items-center justify-end p-3">
            <button
              type="button"
              disabled={disabled || !value.trim()}
              onClick={() => void submit()}
              className={cn(
                "flex items-center justify-center rounded-lg border border-white/15 px-2.5 py-2 text-sm transition-colors",
                value.trim()
                  ? "bg-violet-500 text-white hover:bg-violet-400"
                  : "text-zinc-500",
              )}
            >
              <ArrowUpIcon className="h-4 w-4" />
              <span className="sr-only">Send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
