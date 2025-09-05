package com.knowledge.dto;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

class UserFavoriteDTOTest {

    @Test
    void testUserFavoriteDTO() {
        // 测试DTO构造和setter/getter方法
        UserFavoriteDTO dto = new UserFavoriteDTO();
        
        dto.setId(1L);
        dto.setKnowledgeId(100L);
        dto.setKnowledgeName("测试知识");
        dto.setKnowledgeDescription("这是一个测试知识");
        dto.setNodeType("doc");
        dto.setTags(Arrays.asList("测试", "Java"));
        dto.setCreatedBy("admin");
        dto.setKnowledgeCreatedTime(LocalDateTime.now());
        dto.setSearchCount(10);
        dto.setDownloadCount(5);
        dto.setFavoriteTime(LocalDateTime.now());
        
        assertEquals(1L, dto.getId());
        assertEquals(100L, dto.getKnowledgeId());
        assertEquals("测试知识", dto.getKnowledgeName());
        assertEquals("这是一个测试知识", dto.getKnowledgeDescription());
        assertEquals("doc", dto.getNodeType());
        assertEquals(2, dto.getTags().size());
        assertEquals("admin", dto.getCreatedBy());
        assertEquals(10, dto.getSearchCount());
        assertEquals(5, dto.getDownloadCount());
        assertNotNull(dto.getKnowledgeCreatedTime());
        assertNotNull(dto.getFavoriteTime());
    }

    @Test
    void testUserFavoriteDTOWithNullValues() {
        // 测试空值处理
        UserFavoriteDTO dto = new UserFavoriteDTO();
        
        dto.setId(null);
        dto.setKnowledgeId(null);
        dto.setKnowledgeName(null);
        dto.setTags(null);
        
        assertNull(dto.getId());
        assertNull(dto.getKnowledgeId());
        assertNull(dto.getKnowledgeName());
        assertNull(dto.getTags());
    }
}
