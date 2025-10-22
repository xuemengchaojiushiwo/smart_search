package com.knowledge.service;

import com.alibaba.fastjson2.JSON;
import com.knowledge.exception.BusinessException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
public class PythonService {
    
    @Value("${python.service.url:http://localhost:8000}")
    private String pythonServiceUrl;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    /**
     * 调用Python脚本进行LDAP验证
     */
    public Map<String, Object> validateLdapUser(String username, String password) {
        try {
            String url = pythonServiceUrl + "/ldap/verify";
            
            Map<String, String> requestBody = new HashMap<>();
            requestBody.put("username", username);
            requestBody.put("password", password);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, String>> request = new HttpEntity<>(requestBody, headers);
            
            ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                @SuppressWarnings("unchecked")
                Map<String, Object> result = JSON.parseObject(response.getBody(), Map.class);
                log.info("LDAP验证成功: {}", username);
                return result;
            } else {
                log.error("LDAP验证失败: {}, 状态码: {}", username, response.getStatusCode());
                throw new BusinessException("LDAP验证失败");
            }
        } catch (Exception e) {
            log.error("调用Python LDAP服务失败: {}", e.getMessage(), e);
            throw new BusinessException("LDAP验证服务不可用");
        }
    }
    
    /**
     * 调用Python服务进行普通对话
     */
    public Map<String, Object> chat(String question, String userId) {
        try {
            String url = pythonServiceUrl + "/api/chat";
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("question", question);
            requestBody.put("user_id", userId);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                @SuppressWarnings("unchecked")
                Map<String, Object> result = JSON.parseObject(response.getBody(), Map.class);
                log.info("普通对话成功: {}", question);
                return result;
            } else {
                log.error("普通对话失败: {}, 状态码: {}", question, response.getStatusCode());
                throw new BusinessException("对话服务调用失败");
            }
        } catch (Exception e) {
            log.error("调用Python对话服务失败: {}", e.getMessage(), e);
            throw new BusinessException("对话服务不可用");
        }
    }
    
    /**
     * 调用Python RAG服务进行智能问答
     */
    public Map<String, Object> chatWithRag(String question, String userId) {
        return chatWithRag(question, userId, null, null);
    }
    
    /**
     * 调用Python RAG服务进行智能问答（支持指定文件和工作空间）
     */
    public Map<String, Object> chatWithRag(String question, String userId, String sourceFile, String workspace) {
        try {
            String url = pythonServiceUrl + "/api/rag/chat";
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("question", question);
            requestBody.put("user_id", userId);
            if (sourceFile != null && !sourceFile.trim().isEmpty()) {
                requestBody.put("source_file", sourceFile.trim());
                log.info("RAG对话指定文件: {}", sourceFile);
            }
            if (workspace != null && !workspace.trim().isEmpty()) {
                requestBody.put("workspace", workspace.trim());
                log.info("RAG对话指定工作空间: {}", workspace);
            }
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                @SuppressWarnings("unchecked")
                Map<String, Object> result = JSON.parseObject(response.getBody(), Map.class);
                log.info("RAG对话成功: {} {}", question, sourceFile != null ? "(文件: " + sourceFile + ")" : "");
                return result;
            } else {
                log.error("RAG对话失败: {}, 状态码: {}", question, response.getStatusCode());
                throw new BusinessException("RAG服务调用失败");
            }
        } catch (Exception e) {
            log.error("调用Python RAG服务失败: {}", e.getMessage(), e);
            throw new BusinessException("RAG服务不可用");
        }
    }
    
    /**
     * 调用Python服务处理文档
     */
    public Map<String, Object> processDocument(MultipartFile file, Long knowledgeId, String knowledgeName,
                                              String description, String tags, String effectiveTime, String workspaces) {
        try {
            String url = pythonServiceUrl + "/api/document/process";

            // 外层 multipart 头
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            // 文件资源（不要给文件部分设置 multipart 头，由 RestTemplate 统一封装）
            org.springframework.core.io.ByteArrayResource fileResource = new org.springframework.core.io.ByteArrayResource(file.getBytes()) {
                @Override
                public String getFilename() {
                    return file.getOriginalFilename();
                }
            };

            // 使用 LinkedMultiValueMap 正确构造 multipart 表单
            org.springframework.util.LinkedMultiValueMap<String, Object> form = new org.springframework.util.LinkedMultiValueMap<>();
            form.add("file", fileResource);
            if (knowledgeId != null) form.add("knowledge_id", String.valueOf(knowledgeId));
            if (knowledgeName != null) form.add("knowledge_name", knowledgeName);
            if (description != null) form.add("description", description);
            if (tags != null) form.add("tags", tags);
            if (effectiveTime != null) form.add("effective_time", effectiveTime);
            if (workspaces != null) form.add("workspaces", workspaces);

            HttpEntity<org.springframework.util.LinkedMultiValueMap<String, Object>> request = new HttpEntity<>(form, headers);

            ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);

            if (response.getStatusCode() == HttpStatus.OK) {
                @SuppressWarnings("unchecked")
                Map<String, Object> result = JSON.parseObject(response.getBody(), Map.class);
                log.info("文档处理成功: {}", file.getOriginalFilename());
                return result;
            } else {
                log.error("文档处理失败: {}, 状态码: {}", file.getOriginalFilename(), response.getStatusCode());
                throw new BusinessException("文档处理失败");
            }
        } catch (Exception e) {
            log.error("调用Python文档处理服务失败: {}", e.getMessage(), e);
            throw new BusinessException("文档处理服务不可用");
        }
    }
    
    /**
     * 获取文本的embedding向量
     */
    public java.util.List<Double> getEmbedding(String text) {
        try {
            String url = pythonServiceUrl + "/api/embedding";
            
            Map<String, String> requestBody = new HashMap<>();
            requestBody.put("text", text);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, String>> request = new HttpEntity<>(requestBody, headers);
            
            ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                @SuppressWarnings("unchecked")
                Map<String, Object> result = JSON.parseObject(response.getBody(), Map.class);
                
                if (Boolean.TRUE.equals(result.get("success"))) {
                    @SuppressWarnings("unchecked")
                    java.util.List<Double> embedding = (java.util.List<Double>) result.get("embedding");
                    log.info("获取embedding成功: 文本长度={}, 向量维度={}", text.length(), embedding.size());
                    return embedding;
                } else {
                    log.error("获取embedding失败: {}", result);
                    return null;
                }
            } else {
                log.error("获取embedding失败, 状态码: {}", response.getStatusCode());
                return null;
            }
        } catch (Exception e) {
            log.error("调用Python embedding服务失败: {}", e.getMessage(), e);
            return null;
        }
    }
    
    /**
     * 检查Python服务健康状态
     */
    public Map<String, Object> checkHealth() {
        try {
            String url = pythonServiceUrl + "/api/health";
            
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                @SuppressWarnings("unchecked")
                Map<String, Object> result = JSON.parseObject(response.getBody(), Map.class);
                log.info("Python服务健康检查成功");
                return result;
            } else {
                log.error("Python服务健康检查失败, 状态码: {}", response.getStatusCode());
                throw new BusinessException("Python服务不可用");
            }
        } catch (Exception e) {
            log.error("Python服务健康检查失败: {}", e.getMessage(), e);
            throw new BusinessException("Python服务不可用");
        }
    }
    
    /**
     * 为没有附件的知识生成元数据embedding并存储到ES
     */
    public boolean indexKnowledgeMetadata(com.knowledge.entity.Knowledge knowledge, java.util.List<String> workspaces) {
        try {
            String url = pythonServiceUrl + "/api/knowledge/metadata";
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("knowledge_id", knowledge.getId());
            requestBody.put("knowledge_name", knowledge.getName());
            requestBody.put("description", knowledge.getDescription());
            requestBody.put("tags", knowledge.getTags());
            requestBody.put("effective_time", knowledge.getEffectiveStartTime() != null ? 
                knowledge.getEffectiveStartTime().format(java.time.format.DateTimeFormatter.ISO_LOCAL_DATE_TIME) : null);
            requestBody.put("workspaces", workspaces);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                @SuppressWarnings("unchecked")
                Map<String, Object> result = JSON.parseObject(response.getBody(), Map.class);
                boolean success = Boolean.TRUE.equals(result.get("success"));
                log.info("知识元数据embedding生成{}: knowledgeId={}", success ? "成功" : "失败", knowledge.getId());
                return success;
            } else {
                log.error("知识元数据embedding生成失败, 状态码: {}", response.getStatusCode());
                return false;
            }
        } catch (Exception e) {
            log.error("调用Python知识元数据embedding服务失败: {}", e.getMessage(), e);
            return false;
        }
    }
}