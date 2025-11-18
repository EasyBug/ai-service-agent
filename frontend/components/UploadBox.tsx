"use client";

import { useState, useRef, useEffect } from "react";
import { Upload, FileText, Loader2, CheckCircle2, X, Trash2, RefreshCw } from "lucide-react";
import { apiService } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";

interface RAGFile {
  filename: string;
  size: number;
  modified: number;
}

export function UploadBox() {
  const [isUploading, setIsUploading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);
  const [ragFiles, setRagFiles] = useState<RAGFile[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  // 加载文件列表
  const loadFiles = async () => {
    setIsLoadingFiles(true);
    try {
      const response = await apiService.listRAGFiles();
      if (response.success && response.data) {
        setRagFiles(response.data.files || []);
      }
    } catch (error: any) {
      console.error("加载文件列表失败:", error);
    } finally {
      setIsLoadingFiles(false);
    }
  };

  // 组件加载时获取文件列表
  useEffect(() => {
    loadFiles();
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    // 过滤支持的文件类型
    const allowedTypes = [".txt", ".md", ".pdf"];
    const validFiles = files.filter((file) => {
      const ext = file.name.toLowerCase().substring(file.name.lastIndexOf("."));
      return allowedTypes.includes(ext);
    });
    
    if (validFiles.length !== files.length) {
      toast({
        title: "文件格式不支持",
        description: "仅支持 TXT、MD、PDF 格式",
        variant: "destructive",
      });
    }
    
    setSelectedFiles((prev) => [...prev, ...validFiles]);
  };

  const handleRemoveFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      toast({
        title: "请选择文件",
        description: "请先选择要上传的文件",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    setIsSuccess(false);

    try {
      const response = await apiService.uploadFiles(selectedFiles);

      if (response.success) {
        setIsSuccess(true);
        setSelectedFiles([]);
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
        
        const uploadedCount = response.data.uploaded.length;
        const failedCount = response.data.failed.length;
        
        let description = `成功上传 ${uploadedCount} 个文件`;
        if (response.data.index_updated) {
          description += "，知识库已更新";
        }
        if (failedCount > 0) {
          description += `，${failedCount} 个文件上传失败`;
        }
        
        toast({
          title: "上传成功",
          description,
        });
        
        // 重新加载文件列表
        await loadFiles();
      } else {
        throw new Error(response.message || "上传失败");
      }
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || error.message || "上传失败";
      toast({
        title: "上传失败",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleUpdate = async () => {
    setIsUploading(true);
    setIsSuccess(false);

    try {
      const response = await apiService.updateRAG();

      if (response.success) {
        setIsSuccess(true);
        toast({
          title: "更新成功",
          description: "知识库已成功更新",
        });
        // 重新加载文件列表
        await loadFiles();
      } else {
        throw new Error(response.message || "更新失败");
      }
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || error.message || "更新失败";
      toast({
        title: "更新失败",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteFile = async (filename: string) => {
    if (!confirm(`确定要删除文件 "${filename}" 吗？此操作将删除该文件及其所有索引，且无法恢复！`)) {
      return;
    }

    setIsClearing(true);

    try {
      const response = await apiService.clearRAG(filename);

      if (response.success) {
        toast({
          title: "删除成功",
          description: response.data?.deleted_count 
            ? `已删除文件 "${filename}"，删除了 ${response.data.deleted_count} 条记录`
            : `已删除文件 "${filename}"`,
        });
        // 重新加载文件列表
        await loadFiles();
      } else {
        throw new Error(response.message || "删除失败");
      }
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || error.message || "删除失败";
      toast({
        title: "删除失败",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsClearing(false);
    }
  };

  const handleClearAll = async () => {
    if (!confirm("确定要清空整个知识库吗？此操作将删除所有已索引的文档，且无法恢复！")) {
      return;
    }

    setIsClearing(true);

    try {
      const response = await apiService.clearRAG();

      if (response.success) {
        toast({
          title: "清空成功",
          description: response.data?.deleted_count 
            ? `已删除 ${response.data.deleted_count} 条记录`
            : "知识库已清空",
        });
        // 重新加载文件列表
        await loadFiles();
      } else {
        throw new Error(response.message || "清空失败");
      }
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message || error.message || "清空失败";
      toast({
        title: "清空失败",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsClearing(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>知识库管理</CardTitle>
        <CardDescription>
          更新知识库索引，从 data/ 目录加载文档
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 文件上传区域 */}
        <div className="rounded-lg border-2 border-dashed border-gray-300 p-8 text-center">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-4 text-sm text-muted-foreground">
            选择文件上传到知识库
          </p>
          <p className="mt-2 text-xs text-muted-foreground">
            支持的格式：TXT、MD、PDF
          </p>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".txt,.md,.pdf"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
          />
          <Button
            type="button"
            variant="outline"
            className="mt-4"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
          >
            <Upload className="mr-2 h-4 w-4" />
            选择文件
          </Button>
        </div>

        {/* 已选择的文件列表 */}
        {selectedFiles.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-medium">已选择的文件：</p>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {selectedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between rounded-lg border p-2 text-sm"
                >
                  <span className="truncate flex-1">{file.name}</span>
                  <span className="text-xs text-muted-foreground mr-2">
                    {(file.size / 1024).toFixed(2)} KB
                  </span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveFile(index)}
                    disabled={isUploading}
                    className="h-6 w-6 p-0"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 操作按钮 */}
        <div className="flex gap-2">
          <Button
            onClick={handleUpload}
            disabled={isUploading || isClearing || selectedFiles.length === 0}
            className="flex-1"
          >
            {isUploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                上传中...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                上传并更新知识库
              </>
            )}
          </Button>
          <Button
            onClick={handleUpdate}
            disabled={isUploading || isClearing}
            variant="outline"
            className="flex-1"
          >
            {isUploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                更新中...
              </>
            ) : (
              <>
                <FileText className="mr-2 h-4 w-4" />
                仅更新索引
              </>
            )}
          </Button>
        </div>

        {/* 已上传的文件列表 */}
        {ragFiles.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">已上传的文件：</p>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={loadFiles}
                disabled={isLoadingFiles}
                className="h-7"
              >
                <RefreshCw className={`h-3 w-3 mr-1 ${isLoadingFiles ? 'animate-spin' : ''}`} />
                刷新
              </Button>
            </div>
            <div className="space-y-2 max-h-60 overflow-y-auto rounded-lg border p-2">
              {ragFiles.map((file) => (
                <div
                  key={file.filename}
                  className="flex items-center justify-between rounded-lg border p-2 text-sm hover:bg-gray-50"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{file.filename}</p>
                    <p className="text-xs text-muted-foreground">
                      {(file.size / 1024).toFixed(2)} KB ·{" "}
                      {new Date(file.modified * 1000).toLocaleString("zh-CN")}
                    </p>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteFile(file.filename)}
                    disabled={isUploading || isClearing}
                    className="h-7 w-7 p-0 text-destructive hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 清空整个知识库按钮 */}
        {ragFiles.length > 0 && (
          <Button
            onClick={handleClearAll}
            disabled={isUploading || isClearing}
            variant="destructive"
            className="w-full"
          >
            {isClearing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                清空中...
              </>
            ) : (
              <>
                <Trash2 className="mr-2 h-4 w-4" />
                清空整个知识库
              </>
            )}
          </Button>
        )}

        <div className="rounded-lg bg-muted p-4">
          <p className="text-sm font-medium mb-2">使用说明：</p>
          <ul className="text-xs text-muted-foreground space-y-1 list-disc list-inside">
            <li>点击"选择文件"按钮上传文档（支持 TXT、MD、PDF 格式）</li>
            <li>点击"上传并更新知识库"按钮上传文件并自动更新索引</li>
            <li>或点击"仅更新索引"按钮更新已有文档的索引</li>
            <li>点击"清空知识库"按钮删除所有已索引的文档（不可恢复）</li>
            <li>更新后即可在智能问答中使用</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}

