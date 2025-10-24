package com.knowledge.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.knowledge.dto.KnowledgeDTO;
import com.knowledge.entity.Attachment;
import com.knowledge.entity.Knowledge;
import com.knowledge.service.KnowledgeService;
import com.knowledge.util.SecurityUtils;
import com.knowledge.vo.ApiResponse;
import com.knowledge.entity.User;
import com.knowledge.vo.KnowledgeVO;
import com.knowledge.vo.KnowledgeListVO;
import com.knowledge.vo.TreeSearchResultVO;
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
import java.io.ByteArrayOutputStream;
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
    private com.knowledge.service.UserService userService;


    /**
     * 解析工作空间列表
     * @param userId 用户ID或用户名
     * @param workspace 前端传入的工作空间参数，如果为null则使用用户默认工作空间
     * @return 工作空间列表
     */
    private List<String> resolveWorkspaces(String userId, String workspace) {
        // 如果前端指定了工作空间，直接使用
        if (workspace != null && !workspace.trim().isEmpty()) {
            List<String> list = new ArrayList<>();
            list.add(workspace.trim());
            return list;
        }
        
        // 否则使用用户默认工作空间
        try {
            if (userId == null) return null;
            
            User user = null;
            // 先尝试作为用户名查找（因为resolveUserIdFromHeader返回的是用户名）
            user = userService.findByUsername(userId);
            
            if (user == null) {
                // 如果用户名查找失败，尝试作为用户ID解析
                try {
                    Long uid = Long.valueOf(userId);
                    user = userService.getById(uid);
                } catch (Exception ignore) {
                    // 解析失败，保持user为null
                }
            }
            
            if (user != null) {
                return userService.getAllowedWorkspaces(user.getId());
            }
        } catch (Exception e) {
            log.warn("获取用户工作空间失败: userId={}, error={}", userId, e.getMessage());
        }
        return null;
    }
    
    private String resolveWorkspaceString(String userId, String workspace) {
        // 如果前端指定了工作空间，直接使用
        if (workspace != null && !workspace.trim().isEmpty()) {
            return workspace.trim();
        }
        
        // 否则使用用户默认工作空间字符串
        try {
            if (userId == null) return null;
            
            User user = null;
            // 先尝试作为用户名查找（因为resolveUserIdFromHeader返回的是用户名）
            user = userService.findByUsername(userId);
            
            if (user == null) {
                // 如果用户名查找失败，尝试作为用户ID解析
                try {
                    Long uid = Long.valueOf(userId);
                    user = userService.getById(uid);
                } catch (Exception ignore) {
                    // 解析失败，保持user为null
                }
            }
            
            if (user != null && user.getWorkspace() != null && !user.getWorkspace().trim().isEmpty()) {
                return user.getWorkspace().trim();
            }
        } catch (Exception e) {
            log.warn("获取用户工作空间失败: userId={}, error={}", userId, e.getMessage());
        }
        return null;
    }

    // 从JWT认证获取用户ID
    private String resolveUserIdFromHeader(javax.servlet.http.HttpServletRequest request) {
        // 从JWT认证中获取当前用户
        String currentUser = SecurityUtils.getCurrentUsername();
        if (currentUser != null && !currentUser.isEmpty()) {
            return currentUser;
        }
        
        // 兼容旧的头信息
        String uid = request.getHeader("X-User-Id");
        if (uid != null && !uid.isEmpty()) return uid;
        return null;
    }
    
    @PostMapping
    @Operation(summary = "创建知识", description = "创建新的知识条目")
    public ApiResponse<Knowledge> createKnowledge(
            @Parameter(description = "知识信息", required = true) @Valid @RequestBody KnowledgeDTO dto,
            @Parameter(description = "工作空间，不传则默认为ALL", example = "WPB") @RequestParam(required = false) String workspace) {
        
        // 检查当前用户是否为admin
        String currentUsername = SecurityUtils.getCurrentUsername();
        if (currentUsername == null) {
            return ApiResponse.error("未登录");
        }
        
        User currentUser = userService.findByUsername(currentUsername);
        if (currentUser == null || !"Admin".equals(currentUser.getSystemRole())) {
            return ApiResponse.error("权限不足，只有admin可以创建知识");
        }
        
        // 设置默认工作空间为ALL
        if (workspace == null || workspace.trim().isEmpty()) {
            workspace = "ALL";
        }
        
        Knowledge knowledge = knowledgeService.createKnowledge(dto, currentUsername, workspace);
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
        result.put("tableData", knowledge.getTableData()); // 添加表格数据字段
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
    @Operation(summary = "获取知识列表", description = "分页获取知识列表，只返回必要的ID和名称等基础信息，默认只返回顶层目录")
    public ApiResponse<IPage<KnowledgeListVO>> getKnowledgeList(
            @Parameter(description = "页码", example = "1") @RequestParam(defaultValue = "1") int page,
            @Parameter(description = "每页大小", example = "10") @RequestParam(defaultValue = "10") int size,
            @Parameter(description = "节点类型，可选值：folder/doc", example = "folder") @RequestParam(required = false) String nodeType,
            @Parameter(description = "工作空间，不传则使用用户默认工作空间", example = "WPB") @RequestParam(required = false) String workspace) {
        org.springframework.web.context.request.ServletRequestAttributes attributes = 
            (org.springframework.web.context.request.ServletRequestAttributes) org.springframework.web.context.request.RequestContextHolder.getRequestAttributes();
        javax.servlet.http.HttpServletRequest req = attributes != null ? attributes.getRequest() : null;
        String userId = resolveUserIdFromHeader(req);
        
        // 检查当前用户是否为admin
        boolean isAdmin = false;
        if (userId != null) {
            try {
                User user = userService.findByUsername(userId);
                if (user == null) {
                    // 如果用户名查找失败，尝试作为用户ID解析
                    try {
                        Long uid = Long.valueOf(userId);
                        user = userService.getById(uid);
                    } catch (Exception ignore) {
                        // 解析失败，保持user为null
                    }
                }
                if (user != null && "Admin".equals(user.getSystemRole())) {
                    isAdmin = true;
                }
            } catch (Exception e) {
                log.warn("检查用户角色失败: userId={}, error={}", userId, e.getMessage());
            }
        }
        
        // 解析工作空间：admin用户不受工作空间限制
        String workspaceString = null;
        if (!isAdmin) {
            workspaceString = resolveWorkspaceString(userId, workspace);
            // 如果用户没有工作空间权限，传递空字符串而不是null
            if (workspaceString == null) {
                workspaceString = "";
            }
        }
        
        // 修改为只获取顶层目录（parentId=null或0的记录）
        // 如果指定了nodeType，则按节点类型过滤
        IPage<KnowledgeVO> result = knowledgeService.getChildrenFilteredByWorkspaceString(null, page, size, workspaceString, nodeType);
        
        // 转换为简化版的KnowledgeListVO
        IPage<KnowledgeListVO> simplifiedResult = result.convert(KnowledgeListVO::fromKnowledgeVO);
        return ApiResponse.success("获取知识列表成功", simplifiedResult);
    }
    
    @GetMapping("/{parentId}/children")
    @Operation(summary = "获取子知识", description = "根据父知识ID分页获取直接子节点，parentId传null或0获取根节点，只返回必要的ID和名称等基础信息")
    public ApiResponse<IPage<KnowledgeListVO>> getChildren(
            @Parameter(description = "父知识ID", required = true, example = "1") @PathVariable Long parentId,
            @Parameter(description = "页码", example = "1") @RequestParam(defaultValue = "1") int page,
            @Parameter(description = "每页大小", example = "10") @RequestParam(defaultValue = "10") int size,
            @Parameter(description = "节点类型，可选值：folder/doc", example = "folder") @RequestParam(required = false) String nodeType,
            @Parameter(description = "工作空间，不传则使用用户默认工作空间", example = "WPB") @RequestParam(required = false) String workspace) {
        org.springframework.web.context.request.ServletRequestAttributes attributes = 
            (org.springframework.web.context.request.ServletRequestAttributes) org.springframework.web.context.request.RequestContextHolder.getRequestAttributes();
        javax.servlet.http.HttpServletRequest req = attributes != null ? attributes.getRequest() : null;
        String userId = resolveUserIdFromHeader(req);
        
        // 检查当前用户是否为admin
        boolean isAdmin = false;
        if (userId != null) {
            try {
                User user = userService.findByUsername(userId);
                if (user == null) {
                    // 如果用户名查找失败，尝试作为用户ID解析
                    try {
                        Long uid = Long.valueOf(userId);
                        user = userService.getById(uid);
                    } catch (Exception ignore) {
                        // 解析失败，保持user为null
                    }
                }
                if (user != null && "Admin".equals(user.getSystemRole())) {
                    isAdmin = true;
                }
            } catch (Exception e) {
                log.warn("检查用户角色失败: userId={}, error={}", userId, e.getMessage());
            }
        }
        
        // 解析工作空间：admin用户不受工作空间限制
        List<String> allowed = null;
        if (!isAdmin) {
            allowed = resolveWorkspaces(userId, workspace);
        }
        
        // 添加调试日志
        System.out.println("getChildren - parentId: " + parentId + ", userId: " + userId + ", isAdmin: " + isAdmin + ", allowed: " + allowed + ", nodeType: " + nodeType + ", workspace: " + workspace);
        
        // 如果nodeType为null，则不过滤节点类型，返回所有类型的子节点
        IPage<KnowledgeVO> result = knowledgeService.getChildrenFiltered(parentId == 0 ? null : parentId, page, size, allowed, nodeType);
        
        System.out.println("getChildren - result total: " + result.getTotal() + ", records: " + result.getRecords().size());
        
        // 转换为简化版的KnowledgeListVO
        IPage<KnowledgeListVO> simplifiedResult = result.convert(KnowledgeListVO::fromKnowledgeVO);
        return ApiResponse.success("获取子知识成功", simplifiedResult);
    }

    // 兼容旧接口：按类目获取知识 => 等价于获取父知识下子节点
    @GetMapping("/category/{categoryId}")
    @Operation(summary = "[兼容] 根据类目获取知识", description = "兼容旧接口：等价于 /api/knowledge/{parentId}/children，只返回必要的ID和名称等基础信息")
    public ApiResponse<IPage<KnowledgeListVO>> getKnowledgeByCategoryCompat(
            @Parameter(description = "父知识ID(原类目ID)", required = true, example = "1") @PathVariable Long categoryId,
            @Parameter(description = "页码", example = "1") @RequestParam(defaultValue = "1") int page,
            @Parameter(description = "每页大小", example = "10") @RequestParam(defaultValue = "10") int size,
            @Parameter(description = "节点类型，可选值：folder/doc", example = "folder") @RequestParam(required = false) String nodeType,
            @Parameter(description = "工作空间，不传则使用用户默认工作空间", example = "WPB") @RequestParam(required = false) String workspace) {
        org.springframework.web.context.request.ServletRequestAttributes attributes = 
            (org.springframework.web.context.request.ServletRequestAttributes) org.springframework.web.context.request.RequestContextHolder.getRequestAttributes();
        javax.servlet.http.HttpServletRequest req = attributes != null ? attributes.getRequest() : null;
        String userId = resolveUserIdFromHeader(req);
        List<String> allowed = resolveWorkspaces(userId, workspace);
        
        IPage<KnowledgeVO> result = knowledgeService.getChildrenFiltered(categoryId == 0 ? null : categoryId, page, size, allowed, nodeType);
        
        // 转换为简化版的KnowledgeListVO
        IPage<KnowledgeListVO> simplifiedResult = result.convert(KnowledgeListVO::fromKnowledgeVO);
        return ApiResponse.success("获取子知识成功", simplifiedResult);
    }

    @GetMapping("/tree/search")
    @Operation(summary = "树形搜索", description = "根据节点类型和知识名称模糊查询，返回匹配的节点及其完整路径")
    public ApiResponse<List<TreeSearchResultVO>> searchTree(
            @Parameter(description = "搜索关键词", example = "测试") @RequestParam String keyword,
            @Parameter(description = "节点类型，可选值：folder/doc", example = "folder") @RequestParam(required = false) String nodeType,
            @Parameter(description = "工作空间，不传则使用用户默认工作空间", example = "WPB") @RequestParam(required = false) String workspace,
            @Parameter(description = "最大返回数量", example = "50") @RequestParam(defaultValue = "50") int limit) {
        
        org.springframework.web.context.request.ServletRequestAttributes attributes = 
            (org.springframework.web.context.request.ServletRequestAttributes) org.springframework.web.context.request.RequestContextHolder.getRequestAttributes();
        javax.servlet.http.HttpServletRequest req = attributes != null ? attributes.getRequest() : null;
        String userId = resolveUserIdFromHeader(req);
        List<String> allowed = resolveWorkspaces(userId, workspace);
        
        List<TreeSearchResultVO> results = knowledgeService.searchTree(keyword, nodeType, allowed, limit);
        return ApiResponse.success("树形搜索成功", results);
    }
    
    @GetMapping("/popular")
    @Operation(summary = "获取热门知识", description = "获取热门知识列表")
    public ApiResponse<List<KnowledgeVO>> getPopularKnowledge(
            @Parameter(description = "返回数量", example = "10") @RequestParam(defaultValue = "10") int limit,
            @Parameter(description = "工作空间，不传则使用用户默认工作空间", example = "WPB") @RequestParam(required = false) String workspace) {
        org.springframework.web.context.request.ServletRequestAttributes attributes = 
            (org.springframework.web.context.request.ServletRequestAttributes) org.springframework.web.context.request.RequestContextHolder.getRequestAttributes();
        javax.servlet.http.HttpServletRequest req = attributes != null ? attributes.getRequest() : null;
        String userId = resolveUserIdFromHeader(req);
        String workspaceString = resolveWorkspaceString(userId, workspace);
        // 如果用户没有工作空间权限，传递空字符串而不是null
        if (workspaceString == null) {
            workspaceString = "";
        }
        
        List<KnowledgeVO> result = knowledgeService.getPopularKnowledgeByWorkspaceString(limit, workspaceString);
        return ApiResponse.success("获取热门知识成功", result);
    }
    
    @GetMapping("/latest")
    @Operation(summary = "获取最新知识", description = "获取最新知识列表")
    public ApiResponse<List<KnowledgeVO>> getLatestKnowledge(
            @Parameter(description = "返回数量", example = "10") @RequestParam(defaultValue = "10") int limit,
            @Parameter(description = "工作空间，不传则使用用户默认工作空间", example = "WPB") @RequestParam(required = false) String workspace) {
        org.springframework.web.context.request.ServletRequestAttributes attributes = 
            (org.springframework.web.context.request.ServletRequestAttributes) org.springframework.web.context.request.RequestContextHolder.getRequestAttributes();
        javax.servlet.http.HttpServletRequest req = attributes != null ? attributes.getRequest() : null;
        String userId = resolveUserIdFromHeader(req);
        String workspaceString = resolveWorkspaceString(userId, workspace);
        // 如果用户没有工作空间权限，传递空字符串而不是null
        if (workspaceString == null) {
            workspaceString = "";
        }
        
        List<KnowledgeVO> result = knowledgeService.getLatestKnowledgeByWorkspaceString(limit, workspaceString);
        return ApiResponse.success("获取最新知识成功", result);
    }
    
    @GetMapping("/hot-downloads")
    @Operation(summary = "获取最热资料", description = "根据下载数量倒序获取最热资料列表")
    public ApiResponse<List<KnowledgeVO>> getHotDownloads(
            @Parameter(description = "返回数量", example = "10") @RequestParam(defaultValue = "10") int limit,
            @Parameter(description = "工作空间，不传则使用用户默认工作空间", example = "WPB") @RequestParam(required = false) String workspace) {
        org.springframework.web.context.request.ServletRequestAttributes attributes = 
            (org.springframework.web.context.request.ServletRequestAttributes) org.springframework.web.context.request.RequestContextHolder.getRequestAttributes();
        javax.servlet.http.HttpServletRequest req = attributes != null ? attributes.getRequest() : null;
        String userId = resolveUserIdFromHeader(req);
        String workspaceString = resolveWorkspaceString(userId, workspace);
        // 如果用户没有工作空间权限，传递空字符串而不是null
        if (workspaceString == null) {
            workspaceString = "";
        }
        
        List<KnowledgeVO> result = knowledgeService.getHotDownloadsByWorkspaceString(limit, workspaceString);
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
                ByteArrayOutputStream buffer = new ByteArrayOutputStream();
                byte[] data = new byte[1024];
                int nRead;
                while ((nRead = in.read(data, 0, data.length)) != -1) {
                    buffer.write(data, 0, nRead);
                }
                bytes = buffer.toByteArray();
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
