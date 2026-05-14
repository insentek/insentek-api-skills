package com.insentek.openapi.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.insentek.openapi.model.EcoApiAuth;

public interface EcoApiAuthService extends IService<EcoApiAuth> {

    EcoApiAuth getAuthByAppId(String appid, String secret);

    EcoApiAuth getAuthByUid(Integer uid);

    EcoApiAuth getAuthByToken(String token);
}
