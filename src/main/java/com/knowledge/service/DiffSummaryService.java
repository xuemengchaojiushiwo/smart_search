package com.knowledge.service;

import com.alibaba.fastjson2.JSON;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

/**
 * 差异总结服务
 * 调用Python服务生成版本差异的AI总结
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DiffSummaryService {

    private final RestTemplate restTemplate;

    @Value("${python.service.url}")
    private String pythonServiceUrl;

    /**
     * 获取两个HTML版本之间的差异总结
     * @param oldHtml 旧版本HTML
     * @param newHtml 新版本HTML
     * @return 差异总结文本
     */
    public String getSummary(String oldHtml, String newHtml) {
        try {
            String url = pythonServiceUrl + "/api/diff/summary";
            Map<String, String> requestBody = new HashMap<>();
            requestBody.put("oldHtml", oldHtml != null ? oldHtml : "");
            requestBody.put("newHtml", newHtml != null ? newHtml : "");
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, String>> request = new HttpEntity<>(requestBody, headers);
            
            ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                @SuppressWarnings("unchecked")
                Map<String, Object> result = JSON.parseObject(response.getBody(), Map.class);
                
                if (Boolean.TRUE.equals(result.get("success"))) {
                    return (String) result.get("summary");
                } else {
                    log.warn("获取差异总结失败: {}", result.get("error"));
                    return "无法生成差异总结，请查看HTML对比结果。";
                }
            } else {
                log.error("调用差异总结API失败, 状态码: {}", response.getStatusCode());
                return "调用差异总结服务失败，请查看HTML对比结果。";
            }
        } catch (Exception e) {
            log.error("获取差异总结时发生错误: {}", e.getMessage(), e);
            return "获取差异总结时发生错误，请查看HTML对比结果。";
        }
    }
}
