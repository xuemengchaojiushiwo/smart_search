package com.knowledge.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.knowledge.entity.ChatMessage;
import com.knowledge.entity.ChatSession;
import com.knowledge.mapper.ChatMessageMapper;
import com.knowledge.mapper.ChatSessionMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class ChatPersistenceService {

    @Autowired
    private ChatSessionMapper chatSessionMapper;

    @Autowired
    private ChatMessageMapper chatMessageMapper;

    public void ensureSession(String sessionId, String createdBy) {
        ChatSession exist = chatSessionMapper.selectOne(new LambdaQueryWrapper<ChatSession>()
                .eq(ChatSession::getSessionId, sessionId));
        if (exist == null) {
            ChatSession s = new ChatSession();
            s.setSessionId(sessionId);
            s.setSessionName(null);
            s.setCreatedBy(createdBy);
            s.setStatus("ACTIVE");
            s.setMessageCount(0);
            s.setCreatedTime(LocalDateTime.now());
            s.setLastActiveTime(LocalDateTime.now());
            chatSessionMapper.insert(s);
        }
    }

    public void setSessionTitleIfAbsent(String sessionId, String title) {
        ChatSession s = chatSessionMapper.selectOne(new LambdaQueryWrapper<ChatSession>()
                .eq(ChatSession::getSessionId, sessionId));
        if (s != null && (s.getSessionName() == null || s.getSessionName().isEmpty())) {
            s.setSessionName(title);
            chatSessionMapper.updateById(s);
        }
    }

    public void saveMessage(String sessionId, String messageId, String role, String content, String referencesJson, long timestampMs) {
        ChatMessage m = new ChatMessage();
        m.setSessionId(sessionId);
        m.setMessageId(messageId);
        m.setRole(role);
        m.setContent(content);
        m.setReferencesJson(referencesJson);
        m.setTimestampMs(timestampMs);
        // 补充createdBy便于按用户查询
        ChatSession s = chatSessionMapper.selectOne(new LambdaQueryWrapper<ChatSession>()
                .eq(ChatSession::getSessionId, sessionId));
        if (s != null) {
            m.setCreatedBy(s.getCreatedBy());
        }
        chatMessageMapper.insert(m);

        ChatSession s2 = chatSessionMapper.selectOne(new LambdaQueryWrapper<ChatSession>()
                .eq(ChatSession::getSessionId, sessionId));
        if (s2 != null) {
            s2.setMessageCount((s2.getMessageCount() == null ? 0 : s2.getMessageCount()) + 1);
            s2.setLastActiveTime(LocalDateTime.now());
            // 若会话标题为空，且当前为用户的首条问题，则用问题作为标题（截断至30字符）
            if ((s2.getSessionName() == null || s2.getSessionName().isEmpty()) && "user".equals(role)) {
                String title = content == null ? "" : content.trim();
                if (!title.isEmpty()) {
                    if (title.length() > 30) {
                        title = title.substring(0, 30) + "...";
                    }
                    s2.setSessionName(title);
                }
            }
            chatSessionMapper.updateById(s2);
        }
    }

    public List<ChatSession> listSessions(String createdBy) {
        return chatSessionMapper.selectList(new LambdaQueryWrapper<ChatSession>()
                .eq(ChatSession::getCreatedBy, createdBy)
                .orderByDesc(ChatSession::getLastActiveTime));
    }

    public Page<ChatMessage> listMessages(String sessionId, Integer limit, Long beforeTimestampMs) {
        int size = (limit == null || limit < 1) ? 20 : limit;
        Page<ChatMessage> page = new Page<>(1, size);
        LambdaQueryWrapper<ChatMessage> w = new LambdaQueryWrapper<>();
        w.eq(ChatMessage::getSessionId, sessionId);
        if (beforeTimestampMs != null) {
            w.lt(ChatMessage::getTimestampMs, beforeTimestampMs);
        }
        w.orderByDesc(ChatMessage::getTimestampMs);
        Page<ChatMessage> result = chatMessageMapper.selectPage(page, w);
        // 翻转为时间正序
        List<ChatMessage> records = result.getRecords();
        java.util.Collections.reverse(records);
        result.setRecords(records);
        return result;
    }
}


