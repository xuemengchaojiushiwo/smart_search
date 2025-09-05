package com.knowledge.enums;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class FeedbackTypeTest {

    @Test
    void testFeedbackTypeValues() {
        // 测试枚举值数量
        assertEquals(3, FeedbackType.values().length);
        
        // 测试枚举值
        assertNotNull(FeedbackType.OUT_OF_DATE);
        assertNotNull(FeedbackType.UNCLEAR);
        assertNotNull(FeedbackType.NOT_RELEVANT);
    }

    @Test
    void testFeedbackTypeCodes() {
        // 测试代码值
        assertEquals("out_of_date", FeedbackType.OUT_OF_DATE.getCode());
        assertEquals("unclear", FeedbackType.UNCLEAR.getCode());
        assertEquals("not_relevant", FeedbackType.NOT_RELEVANT.getCode());
    }

    @Test
    void testFeedbackTypeDescriptions() {
        // 测试描述值
        assertEquals("内容过时", FeedbackType.OUT_OF_DATE.getDescription());
        assertEquals("内容不清晰", FeedbackType.UNCLEAR.getDescription());
        assertEquals("内容不相关", FeedbackType.NOT_RELEVANT.getDescription());
    }

    @Test
    void testFromCode() {
        // 测试fromCode方法
        assertEquals(FeedbackType.OUT_OF_DATE, FeedbackType.fromCode("out_of_date"));
        assertEquals(FeedbackType.UNCLEAR, FeedbackType.fromCode("unclear"));
        assertEquals(FeedbackType.NOT_RELEVANT, FeedbackType.fromCode("not_relevant"));
        
        // 测试无效代码
        assertNull(FeedbackType.fromCode("invalid"));
        assertNull(FeedbackType.fromCode(null));
    }
}
