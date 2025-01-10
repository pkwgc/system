<?php

return [
    // 默认使用的数据库连接配置
    'default'         => 'sqlite',

    // 自动写入时间戳字段
    'auto_timestamp'  => true,

    // 时间字段取出后的默认时间格式
    'datetime_format' => 'Y-m-d H:i:s',

    // 数据库连接配置信息
    'connections'     => [
        'sqlite' => [
            // 数据库类型
            'type'            => 'sqlite',
            // 数据库文件路径
            'database'        => '/home/ubuntu/projects/order-management/order-api/database/database.sqlite',
            // 数据库表前缀
            'prefix'          => '',
            // 是否严格检查字段是否存在
            'fields_strict'   => true,
            // 监听SQL
            'trigger_sql'     => true,
            // 开启字段缓存
            'fields_cache'    => false,
        ],

        // 更多的数据库配置信息
    ],
];
