package com.knowledge.vo;

import lombok.Data;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 树形搜索结果VO
 */
@Data
public class TreeSearchResultVO {
    
    /**
     * 知识ID
     */
    private Long id;
    
    /**
     * 知识名称
     */
    private String name;
    
    /**
     * 知识描述
     */
    private String description;
    
    /**
     * 父节点ID
     */
    private Long parentId;
    
    /**
     * 节点类型
     */
    private String nodeType;
    
    /**
     * 标签列表
     */
    private List<String> tags;
    
    /**
     * 创建时间
     */
    private LocalDateTime createdTime;
    
    /**
     * 更新时间
     */
    private LocalDateTime updatedTime;
    
    /**
     * 完整路径（从根节点到当前节点的路径）
     */
    private List<PathNodeVO> fullPath;
    
    /**
     * 路径节点VO
     */
    @Data
    public static class PathNodeVO {
        /**
         * 节点ID
         */
        private Long id;
        
        /**
         * 节点名称
         */
        private String name;
        
        /**
         * 节点类型
         */
        private String nodeType;
        
        /**
         * 是否为当前匹配的节点
         */
        private Boolean isMatched;
        
        public PathNodeVO() {}
        
        public PathNodeVO(Long id, String name, String nodeType, Boolean isMatched) {
            this.id = id;
            this.name = name;
            this.nodeType = nodeType;
            this.isMatched = isMatched;
        }
    }
}
