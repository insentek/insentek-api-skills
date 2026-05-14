package com.insentek.openapi.model;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

@TableName("eco_api_auth")
@Data
public class EcoApiAuth implements Serializable {

    @TableId
    private Integer id;
    private String name;
    private String token;
    private int uid;
    private String ipAllow;
    private Boolean debug;
    @JSONField(format = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime createTime;
    @JSONField(format = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime updateTime;
    private String appid;
    private String appsecret;
    private String notify_url;
    @JSONField(format = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime lastModifyTime;
}
