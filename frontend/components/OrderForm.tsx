"use client";

import { useState } from "react";
import { Search, Loader2 } from "lucide-react";
import { apiService } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";

interface OrderData {
  id: number;
  order_id: string;
  customer_name: string;
  customer_email: string;
  product: string;
  status: string;
  amount: string;
  created_at: string;
  updated_at: string;
  can_send_email?: boolean;
}

export function OrderForm() {
  const [orderId, setOrderId] = useState("");
  const [order, setOrder] = useState<OrderData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSendingEmail, setIsSendingEmail] = useState(false);
  const { toast } = useToast();

  const handleSearch = async () => {
    if (!orderId.trim()) {
      toast({
        title: "请输入订单号",
        description: "订单号不能为空",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setOrder(null);

    try {
      const response = await apiService.queryOrder(orderId.trim());

      // 检查响应是否成功
      if (response.success && response.data) {
        setOrder(response.data);
        toast({
          title: "查询成功",
          description: "订单信息已加载",
        });
      } else {
        // 如果响应不成功，显示错误消息
        const errorMessage = response.message || "订单不存在";
        toast({
          title: "查询失败",
          description: errorMessage,
          variant: "destructive",
        });
        setOrder(null);
      }
    } catch (error: any) {
      // 处理网络错误或后端返回的错误响应
      const errorMessage =
        error.response?.data?.message || 
        error.message || 
        "查询失败，请稍后重试";
      toast({
        title: "查询失败",
        description: errorMessage,
        variant: "destructive",
      });
      setOrder(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendEmail = async () => {
    if (!order) return;
    const confirmed = window.confirm(
      `是否将订单 ${order.order_id} 的信息发送到邮箱 ${order.customer_email}?`
    );
    if (!confirmed) return;

    setIsSendingEmail(true);
    try {
      const response = await apiService.sendOrderEmail(order.order_id);
      if (response.success) {
        toast({
          title: "邮件发送成功",
          description: `已发送至 ${order.customer_email}`,
        });
      } else {
        throw new Error(response.message || "发送失败");
      }
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message ||
        error.message ||
        "发送失败，请稍后重试";
      toast({
        title: "发送失败",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsSendingEmail(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Form */}
      <Card>
        <CardHeader>
          <CardTitle>订单查询</CardTitle>
          <CardDescription>请输入订单号进行查询</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input
              value={orderId}
              onChange={(e) => setOrderId(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="例如：ORD-2024-001"
              disabled={isLoading}
            />
            <Button onClick={handleSearch} disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  查询中...
                </>
              ) : (
                <>
                  <Search className="mr-2 h-4 w-4" />
                  查询
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Order Result */}
      {order && (
        <Card>
          <CardHeader>
            <CardTitle>订单详情</CardTitle>
            <CardDescription>订单号：{order.order_id}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">客户姓名</p>
                <p className="text-base font-semibold">{order.customer_name}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">客户邮箱</p>
                <p className="text-base font-semibold">{order.customer_email}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">产品名称</p>
                <p className="text-base font-semibold">{order.product}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">订单金额</p>
                <p className="text-base font-semibold">¥{order.amount}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">订单状态</p>
                <p className="text-base font-semibold">{order.status}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">创建时间</p>
                <p className="text-base font-semibold">
                  {new Date(order.created_at).toLocaleString("zh-CN")}
                </p>
              </div>
            </div>
            <div className="flex justify-end">
              <Button
                onClick={handleSendEmail}
                disabled={isSendingEmail}
                variant="secondary"
              >
                {isSendingEmail ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    正在发送...
                  </>
                ) : (
                  "发送订单信息到邮箱"
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

