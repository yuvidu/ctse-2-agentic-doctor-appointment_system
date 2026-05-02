"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type KeyboardEvent,
  type ReactNode,
} from "react";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import {
  ArrowUpIcon,
  CircleUserRound,
  FileUp,
  Palette,
  ImageIcon,
  MonitorIcon,
  Paperclip,
  PlusIcon,
} from "lucide-react";

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
      <h1 className="text-center text-3xl font-bold tracking-tight text-foreground md:text-4xl">
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
        <div className="relative rounded-xl border border-border bg-card/80 shadow-sm backdrop-blur-sm">
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
                "text-sm text-foreground",
                "focus:outline-none",
                "focus-visible:ring-0 focus-visible:ring-offset-0",
                "placeholder:text-muted-foreground placeholder:text-sm",
                "min-h-[60px]",
              )}
              style={{ overflow: "hidden" }}
            />
          </div>

          <div className="flex items-center justify-between p-3">
            <div className="flex items-center gap-2">
              <button
                type="button"
                disabled={disabled}
                className="group flex items-center gap-1 rounded-lg p-2 transition-colors hover:bg-muted disabled:opacity-50"
              >
                <Paperclip className="h-4 w-4 text-foreground" />
                <span className="hidden text-xs text-muted-foreground transition-opacity group-hover:inline">
                  Attach
                </span>
              </button>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                disabled={disabled}
                className="flex items-center justify-between gap-1 rounded-lg border border-dashed border-border px-2 py-1 text-sm text-muted-foreground transition-colors hover:bg-muted disabled:opacity-50"
              >
                <PlusIcon className="h-4 w-4" />
                Project
              </button>
              <button
                type="button"
                disabled={disabled || !value.trim()}
                onClick={() => void submit()}
                className={cn(
                  "flex items-center justify-between gap-1 rounded-lg border border-border px-1.5 py-1.5 text-sm transition-colors hover:bg-muted",
                  value.trim()
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground",
                )}
              >
                <ArrowUpIcon
                  className={cn(
                    "h-4 w-4",
                    value.trim() ? "text-primary-foreground" : "text-muted-foreground",
                  )}
                />
                <span className="sr-only">Send</span>
              </button>
            </div>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-center gap-2 md:gap-3">
          <ActionButton
            icon={<ImageIcon className="h-4 w-4" />}
            label="Clone a Screenshot"
            disabled={disabled}
          />
          <ActionButton
            icon={<Palette className="h-4 w-4" />}
            label="Import from Figma"
            disabled={disabled}
          />
          <ActionButton
            icon={<FileUp className="h-4 w-4" />}
            label="Upload a Project"
            disabled={disabled}
          />
          <ActionButton
            icon={<MonitorIcon className="h-4 w-4" />}
            label="Landing Page"
            disabled={disabled}
          />
          <ActionButton
            icon={<CircleUserRound className="h-4 w-4" />}
            label="Sign Up Form"
            disabled={disabled}
          />
        </div>
      </div>
    </div>
  );
}

interface ActionButtonProps {
  icon: ReactNode;
  label: string;
  disabled?: boolean;
}

function ActionButton({ icon, label, disabled }: ActionButtonProps) {
  return (
    <button
      type="button"
      disabled={disabled}
      className="flex items-center gap-2 rounded-full border border-border bg-card/80 px-3 py-2 text-xs text-muted-foreground backdrop-blur-sm transition-colors hover:bg-muted hover:text-foreground disabled:opacity-50 md:px-4"
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}
