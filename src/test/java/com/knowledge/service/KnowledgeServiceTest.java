package com.knowledge.service;

import com.knowledge.dto.KnowledgeDTO;
import com.knowledge.entity.Knowledge;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.util.Arrays;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@Transactional
class KnowledgeServiceTest {

    @Autowired
    private KnowledgeService knowledgeService;

    @Test
    void testCreateKnowledge() {
        // 准备测试数据
        KnowledgeDTO dto = new KnowledgeDTO();
        dto.setName("测试知识");
        dto.setDescription("这是一个测试知识");
        dto.setParentId(0L); // 放在根下
        dto.setNodeType("doc");
        dto.setTags(java.util.Arrays.asList("测试", "Java"));
        
        // 执行测试
        Knowledge knowledge = knowledgeService.createKnowledge(dto, "admin");
        
        // 验证结果
        assertNotNull(knowledge);
        assertNotNull(knowledge.getId());
        assertEquals("测试知识", knowledge.getName());
        assertEquals("admin", knowledge.getCreatedBy());
        assertEquals(1, knowledge.getStatus());
        assertEquals(0, knowledge.getSearchCount());
        assertEquals(0, knowledge.getDownloadCount());
    }

    @Test
    void testGetKnowledgeList() {
        // 执行测试
        com.baomidou.mybatisplus.core.metadata.IPage<com.knowledge.vo.KnowledgeVO> result = knowledgeService.getKnowledgeList(1, 10);
        
        // 验证结果
        assertNotNull(result);
        assertTrue(result.getTotal() > 0);
        assertFalse(result.getRecords().isEmpty());
    }

    @Test
    void testGetPopularKnowledge() {
        // 执行测试
        java.util.List<com.knowledge.vo.KnowledgeVO> result = knowledgeService.getPopularKnowledge(5);
        
        // 验证结果
        assertNotNull(result);
        assertFalse(result.isEmpty());
    }
} 