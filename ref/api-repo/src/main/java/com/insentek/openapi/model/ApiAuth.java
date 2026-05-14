package com.insentek.openapi.model;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.io.Serializable;

@TableName("m2m_user_auth")
@Data
public class ApiAuth implements Serializable {

    @TableId
    private Integer uId;
    private String authCode;
    private Integer dataNotify;
    private String notifyUrl;
    private Integer type;
    private String events;
    private String accessId;
    private String emails;
    private Integer enablePushV2;
}
