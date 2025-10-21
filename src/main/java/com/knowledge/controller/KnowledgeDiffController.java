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
     * 通过 knowledgeId + fromVersion/toVersion 直接生成对比（从新表获取数据）。
     * 若指定版本不存在，则回退到当前知识描述；若两边均为空，返回空对象。
     * 返回包含AI总结和HTML对比结果的JSON响应。
     */
    @GetMapping(value = "/{knowledgeId}/diff", produces = MediaType.APPLICATION_JSON_VALUE)
    public DiffResponse diffByVersion(@PathVariable("knowledgeId") Long knowledgeId,
                                @RequestParam(value = "from", required = false) Integer fromVersionNumber,
                                @RequestParam(value = "to", required = false) Integer toVersionNumber) {
        String fromHtml = null;
        String toHtml = null;

        // 从新表获取版本数据
        if (fromVersionNumber != null) {
            KnowledgeHistoryVersion fromVersion = knowledgeHistoryVersionService.getVersion(knowledgeId, fromVersionNumber);
            if (fromVersion != null) {
                fromHtml = fromVersion.getDescription();
            }
        }
        if (toVersionNumber != null) {
            KnowledgeHistoryVersion toVersion = knowledgeHistoryVersionService.getVersion(knowledgeId, toVersionNumber);
            if (toVersion != null) {
                toHtml = toVersion.getDescription();
            }
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
        response.setFromVersion(fromVersionNumber != null ? fromVersionNumber.toString() : null);
        response.setToVersion(toVersionNumber != null ? toVersionNumber.toString() : null);

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
                        item.setCreatedTime(version.getCreatedTime());
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
    public static class DiffResponse {
        private Long knowledgeId;
        private String fromVersion;
        private String toVersion;
        private String htmlDiff; // HTML格式的差异对比结果
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
        private java.time.LocalDateTime createdTime;
    }
}


