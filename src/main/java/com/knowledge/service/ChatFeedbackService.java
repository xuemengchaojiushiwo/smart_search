package com.knowledge.service;

import com.knowledge.entity.ChatFeedback;
import com.knowledge.mapper.ChatFeedbackMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
public class ChatFeedbackService {

    @Autowired
    private ChatFeedbackMapper chatFeedbackMapper;

    public void likeAnswer(String sessionId, String messageId, Long userId) {
        ChatFeedback fb = new ChatFeedback();
        fb.setSessionId(sessionId);
        fb.setMessageId(messageId);
        fb.setUserId(userId);
        fb.setAttitude("like");
        fb.setContent(null);
        fb.setCreatedTime(LocalDateTime.now());
        fb.setDeleted(0);
        chatFeedbackMapper.insert(fb);
    }

    public void dislikeAnswer(String sessionId, String messageId, Long userId, String content, String feedbackType) {
        ChatFeedback fb = new ChatFeedback();
        fb.setSessionId(sessionId);
        fb.setMessageId(messageId);
        fb.setUserId(userId);
        fb.setAttitude("dislike");
        fb.setFeedbackType(feedbackType);
        fb.setContent(content);
        fb.setCreatedTime(LocalDateTime.now());
        fb.setDeleted(0);
        chatFeedbackMapper.insert(fb);
    }
}


