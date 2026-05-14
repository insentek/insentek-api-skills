package com.insentek.openapi.model;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

@TableName("eco_api_last_sync")
@Data
public class ApiSync implements Serializable {

    private Integer id;
    private Integer uid;
    private String sn;
    @JSONField(format = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime lastCallTime;
    @JSONField(format = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime lastDataTime;
    private Integer appId;
}
