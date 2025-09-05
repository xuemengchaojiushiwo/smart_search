package com.knowledge.dto;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class FeedbackTypeDTOTest {

    @Test
    void testFeedbackTypeDTO() {
        // 测试DTO构造和getter方法
        FeedbackTypeDTO dto = new FeedbackTypeDTO("test_code", "测试描述");
        
        assertEquals("test_code", dto.getCode());
        assertEquals("测试描述", dto.getDescription());
    }

    @Test
    void testFeedbackTypeDTOSetter() {
        // 测试setter方法
        FeedbackTypeDTO dto = new FeedbackTypeDTO("", "");
        
        dto.setCode("new_code");
        dto.setDescription("新描述");
        
        assertEquals("new_code", dto.getCode());
        assertEquals("新描述", dto.getDescription());
    }
}
