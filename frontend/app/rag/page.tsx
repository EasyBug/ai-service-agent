"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/useAuthStore";
import { Sidebar } from "@/components/Sidebar";
import { UploadBox } from "@/components/UploadBox";

export default function RAGPage() {
  const router = useRouter();
  const { isAuthenticated, hasPermission } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    } else if (!hasPermission("rag_access")) {
      // 没有权限，重定向到首页
      router.push("/");
    }
  }, [isAuthenticated, hasPermission, router]);

  if (!isAuthenticated || !hasPermission("rag_access")) {
    return null;
  }

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-gray-50 p-8">
        <div className="mx-auto max-w-2xl">
          <UploadBox />
        </div>
      </main>
    </div>
  );
}

