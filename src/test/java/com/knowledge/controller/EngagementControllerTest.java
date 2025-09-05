package com.knowledge.controller;

import com.knowledge.dto.FeedbackTypeDTO;
import com.knowledge.enums.FeedbackType;
import com.knowledge.vo.ApiResponse;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.result.MockMvcResultMatchers;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;

@WebMvcTest(EngagementController.class)
class EngagementControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private com.knowledge.service.EngagementService engagementService;

    @Test
    void testGetFeedbackTypes() throws Exception {
        // 执行测试
        mockMvc.perform(MockMvcRequestBuilders.get("/api/engagement/feedback/types"))
                .andDo(print())
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.code").value(200))
                .andExpect(MockMvcResultMatchers.jsonPath("$.data").isArray())
                .andExpect(MockMvcResultMatchers.jsonPath("$.data.length()").value(3))
                .andExpect(MockMvcResultMatchers.jsonPath("$.data[0].code").value("out_of_date"))
                .andExpect(MockMvcResultMatchers.jsonPath("$.data[0].description").value("内容过时"))
                .andExpect(MockMvcResultMatchers.jsonPath("$.data[1].code").value("unclear"))
                .andExpect(MockMvcResultMatchers.jsonPath("$.data[1].description").value("内容不清晰"))
                .andExpect(MockMvcResultMatchers.jsonPath("$.data[2].code").value("not_relevant"))
                .andExpect(MockMvcResultMatchers.jsonPath("$.data[2].description").value("内容不相关"));
    }

    @Test
    void testFeedbackTypeEnum() {
        // 测试枚举值
        assertEquals(3, FeedbackType.values().length);
        
        // 测试fromCode方法
        assertEquals(FeedbackType.OUT_OF_DATE, FeedbackType.fromCode("out_of_date"));
        assertEquals(FeedbackType.UNCLEAR, FeedbackType.fromCode("unclear"));
        assertEquals(FeedbackType.NOT_RELEVANT, FeedbackType.fromCode("not_relevant"));
        assertNull(FeedbackType.fromCode("invalid"));
        
        // 测试getter方法
        assertEquals("out_of_date", FeedbackType.OUT_OF_DATE.getCode());
        assertEquals("内容过时", FeedbackType.OUT_OF_DATE.getDescription());
    }

    @Test
    void testFeedbackTypeDTO() {
        // 测试DTO构造和getter方法
        FeedbackTypeDTO dto = new FeedbackTypeDTO("test_code", "测试描述");
        assertEquals("test_code", dto.getCode());
        assertEquals("测试描述", dto.getDescription());
    }
}
