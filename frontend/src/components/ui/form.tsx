"use client";

import type { FieldPath, FieldValues, UseFormReturn } from "react-hook-form";
import { FormProvider, useFormContext } from "react-hook-form";

import { cn } from "@/lib/utils";

const Form = FormProvider;

function FormField<TFieldValues extends FieldValues>({
  name,
  children
}: {
  name: FieldPath<TFieldValues>;
  children: (field: ReturnType<UseFormReturn<TFieldValues>["register"]>) => React.ReactNode;
}) {
  const form = useFormContext<TFieldValues>();

  return <>{children(form.register(name))}</>;
}

function FormItem({
  className,
  ...props
}: React.ComponentProps<"div">) {
  return <div className={cn("space-y-2", className)} {...props} />;
}

function FormLabel({
  className,
  ...props
}: React.ComponentProps<"label">) {
  return (
    <label
      className={cn("text-sm leading-none font-medium", className)}
      {...props}
    />
  );
}

function FormControl({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}

function FormMessage({
  children,
  className,
  ...props
}: React.ComponentProps<"p">) {
  if (!children) {
    return null;
  }

  return (
    <p className={cn("text-destructive text-sm", className)} {...props}>
      {children}
    </p>
  );
}

export { Form, FormControl, FormField, FormItem, FormLabel, FormMessage };
