import type { HTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium", {
  variants: {
    variant: {
      neutral: "bg-silver-200 text-brand-900",
      brand: "bg-brand-100 text-brand-700",
      success: "bg-green-100 text-tricolore-verde",
      danger: "bg-red-100 text-tricolore-rosso",
    },
  },
  defaultVariants: { variant: "neutral" },
});

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
