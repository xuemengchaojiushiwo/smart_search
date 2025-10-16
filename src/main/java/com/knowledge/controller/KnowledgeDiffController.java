package com.knowledge.controller;

import com.knowledge.entity.KnowledgeDescriptionVersion;
import com.knowledge.service.DescriptionDiffService;
import com.knowledge.service.DiffSummaryService;
import com.knowledge.service.KnowledgeVersionService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/knowledge")
@RequiredArgsConstructor
public class KnowledgeDiffController {

    private final DescriptionDiffService descriptionDiffService;
    private final KnowledgeVersionService knowledgeVersionService;
    private final DiffSummaryService diffSummaryService;

    /**
     * 生成知识描述的差异高亮 HTML（仅新增/删除）。
     * 入参：旧版与新版描述（HTML 字符串），或后续可扩展为按 versionId 加载。
     * 返回：可直接渲染的 HTML 片段（含内联样式）。
     */
    @PostMapping(value = "/diff", consumes = MediaType.APPLICATION_JSON_VALUE, produces = MediaType.TEXT_HTML_VALUE)
    public String diffHtml(@RequestBody DiffRequest req) {
        String oldHtml = req.getOldHtml();
        String newHtml = req.getNewHtml();
        return descriptionDiffService.generateHtmlDiff(oldHtml, newHtml);
    }

    /**
     * 通过 knowledgeId + fromVersion/toVersion 直接生成对比。
     * 若指定版本不存在，则回退到当前知识描述；若两边均为空，返回空对象。
     * 返回包含AI总结和HTML对比结果的JSON响应。
     */
    @GetMapping(value = "/{knowledgeId}/diff", produces = MediaType.APPLICATION_JSON_VALUE)
    public DiffResponse diffByVersion(@PathVariable("knowledgeId") Long knowledgeId,
                                @RequestParam(value = "from", required = false) String fromVersion,
                                @RequestParam(value = "to", required = false) String toVersion) {
        String fromHtml = null;
        String toHtml = null;

        if (fromVersion != null && !fromVersion.isEmpty()) {
            fromHtml = knowledgeVersionService.findDescriptionByVersion(knowledgeId, fromVersion);
        }
        if (toVersion != null && !toVersion.isEmpty()) {
            toHtml = knowledgeVersionService.findDescriptionByVersion(knowledgeId, toVersion);
        }

        // 回退到当前描述
        if (fromHtml == null) {
            fromHtml = knowledgeVersionService.findCurrentDescription(knowledgeId);
        }
        if (toHtml == null) {
            toHtml = knowledgeVersionService.findCurrentDescription(knowledgeId);
        }

        DiffResponse response = new DiffResponse();
        response.setKnowledgeId(knowledgeId);
        response.setFromVersion(fromVersion);
        response.setToVersion(toVersion);

        if ((fromHtml == null || fromHtml.isEmpty()) && (toHtml == null || toHtml.isEmpty())) {
            response.setHtmlDiff("");
            response.setSummary("无法获取版本内容，请确认版本号是否正确。");
            return response;
        }

        // 生成HTML差异
        String safeFromHtml = fromHtml == null ? "" : fromHtml;
        String safeToHtml = toHtml == null ? "" : toHtml;
        String htmlDiff = descriptionDiffService.generateHtmlDiff(safeFromHtml, safeToHtml);
        response.setHtmlDiff(htmlDiff);
        
        // 获取AI总结
        String summary = diffSummaryService.getSummary(safeFromHtml, safeToHtml);
        response.setSummary(summary);
        
        return response;
    }
    
    /**
     * 通过 knowledgeId + fromVersion/toVersion 直接生成HTML对比。
     * 与JSON版本相同，但只返回HTML片段，方便前端直接嵌入iframe或div。
     */
    @GetMapping(value = "/{knowledgeId}/diff/html", produces = MediaType.TEXT_HTML_VALUE)
    public String diffByVersionHtml(@PathVariable("knowledgeId") Long knowledgeId,
                                @RequestParam(value = "from", required = false) String fromVersion,
                                @RequestParam(value = "to", required = false) String toVersion) {
        String fromHtml = null;
        String toHtml = null;

        if (fromVersion != null && !fromVersion.isEmpty()) {
            fromHtml = knowledgeVersionService.findDescriptionByVersion(knowledgeId, fromVersion);
        }
        if (toVersion != null && !toVersion.isEmpty()) {
            toHtml = knowledgeVersionService.findDescriptionByVersion(knowledgeId, toVersion);
        }

        // 回退到当前描述
        if (fromHtml == null) {
            fromHtml = knowledgeVersionService.findCurrentDescription(knowledgeId);
        }
        if (toHtml == null) {
            toHtml = knowledgeVersionService.findCurrentDescription(knowledgeId);
        }

        if ((fromHtml == null || fromHtml.isEmpty()) && (toHtml == null || toHtml.isEmpty())) {
            return "<p>无法获取版本内容，请确认版本号是否正确。</p>";
        }
        
        String safeFromHtml = fromHtml == null ? "" : fromHtml;
        String safeToHtml = toHtml == null ? "" : toHtml;
        return descriptionDiffService.generateHtmlDiff(safeFromHtml, safeToHtml);
    }
    
    /**
     * 获取知识的所有版本列表
     * @param knowledgeId 知识ID
     * @return 版本列表
     */
    @GetMapping("/{knowledgeId}/versions")
    public VersionListResponse getVersionList(@PathVariable("knowledgeId") Long knowledgeId) {
        List<KnowledgeDescriptionVersion> versions = knowledgeVersionService.getVersionList(knowledgeId);
        
        VersionListResponse response = new VersionListResponse();
        response.setKnowledgeId(knowledgeId);
        response.setVersions(versions);
        response.setTotal(versions.size());
        
        return response;
    }
    
    /**
     * 获取指定版本的详情
     * @param knowledgeId 知识ID
     * @param version 版本号
     * @return 版本详情
     */
    @GetMapping("/{knowledgeId}/versions/{version}")
    public VersionDetailResponse getVersionDetail(@PathVariable("knowledgeId") Long knowledgeId,
                                                   @PathVariable("version") String version) {
        KnowledgeDescriptionVersion versionEntity = knowledgeVersionService.getVersionByNumber(knowledgeId, version);
        
        VersionDetailResponse response = new VersionDetailResponse();
        if (versionEntity != null) {
            response.setId(versionEntity.getId());
            response.setKnowledgeId(versionEntity.getKnowledgeId());
            response.setVersion(versionEntity.getVersion());
            response.setContent(versionEntity.getContent());
            response.setEditor(versionEntity.getEditor());
            response.setEditorId(versionEntity.getEditorId());
            response.setCreatedAt(versionEntity.getCreatedAt());
            response.setCreatedBy(versionEntity.getCreatedBy());
        }
        
        return response;
    }

    @Data
    public static class DiffRequest {
        private String oldHtml;
        private String newHtml;
    }
    
    @Data
    public static class VersionListResponse {
        private Long knowledgeId;
        private List<KnowledgeDescriptionVersion> versions;
        private Integer total;
    }
    
    @Data
    public static class VersionDetailResponse {
        private Long id;
        private Long knowledgeId;
        private String version;
        private String content;
        private String editor;
        private Long editorId;
        private java.time.LocalDateTime createdAt;
        private String createdBy;
    }
    
    @Data
    public static class DiffResponse {
        private Long knowledgeId;
        private String fromVersion;
        private String toVersion;
        private String htmlDiff; // HTML格式的差异对比结果
        private String summary;  // AI生成的差异总结
    }
}


