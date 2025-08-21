package com.knowledge.controller;

import com.knowledge.dto.ChatRequest;
import com.alibaba.fastjson2.JSON;
import com.knowledge.dto.CreateSessionRequest;
import com.knowledge.service.PythonService;
import com.knowledge.util.JwtTokenProvider;
import com.knowledge.vo.ChatResponse;
import com.knowledge.vo.ChatSessionVO;
import com.knowledge.vo.ChatMessageVO;
import com.knowledge.vo.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.validation.Valid;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.HashMap;
import java.util.ArrayList;

@Slf4j
@RestController
@RequestMapping("/api/chat")
@Tag(name = "RAG智能问答", description = "基于知识库的智能问答相关接口")
public class ChatController {
    
    @Autowired
    private PythonService pythonService;
    
    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    @Autowired
    private com.knowledge.service.ChatHistoryService chatHistoryService;
    
    /**
     * 创建RAG对话会话
     */
    @PostMapping("/sessions")
    @Operation(summary = "创建RAG会话", description = "创建一个新的RAG对话会话")
    public ApiResponse<ChatSessionVO> createSession(
            @Parameter(description = "创建会话请求", required = true) @Valid @RequestBody CreateSessionRequest request,
            HttpServletRequest httpRequest) {
        
        try {
            String username = extractUsername(httpRequest);
            
            // 生成会话ID
            String sessionId = UUID.randomUUID().toString();
            
            // 创建会话VO（这里应该调用会话服务）
            ChatSessionVO session = new ChatSessionVO();
            session.setSessionId(sessionId);
            session.setSessionName(request.getSessionName());
            session.setDescription(request.getDescription());
            session.setKnowledgeIds(request.getKnowledgeIds());
            session.setCreatedBy(username);
            session.setStatus("ACTIVE");
            
            log.info("创建RAG会话 - 用户: {}, 会话: {}", username, sessionId);
            
            // 初始化会话历史
            chatHistoryService.createSessionIfAbsent(sessionId, username);

            return ApiResponse.success(session);
            
        } catch (Exception e) {
            log.error("创建会话失败: {}", e.getMessage(), e);
            return ApiResponse.error("创建会话失败: " + e.getMessage());
        }
    }
    
    /**
     * 获取用户RAG会话列表
     */
    @GetMapping("/sessions")
    @Operation(summary = "获取RAG会话列表", description = "获取当前用户的所有RAG对话会话")
    public ApiResponse<List<ChatSessionVO>> getSessions(HttpServletRequest httpRequest) {
        
        try {
            String username = extractUsername(httpRequest);
            
            // 这里应该调用会话服务获取用户会话列表
            // 暂时返回空列表
            List<ChatSessionVO> sessions = new ArrayList<>();
            
            log.info("获取RAG会话列表 - 用户: {}", username);
            
            return ApiResponse.success(sessions);
            
        } catch (Exception e) {
            log.error("获取会话列表失败: {}", e.getMessage(), e);
            return ApiResponse.error("获取会话列表失败: " + e.getMessage());
        }
    }

    /**
     * 获取会话历史消息
     */
    @GetMapping("/history/{sessionId}")
    @Operation(summary = "获取对话历史", description = "按会话ID获取历史消息")
    public ApiResponse<List<ChatMessageVO>> getHistory(
            @Parameter(description = "会话ID", required = true) @PathVariable String sessionId,
            @Parameter(description = "最多返回条数") @RequestParam(required = false) Integer limit,
            @Parameter(description = "返回该时间戳之前的消息") @RequestParam(required = false, name = "before") Long beforeTimestamp,
            HttpServletRequest httpRequest) {

        String username = extractUsername(httpRequest);
        log.info("获取对话历史 - 用户: {}, 会话: {}", username, sessionId);
        List<ChatMessageVO> messages = chatHistoryService.getMessages(sessionId, limit, beforeTimestamp);
        return ApiResponse.success(messages);
    }
    
//     /**
//      * RAG对话（基于知识库的智能问答）
//      */
//     @PostMapping("/rag")
//     @Operation(summary = "RAG对话", description = "基于知识库的智能问答")
//     public ApiResponse<ChatResponse> ragChat(
//             @Parameter(description = "RAG聊天请求", required = true) @Valid @RequestBody ChatRequest request,
//             HttpServletRequest httpRequest) {
//
//         try {
//             String username = extractUsername(httpRequest);
//
//             // 如果没有sessionId，生成新的
//             if (request.getSessionId() == null) {
//                 request.setSessionId(UUID.randomUUID().toString());
//             }
//
//             log.info("开始RAG对话 - 用户: {}, 问题: {}, Session: {}", username, request.getQuestion(), request.getSessionId());
//             // 记录用户问题到历史（并用于自动生成会话标题）
//             chatHistoryService.createSessionIfAbsent(request.getSessionId(), username);
//             chatHistoryService.appendUserMessage(request.getSessionId(), request.getQuestion(), System.currentTimeMillis());
//
//             // 尝试调用Python RAG服务，如果失败则使用模拟响应
//             Map<String, Object> ragResult;
//             try {
//                 ragResult = pythonService.chatWithRag(request.getQuestion(), username);
//             } catch (Exception e) {
//                 log.warn("Python服务不可用，使用模拟响应: {}", e.getMessage());
//                 // 创建模拟响应
//                 ragResult = new HashMap<>();
//                 ragResult.put("answer", "This is a simulated response for testing. The Python RAG service is not available.");
//                 ragResult.put("references", new ArrayList<>());
//             }
//
//             // 构建响应
//             ChatResponse response = new ChatResponse();
//             response.setAnswer((String) ragResult.get("answer"));
//             response.setSessionId(request.getSessionId());
//             response.setTimestamp(System.currentTimeMillis());
//
//             // 处理知识引用
//             @SuppressWarnings("unchecked")
//             List<Map<String, Object>> references = (List<Map<String, Object>>) ragResult.get("references");
//             if (references != null) {
//                 List<ChatResponse.KnowledgeReference> knowledgeReferences = references.stream()
//                     .map(ref -> {
//                         ChatResponse.KnowledgeReference kr = new ChatResponse.KnowledgeReference();
//                         kr.setKnowledgeId(Long.valueOf(ref.get("knowledge_id").toString()));
//                         kr.setKnowledgeName((String) ref.get("knowledge_name"));
//                         kr.setDescription((String) ref.get("description"));
//                         kr.setTags((List<String>) ref.get("tags"));
//                         kr.setEffectiveTime((String) ref.get("effective_time"));
//                         kr.setAttachments((List<String>) ref.get("attachments"));
//                         kr.setRelevance(Double.valueOf(ref.get("relevance").toString()));
//                         // 溯源字段（可选）
//                         if (ref.get("source_file") != null) kr.setSourceFile(ref.get("source_file").toString());
//                         if (ref.get("page_num") != null) kr.setPageNum(Integer.valueOf(ref.get("page_num").toString()));
//                         if (ref.get("chunk_index") != null) kr.setChunkIndex(Integer.valueOf(ref.get("chunk_index").toString()));
//                         if (ref.get("chunk_type") != null) kr.setChunkType(ref.get("chunk_type").toString());
//                         if (ref.get("bbox_union") != null) {
//                             @SuppressWarnings("unchecked")
//                             List<Double> bbox = (List<Double>) ref.get("bbox_union");
//                             kr.setBboxUnion(bbox);
//                         }
//                         if (ref.get("char_start") != null) kr.setCharStart(Integer.valueOf(ref.get("char_start").toString()));
//                         if (ref.get("char_end") != null) kr.setCharEnd(Integer.valueOf(ref.get("char_end").toString()));
//                         return kr;
//                     })
//                     .collect(Collectors.toList());
//                 response.setReferences(knowledgeReferences);
//             }
//
//             return ApiResponse.success(response);
//
//         } catch (Exception e) {
//             log.error("RAG对话失败: {}", e.getMessage(), e);
//             return ApiResponse.error("RAG对话失败: " + e.getMessage());
//         }
//     }
    
    /**
     * RAG流式对话（SSE）
     */
    @PostMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    @Operation(summary = "RAG流式对话", description = "支持流式响应的RAG对话接口，返回SSE格式数据")
    public void ragChatStream(
            @Parameter(description = "RAG聊天请求", required = true) @Valid @RequestBody ChatRequest request,
            HttpServletRequest httpRequest,
            HttpServletResponse response) {
        
        try {
            String username = extractUsername(httpRequest);
            
            // 如果没有sessionId，生成新的
            if (request.getSessionId() == null) {
                request.setSessionId(UUID.randomUUID().toString());
            }
            
            log.info("开始RAG流式对话 - 用户: {}, 问题: {}, Session: {}", username, request.getQuestion(), request.getSessionId());
            
            // 设置SSE响应头
            response.setContentType("text/event-stream");
            response.setCharacterEncoding("UTF-8");
            response.setHeader("Cache-Control", "no-cache");
            response.setHeader("Connection", "keep-alive");
            response.setHeader("Access-Control-Allow-Origin", "*");
            response.setHeader("Access-Control-Allow-Headers", "Cache-Control");
            
            PrintWriter writer = response.getWriter();
            
            // 发送开始事件
            writer.write("event: start\n");
            writer.write("data: {\"message\":\"Start RAG chat\",\"sessionId\":\"" + request.getSessionId() + "\"}\n\n");
            writer.flush();
            
            // 尝试调用Python RAG服务，如果失败则使用模拟响应
            Map<String, Object> result;
            try {
                result = pythonService.chatWithRag(request.getQuestion(), username);
            } catch (Exception e) {
                log.warn("Python服务不可用，使用模拟响应: {}", e.getMessage());
                // 创建模拟响应
                result = new HashMap<>();
                result.put("answer", "This is a simulated response for testing. The Python RAG service is not available.");
                result.put("references", new ArrayList<>());
            }
            
            // 发送回答内容（模拟流式输出）
            String answer = (String) result.get("answer");
            if (answer != null) {
                // 模拟逐字输出
                String[] words = answer.split(" ");
                for (int i = 0; i < words.length; i++) {
                    writer.write("event: message\n");
                    writer.write("data: {\"content\":\"" + words[i] + " \",\"index\":" + i + "}\n\n");
                    writer.flush();
                    
                    // 模拟延迟
                    try {
                        Thread.sleep(100);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            }
            
            // 处理知识引用（返回完整引用数组，包含页码与坐标等溯源信息）
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> references = (List<Map<String, Object>>) result.get("references");
            if (references != null) {
                writer.write("event: references\n");
                writer.write("data: " + JSON.toJSONString(references) + "\n\n");
                writer.flush();
            }
            
            // 发送结束事件
            writer.write("event: end\n");
            writer.write("data: {\"message\":\"RAG chat completed\",\"sessionId\":\"" + request.getSessionId() + "\"}\n\n");
            writer.flush();
            
            // 记录助手消息与引用到历史
            chatHistoryService.appendAssistantMessage(request.getSessionId(), answer != null ? answer : "", references, System.currentTimeMillis());

            // 若会话标题为空，基于第一条用户问题自动生成一个简短标题（简单截断版，后续可接入AI摘要）
            try {
                if (request.getQuestion() != null) {
                    String q = request.getQuestion().trim();
                    if (!q.isEmpty()) {
                        String title = q.length() > 30 ? q.substring(0, 30) + "..." : q;
                        chatHistoryService.setSessionTitleIfAbsent(request.getSessionId(), title);
                    }
                }
            } catch (Exception ignore) {}

            log.info("RAG流式对话完成 - 用户: {}, Session: {}", username, request.getSessionId());
            
        } catch (Exception e) {
            log.error("RAG流式对话失败: {}", e.getMessage(), e);
            try {
                PrintWriter writer = response.getWriter();
                writer.write("event: error\n");
                writer.write("data: {\"message\":\"RAG stream chat failed\"}\n\n");
                writer.flush();
            } catch (IOException ex) {
                log.error("发送错误响应失败", ex);
            }
        }
    }
    
    /**
     * 从请求头中提取用户名（支持JWT token或直接用户名）
     */
    private String extractUsername(HttpServletRequest request) {
        // 暂时去掉JWT token验证，直接使用默认用户名
        return "test_user";
    }
    
    /**
     * 从请求头中提取JWT token
     */
    private String extractToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        throw new RuntimeException("未找到有效的JWT token");
    }
}