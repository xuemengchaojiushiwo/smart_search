package com.knowledge.dto;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 用户收藏DTO
 */
@Data
public class UserFavoriteDTO {
    private Long id; // 收藏记录ID
    private Long knowledgeId; // 知识ID
    private String knowledgeName; // 知识名称
    private String knowledgeDescription; // 知识描述
    private String nodeType; // 节点类型
    private List<String> tags; // 标签
    private String createdBy; // 知识创建者
    private LocalDateTime knowledgeCreatedTime; // 知识创建时间
    private Integer searchCount; // 搜索次数
    private Integer downloadCount; // 下载次数
    private LocalDateTime favoriteTime; // 收藏时间
}
