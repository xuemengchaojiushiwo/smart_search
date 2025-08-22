package com.knowledge.service;

import com.knowledge.vo.ChatMessageVO;
import com.knowledge.vo.ChatSessionVO;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class ChatHistoryService {

    private final ConcurrentHashMap<String, List<ChatMessageVO>> sessionIdToMessages = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, ChatSessionVO> sessions = new ConcurrentHashMap<>();

    public void createSessionIfAbsent(String sessionId, String createdBy) {
        sessionIdToMessages.computeIfAbsent(sessionId, k -> new ArrayList<>());
        sessions.computeIfAbsent(sessionId, k -> {
            ChatSessionVO vo = new ChatSessionVO();
            vo.setSessionId(sessionId);
            vo.setSessionName(null);
            vo.setCreatedBy(createdBy);
            vo.setStatus("ACTIVE");
            vo.setMessageCount(0);
            vo.setCreatedTime(java.time.LocalDateTime.now());
            vo.setLastActiveTime(java.time.LocalDateTime.now());
            return vo;
        });
    }

    public void setSessionTitleIfAbsent(String sessionId, String title) {
        ChatSessionVO vo = sessions.get(sessionId);
        if (vo != null && (vo.getSessionName() == null || vo.getSessionName().isEmpty())) {
            vo.setSessionName(title);
        }
    }

    public ChatSessionVO getSession(String sessionId) {
        return sessions.get(sessionId);
    }

    public List<ChatSessionVO> listSessions(String createdBy) {
        List<ChatSessionVO> list = new ArrayList<>();
        for (ChatSessionVO vo : sessions.values()) {
            if (createdBy == null || createdBy.equals(vo.getCreatedBy())) {
                list.add(vo);
            }
        }
        list.sort((a, b) -> {
            java.time.LocalDateTime la = a.getLastActiveTime();
            java.time.LocalDateTime lb = b.getLastActiveTime();
            if (la == null && lb == null) return 0;
            if (la == null) return 1;
            if (lb == null) return -1;
            return lb.compareTo(la);
        });
        return list;
    }

	public void appendUserMessage(String sessionId, String content, long timestampMs) {
		appendMessage(sessionId, "user", content, null, timestampMs);
	}

	public void appendAssistantMessage(String sessionId, String content, List<Map<String, Object>> references, long timestampMs) {
		appendMessage(sessionId, "assistant", content, references, timestampMs);
	}

	public List<ChatMessageVO> getMessages(String sessionId, Integer limit, Long beforeTimestampMs) {
		List<ChatMessageVO> list = sessionIdToMessages.getOrDefault(sessionId, Collections.emptyList());
		if (list.isEmpty()) {
			return Collections.emptyList();
		}
		List<ChatMessageVO> filtered = new ArrayList<>();
		for (int i = list.size() - 1; i >= 0; i--) {
			ChatMessageVO msg = list.get(i);
			if (beforeTimestampMs != null && msg.getTimestamp() >= beforeTimestampMs) {
				continue;
			}
			filtered.add(msg);
			if (limit != null && filtered.size() >= limit) {
				break;
			}
		}
		Collections.reverse(filtered);
		return filtered;
	}

	private void appendMessage(String sessionId, String role, String content, List<Map<String, Object>> references, long timestampMs) {
		List<ChatMessageVO> list = sessionIdToMessages.computeIfAbsent(sessionId, k -> new ArrayList<>());
		ChatMessageVO vo = new ChatMessageVO();
		vo.setId(UUID.randomUUID().toString());
		vo.setSessionId(sessionId);
		vo.setRole(role);
		vo.setContent(content);
		vo.setReferences(references);
		vo.setTimestamp(timestampMs);
		list.add(vo);
		ChatSessionVO session = sessions.get(sessionId);
		if (session != null) {
			session.setMessageCount((session.getMessageCount() == null ? 0 : session.getMessageCount()) + 1);
			session.setLastActiveTime(java.time.LocalDateTime.now());
		}
	}
}


