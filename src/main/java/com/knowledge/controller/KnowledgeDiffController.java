package com.knowledge.controller;

import com.knowledge.entity.KnowledgeHistoryVersion;
import com.knowledge.service.DescriptionDiffService;
import com.knowledge.service.DiffSummaryService;
import com.knowledge.service.KnowledgeVersionService;
import com.knowledge.service.KnowledgeHistoryVersionService;
import com.knowledge.vo.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
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
    private final KnowledgeHistoryVersionService knowledgeHistoryVersionService;


    /**
     * 获取版本对比的AI总结（从新表获取数据）
     */
    @GetMapping(value = "/{knowledgeId}/diff/summary", produces = MediaType.APPLICATION_JSON_VALUE)
    @Operation(summary = "获取版本对比AI总结", description = "根据版本号获取两个版本的AI对比总结")
    public ApiResponse<DiffSummaryResponse> getDiffSummary(@PathVariable("knowledgeId") Long knowledgeId,
                                                          @RequestParam(value = "from", required = false) Integer fromVersionNumber,
                                                          @RequestParam(value = "to", required = false) Integer toVersionNumber) {
        try {
            String fromHtml = getVersionDescription(knowledgeId, fromVersionNumber);
            String toHtml = getVersionDescription(knowledgeId, toVersionNumber);

            DiffSummaryResponse response = new DiffSummaryResponse();
            response.setKnowledgeId(knowledgeId);
            response.setFromVersion(fromVersionNumber != null ? fromVersionNumber.toString() : null);
            response.setToVersion(toVersionNumber != null ? toVersionNumber.toString() : null);

            if ((fromHtml == null || fromHtml.isEmpty()) && (toHtml == null || toHtml.isEmpty())) {
                response.setSummary("无法获取版本内容，请确认版本号是否正确。");
                return ApiResponse.success("获取AI总结成功", response);
            }

            // 获取AI总结
            String safeFromHtml = fromHtml == null ? "" : fromHtml;
            String safeToHtml = toHtml == null ? "" : toHtml;
            String summary = diffSummaryService.getSummary(safeFromHtml, safeToHtml);
            response.setSummary(summary);
            
            return ApiResponse.success("获取AI总结成功", response);
        } catch (Exception e) {
            return ApiResponse.error("获取AI总结失败: " + e.getMessage());
        }
    }

    /**
     * 获取版本对比的HTML差异（从新表获取数据）
     */
    @GetMapping(value = "/{knowledgeId}/diff/html", produces = MediaType.TEXT_HTML_VALUE)
    @Operation(summary = "获取版本对比HTML差异", description = "根据版本号获取两个版本的HTML差异对比")
    public String getDiffHtml(@PathVariable("knowledgeId") Long knowledgeId,
                             @RequestParam(value = "from", required = false) Integer fromVersionNumber,
                             @RequestParam(value = "to", required = false) Integer toVersionNumber) {
        try {
            String fromHtml = getVersionDescription(knowledgeId, fromVersionNumber);
            String toHtml = getVersionDescription(knowledgeId, toVersionNumber);

            if ((fromHtml == null || fromHtml.isEmpty()) && (toHtml == null || toHtml.isEmpty())) {
                return "<p>无法获取版本内容，请确认版本号是否正确。</p>";
            }

            // 生成HTML差异
            String safeFromHtml = fromHtml == null ? "" : fromHtml;
            String safeToHtml = toHtml == null ? "" : toHtml;
            return descriptionDiffService.generateHtmlDiff(safeFromHtml, safeToHtml);
        } catch (Exception e) {
            return "<p>生成HTML差异失败: " + e.getMessage() + "</p>";
        }
    }

    /**
     * 获取版本描述内容的辅助方法
     */
    private String getVersionDescription(Long knowledgeId, Integer versionNumber) {
        if (versionNumber != null) {
            KnowledgeHistoryVersion version = knowledgeHistoryVersionService.getVersion(knowledgeId, versionNumber);
            if (version != null) {
                return version.getDescription();
            }
        }
        // 回退到当前描述
        return knowledgeVersionService.findCurrentDescription(knowledgeId);
    }
    
    /**
     * 获取知识的所有历史版本列表
     */
    @GetMapping("/{knowledgeId}/versions")
    @Operation(summary = "获取知识历史版本列表", description = "根据知识ID获取所有历史版本的基本信息")
    public ApiResponse<List<VersionListItem>> getKnowledgeVersions(
            @Parameter(description = "知识ID", required = true, example = "1") 
            @PathVariable Long knowledgeId) {
        
        try {
            List<KnowledgeHistoryVersion> versions = knowledgeHistoryVersionService.getKnowledgeVersions(knowledgeId);
            
            // 转换为简化的版本列表
            List<VersionListItem> versionList = versions.stream()
                    .map(version -> {
                        VersionListItem item = new VersionListItem();
                        item.setId(version.getId());
                        item.setVersionNumber(version.getVersionNumber());
                        item.setVersionName(version.getVersionName());
                        item.setName(version.getName());
                        item.setChangeType(version.getChangeType());
                        item.setChangeReason(version.getChangeReason());
                        item.setCreatedBy(version.getCreatedBy());
                        // 直接设置格式化后的时间字符串
                        if (version.getCreatedTime() != null) {
                            item.setCreatedTime(version.getCreatedTime().format(java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
                        } else {
                            item.setCreatedTime(null);
                        }
                        return item;
                    })
                    .collect(java.util.stream.Collectors.toList());
            
            return ApiResponse.success("获取版本列表成功", versionList);
        } catch (Exception e) {
            return ApiResponse.error("获取版本列表失败: " + e.getMessage());
        }
    }
    
    /**
     * 获取指定版本的详情（从新表获取）
     * @param knowledgeId 知识ID
     * @param versionNumber 版本号
     * @return 版本详情
     */
    @GetMapping("/{knowledgeId}/versions/{versionNumber}")
    public ApiResponse<KnowledgeHistoryVersion> getVersionDetail(@PathVariable("knowledgeId") Long knowledgeId,
                                                                 @PathVariable("versionNumber") Integer versionNumber) {
        try {
            KnowledgeHistoryVersion version = knowledgeHistoryVersionService.getVersion(knowledgeId, versionNumber);
            if (version == null) {
                return ApiResponse.error("指定版本的知识不存在");
            }
            return ApiResponse.success("获取版本详情成功", version);
        } catch (Exception e) {
            return ApiResponse.error("获取版本详情失败: " + e.getMessage());
        }
    }

    @Data
    public static class DiffRequest {
        private String oldHtml;
        private String newHtml;
    }
    
    @Data
    public static class DiffSummaryResponse {
        private Long knowledgeId;
        private String fromVersion;
        private String toVersion;
        private String summary;  // AI生成的差异总结
    }
    
    /**
     * 版本列表项
     */
    @Data
    public static class VersionListItem {
        private Long id;
        private Integer versionNumber;
        private String versionName;
        private String name;
        private String changeType;
        private String changeReason;
        private String createdBy;
        
        private String createdTime; // 直接存储格式化后的时间字符串
        
        // Getters and Setters
        public Long getId() { return id; }
        public void setId(Long id) { this.id = id; }
        
        public Integer getVersionNumber() { return versionNumber; }
        public void setVersionNumber(Integer versionNumber) { this.versionNumber = versionNumber; }
        
        public String getVersionName() { return versionName; }
        public void setVersionName(String versionName) { this.versionName = versionName; }
        
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        
        public String getChangeType() { return changeType; }
        public void setChangeType(String changeType) { this.changeType = changeType; }
        
        public String getChangeReason() { return changeReason; }
        public void setChangeReason(String changeReason) { this.changeReason = changeReason; }
        
        public String getCreatedBy() { return createdBy; }
        public void setCreatedBy(String createdBy) { this.createdBy = createdBy; }
        
        public String getCreatedTime() { return createdTime; }
        public void setCreatedTime(String createdTime) { this.createdTime = createdTime; }
    }
}


