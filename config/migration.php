<?php

return [
    // 默认数据库连接标识
    'default'     => 'mysql',
    // 数据库连接配置信息
    'connections' => [
        'mysql' => [
            // 数据库类型
            'type'     => 'mysql',
            // 服务器地址
            'hostname' => '127.0.0.1',
            // 数据库名
            'database' => 'order_management',
            // 用户名
            'username' => 'root',
            // 密码
            'password' => '',
            // 端口
            'hostport' => '3306',
            // 数据库编码默认采用utf8mb4
            'charset'  => 'utf8mb4',
            // 数据库表前缀
            'prefix'   => '',
        ],
    ],
];
