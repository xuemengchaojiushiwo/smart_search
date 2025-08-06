package com.knowledge.service;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.knowledge.entity.KnowledgeVersion;
import com.knowledge.mapper.KnowledgeVersionMapper;
import org.springframework.stereotype.Service;

@Service
public class KnowledgeVersionService extends ServiceImpl<KnowledgeVersionMapper, KnowledgeVersion> {
}
