package com.insentek.openapi.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.insentek.openapi.mapper.EcoApiAuthMapper;
import com.insentek.openapi.model.EcoApiAuth;
import com.insentek.openapi.service.EcoApiAuthService;
import org.springframework.stereotype.Service;

@Service
public class EcoApiAuthServiceImpl extends ServiceImpl<EcoApiAuthMapper, EcoApiAuth> implements EcoApiAuthService {

    @Override
    public EcoApiAuth getAuthByAppId(String appid, String secret) {
        return this.getOne(
                new LambdaQueryWrapper<EcoApiAuth>()
                        .eq(EcoApiAuth::getAppid, appid)
                        .eq(EcoApiAuth::getAppsecret, secret)
        );
    }

    @Override
    public EcoApiAuth getAuthByUid(Integer uid) {
        return this.getOne(
                new LambdaQueryWrapper<EcoApiAuth>()
                        .eq(EcoApiAuth::getUid, uid)
        );
    }

    @Override
    public EcoApiAuth getAuthByToken(String token) {
        return this.getOne(
                new LambdaQueryWrapper<EcoApiAuth>()
                        .eq(EcoApiAuth::getToken, token)
        );
    }
}
