package com.knowledge.service;

import com.knowledge.dto.KnowledgeDTO;
import com.knowledge.entity.Knowledge;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@Transactional
class KnowledgeWorkspaceBindingTest {

    @Autowired
    private KnowledgeService knowledgeService;

    @Autowired
    private KnowledgeWorkspaceService knowledgeWorkspaceService;

    @Test
    void createKnowledgeWithWorkspaces() {
        KnowledgeDTO dto = new KnowledgeDTO();
        dto.setName("多Workspace绑定");
        dto.setDescription("测试多workspace绑定");
        dto.setNodeType("doc");
        dto.setParentId(0L);
        dto.setWorkspaces(Arrays.asList("WPB", "IWS"));

        Knowledge k = knowledgeService.createKnowledge(dto, "admin");
        assertNotNull(k.getId());

        List<String> ws = knowledgeWorkspaceService.listWorkspaces(k.getId());
        assertTrue(ws.contains("WPB"));
        assertTrue(ws.contains("IWS"));
    }
}


