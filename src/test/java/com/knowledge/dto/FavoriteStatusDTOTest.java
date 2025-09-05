package com.knowledge.dto;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.time.LocalDateTime;

class FavoriteStatusDTOTest {

    @Test
    void testFavoriteStatusDTO() {
        // 测试DTO构造和setter/getter方法
        FavoriteStatusDTO dto = new FavoriteStatusDTO();
        
        dto.setKnowledgeId(100L);
        dto.setUserId(1L);
        dto.setIsFavorited(true);
        dto.setFavoriteTime(LocalDateTime.now());
        dto.setFavoriteId(50L);
        
        assertEquals(100L, dto.getKnowledgeId());
        assertEquals(1L, dto.getUserId());
        assertTrue(dto.getIsFavorited());
        assertNotNull(dto.getFavoriteTime());
        assertEquals(50L, dto.getFavoriteId());
    }

    @Test
    void testFavoriteStatusDTONotFavorited() {
        // 测试未收藏状态
        FavoriteStatusDTO dto = new FavoriteStatusDTO();
        
        dto.setKnowledgeId(200L);
        dto.setUserId(2L);
        dto.setIsFavorited(false);
        dto.setFavoriteTime(null);
        dto.setFavoriteId(null);
        
        assertEquals(200L, dto.getKnowledgeId());
        assertEquals(2L, dto.getUserId());
        assertFalse(dto.getIsFavorited());
        assertNull(dto.getFavoriteTime());
        assertNull(dto.getFavoriteId());
    }

    @Test
    void testFavoriteStatusDTOWithNullValues() {
        // 测试空值处理
        FavoriteStatusDTO dto = new FavoriteStatusDTO();
        
        dto.setKnowledgeId(null);
        dto.setUserId(null);
        dto.setIsFavorited(null);
        
        assertNull(dto.getKnowledgeId());
        assertNull(dto.getUserId());
        assertNull(dto.getIsFavorited());
    }
}
