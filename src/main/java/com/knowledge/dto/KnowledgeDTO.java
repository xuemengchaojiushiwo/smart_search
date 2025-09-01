package com.knowledge.dto;

import lombok.Data;

import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotBlank;
import java.time.LocalDateTime;
import java.util.List;

@Data
@Schema(name = "KnowledgeDTO", description = "知识创建/更新请求体")
public class KnowledgeDTO {

    @NotBlank(message = "知识名称不能为空")
    @Schema(description = "知识名称", required = true, example = "请假制度V1")
    private String name;

    @Schema(description = "描述/正文摘要", example = "这是知识的简要说明……")
    private String description;

    @Schema(description = "父知识ID，根节点为null；当nodeType=doc时必填，且父节点必须为folder", example = "123")
    private Long parentId; // 父知识ID

    @Schema(description = "节点类型：folder=类目(可含内容)，doc=条目/文档", allowableValues = {"folder", "doc"}, example = "doc")
    private String nodeType; // folder/doc

    @Schema(description = "标签列表", example = "[\"HR\",\"流程\"]")
    private List<String> tags;

    // 结构化表格数据：{columns:[{name,type}], rows:[...]}
    @Schema(description = "结构化表格数据(JSON)", example = "{\"columns\":[{\"name\":\"类型\",\"type\":\"string\"}],\"rows\":[[\"带薪\"]]}")
    private Object tableData;

    @Schema(description = "生效开始时间", type = "string", format = "date-time", example = "2025-01-01T00:00:00")
    private LocalDateTime effectiveStartTime;

    @Schema(description = "生效结束时间", type = "string", format = "date-time", example = "2025-12-31T23:59:59")
    private LocalDateTime effectiveEndTime;

    @Schema(description = "本次变更原因(用于审计/版本记录)", example = "新增假期类型")
    private String changeReason;

    @Schema(description = "绑定的工作空间列表(多选)", example = "[\"WPB\",\"IWS\"]")
    private java.util.List<String> workspaces;
}
