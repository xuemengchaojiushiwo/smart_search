package com.knowledge.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.knowledge.dto.KnowledgeDTO;
import com.knowledge.entity.Attachment;
import com.knowledge.entity.Knowledge;
import com.knowledge.service.KnowledgeService;
import com.knowledge.vo.ApiResponse;
import com.knowledge.vo.KnowledgeVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import javax.validation.Valid;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/knowledge")
@Tag(name = "知识管理", description = "知识库管理相关接口")
public class KnowledgeController {
    
    @Autowired
    private KnowledgeService knowledgeService;
    
    @PostMapping
    @Operation(summary = "创建知识", description = "创建新的知识条目")
    public ApiResponse<Knowledge> createKnowledge(
            @Parameter(description = "知识信息", required = true) @Valid @RequestBody KnowledgeDTO dto) {
        Knowledge knowledge = knowledgeService.createKnowledge(dto, "admin");
        return ApiResponse.success("创建知识成功", knowledge);
    }
    
    @PostMapping("/create")
    @Operation(summary = "创建知识（支持文件上传）", description = "创建新的知识条目，支持同时上传附件文件")
    public ApiResponse<Knowledge> createKnowledgeWithFileUpload(
            @Parameter(description = "知识名称", required = true) @RequestParam("name") String name,
            @Parameter(description = "知识描述") @RequestParam(value = "description", required = false) String description,
            @Parameter(description = "类目ID", required = true) @RequestParam("categoryId") Long categoryId,
            @Parameter(description = "标签（逗号分隔）") @RequestParam(value = "tags", required = false) String tags,
            @Parameter(description = "生效开始时间") @RequestParam(value = "effectiveStartTime", required = false) String effectiveStartTime,
            @Parameter(description = "生效结束时间") @RequestParam(value = "effectiveEndTime", required = false) String effectiveEndTime,
            @Parameter(description = "变更原因") @RequestParam(value = "changeReason", required = false) String changeReason,
            @Parameter(description = "附件文件列表") @RequestParam(value = "files", required = false) MultipartFile[] files) {
        
        KnowledgeDTO dto = new KnowledgeDTO();
        dto.setName(name);
        dto.setDescription(description);
        dto.setCategoryId(categoryId);
        // 处理标签
        if (tags != null && !tags.trim().isEmpty()) {
            dto.setTags(java.util.Arrays.asList(tags.split(",")));
        }
        // 处理时间
        if (effectiveStartTime != null && !effectiveStartTime.trim().isEmpty()) {
            try {
                dto.setEffectiveStartTime(java.time.LocalDateTime.parse(effectiveStartTime));
            } catch (Exception e) {
                log.warn("解析生效开始时间失败: {}", effectiveStartTime);
            }
        }
        if (effectiveEndTime != null && !effectiveEndTime.trim().isEmpty()) {
            try {
                dto.setEffectiveEndTime(java.time.LocalDateTime.parse(effectiveEndTime));
            } catch (Exception e) {
                log.warn("解析生效结束时间失败: {}", effectiveEndTime);
            }
        }
        dto.setChangeReason(changeReason);
        
        Knowledge knowledge = knowledgeService.createKnowledgeWithFiles(dto, files, "admin");
        return ApiResponse.success("创建知识成功", knowledge);
    }
    
    @PutMapping("/{id}")
    @Operation(summary = "更新知识", description = "根据ID更新知识信息")
    public ApiResponse<Knowledge> updateKnowledge(
            @Parameter(description = "知识ID", required = true, example = "1") @PathVariable Long id,
            @Parameter(description = "知识信息", required = true) @Valid @RequestBody KnowledgeDTO dto) {
        Knowledge knowledge = knowledgeService.updateKnowledge(id, dto, "admin");
        return ApiResponse.success("更新知识成功", knowledge);
    }
    
    @DeleteMapping("/{id}")
    @Operation(summary = "删除知识", description = "根据ID删除知识")
    public ApiResponse<Void> deleteKnowledge(
            @Parameter(description = "知识ID", required = true, example = "1") @PathVariable Long id) {
        knowledgeService.deleteKnowledge(id, "admin");
        return ApiResponse.success(null);
    }
    
    @GetMapping("/{id}")
    @Operation(summary = "获取知识详情", description = "根据ID获取知识详细信息，包含附件信息")
    public ApiResponse<Map<String, Object>> getKnowledge(
            @Parameter(description = "知识ID", required = true, example = "1") @PathVariable Long id) {
        Knowledge knowledge = knowledgeService.getById(id);
        if (knowledge == null) {
            return ApiResponse.error("知识不存在");
        }
        
        // 获取附件信息
        List<Attachment> attachments = knowledgeService.getAttachmentsByKnowledgeId(id);
        
        // 构建返回结果
        Map<String, Object> result = new HashMap<>();
        result.put("id", knowledge.getId());
        result.put("name", knowledge.getName());
        result.put("description", knowledge.getDescription());
        result.put("categoryId", knowledge.getCategoryId());
        result.put("tags", knowledge.getTags());
        result.put("effectiveStartTime", knowledge.getEffectiveStartTime());
        result.put("effectiveEndTime", knowledge.getEffectiveEndTime());
        result.put("status", knowledge.getStatus());
        result.put("createdBy", knowledge.getCreatedBy());
        result.put("createdTime", knowledge.getCreatedTime());
        result.put("updatedBy", knowledge.getUpdatedBy());
        result.put("updatedTime", knowledge.getUpdatedTime());
        result.put("searchCount", knowledge.getSearchCount());
        result.put("downloadCount", knowledge.getDownloadCount());
        result.put("attachments", attachments);
        
        return ApiResponse.success("获取知识详情成功", result);
    }
    
    @GetMapping
    @Operation(summary = "获取知识列表", description = "分页获取知识列表")
    public ApiResponse<IPage<KnowledgeVO>> getKnowledgeList(
            @Parameter(description = "页码", example = "1") @RequestParam(defaultValue = "1") int page,
            @Parameter(description = "每页大小", example = "10") @RequestParam(defaultValue = "10") int size) {
        IPage<KnowledgeVO> result = knowledgeService.getKnowledgeList(page, size);
        return ApiResponse.success("获取知识列表成功", result);
    }
    
    @GetMapping("/category/{categoryId}")
    @Operation(summary = "根据类目获取知识", description = "根据类目ID分页获取知识列表")
    public ApiResponse<IPage<KnowledgeVO>> getKnowledgeByCategory(
            @Parameter(description = "类目ID", required = true, example = "1") @PathVariable Long categoryId,
            @Parameter(description = "页码", example = "1") @RequestParam(defaultValue = "1") int page,
            @Parameter(description = "每页大小", example = "10") @RequestParam(defaultValue = "10") int size) {
        IPage<KnowledgeVO> result = knowledgeService.getKnowledgeByCategory(categoryId, page, size);
        return ApiResponse.success("获取类目知识成功", result);
    }
    
    @GetMapping("/popular")
    @Operation(summary = "获取热门知识", description = "获取热门知识列表")
    public ApiResponse<List<KnowledgeVO>> getPopularKnowledge(
            @Parameter(description = "返回数量", example = "10") @RequestParam(defaultValue = "10") int limit) {
        List<KnowledgeVO> result = knowledgeService.getPopularKnowledge(limit);
        return ApiResponse.success("获取热门知识成功", result);
    }
    
    @GetMapping("/latest")
    @Operation(summary = "获取最新知识", description = "获取最新知识列表")
    public ApiResponse<List<KnowledgeVO>> getLatestKnowledge(
            @Parameter(description = "返回数量", example = "10") @RequestParam(defaultValue = "10") int limit) {
        List<KnowledgeVO> result = knowledgeService.getLatestKnowledge(limit);
        return ApiResponse.success("获取最新知识成功", result);
    }
    
    @GetMapping("/hot-downloads")
    @Operation(summary = "获取最热资料", description = "根据下载数量倒序获取最热资料列表")
    public ApiResponse<List<KnowledgeVO>> getHotDownloads(
            @Parameter(description = "返回数量", example = "10") @RequestParam(defaultValue = "10") int limit) {
        List<KnowledgeVO> result = knowledgeService.getHotDownloads(limit);
        return ApiResponse.success("获取最热资料成功", result);
    }
    
    @PostMapping("/{id}/document")
    @Operation(summary = "处理知识文档", description = "上传并处理知识文档，存入ES")
    public ApiResponse<Map<String, Object>> processDocument(
            @Parameter(description = "知识ID", required = true, example = "1") @PathVariable Long id,
            @Parameter(description = "文档文件", required = true) @RequestParam("file") MultipartFile file) {
        Map<String, Object> result = knowledgeService.processKnowledgeDocument(file, id, "admin");
        return ApiResponse.success("文档处理成功", result);
    }
    
    @PostMapping("/{id}/documents")
    @Operation(summary = "处理多个知识文档", description = "上传并处理多个知识文档，存入ES")
    public ApiResponse<Map<String, Object>> processDocuments(
            @Parameter(description = "知识ID", required = true, example = "1") @PathVariable Long id,
            @Parameter(description = "文档文件列表", required = true) @RequestParam("files") MultipartFile[] files) {
        Map<String, Object> result = knowledgeService.processKnowledgeDocuments(files, id, "admin");
        return ApiResponse.success("文档处理成功", result);
    }
} 
