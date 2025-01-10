<?php

return [
    // 默认数据库连接标识
    'default'     => 'sqlite',
    // 数据库连接配置信息
    'connections' => [
        'sqlite' => [
            // 数据库类型
            'type'     => 'sqlite',
            // 数据库文件路径
            'database' => '/home/ubuntu/projects/order-management/order-api/database/database.sqlite',
            // 数据库表前缀
            'prefix'   => '',
        ],
    ],
];
