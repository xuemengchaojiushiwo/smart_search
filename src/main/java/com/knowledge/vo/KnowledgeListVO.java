package com.knowledge.vo;

import lombok.Data;
import io.swagger.v3.oas.annotations.media.Schema;
import java.time.LocalDateTime;

@Data
@Schema(name = "KnowledgeListVO", description = "知识列表简化返回体")
public class KnowledgeListVO {

    @Schema(description = "知识ID", example = "1001")
    private Long id;

    @Schema(description = "知识名称", example = "请假制度V1")
    private String name;

    @Schema(description = "父知识ID，根节点为null", example = "123")
    private Long parentId;

    @Schema(description = "节点类型：folder=类目，doc=条目/文档", allowableValues = {"folder", "doc"}, example = "doc")
    private String nodeType;

    @Schema(description = "更新时间", type = "string", format = "date-time")
    private LocalDateTime updatedTime;
    
    // 构造函数，从KnowledgeVO转换
    public static KnowledgeListVO fromKnowledgeVO(KnowledgeVO vo) {
        KnowledgeListVO listVO = new KnowledgeListVO();
        listVO.setId(vo.getId());
        listVO.setName(vo.getName());
        listVO.setParentId(vo.getParentId());
        listVO.setNodeType(vo.getNodeType());
        listVO.setUpdatedTime(vo.getUpdatedTime());
        return listVO;
    }
}
