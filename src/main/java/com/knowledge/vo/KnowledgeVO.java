package com.knowledge.vo;

import lombok.Data;

import io.swagger.v3.oas.annotations.media.Schema;
import java.time.LocalDateTime;
import java.util.List;

@Data
@Schema(name = "KnowledgeVO", description = "知识详情/列表返回体")
public class KnowledgeVO {

    @Schema(description = "知识ID", example = "1001")
    private Long id;

    @Schema(description = "知识名称", example = "请假制度V1")
    private String name;

    @Schema(description = "描述/正文摘要", example = "这是知识的简要说明……")
    private String description;

    // 兼容字段：等同于 parentId
    @Schema(description = "兼容字段：等同于parentId", example = "123")
    private Long categoryId;

    @Schema(description = "父知识ID，根节点为null", example = "123")
    private Long parentId;

    @Schema(description = "节点类型：folder=类目，doc=条目/文档", allowableValues = {"folder", "doc"}, example = "doc")
    private String nodeType;

    @Schema(description = "标签列表", example = "[\"HR\",\"流程\"]")
    private List<String> tags;

    @Schema(description = "生效开始时间", type = "string", format = "date-time", example = "2025-01-01T00:00:00")
    private LocalDateTime effectiveStartTime;

    @Schema(description = "生效结束时间", type = "string", format = "date-time", example = "2025-12-31T23:59:59")
    private LocalDateTime effectiveEndTime;

    @Schema(description = "状态：1-生效，0-失效", example = "1")
    private Integer status;

    @Schema(description = "创建人", example = "admin")
    private String createdBy;

    @Schema(description = "创建时间", type = "string", format = "date-time")
    private LocalDateTime createdTime;

    @Schema(description = "更新人", example = "admin")
    private String updatedBy;

    @Schema(description = "更新时间", type = "string", format = "date-time")
    private LocalDateTime updatedTime;

    @Schema(description = "搜索次数", example = "12")
    private Integer searchCount;

    @Schema(description = "下载次数", example = "3")
    private Integer downloadCount;

    @Schema(description = "附件信息列表")
    private List<AttachmentVO> attachments;

    @Schema(description = "结构化表格数据(JSON)")
    private Object tableData;

    @Schema(description = "绑定的工作空间列表")
    private java.util.List<String> workspaces;
}
