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
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.net.URLEncoder;

import javax.validation.Valid;
import java.util.ArrayList;
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
    @Autowired
    private com.knowledge.service.AttachmentService attachmentService;
    @Autowired
    private com.knowledge.service.UserDeptRoleService userDeptRoleService;
    @Autowired
    private com.knowledge.service.UserService userService;

    private List<String> resolveAllowedWorkspaces(String userId) {
        try {
            if (userId == null) return null;
            Long uid = null;
            try { uid = Long.valueOf(userId); } catch (Exception ignore) {}
            if (uid != null) {
                List<com.knowledge.entity.UserDeptRole> records = userDeptRoleService.listByUser(uid);
                if (records != null && !records.isEmpty()) {
                    List<String> list = new ArrayList<>();
                    for (com.knowledge.entity.UserDeptRole r : records) {
                        if (r.getDept() != null && !r.getDept().trim().isEmpty()) list.add(r.getDept().trim());
                    }
                    if (!list.isEmpty()) return list;
                }
                com.knowledge.entity.User u = userService.getById(uid);
                if (u != null && u.getWorkspace() != null && !u.getWorkspace().trim().isEmpty()) {
                    String[] parts = u.getWorkspace().split(",");
                    List<String> list = new ArrayList<>();
                    for (String p : parts) { if (!p.trim().isEmpty()) list.add(p.trim()); }
                    if (!list.isEmpty()) return list;
                }
            }
        } catch (Exception ignore) {}
        return null;
    }

    // 简化：从头部兼容获取用户ID
    private String resolveUserIdFromHeader(javax.servlet.http.HttpServletRequest request) {
        String uid = request.getHeader("X-User-Id");
        if (uid != null && !uid.isEmpty()) return uid;
        return null; // 可扩展JWT解析
    }
    
    @PostMapping
    @Operation(summary = "创建知识", description = "创建新的知识条目")
    public ApiResponse<Knowledge> createKnowledge(
            @Parameter(description = "知识信息", required = true) @Valid @RequestBody KnowledgeDTO dto) {
        Knowledge knowledge = knowledgeService.createKnowledge(dto, "admin");
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

    @DeleteMapping("/{id}/document/{attachmentId}")
    @Operation(summary = "删除知识文档（软删除）", description = "软删除知识对应的文档记录，并从ES中删除对应chunks/引用")
    public ApiResponse<Void> softDeleteKnowledgeDocument(
            @Parameter(description = "知识ID", required = true) @PathVariable Long id,
            @Parameter(description = "附件ID", required = true) @PathVariable Long attachmentId) {
        knowledgeService.softDeleteAttachment(id, attachmentId, "admin");
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
        
        // 获取附件信息并转换为下载URL格式
        List<Attachment> attachments = knowledgeService.getAttachmentsByKnowledgeId(id);
        List<Map<String, Object>> attachmentVOs = new ArrayList<>();
        
        if (attachments != null && !attachments.isEmpty()) {
            for (Attachment att : attachments) {
                Map<String, Object> attVO = new HashMap<>();
                attVO.put("id", att.getId());
                attVO.put("fileName", att.getFileName());
                // 将filePath改为下载URL格式，与/api/chat/stream接口保持一致
                attVO.put("filePath", "/api/knowledge/" + id + "/document/" + att.getId() + "/download");
                attVO.put("fileSize", att.getFileSize());
                attVO.put("fileType", att.getFileType());
                attVO.put("uploadTime", att.getUploadTime());
                attVO.put("downloadCount", att.getDownloadCount());
                attachmentVOs.add(attVO);
            }
        }
        
        // 构建返回结果
        Map<String, Object> result = new HashMap<>();
        result.put("id", knowledge.getId());
        result.put("name", knowledge.getName());
        result.put("description", knowledge.getDescription());
        result.put("parentId", knowledge.getParentId());
        result.put("nodeType", knowledge.getNodeType());
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
        result.put("attachments", attachmentVOs);
        
        return ApiResponse.success("获取知识详情成功", result);
    }
    
    @GetMapping
    @Operation(summary = "获取知识列表", description = "分页获取知识列表")
    public ApiResponse<IPage<KnowledgeVO>> getKnowledgeList(
            @Parameter(description = "页码", example = "1") @RequestParam(defaultValue = "1") int page,
            @Parameter(description = "每页大小", example = "10") @RequestParam(defaultValue = "10") int size) {
        javax.servlet.http.HttpServletRequest req = ((org.springframework.web.context.request.ServletRequestAttributes) org.springframework.web.context.request.RequestContextHolder.getRequestAttributes()).getRequest();
        String userId = resolveUserIdFromHeader(req);
        List<String> allowed = resolveAllowedWorkspaces(userId);
        IPage<KnowledgeVO> result = knowledgeService.getKnowledgeListFiltered(page, size, allowed);
        return ApiResponse.success("获取知识列表成功", result);
    }
    
    @GetMapping("/{parentId}/children")
    @Operation(summary = "获取子知识", description = "根据父知识ID分页获取直接子节点，parentId传null或0获取根节点")
    public ApiResponse<IPage<KnowledgeVO>> getChildren(
            @Parameter(description = "父知识ID", required = true, example = "1") @PathVariable Long parentId,
            @Parameter(description = "页码", example = "1") @RequestParam(defaultValue = "1") int page,
            @Parameter(description = "每页大小", example = "10") @RequestParam(defaultValue = "10") int size) {
        javax.servlet.http.HttpServletRequest req = ((org.springframework.web.context.request.ServletRequestAttributes) org.springframework.web.context.request.RequestContextHolder.getRequestAttributes()).getRequest();
        String userId = resolveUserIdFromHeader(req);
        List<String> allowed = resolveAllowedWorkspaces(userId);
        IPage<KnowledgeVO> result = knowledgeService.getChildrenFiltered(parentId == 0 ? null : parentId, page, size, allowed);
        return ApiResponse.success("获取子知识成功", result);
    }

    // 兼容旧接口：按类目获取知识 => 等价于获取父知识下子节点
    @GetMapping("/category/{categoryId}")
    @Operation(summary = "[兼容] 根据类目获取知识", description = "兼容旧接口：等价于 /api/knowledge/{parentId}/children")
    public ApiResponse<IPage<KnowledgeVO>> getKnowledgeByCategoryCompat(
            @Parameter(description = "父知识ID(原类目ID)", required = true, example = "1") @PathVariable Long categoryId,
            @Parameter(description = "页码", example = "1") @RequestParam(defaultValue = "1") int page,
            @Parameter(description = "每页大小", example = "10") @RequestParam(defaultValue = "10") int size) {
        IPage<KnowledgeVO> result = knowledgeService.getChildren(categoryId == 0 ? null : categoryId, page, size);
        return ApiResponse.success("获取子知识成功", result);
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

    @GetMapping("/{knowledgeId}/document/{attachmentId}/download")
    @Operation(summary = "下载知识文档", description = "根据附件ID下载对应文档")
    public ResponseEntity<byte[]> downloadAttachment(
            @Parameter(description = "知识ID", required = true) @PathVariable Long knowledgeId,
            @Parameter(description = "附件ID", required = true) @PathVariable Long attachmentId) {
        Attachment att = attachmentService.getById(attachmentId);
        if (att == null || !att.getKnowledgeId().equals(knowledgeId) || att.getDeleted() != null && att.getDeleted() == 1) {
            return ResponseEntity.notFound().build();
        }
        try {
            File file = new File(att.getFilePath());
            if (!file.exists()) {
                return ResponseEntity.notFound().build();
            }
            byte[] bytes;
            try (InputStream in = new FileInputStream(file)) {
                bytes = in.readAllBytes();
            }
            // 下载计数+1（忽略并发的轻微不一致）
            try {
                att.setDownloadCount(att.getDownloadCount() == null ? 1 : att.getDownloadCount() + 1);
                attachmentService.updateById(att);
            } catch (Exception ignore) {}
            String encoded = URLEncoder.encode(att.getFileName(), "UTF-8").replaceAll("\\+", "%20");
            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + encoded + "\"")
                    .contentType(MediaType.APPLICATION_OCTET_STREAM)
                    .contentLength(bytes.length)
                    .body(bytes);
        } catch (Exception e) {
            return ResponseEntity.status(500).build();
        }
    }
} 
