package com.knowledge.util;

import com.knowledge.entity.Knowledge;
import com.knowledge.entity.KnowledgeHistoryVersion;
import lombok.extern.slf4j.Slf4j;
import org.springframework.util.CollectionUtils;

import java.util.*;

/**
 * 版本比较工具类
 * 用于比较知识的不同版本，生成变更摘要
 */
@Slf4j
public class VersionComparisonUtil {
    
    /**
     * 比较两个知识对象，生成变更详情
     */
    public static Map<String, Object> compareKnowledgeVersions(Knowledge oldVersion, Knowledge newVersion) {
        Map<String, Object> changes = new HashMap<>();
        
        if (oldVersion == null || newVersion == null) {
            return changes;
        }
        
        // 比较基本字段
        compareField(changes, "name", oldVersion.getName(), newVersion.getName());
        compareField(changes, "description", oldVersion.getDescription(), newVersion.getDescription());
        compareField(changes, "parentId", oldVersion.getParentId(), newVersion.getParentId());
        compareField(changes, "nodeType", oldVersion.getNodeType(), newVersion.getNodeType());
        compareField(changes, "tableData", oldVersion.getTableData(), newVersion.getTableData());
        compareField(changes, "effectiveStartTime", oldVersion.getEffectiveStartTime(), newVersion.getEffectiveStartTime());
        compareField(changes, "effectiveEndTime", oldVersion.getEffectiveEndTime(), newVersion.getEffectiveEndTime());
        compareField(changes, "status", oldVersion.getStatus(), newVersion.getStatus());
        compareField(changes, "searchCount", oldVersion.getSearchCount(), newVersion.getSearchCount());
        compareField(changes, "downloadCount", oldVersion.getDownloadCount(), newVersion.getDownloadCount());
        
        // 比较标签列表
        compareTags(changes, oldVersion.getTags(), newVersion.getTags());
        
        return changes;
    }
    
    /**
     * 比较两个历史版本对象
     */
    public static Map<String, Object> compareHistoryVersions(KnowledgeHistoryVersion oldVersion, KnowledgeHistoryVersion newVersion) {
        Map<String, Object> changes = new HashMap<>();
        
        if (oldVersion == null || newVersion == null) {
            return changes;
        }
        
        // 比较基本字段
        compareField(changes, "name", oldVersion.getName(), newVersion.getName());
        compareField(changes, "description", oldVersion.getDescription(), newVersion.getDescription());
        compareField(changes, "parentId", oldVersion.getParentId(), newVersion.getParentId());
        compareField(changes, "nodeType", oldVersion.getNodeType(), newVersion.getNodeType());
        compareField(changes, "tableData", oldVersion.getTableData(), newVersion.getTableData());
        compareField(changes, "effectiveStartTime", oldVersion.getEffectiveStartTime(), newVersion.getEffectiveStartTime());
        compareField(changes, "effectiveEndTime", oldVersion.getEffectiveEndTime(), newVersion.getEffectiveEndTime());
        compareField(changes, "status", oldVersion.getStatus(), newVersion.getStatus());
        compareField(changes, "searchCount", oldVersion.getSearchCount(), newVersion.getSearchCount());
        compareField(changes, "downloadCount", oldVersion.getDownloadCount(), newVersion.getDownloadCount());
        
        // 比较标签列表
        compareTags(changes, oldVersion.getTags(), newVersion.getTags());
        
        return changes;
    }
    
    /**
     * 比较单个字段
     */
    private static void compareField(Map<String, Object> changes, String fieldName, Object oldValue, Object newValue) {
        if (!Objects.equals(oldValue, newValue)) {
            Map<String, Object> fieldChange = new HashMap<>();
            fieldChange.put("oldValue", oldValue);
            fieldChange.put("newValue", newValue);
            fieldChange.put("changed", true);
            changes.put(fieldName, fieldChange);
        }
    }
    
    /**
     * 比较标签列表
     */
    private static void compareTags(Map<String, Object> changes, List<String> oldTags, List<String> newTags) {
        if (!CollectionUtils.isEmpty(oldTags) || !CollectionUtils.isEmpty(newTags)) {
            Set<String> oldTagSet = oldTags != null ? new HashSet<>(oldTags) : new HashSet<>();
            Set<String> newTagSet = newTags != null ? new HashSet<>(newTags) : new HashSet<>();
            
            if (!oldTagSet.equals(newTagSet)) {
                Map<String, Object> tagChange = new HashMap<>();
                tagChange.put("oldValue", oldTags);
                tagChange.put("newValue", newTags);
                tagChange.put("added", new HashSet<>(newTagSet));
                newTagSet.removeAll(oldTagSet);
                tagChange.put("removed", new HashSet<>(oldTagSet));
                oldTagSet.removeAll(newTagSet);
                tagChange.put("changed", true);
                changes.put("tags", tagChange);
            }
        }
    }
    
    /**
     * 生成变更摘要
     */
    public static String generateChangeSummary(Map<String, Object> changes) {
        if (changes.isEmpty()) {
            return "无变更";
        }
        
        List<String> changeList = new ArrayList<>();
        
        for (Map.Entry<String, Object> entry : changes.entrySet()) {
            String fieldName = entry.getKey();
            Object changeInfo = entry.getValue();
            
            if (changeInfo instanceof Map) {
                Map<?, ?> changeMap = (Map<?, ?>) changeInfo;
                Boolean changed = (Boolean) changeMap.get("changed");
                
                if (Boolean.TRUE.equals(changed)) {
                    String fieldDisplayName = getFieldDisplayName(fieldName);
                    changeList.add(fieldDisplayName);
                }
            }
        }
        
        if (changeList.isEmpty()) {
            return "无变更";
        }
        
        return "变更字段：" + String.join("、", changeList);
    }
    
    /**
     * 获取字段显示名称
     */
    private static String getFieldDisplayName(String fieldName) {
        switch (fieldName) {
            case "name": return "名称";
            case "description": return "描述";
            case "parentId": return "父级ID";
            case "nodeType": return "节点类型";
            case "effectiveStartTime": return "生效开始时间";
            case "effectiveEndTime": return "生效结束时间";
            case "status": return "状态";
            case "searchCount": return "搜索次数";
            case "downloadCount": return "下载次数";
            case "tags": return "标签";
            default: return fieldName;
        }
    }
    
    /**
     * 检查是否有变更
     */
    public static boolean hasChanges(Map<String, Object> changes) {
        return !changes.isEmpty();
    }
    
    /**
     * 获取变更的字段数量
     */
    public static int getChangedFieldCount(Map<String, Object> changes) {
        return changes.size();
    }
}
