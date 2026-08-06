import { type TextareaHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn(
        "w-full rounded-md border border-silver-300 bg-white px-3 py-2 text-sm text-brand-950",
        "placeholder:text-brand-950/40 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20",
        "disabled:bg-silver-100 disabled:text-brand-950/50",
        className,
      )}
      {...props}
    />
  ),
);
Textarea.displayName = "Textarea";
