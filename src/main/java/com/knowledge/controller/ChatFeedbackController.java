package com.knowledge.controller;

import com.knowledge.service.ChatFeedbackService;
import com.knowledge.vo.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.Data;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
@Tag(name = "AI回答反馈", description = "针对单次AI回答的点赞/点踩/反馈")
public class ChatFeedbackController {

    @Autowired
    private ChatFeedbackService chatFeedbackService;

    @PostMapping("/answer/{sessionId}/{messageId}/like")
    @Operation(summary = "点赞AI回答")
    public ApiResponse<Void> likeAnswer(@PathVariable String sessionId,
                                        @PathVariable String messageId,
                                        @RequestParam(defaultValue = "1") Long userId) {
        chatFeedbackService.likeAnswer(sessionId, messageId, userId);
        return ApiResponse.success(null);
    }

    @PostMapping("/answer/{sessionId}/{messageId}/dislike")
    @Operation(summary = "点踩AI回答（原因可空）")
    public ApiResponse<Void> dislikeAnswer(@PathVariable String sessionId,
                                           @PathVariable String messageId,
                                           @RequestParam(defaultValue = "1") Long userId,
                                           @RequestBody(required = false) DislikeBody body) {
        Long uid = (body != null && body.getUserId() != null) ? body.getUserId() : userId;
        String content = body != null ? body.getContent() : null;
        chatFeedbackService.dislikeAnswer(sessionId, messageId, uid, content);
        return ApiResponse.success(null);
    }

    @Data
    private static class DislikeBody {
        private String content;
        private Long userId;
    }
}


