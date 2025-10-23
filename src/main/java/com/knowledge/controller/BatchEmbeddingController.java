package com.knowledge.controller;

import com.knowledge.vo.ApiResponse;
import com.knowledge.entity.Knowledge;
import com.knowledge.entity.Attachment;
import com.knowledge.service.KnowledgeService;
import com.knowledge.service.AttachmentService;
import com.knowledge.service.KnowledgeWorkspaceService;
import com.knowledge.service.PythonService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.ArrayList;
import java.nio.file.Files;

/**
 * 批量嵌入处理控制器
 */
@Slf4j
@RestController
@RequestMapping("/api/batch")
@RequiredArgsConstructor
@Tag(name = "批量嵌入处理", description = "批量处理知识嵌入到ES")
public class BatchEmbeddingController {

    private final KnowledgeService knowledgeService;
    private final AttachmentService attachmentService;
    private final KnowledgeWorkspaceService knowledgeWorkspaceService;
    private final PythonService pythonService;

    /**
     * 启动批量嵌入处理
     */
    @PostMapping("/embedding/start")
    @Operation(summary = "启动批量嵌入处理", description = "查询数据库中的知识数据，调用Python处理ES嵌入")
    public ApiResponse<Map<String, Object>> startBatchEmbedding(
            @Parameter(description = "起始知识ID") @RequestParam(required = false) Long startKnowledgeId,
            @Parameter(description = "批次大小") @RequestParam(defaultValue = "10") Integer batchSize,
            @Parameter(description = "是否强制重新处理") @RequestParam(defaultValue = "false") Boolean forceReprocess) {
        
        try {
            log.info("开始批量嵌入处理: startKnowledgeId={}, batchSize={}, forceReprocess={}", 
                    startKnowledgeId, batchSize, forceReprocess);
            
            // 1. 查询需要处理的知识列表
            List<Knowledge> knowledgeList = knowledgeService.getKnowledgeListForEmbedding(startKnowledgeId, batchSize);
            
            if (knowledgeList.isEmpty()) {
                return ApiResponse.success("没有找到需要处理的知识", Map.of(
                    "processedCount", 0,
                    "totalCount", 0,
                    "message", "没有找到需要处理的知识"
                ));
            }
            
            log.info("找到 {} 个知识需要处理", knowledgeList.size());
            
            int processedCount = 0;
            int errorCount = 0;
            List<String> errors = new ArrayList<>();
            
            // 2. 逐个处理知识
            for (Knowledge knowledge : knowledgeList) {
                try {
                    // 获取知识的工作空间
                    List<String> workspaces = knowledgeWorkspaceService.listWorkspaces(knowledge.getId());
                    String workspacesStr = workspaces != null && !workspaces.isEmpty() ? String.join(",", workspaces) : "WPB";
                    
                    // 获取知识的附件
                    List<Attachment> attachments = attachmentService.getByKnowledgeId(knowledge.getId());
                    
                    boolean knowledgeSuccess = true;
                    int fileProcessedCount = 0;
                    
                    // 3. 处理元数据embedding（无论是否有文件都要处理）
                    try {
                        String effectiveTime = knowledge.getEffectiveStartTime() != null ? 
                            knowledge.getEffectiveStartTime().toString() : null;
                        String tagsStr = knowledge.getTags() != null ? String.join(",", knowledge.getTags()) : null;
                        
                        boolean metadataSuccess = pythonService.indexKnowledgeMetadata(knowledge, workspaces);
                        if (metadataSuccess) {
                            log.info("知识ID {} 元数据embedding处理成功", knowledge.getId());
                        } else {
                            log.warn("知识ID {} 元数据embedding处理失败", knowledge.getId());
                            knowledgeSuccess = false;
                        }
                    } catch (Exception e) {
                        log.error("处理知识ID {} 元数据embedding时发生异常: {}", knowledge.getId(), e.getMessage(), e);
                        knowledgeSuccess = false;
                    }
                    
                    // 4. 处理文件embedding（如果有文件的话）
                    for (Attachment attachment : attachments) {
                        try {
                            // 使用Attachment实体的实际文件路径
                            String actualFilePath = attachment.getFilePath();
                            log.info("处理附件: ID={}, 文件名={}, 文件路径={}", attachment.getId(), attachment.getFileName(), actualFilePath);
                            
                            // 读取文件并转换为MultipartFile
                            java.io.File file = new java.io.File(actualFilePath);
                            if (!file.exists()) {
                                log.warn("文件不存在，跳过: {}", actualFilePath);
                                continue;
                            }
                            
                            // 创建MultipartFile
                            byte[] fileBytes = Files.readAllBytes(file.toPath());
                            org.springframework.web.multipart.MultipartFile multipartFile = 
                                new org.springframework.web.multipart.MultipartFile() {
                                    @Override
                                    public String getName() { return "file"; }
                                    
                                    @Override
                                    public String getOriginalFilename() { return attachment.getFileName(); }
                                    
                                    @Override
                                    public String getContentType() { return attachment.getFileType(); }
                                    
                                    @Override
                                    public boolean isEmpty() { return fileBytes.length == 0; }
                                    
                                    @Override
                                    public long getSize() { return fileBytes.length; }
                                    
                                    @Override
                                    public byte[] getBytes() { return fileBytes; }
                                    
                                    @Override
                                    public java.io.InputStream getInputStream() { 
                                        return new java.io.ByteArrayInputStream(fileBytes); 
                                    }
                                    
                                    @Override
                                    public void transferTo(java.io.File dest) throws java.io.IOException {
                                        Files.write(dest.toPath(), fileBytes);
                                    }
                                };
                            
                            // 调用现有的processDocument方法
                            String effectiveTime = knowledge.getEffectiveStartTime() != null ? 
                                knowledge.getEffectiveStartTime().toString() : null;
                            String tagsStr = knowledge.getTags() != null ? String.join(",", knowledge.getTags()) : null;
                            
                            Map<String, Object> fileResponse = pythonService.processDocument(
                                multipartFile,
                                knowledge.getId(),
                                knowledge.getName(),
                                knowledge.getDescription(),
                                tagsStr,
                                effectiveTime,
                                workspacesStr
                            );
                            
                            log.info("文件处理响应: {}", fileResponse);
                            boolean fileSuccess = fileResponse != null && Boolean.TRUE.equals(fileResponse.get("success"));
                            
                            if (fileSuccess) {
                                fileProcessedCount++;
                                log.info("知识ID {} 文件 {} 处理成功", knowledge.getId(), attachment.getFileName());
                            } else {
                                log.warn("知识ID {} 文件 {} 处理失败", knowledge.getId(), attachment.getFileName());
                                knowledgeSuccess = false;
                            }
                            
                        } catch (Exception e) {
                            log.error("处理知识ID {} 文件 {} 时发生异常: {}", knowledge.getId(), attachment.getFileName(), e.getMessage(), e);
                            knowledgeSuccess = false;
                        }
                    }
                    
                    if (knowledgeSuccess) {
                        processedCount++;
                        log.info("知识ID {} 嵌入处理成功，处理了 {} 个文件", knowledge.getId(), fileProcessedCount);
                    } else {
                        errorCount++;
                        String error = String.format("知识ID %d 嵌入处理失败", knowledge.getId());
                        errors.add(error);
                        log.warn(error);
                    }
                    
                } catch (Exception e) {
                    errorCount++;
                    String error = String.format("知识ID %d 处理异常: %s", knowledge.getId(), e.getMessage());
                    errors.add(error);
                    log.error("处理知识ID {} 时发生异常", knowledge.getId(), e);
                }
            }
            
            // 3. 返回处理结果
            Map<String, Object> result = new HashMap<>();
            result.put("processedCount", processedCount);
            result.put("totalCount", knowledgeList.size());
            result.put("errorCount", errorCount);
            result.put("errors", errors);
            result.put("message", String.format("批量嵌入处理完成，成功处理 %d/%d 个知识", processedCount, knowledgeList.size()));
            
            return ApiResponse.success("批量嵌入处理完成", result);
            
        } catch (Exception e) {
            log.error("批量嵌入处理失败", e);
            return ApiResponse.error("批量嵌入处理失败: " + e.getMessage());
        }
    }
    
    /**
     * 获取批量处理状态
     */
    @GetMapping("/embedding/status")
    @Operation(summary = "获取批量处理状态", description = "获取当前批量处理的状态信息")
    public ApiResponse<Map<String, Object>> getBatchEmbeddingStatus() {
        // 这里可以添加状态跟踪逻辑
        Map<String, Object> status = new HashMap<>();
        status.put("isRunning", false);
        status.put("message", "批量处理服务就绪");
        return ApiResponse.success("获取状态成功", status);
    }
}
