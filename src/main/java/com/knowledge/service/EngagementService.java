package com.knowledge.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.knowledge.entity.KnowledgeFavorite;
import com.knowledge.entity.KnowledgeFeedback;
import com.knowledge.entity.KnowledgeLike;
import com.knowledge.exception.BusinessException;
import com.knowledge.mapper.KnowledgeFavoriteMapper;
import com.knowledge.mapper.KnowledgeFeedbackMapper;
import com.knowledge.mapper.KnowledgeLikeMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Slf4j
@Service
public class EngagementService {

	@Autowired
	private KnowledgeLikeMapper likeMapper;

	@Autowired
	private KnowledgeFavoriteMapper favoriteMapper;

	@Autowired
	private KnowledgeFeedbackMapper feedbackMapper;

	public void like(Long knowledgeId, Long userId) {
		LambdaQueryWrapper<KnowledgeLike> w = new LambdaQueryWrapper<>();
		w.eq(KnowledgeLike::getKnowledgeId, knowledgeId).eq(KnowledgeLike::getUserId, userId).eq(KnowledgeLike::getDeleted, 0);
		if (likeMapper.selectCount(w) > 0) {
			throw new BusinessException("已点赞");
		}
		KnowledgeLike k = new KnowledgeLike();
		k.setKnowledgeId(knowledgeId);
		k.setUserId(userId);
		k.setCreatedTime(LocalDateTime.now());
		k.setDeleted(0);
		likeMapper.insert(k);
	}

	public void unlike(Long knowledgeId, Long userId) {
		LambdaQueryWrapper<KnowledgeLike> w = new LambdaQueryWrapper<>();
		w.eq(KnowledgeLike::getKnowledgeId, knowledgeId).eq(KnowledgeLike::getUserId, userId).eq(KnowledgeLike::getDeleted, 0);
		KnowledgeLike k = likeMapper.selectOne(w);
		if (k != null) {
			k.setDeleted(1);
			likeMapper.updateById(k);
		}
	}

	public void favorite(Long knowledgeId, Long userId) {
		LambdaQueryWrapper<KnowledgeFavorite> w = new LambdaQueryWrapper<>();
		w.eq(KnowledgeFavorite::getKnowledgeId, knowledgeId).eq(KnowledgeFavorite::getUserId, userId).eq(KnowledgeFavorite::getDeleted, 0);
		if (favoriteMapper.selectCount(w) > 0) {
			throw new BusinessException("已收藏");
		}
		KnowledgeFavorite f = new KnowledgeFavorite();
		f.setKnowledgeId(knowledgeId);
		f.setUserId(userId);
		f.setCreatedTime(LocalDateTime.now());
		f.setDeleted(0);
		favoriteMapper.insert(f);
	}

	public void unfavorite(Long knowledgeId, Long userId) {
		LambdaQueryWrapper<KnowledgeFavorite> w = new LambdaQueryWrapper<>();
		w.eq(KnowledgeFavorite::getKnowledgeId, knowledgeId).eq(KnowledgeFavorite::getUserId, userId).eq(KnowledgeFavorite::getDeleted, 0);
		KnowledgeFavorite f = favoriteMapper.selectOne(w);
		if (f != null) {
			f.setDeleted(1);
			favoriteMapper.updateById(f);
		}
	}

	public void feedback(Long knowledgeId, Long userId, String content) {
		KnowledgeFeedback fb = new KnowledgeFeedback();
		fb.setKnowledgeId(knowledgeId);
		fb.setUserId(userId);
		fb.setContent(content);
		fb.setCreatedTime(LocalDateTime.now());
		fb.setDeleted(0);
		feedbackMapper.insert(fb);
	}

	public int countLikes(Long knowledgeId) {
		LambdaQueryWrapper<KnowledgeLike> w = new LambdaQueryWrapper<>();
		w.eq(KnowledgeLike::getKnowledgeId, knowledgeId).eq(KnowledgeLike::getDeleted, 0);
		return likeMapper.selectCount(w).intValue();
	}

	public int countFavorites(Long knowledgeId) {
		LambdaQueryWrapper<KnowledgeFavorite> w = new LambdaQueryWrapper<>();
		w.eq(KnowledgeFavorite::getKnowledgeId, knowledgeId).eq(KnowledgeFavorite::getDeleted, 0);
		return favoriteMapper.selectCount(w).intValue();
	}
}


