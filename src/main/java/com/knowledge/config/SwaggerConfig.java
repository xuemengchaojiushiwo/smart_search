package com.knowledge.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * OpenAPI配置�?
 * 提供API文档和调试功�?
 */
@Configuration
public class SwaggerConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("知识库管理系�?API")
                        .description("知识库管理系统的RESTful API接口文档")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("开发团�?")
                                .url("http://localhost:8080")
                                .email("dev@example.com")));
    }
}
