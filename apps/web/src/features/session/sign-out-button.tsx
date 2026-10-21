"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { LogOut } from "@/components/ui/icons";
import { useStatus } from "@/components/ui/notice";
import { errorText, SessionExpiredError } from "@/lib/api-client";

import { useSession } from "./session-provider";

export function SignOutButton() {
  const router = useRouter();
  const { request } = useSession();
  const { announce } = useStatus();
  const [pending, setPending] = useState(false);

  async function signOut() {
    setPending(true);
    try {
      await request("/api/session", { method: "DELETE" });
    } catch (error) {
      if (!(error instanceof SessionExpiredError)) {
        announce(errorText(error));
        setPending(false);
        return;
      }
    }
    router.replace("/login");
    router.refresh();
  }

  return (
    <button type="button" className="btn btn-on-dark min-h-10 px-3 py-2" onClick={signOut} disabled={pending}>
      <LogOut aria-hidden="true" className="size-4" />
      Sign out
    </button>
  );
}
