"use client";

import { Message } from "@/lib/useChatStore";
import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { formatResponse, FormattedContent } from "@/lib/formatResponse";

interface MessageBubbleProps {
  message: Message;
}

function renderFormattedContent(item: FormattedContent) {
  if (item.type === 'table' && Array.isArray(item.content)) {
    const table = item.content as string[][];
    return (
      <div className="overflow-x-auto my-1 -mx-0.5 text-left">
        <table className="min-w-full border-collapse text-base">
          <thead>
            <tr className="bg-gray-50/50">
              {table[0]?.map((header, idx) => (
                <th
                  key={idx}
                  className="border-b border-gray-200 px-2 py-1.5 text-left font-semibold text-gray-700"
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.slice(1).map((row, rowIdx) => (
              <tr 
                key={rowIdx} 
                className={rowIdx % 2 === 0 ? "bg-white" : "bg-gray-50/30"}
              >
                {row.map((cell, cellIdx) => (
                  <td
                    key={cellIdx}
                    className="border-b border-gray-100 px-2 py-1.5 text-left text-gray-800"
                  >
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }
  
  return (
    <p className="whitespace-normal text-base leading-normal text-left">
      {item.content as string}
    </p>
  );
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const formattedContent = !isUser ? formatResponse(message.content) : null;
  const userBubbleStyle = {
    backgroundColor: "#1FB464",
    color: "#FFFFFF",
  };

  return (
    <div
      className={cn(
        "flex w-full",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div className={cn("flex max-w-[85%] flex-col gap-1", isUser ? "items-end" : "items-start")}>
        <Card
          className={cn(
            "rounded-lg shadow-sm",
            isUser
              ? "text-white"
              : "bg-gray-100 text-gray-900"
          )}
          style={isUser ? userBubbleStyle : undefined}
        >
          <CardContent className="p-0 px-3 pt-3 pb-2">
            {isUser ? (
              <p className="whitespace-normal text-base leading-normal text-left">
                {message.content}
              </p>
            ) : (
              <div className="space-y-1.5 text-left">
                {formattedContent?.map((item, idx) => (
                  <div key={idx} className="text-left">
                    {renderFormattedContent(item)}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
        <span className="text-xs text-muted-foreground">
          {message.timestamp.toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
}

