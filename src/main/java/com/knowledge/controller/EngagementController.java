package com.knowledge.controller;

import com.knowledge.service.EngagementService;
import com.knowledge.vo.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/engagement")
@Tag(name = "知识互动", description = "点赞/收藏/反馈接口")
public class EngagementController {

	@Autowired
	private EngagementService engagementService;

	@PostMapping("/like/{knowledgeId}")
	@Operation(summary = "点赞")
	public ApiResponse<Void> like(@PathVariable Long knowledgeId, @RequestParam(defaultValue = "1") Long userId) {
		engagementService.like(knowledgeId, userId);
		return ApiResponse.success(null);
	}

	@PostMapping("/unlike/{knowledgeId}")
	@Operation(summary = "取消点赞")
	public ApiResponse<Void> unlike(@PathVariable Long knowledgeId, @RequestParam(defaultValue = "1") Long userId) {
		engagementService.unlike(knowledgeId, userId);
		return ApiResponse.success(null);
	}

	@PostMapping("/favorite/{knowledgeId}")
	@Operation(summary = "收藏")
	public ApiResponse<Void> favorite(@PathVariable Long knowledgeId, @RequestParam(defaultValue = "1") Long userId) {
		engagementService.favorite(knowledgeId, userId);
		return ApiResponse.success(null);
	}

	@PostMapping("/unfavorite/{knowledgeId}")
	@Operation(summary = "取消收藏")
	public ApiResponse<Void> unfavorite(@PathVariable Long knowledgeId, @RequestParam(defaultValue = "1") Long userId) {
		engagementService.unfavorite(knowledgeId, userId);
		return ApiResponse.success(null);
	}

	@PostMapping("/feedback/{knowledgeId}")
	@Operation(summary = "提交反馈")
	public ApiResponse<Void> feedback(
			@PathVariable Long knowledgeId,
			@Parameter(description = "反馈内容") @RequestParam(required = false) String content,
			@RequestParam(defaultValue = "1") Long userId) {
		engagementService.feedback(knowledgeId, userId, content);
		return ApiResponse.success(null);
	}
}


