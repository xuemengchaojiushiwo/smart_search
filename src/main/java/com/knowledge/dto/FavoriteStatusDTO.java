package com.knowledge.dto;

import lombok.Data;

import java.time.LocalDateTime;

/**
 * 收藏状态DTO
 */
@Data
public class FavoriteStatusDTO {
    private Long knowledgeId; // 知识ID
    private Long userId; // 用户ID
    private Boolean isFavorited; // 是否已收藏
    private LocalDateTime favoriteTime; // 收藏时间（如果已收藏）
    private Long favoriteId; // 收藏记录ID（如果已收藏）
}
