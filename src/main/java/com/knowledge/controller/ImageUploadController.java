package com.knowledge.controller;

import com.knowledge.vo.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.ByteArrayOutputStream;
import java.net.URLEncoder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * 图片上传控制器
 * 专门处理知识描述中的图片上传和下载
 */
@Slf4j
@RestController
@RequestMapping("/api/images")
@Tag(name = "图片管理", description = "知识描述图片上传和下载相关接口")
public class ImageUploadController {
    
    @Value("${app.image-upload-dir:uploads/images}")
    private String imageUploadDir;
    
    // 支持的图片格式
    private static final String[] ALLOWED_IMAGE_EXTENSIONS = {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"
    };
    
    // 最大文件大小 (10MB)
    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024;

    @PostMapping("/upload")
    @Operation(summary = "上传图片", description = "上传图片文件，返回下载地址")
    public ApiResponse<Map<String, Object>> uploadImage(
            @Parameter(description = "图片文件", required = true) @RequestParam("file") MultipartFile file) {
        
        try {
            // 验证文件
            if (file == null || file.isEmpty()) {
                return ApiResponse.error("请选择要上传的图片文件");
            }
            
            // 检查文件大小
            if (file.getSize() > MAX_FILE_SIZE) {
                return ApiResponse.error("图片文件大小不能超过10MB");
            }
            
            // 检查文件类型
            String originalFilename = file.getOriginalFilename();
            if (originalFilename == null || originalFilename.isEmpty()) {
                return ApiResponse.error("文件名不能为空");
            }
            
            String fileExtension = getFileExtension(originalFilename).toLowerCase();
            boolean isAllowedImage = false;
            for (String allowedExt : ALLOWED_IMAGE_EXTENSIONS) {
                if (fileExtension.equals(allowedExt)) {
                    isAllowedImage = true;
                    break;
                }
            }
            
            if (!isAllowedImage) {
                return ApiResponse.error("不支持的图片格式，支持的格式：jpg, jpeg, png, gif, bmp, tiff, webp, svg");
            }
            
            // 创建上传目录
            Path uploadPath = Paths.get(imageUploadDir).toAbsolutePath().normalize();
            Files.createDirectories(uploadPath);
            
            // 生成唯一文件名
            String uniqueFilename = UUID.randomUUID().toString().replace("-", "") + "_" + originalFilename;
            Path targetPath = uploadPath.resolve(uniqueFilename);
            
            // 保存文件
            Files.copy(file.getInputStream(), targetPath);
            
            // 构建下载URL
            String downloadUrl = "/api/images/download/" + uniqueFilename;
            
            // 返回结果
            Map<String, Object> result = new HashMap<>();
            result.put("originalName", originalFilename);
            result.put("fileName", uniqueFilename);
            result.put("fileSize", file.getSize());
            result.put("fileType", file.getContentType());
            result.put("downloadUrl", downloadUrl);
            result.put("uploadTime", System.currentTimeMillis());
            
            log.info("图片上传成功: originalName={}, fileName={}, size={}", 
                    originalFilename, uniqueFilename, file.getSize());
            
            return ApiResponse.success("图片上传成功", result);
            
        } catch (Exception e) {
            log.error("图片上传失败: {}", e.getMessage(), e);
            return ApiResponse.error("图片上传失败: " + e.getMessage());
        }
    }
    
    @GetMapping("/download/{fileName}")
    @Operation(summary = "下载图片", description = "根据文件名下载图片")
    public ResponseEntity<byte[]> downloadImage(
            @Parameter(description = "文件名", required = true) @PathVariable String fileName) {
        
        try {
            // 验证文件名安全性
            if (fileName == null || fileName.isEmpty() || fileName.contains("..") || fileName.contains("/")) {
                return ResponseEntity.badRequest().build();
            }
            
            // 构建文件路径
            Path filePath = Paths.get(imageUploadDir).toAbsolutePath().normalize().resolve(fileName);
            
            // 检查文件是否存在
            if (!Files.exists(filePath) || !Files.isRegularFile(filePath)) {
                log.warn("图片文件不存在: {}", fileName);
                return ResponseEntity.notFound().build();
            }
            
            // 读取文件
            byte[] fileBytes = Files.readAllBytes(filePath);
            
            // 确定Content-Type
            String contentType = getContentType(fileName);
            
            // 设置响应头
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.parseMediaType(contentType));
            headers.setContentLength(fileBytes.length);
            headers.setCacheControl("public, max-age=31536000"); // 缓存1年
            
            // 设置文件名（URL编码）
            String encodedFileName = URLEncoder.encode(fileName, "UTF-8");
            headers.setContentDispositionFormData("inline", encodedFileName);
            
            log.info("图片下载成功: fileName={}, size={}", fileName, fileBytes.length);
            
            return ResponseEntity.ok()
                    .headers(headers)
                    .body(fileBytes);
                    
        } catch (Exception e) {
            log.error("图片下载失败: fileName={}, error={}", fileName, e.getMessage(), e);
            return ResponseEntity.internalServerError().build();
        }
    }
    
    @DeleteMapping("/{fileName}")
    @Operation(summary = "删除图片", description = "根据文件名删除图片")
    public ApiResponse<Void> deleteImage(
            @Parameter(description = "文件名", required = true) @PathVariable String fileName) {
        
        try {
            // 验证文件名安全性
            if (fileName == null || fileName.isEmpty() || fileName.contains("..") || fileName.contains("/")) {
                return ApiResponse.error("无效的文件名");
            }
            
            // 构建文件路径
            Path filePath = Paths.get(imageUploadDir).toAbsolutePath().normalize().resolve(fileName);
            
            // 检查文件是否存在
            if (!Files.exists(filePath) || !Files.isRegularFile(filePath)) {
                return ApiResponse.error("图片文件不存在");
            }
            
            // 删除文件
            Files.delete(filePath);
            
            log.info("图片删除成功: fileName={}", fileName);
            
            return ApiResponse.success("图片删除成功", null);
            
        } catch (Exception e) {
            log.error("图片删除失败: fileName={}, error={}", fileName, e.getMessage(), e);
            return ApiResponse.error("图片删除失败: " + e.getMessage());
        }
    }
    
    /**
     * 获取文件扩展名
     */
    private String getFileExtension(String filename) {
        int lastDotIndex = filename.lastIndexOf('.');
        if (lastDotIndex > 0 && lastDotIndex < filename.length() - 1) {
            return filename.substring(lastDotIndex);
        }
        return "";
    }
    
    /**
     * 根据文件名获取Content-Type
     */
    private String getContentType(String filename) {
        String extension = getFileExtension(filename).toLowerCase();
        switch (extension) {
            case ".jpg":
            case ".jpeg":
                return "image/jpeg";
            case ".png":
                return "image/png";
            case ".gif":
                return "image/gif";
            case ".bmp":
                return "image/bmp";
            case ".tiff":
                return "image/tiff";
            case ".webp":
                return "image/webp";
            case ".svg":
                return "image/svg+xml";
            default:
                return "application/octet-stream";
        }
    }
}
