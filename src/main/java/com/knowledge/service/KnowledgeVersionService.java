package com.knowledge.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.knowledge.entity.KnowledgeDescriptionVersion;
import com.knowledge.entity.KnowledgeVersion;
import com.knowledge.mapper.KnowledgeDescriptionVersionMapper;
import com.knowledge.mapper.KnowledgeVersionMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
@RequiredArgsConstructor
public class KnowledgeVersionService extends ServiceImpl<KnowledgeVersionMapper, KnowledgeVersion> {

    private final JdbcTemplate jdbcTemplate;
    private final KnowledgeDescriptionVersionMapper descriptionVersionMapper;

    /**
     * 保存知识描述版本
     * @param knowledgeId 知识ID
     * @param content 描述内容
     * @param editor 修改人
     * @param editorId 修改人ID
     * @return 版本号
     */
    public String saveDescriptionVersion(Long knowledgeId, String content, String editor, Long editorId) {
        // 生成版本号：格式为 V1, V2, V3...
        String version = generateVersionNumber(knowledgeId);
        
        KnowledgeDescriptionVersion versionEntity = new KnowledgeDescriptionVersion();
        versionEntity.setKnowledgeId(knowledgeId);
        versionEntity.setVersion(version);
        versionEntity.setContent(content);
        versionEntity.setEditor(editor);
        versionEntity.setEditorId(editorId);
        versionEntity.setCreatedBy(editor);
        versionEntity.setUpdatedBy(editor);
        
        descriptionVersionMapper.insert(versionEntity);
        
        return version;
    }
    
    /**
     * 生成版本号
     */
    private String generateVersionNumber(Long knowledgeId) {
        // 查询该知识已有的版本数量
        LambdaQueryWrapper<KnowledgeDescriptionVersion> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(KnowledgeDescriptionVersion::getKnowledgeId, knowledgeId);
        long count = descriptionVersionMapper.selectCount(wrapper);
        
        return "V" + (count + 1);
    }
    
    /**
     * 获取知识的所有版本列表
     */
    public List<KnowledgeDescriptionVersion> getVersionList(Long knowledgeId) {
        LambdaQueryWrapper<KnowledgeDescriptionVersion> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(KnowledgeDescriptionVersion::getKnowledgeId, knowledgeId)
               .orderByDesc(KnowledgeDescriptionVersion::getCreatedAt);
        return descriptionVersionMapper.selectList(wrapper);
    }
    
    /**
     * 根据版本号获取版本内容
     */
    public KnowledgeDescriptionVersion getVersionByNumber(Long knowledgeId, String version) {
        LambdaQueryWrapper<KnowledgeDescriptionVersion> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(KnowledgeDescriptionVersion::getKnowledgeId, knowledgeId)
               .eq(KnowledgeDescriptionVersion::getVersion, version);
        return descriptionVersionMapper.selectOne(wrapper);
    }

    /**
     * 优先从版本表读取指定版本的描述；不存在则返回 null。
     * 表结构假定：knowledge_description_versions(knowledge_id BIGINT, version VARCHAR, content TEXT)
     */
    public String findDescriptionByVersion(Long knowledgeId, String version) {
        try {
            String sql = "SELECT content FROM knowledge_description_versions WHERE knowledge_id=? AND version=? ORDER BY created_at DESC LIMIT 1";
            return jdbcTemplate.queryForObject(sql, String.class, knowledgeId, version);
        } catch (EmptyResultDataAccessException e) {
            return null;
        } catch (Exception e) {
            // 表可能不存在或字段不同，容错为 null
            return null;
        }
    }

    /**
     * 回退读取当前知识表中的描述。
     * 表结构假定：knowledge(id BIGINT, description TEXT)
     */
    public String findCurrentDescription(Long knowledgeId) {
        try {
            String sql = "SELECT description FROM knowledge WHERE id=? LIMIT 1";
            return jdbcTemplate.queryForObject(sql, String.class, knowledgeId);
        } catch (EmptyResultDataAccessException e) {
            return null;
        } catch (Exception e) {
            return null;
        }
    }
}
 
