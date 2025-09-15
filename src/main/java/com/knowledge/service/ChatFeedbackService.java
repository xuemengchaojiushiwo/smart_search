package com.knowledge.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
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
        // 先检查是否已经有点赞记录
        LambdaQueryWrapper<ChatFeedback> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatFeedback::getSessionId, sessionId)
               .eq(ChatFeedback::getMessageId, messageId)
               .eq(ChatFeedback::getUserId, userId)
               .eq(ChatFeedback::getAttitude, "like")
               .eq(ChatFeedback::getDeleted, 0);
        
        ChatFeedback existingFeedback = chatFeedbackMapper.selectOne(wrapper);
        if (existingFeedback != null) {
            // 已经有点赞记录，直接返回
            return;
        }
        
        // 检查是否有dislike记录，如果有则删除
        LambdaQueryWrapper<ChatFeedback> dislikeWrapper = new LambdaQueryWrapper<>();
        dislikeWrapper.eq(ChatFeedback::getSessionId, sessionId)
                     .eq(ChatFeedback::getMessageId, messageId)
                     .eq(ChatFeedback::getUserId, userId)
                     .eq(ChatFeedback::getAttitude, "dislike")
                     .eq(ChatFeedback::getDeleted, 0);
        
        ChatFeedback dislikeFeedback = chatFeedbackMapper.selectOne(dislikeWrapper);
        if (dislikeFeedback != null) {
            dislikeFeedback.setDeleted(1);
            chatFeedbackMapper.updateById(dislikeFeedback);
        }
        
        // 插入新的点赞记录
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
        // 先检查是否已经有dislike记录
        LambdaQueryWrapper<ChatFeedback> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatFeedback::getSessionId, sessionId)
               .eq(ChatFeedback::getMessageId, messageId)
               .eq(ChatFeedback::getUserId, userId)
               .eq(ChatFeedback::getAttitude, "dislike")
               .eq(ChatFeedback::getDeleted, 0);
        
        ChatFeedback existingFeedback = chatFeedbackMapper.selectOne(wrapper);
        if (existingFeedback != null) {
            // 已经有dislike记录，更新内容
            existingFeedback.setContent(content);
            existingFeedback.setFeedbackType(feedbackType);
            existingFeedback.setCreatedTime(LocalDateTime.now());
            chatFeedbackMapper.updateById(existingFeedback);
            return;
        }
        
        // 检查是否有like记录，如果有则删除
        LambdaQueryWrapper<ChatFeedback> likeWrapper = new LambdaQueryWrapper<>();
        likeWrapper.eq(ChatFeedback::getSessionId, sessionId)
                  .eq(ChatFeedback::getMessageId, messageId)
                  .eq(ChatFeedback::getUserId, userId)
                  .eq(ChatFeedback::getAttitude, "like")
                  .eq(ChatFeedback::getDeleted, 0);
        
        ChatFeedback likeFeedback = chatFeedbackMapper.selectOne(likeWrapper);
        if (likeFeedback != null) {
            likeFeedback.setDeleted(1);
            chatFeedbackMapper.updateById(likeFeedback);
        }
        
        // 插入新的dislike记录
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

    public void unlikeAnswer(String sessionId, String messageId, Long userId) {
        LambdaQueryWrapper<ChatFeedback> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatFeedback::getSessionId, sessionId)
               .eq(ChatFeedback::getMessageId, messageId)
               .eq(ChatFeedback::getUserId, userId)
               .eq(ChatFeedback::getAttitude, "like")
               .eq(ChatFeedback::getDeleted, 0);
        
        // 使用selectList获取所有匹配的记录，然后批量删除
        java.util.List<ChatFeedback> feedbacks = chatFeedbackMapper.selectList(wrapper);
        if (!feedbacks.isEmpty()) {
            for (ChatFeedback feedback : feedbacks) {
                feedback.setDeleted(1);
                chatFeedbackMapper.updateById(feedback);
            }
        }
    }

    public void undislikeAnswer(String sessionId, String messageId, Long userId) {
        LambdaQueryWrapper<ChatFeedback> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatFeedback::getSessionId, sessionId)
               .eq(ChatFeedback::getMessageId, messageId)
               .eq(ChatFeedback::getUserId, userId)
               .eq(ChatFeedback::getAttitude, "dislike")
               .eq(ChatFeedback::getDeleted, 0);
        
        // 使用selectList获取所有匹配的记录，然后批量删除
        java.util.List<ChatFeedback> feedbacks = chatFeedbackMapper.selectList(wrapper);
        if (!feedbacks.isEmpty()) {
            for (ChatFeedback feedback : feedbacks) {
                feedback.setDeleted(1);
                chatFeedbackMapper.updateById(feedback);
            }
        }
    }
}


