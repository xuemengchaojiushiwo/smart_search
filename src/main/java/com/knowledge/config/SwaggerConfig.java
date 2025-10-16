package com.knowledge.config;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * OpenAPI配置
 * 提供API文档和调试功能
 */
@Configuration
public class SwaggerConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        final String securitySchemeName = "bearerAuth";
        
        return new OpenAPI()
                .info(new Info()
                        .title("知识库管理系统 API")
                        .description("知识库管理系统的RESTful API接口文档\n\n" +
                                "**使用说明：**\n" +
                                "1. 先调用 `/api/auth/login` 接口登录获取token\n" +
                                "2. 点击右上角的 `Authorize` 按钮\n" +
                                "3. 在弹出框中输入 `Bearer {token}` (注意Bearer后面有空格)\n" +
                                "4. 点击 `Authorize` 完成授权\n" +
                                "5. 之后所有接口调用都会自动携带token")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("开发团队")
                                .url("http://localhost:8080")
                                .email("dev@example.com")))
                .addSecurityItem(new SecurityRequirement().addList(securitySchemeName))
                .components(new Components()
                        .addSecuritySchemes(securitySchemeName,
                                new SecurityScheme()
                                        .name(securitySchemeName)
                                        .type(SecurityScheme.Type.HTTP)
                                        .scheme("bearer")
                                        .bearerFormat("JWT")
                                        .description("JWT认证，格式：Bearer {token}")));
    }
}
