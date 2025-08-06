package com.knowledge.service;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.knowledge.entity.CategoryChangeLog;
import com.knowledge.mapper.CategoryChangeLogMapper;
import org.springframework.stereotype.Service;

@Service
public class CategoryChangeLogService extends ServiceImpl<CategoryChangeLogMapper, CategoryChangeLog> {
}
