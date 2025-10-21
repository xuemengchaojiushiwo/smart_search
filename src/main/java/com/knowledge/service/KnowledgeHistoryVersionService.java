package com.knowledge.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.knowledge.entity.Knowledge;
import com.knowledge.entity.KnowledgeHistoryVersion;
import com.knowledge.mapper.KnowledgeHistoryVersionMapper;
import com.knowledge.util.VersionComparisonUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;

/**
 * 知识历史版本服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class KnowledgeHistoryVersionService extends ServiceImpl<KnowledgeHistoryVersionMapper, KnowledgeHistoryVersion> {
    
    private final KnowledgeHistoryVersionMapper historyVersionMapper;
    
    /**
     * 创建知识时保存V1版本
     */
    @Transactional
    public KnowledgeHistoryVersion createInitialVersion(Knowledge knowledge, String currentUser) {
        log.info("为知识创建初始版本: knowledgeId={}, name={}", knowledge.getId(), knowledge.getName());
        
        KnowledgeHistoryVersion version = new KnowledgeHistoryVersion();
        copyKnowledgeToVersion(knowledge, version);
        
        version.setVersionNumber(1);
        version.setVersionName("V1");
        version.setChangeType("CREATE");
        version.setChangeReason("创建知识");
        version.setChangeSummary("初始版本创建");
        version.setCreatedBy(currentUser);
        version.setUpdatedBy(currentUser);
        
        // 初始化字段变更信息为空
        version.setFieldChanges(Map.of());
        
        save(version);
        
        log.info("知识初始版本创建成功: knowledgeId={}, versionId={}, versionNumber={}", 
                knowledge.getId(), version.getId(), version.getVersionNumber());
        
        return version;
    }
    
    /**
     * 更新知识时保存新版本
     */
    @Transactional
    public KnowledgeHistoryVersion createUpdateVersion(Knowledge oldKnowledge, Knowledge newKnowledge, 
                                                      String currentUser, String changeReason) {
        log.info("为知识创建更新版本: knowledgeId={}, name={}", newKnowledge.getId(), newKnowledge.getName());
        
        // 比较版本差异
        Map<String, Object> fieldChanges = VersionComparisonUtil.compareKnowledgeVersions(oldKnowledge, newKnowledge);
        
        // 如果没有变更，不创建新版本
        if (!VersionComparisonUtil.hasChanges(fieldChanges)) {
            log.info("知识无变更，跳过版本创建: knowledgeId={}", newKnowledge.getId());
            return null;
        }
        
        // 获取下一个版本号
        Integer nextVersionNumber = getNextVersionNumber(newKnowledge.getId());
        
        KnowledgeHistoryVersion version = new KnowledgeHistoryVersion();
        copyKnowledgeToVersion(newKnowledge, version);
        
        version.setVersionNumber(nextVersionNumber);
        version.setVersionName("V" + nextVersionNumber);
        version.setChangeType("UPDATE");
        version.setChangeReason(changeReason != null ? changeReason : "知识更新");
        version.setChangeSummary(VersionComparisonUtil.generateChangeSummary(fieldChanges));
        version.setFieldChanges(fieldChanges);
        version.setCreatedBy(currentUser);
        version.setUpdatedBy(currentUser);
        
        save(version);
        
        log.info("知识更新版本创建成功: knowledgeId={}, versionId={}, versionNumber={}, changes={}", 
                newKnowledge.getId(), version.getId(), version.getVersionNumber(), 
                VersionComparisonUtil.getChangedFieldCount(fieldChanges));
        
        return version;
    }
    
    /**
     * 删除知识时保存删除版本
     */
    @Transactional
    public KnowledgeHistoryVersion createDeleteVersion(Knowledge knowledge, String currentUser, String changeReason) {
        log.info("为知识创建删除版本: knowledgeId={}, name={}", knowledge.getId(), knowledge.getName());
        
        // 获取下一个版本号
        Integer nextVersionNumber = getNextVersionNumber(knowledge.getId());
        
        KnowledgeHistoryVersion version = new KnowledgeHistoryVersion();
        copyKnowledgeToVersion(knowledge, version);
        
        version.setVersionNumber(nextVersionNumber);
        version.setVersionName("V" + nextVersionNumber);
        version.setChangeType("DELETE");
        version.setChangeReason(changeReason != null ? changeReason : "知识删除");
        version.setChangeSummary("知识被删除");
        version.setFieldChanges(Map.of());
        version.setCreatedBy(currentUser);
        version.setUpdatedBy(currentUser);
        
        save(version);
        
        log.info("知识删除版本创建成功: knowledgeId={}, versionId={}, versionNumber={}", 
                knowledge.getId(), version.getId(), version.getVersionNumber());
        
        return version;
    }
    
    /**
     * 获取知识的所有历史版本
     */
    public List<KnowledgeHistoryVersion> getKnowledgeVersions(Long knowledgeId) {
        LambdaQueryWrapper<KnowledgeHistoryVersion> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(KnowledgeHistoryVersion::getKnowledgeId, knowledgeId)
               .orderByAsc(KnowledgeHistoryVersion::getVersionNumber);
        return list(wrapper);
    }
    
    /**
     * 获取特定版本
     */
    public KnowledgeHistoryVersion getVersion(Long knowledgeId, Integer versionNumber) {
        LambdaQueryWrapper<KnowledgeHistoryVersion> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(KnowledgeHistoryVersion::getKnowledgeId, knowledgeId)
               .eq(KnowledgeHistoryVersion::getVersionNumber, versionNumber);
        return getOne(wrapper);
    }
    
    /**
     * 获取最新版本
     */
    public KnowledgeHistoryVersion getLatestVersion(Long knowledgeId) {
        LambdaQueryWrapper<KnowledgeHistoryVersion> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(KnowledgeHistoryVersion::getKnowledgeId, knowledgeId)
               .orderByDesc(KnowledgeHistoryVersion::getVersionNumber)
               .last("LIMIT 1");
        return getOne(wrapper);
    }
    
    /**
     * 比较两个版本
     */
    public Map<String, Object> compareVersions(Long knowledgeId, Integer versionNumber1, Integer versionNumber2) {
        KnowledgeHistoryVersion version1 = getVersion(knowledgeId, versionNumber1);
        KnowledgeHistoryVersion version2 = getVersion(knowledgeId, versionNumber2);
        
        if (version1 == null || version2 == null) {
            throw new IllegalArgumentException("版本不存在");
        }
        
        return VersionComparisonUtil.compareHistoryVersions(version1, version2);
    }
    
    /**
     * 获取下一个版本号
     */
    private Integer getNextVersionNumber(Long knowledgeId) {
        Integer maxVersion = historyVersionMapper.getMaxVersionNumber(knowledgeId);
        return maxVersion != null ? maxVersion + 1 : 1;
    }
    
    /**
     * 将Knowledge对象复制到KnowledgeHistoryVersion对象
     */
    private void copyKnowledgeToVersion(Knowledge knowledge, KnowledgeHistoryVersion version) {
        version.setKnowledgeId(knowledge.getId());
        version.setName(knowledge.getName());
        version.setDescription(knowledge.getDescription());
        version.setParentId(knowledge.getParentId());
        version.setNodeType(knowledge.getNodeType());
        version.setTags(knowledge.getTags());
        version.setTableData(knowledge.getTableData());
        version.setEffectiveStartTime(knowledge.getEffectiveStartTime());
        version.setEffectiveEndTime(knowledge.getEffectiveEndTime());
        version.setStatus(knowledge.getStatus());
        version.setSearchCount(knowledge.getSearchCount());
        version.setDownloadCount(knowledge.getDownloadCount());
    }
}
